import base64
import hashlib
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from evidence.capture import capture_png, normalize_selection
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

        self.assertEqual(loaded["schema_version"], 1)
        self.assertEqual(loaded["name"], "Profile header")
        self.assertEqual(loaded["capture"]["scope"], "region")
        self.assertEqual(loaded["artifacts"][0]["sha256"], "a" * 64)


if __name__ == "__main__":
    unittest.main()
