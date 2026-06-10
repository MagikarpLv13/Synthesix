import asyncio
import hashlib
import json
import logging
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
import unittest
from types import SimpleNamespace
from tempfile import TemporaryDirectory
from unittest.mock import AsyncMock, Mock, patch

from main import (
    _cached_history_payload,
    _default_capture_name,
    _delete_evidence_capture,
    _install_and_consume_save_overlay,
    _investigation_payload,
    _is_external_web_tab,
    _open_or_refresh_investigation_page,
    _log_level_from_args,
    _verify_evidence_capture,
    apply_cli_runtime_overrides,
    configure_event_loop_policy,
    parse_cli_args,
    wait_for_home_action,
)
from settings import get_settings


class MainCliTestCase(unittest.TestCase):
    def test_default_capture_name_uses_timestamp(self):
        self.assertEqual(
            _default_capture_name("2026-06-10T12:34:56.123456+00:00"),
            "screenshot_2026-06-10_12-34-56",
        )

    def test_cli_log_levels(self):
        self.assertEqual(_log_level_from_args(parse_cli_args([])), logging.INFO)
        self.assertEqual(_log_level_from_args(parse_cli_args(["--quiet"])), logging.WARNING)
        self.assertEqual(_log_level_from_args(parse_cli_args(["--verbose"])), logging.DEBUG)

    def test_cli_rejects_conflicting_verbosity_flags(self):
        with redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit):
                parse_cli_args(["--quiet", "--verbose"])

    def test_debug_html_flag_enables_runtime_setting(self):
        args = parse_cli_args(["--debug-html"])

        with patch.dict("os.environ", {}, clear=True):
            apply_cli_runtime_overrides(args)
            settings = get_settings()

        self.assertTrue(settings.debug_html)

    def test_windows_event_loop_policy_is_configured_on_windows(self):
        policy = object()
        with patch("main.sys.platform", "win32"):
            with patch("main.asyncio.WindowsSelectorEventLoopPolicy", return_value=policy, create=True):
                with patch("main.asyncio.set_event_loop_policy") as set_policy:
                    configure_event_loop_policy()

        set_policy.assert_called_once_with(policy)


class HomeHistoryCacheTestCase(unittest.TestCase):
    def test_cached_history_payload_refreshes_when_file_changes(self):
        with TemporaryDirectory() as temp_dir:
            with patch.dict("os.environ", {"SYNTHESIX_BASE_DIR": temp_dir}, clear=True):
                settings = get_settings()

                cache = {}
                history_json, version = _cached_history_payload(settings, cache)
                self.assertEqual(json.loads(history_json), [])
                self.assertEqual(version, "")

                settings.history_json_path.parent.mkdir(parents=True, exist_ok=True)
                settings.history_json_path.write_text(
                    json.dumps([
                        {
                            "date": "2026-06-06 00:00",
                            "query": "first query",
                            "smart_query": '"first query"',
                            "nb_results": 1,
                            "link": "first.html",
                        }
                    ]),
                    encoding="utf-8",
                )

                refreshed_json, refreshed_version = _cached_history_payload(settings, cache)

        self.assertNotEqual(refreshed_version, version)
        self.assertEqual(json.loads(refreshed_json)[0]["query"], "first query")


class InvestigationPayloadTestCase(unittest.TestCase):
    def test_payload_is_stable_and_version_changes_with_content(self):
        class FakeService:
            def __init__(self):
                self.payload = [{"id": "case-1", "title": "Case One"}]

            def list_payload(self, *, include_archived=False):
                self.include_archived = include_archived
                return self.payload

        service = FakeService()
        payload, version = _investigation_payload(service)
        repeated_payload, repeated_version = _investigation_payload(service)

        self.assertEqual(json.loads(payload), service.payload)
        self.assertTrue(service.include_archived)
        self.assertEqual((payload, version), (repeated_payload, repeated_version))

        service.payload = [{"id": "case-1", "title": "Renamed"}]
        changed_payload, changed_version = _investigation_payload(service)

        self.assertNotEqual(changed_payload, payload)
        self.assertNotEqual(changed_version, version)


class InvestigationPageRoutingTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_verify_evidence_detects_file_change(self):
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            evidence_dir = base_dir / "data" / "evidence"
            png_path = evidence_dir / "case-1" / "capture-1" / "capture.png"
            png_path.parent.mkdir(parents=True)
            png_path.write_bytes(b"original")
            expected_hash = hashlib.sha256(b"original").hexdigest()
            service = SimpleNamespace(
                get_evidence_capture=lambda *_args: SimpleNamespace(
                    artifacts=(
                        SimpleNamespace(
                            artifact_type="png",
                            file_path=(
                                "data/evidence/case-1/capture-1/capture.png"
                            ),
                            sha256=expected_hash,
                        ),
                    )
                )
            )
            settings = SimpleNamespace(
                base_dir=base_dir,
                evidence_dir=evidence_dir,
            )

            self.assertTrue(
                await _verify_evidence_capture(
                    service,
                    settings,
                    "case-1",
                    "capture-1",
                )
            )
            png_path.write_bytes(b"modified")
            self.assertFalse(
                await _verify_evidence_capture(
                    service,
                    settings,
                    "case-1",
                    "capture-1",
                )
            )

    async def test_delete_evidence_removes_capture_directory_and_database_row(self):
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            capture_dir = base_dir / "data" / "evidence" / "case-1" / "capture-1"
            capture_dir.mkdir(parents=True)
            manifest_path = capture_dir / "manifest.json"
            manifest_path.write_text("{}", encoding="utf-8")
            service = SimpleNamespace(
                get_evidence_capture=lambda *_args: SimpleNamespace(
                    manifest_path="data/evidence/case-1/capture-1/manifest.json"
                ),
                delete_evidence_capture=Mock(),
            )
            settings = SimpleNamespace(
                base_dir=base_dir,
                evidence_dir=base_dir / "data" / "evidence",
            )

            await _delete_evidence_capture(
                service,
                settings,
                "case-1",
                "capture-1",
            )

            self.assertFalse(capture_dir.exists())
            service.delete_evidence_capture.assert_called_once_with(
                "case-1",
                "capture-1",
            )

    async def test_open_tabs_keeps_live_targets_without_websocket(self):
        from main import _open_tabs

        live_tab = SimpleNamespace(target_id="live", closed=True)
        stale_tab = SimpleNamespace(target_id="stale", closed=False)
        browser = SimpleNamespace(
            tabs=[live_tab, stale_tab],
            update_targets=AsyncMock(),
            _get_targets=AsyncMock(
                return_value=[
                    SimpleNamespace(target_id="live", type_="page"),
                    SimpleNamespace(target_id="worker", type_="service_worker"),
                ]
            ),
        )

        tabs = await _open_tabs(browser)

        self.assertEqual(tabs, [live_tab])
        browser.update_targets.assert_awaited_once()

    async def test_external_page_overlay_returns_save_action(self):
        class FakeTab:
            url = "https://example.com/profile"

            async def evaluate(self, script):
                self.script = script
                return {
                    "action": "save_page_to_investigation",
                    "investigationId": "case-1",
                    "page": {"url": self.url},
                }

        tab = FakeTab()
        action = await _install_and_consume_save_overlay(
            tab,
            {"id": "case-1", "title": "Case One"},
        )

        self.assertTrue(_is_external_web_tab(tab))
        self.assertEqual(action["action"], "save_page_to_investigation")
        self.assertIn("__synthesix-save-overlay", tab.script)
        self.assertIn("Case One", tab.script)
        self.assertIn("Save page", tab.script)
        self.assertIn("observe_saved_page", tab.script)
        self.assertIn("M58 12 69 6l9 38-12 9-9-7z", tab.script)
        self.assertIn("Capture evidence", tab.script)
        self.assertIn("Capture name (optional)", tab.script)
        self.assertIn("captureName", tab.script)
        self.assertIn("screenshot_", tab.script)
        self.assertIn("Visible area", tab.script)
        self.assertIn("Select area", tab.script)
        self.assertIn("capture_evidence_to_investigation", tab.script)
        self.assertIn("__synthesix-evidence-selection", tab.script)
        self.assertFalse(_is_external_web_tab(SimpleNamespace(url="file:///index.html")))

    async def test_external_page_overlay_can_focus_home_without_active_case(self):
        class FakeTab:
            url = "https://example.com/profile"

            async def evaluate(self, script):
                self.script = script
                return {"action": "focus_home"}

        tab = FakeTab()
        action = await _install_and_consume_save_overlay(tab)

        self.assertEqual(action["action"], "focus_home")
        self.assertIn("Select investigation", tab.script)
        self.assertNotIn("shadow.innerHTML", tab.script)

    async def test_external_tab_gets_overlay_without_active_case(self):
        tab = SimpleNamespace(url="https://example.com/", closed=False)
        settings = SimpleNamespace(
            home_poll_interval=0,
            empty_tabs_grace_seconds=0,
            default_history_limit=25,
        )
        install_overlay = AsyncMock(return_value={"action": "focus_home"})
        focus_home = AsyncMock()
        with (
            patch("main._open_tabs", return_value=[tab]),
            patch(
                "main._install_and_consume_save_overlay",
                new=install_overlay,
            ),
            patch("main._focus_or_open_home_tab", new=focus_home),
        ):
            browser = SimpleNamespace(stopped=False)
            with self.assertRaises(asyncio.TimeoutError):
                await asyncio.wait_for(
                    wait_for_home_action(
                        browser,
                        "file:///tmp/index.html",
                        settings=settings,
                    ),
                    timeout=0.01,
                )

        install_overlay.assert_awaited()
        focus_home.assert_awaited()

    async def test_non_home_page_action_is_returned_with_source_tab(self):
        class FakeTab:
            url = "file:///tmp/case.html"
            closed = False

            async def evaluate(self, _script):
                return {
                    "action": "update_investigation_result",
                    "investigationId": "case-1",
                    "resultId": "result-1",
                }

        tab = FakeTab()
        settings = SimpleNamespace(
            home_poll_interval=0,
            empty_tabs_grace_seconds=0,
            default_history_limit=25,
        )
        with patch("main._open_tabs", return_value=[tab]):
            action = await wait_for_home_action(
                SimpleNamespace(stopped=False),
                "file:///tmp/index.html",
                settings=settings,
            )

        self.assertEqual(action["action"], "update_investigation_result")
        self.assertIs(action["_source_tab"], tab)

    async def test_refresh_does_not_open_missing_investigation_tab(self):
        browser = SimpleNamespace()
        browser.get = AsyncMock()

        with patch("main._open_tabs", return_value=[]):
            await _open_or_refresh_investigation_page(
                browser,
                Path("missing.html"),
                bring_to_front=False,
                open_if_missing=False,
            )

        browser.get.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
