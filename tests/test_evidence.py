import base64
import hashlib
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from evidence.capture import (
    capture_html,
    capture_mhtml,
    capture_png,
    normalize_selection,
    normalize_html_text,
    sanitize_html,
    sanitize_mhtml,
)
from evidence.changes import compare_page_text
from evidence.hashing import sha256_file
from evidence.manifest import build_evidence_manifest, write_manifest


class EvidenceCaptureTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_captures_png_and_calculates_sha256(self):
        content = b"\x89PNG\r\n\x1a\nsynthetic"

        class FakeTab:
            async def send(self, command):
                self.command = command
                return base64.b64encode(content).decode("ascii")

        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "capture.png"
            tab = FakeTab()
            captured = await capture_png(
                tab,
                output_path,
                {"x": 10, "y": 20, "width": 300, "height": 200},
            )

            self.assertEqual(output_path.read_bytes(), content)

        self.assertEqual(captured.sha256, hashlib.sha256(content).hexdigest())
        self.assertEqual(captured.byte_size, len(content))
        self.assertEqual(captured.width, 300)
        self.assertEqual(captured.height, 200)

    def test_rejects_too_small_selection(self):
        with self.assertRaises(ValueError):
            normalize_selection(
                {"x": 0, "y": 0, "width": 4, "height": 4}
            )

    async def test_captures_sanitized_html(self):
        content = (
            '<!DOCTYPE html><html><body><input name="csrf_token" '
            'value="LEAK"><p>Public</p></body></html>'
        )

        class FakeTab:
            def __init__(self):
                self.calls = 0

            async def send(self, command):
                self.calls += 1
                if self.calls == 1:
                    return SimpleNamespace(node_id=1)
                return content

        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "page.html"
            captured = await capture_html(FakeTab(), output_path)
            written = output_path.read_text(encoding="utf-8")

        self.assertNotIn("LEAK", written)
        self.assertIn("[REDACTED]", written)
        self.assertIn("<p>Public</p>", written)
        self.assertEqual(captured.sha256, hashlib.sha256(written.encode()).hexdigest())

    async def test_captures_sanitized_mhtml(self):
        content = (
            "Content-Type: multipart/related\r\n"
            "Cookie: session=LEAK\r\n"
            "\tcontinued-secret\r\n"
            "Authorization: Bearer LEAK\r\n"
            "\r\n"
            "Public body\r\n"
        )

        class FakeTab:
            async def send(self, command):
                return content

        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "page.mhtml"
            captured = await capture_mhtml(FakeTab(), output_path)
            written_bytes = output_path.read_bytes()
            written = written_bytes.decode("utf-8")

        self.assertNotIn("LEAK", written)
        self.assertNotIn("continued-secret", written)
        self.assertIn("Content-Type: multipart/related", written)
        self.assertIn("Public body", written)
        self.assertEqual(captured.byte_size, len(written_bytes))


class EvidenceSanitizationTestCase(unittest.TestCase):
    def test_redacts_sensitive_form_fields_and_preserves_public_values(self):
        content = (
            '<svg viewBox="0 0 10 10"><linearGradient id="PublicGradient">'
            "</linearGradient></svg>"
            '<input type="password" value="PASSWORD">'
            '<textarea id="session_token">SESSION</textarea>'
            '<meta name="csrf-token" content="CSRF">'
            '<input name="display_name" value="Public">'
        )

        sanitized = sanitize_html(content)

        self.assertNotIn("PASSWORD", sanitized)
        self.assertNotIn("SESSION", sanitized)
        self.assertNotIn("CSRF", sanitized)
        self.assertIn('value="Public"', sanitized)
        self.assertIn('viewBox="0 0 10 10"', sanitized)
        self.assertIn("<linearGradient", sanitized)

    def test_normalizes_visible_text_without_script_noise(self):
        normalized = normalize_html_text(
            "<html><style>hidden</style><body><h1>Hello</h1>"
            "<script>noise()</script><p>world</p></body></html>"
        )

        self.assertEqual(normalized, "Hello world")

    def test_removes_sensitive_mhtml_headers(self):
        content = (
            "Content-Type: text/html\n"
            "Set-Cookie: session=COOKIE\n"
            "X-Api-Key: APIKEY\n"
            "\n"
            "<html>Public</html>\n"
        )

        sanitized = sanitize_mhtml(content)

        self.assertNotIn("COOKIE", sanitized)
        self.assertNotIn("APIKEY", sanitized)
        self.assertIn("Content-Type: text/html", sanitized)
        self.assertIn("<html>Public</html>", sanitized)


class EvidenceManifestTestCase(unittest.TestCase):
    def test_writes_versioned_manifest(self):
        manifest = build_evidence_manifest(
            capture_id="capture-1",
            investigation_id="case-1",
            result_id="result-1",
            name="Profile header",
            captured_at="2026-06-10T10:00:00+00:00",
            source_url="https://example.com/",
            page_title="Example",
            capture_scope="region",
            selection={"x": 1, "y": 2, "width": 3, "height": 4},
            browser_context={"user_agent": "Test"},
            tool_version="test",
            status="partial",
            errors=["MHTML capture unavailable."],
            artifacts=[
                {
                    "type": "png",
                    "sha256": "a" * 64,
                    "byte_size": 123,
                }
            ],
        )

        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "manifest.json"
            write_manifest(output_path, manifest)
            loaded = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(loaded["schema_version"], 3)
        self.assertEqual(loaded["capture"]["kind"], "screenshot")
        self.assertEqual(loaded["name"], "Profile header")
        self.assertEqual(loaded["capture"]["scope"], "region")
        self.assertEqual(loaded["status"], "partial")
        self.assertEqual(loaded["errors"], ["MHTML capture unavailable."])
        self.assertEqual(loaded["artifacts"][0]["sha256"], "a" * 64)

    def test_hashes_file_content(self):
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "capture.png"
            path.write_bytes(b"evidence")
            digest = sha256_file(path)

        self.assertEqual(
            digest,
            hashlib.sha256(b"evidence").hexdigest(),
        )


class PageChangeTestCase(unittest.TestCase):
    def test_separates_minor_and_significant_text_changes(self):
        base = " ".join(f"word-{index}" for index in range(500))

        minor = compare_page_text(base, base + " updated")
        changed = compare_page_text(base, "Completely different page content")
        unchanged = compare_page_text(base, base)

        self.assertEqual(minor.status, "minor_change")
        self.assertEqual(changed.status, "changed")
        self.assertEqual(unchanged.status, "unchanged")
        self.assertEqual(unchanged.similarity, 1.0)


if __name__ == "__main__":
    unittest.main()
