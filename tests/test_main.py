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
    _archive_page,
    _attach_selection_to_graph_entity,
    _apply_settings_to_tabs,
    _cached_history_payload,
    _capture_evidence,
    _consume_settings_change,
    _create_graph_entity_from_selection,
    _default_capture_name,
    _delete_evidence_capture,
    _delete_investigation_export,
    _install_and_consume_save_overlay,
    _investigation_payload,
    _is_external_web_tab,
    _log_level_from_args,
    _open_or_refresh_investigation_page,
    _prepare_base_query,
    _retry_search_combination,
    _verify_evidence_capture,
    apply_cli_runtime_overrides,
    configure_event_loop_policy,
    parse_cli_args,
    wait_for_home_action,
)
from settings import get_settings


class MainCliTestCase(unittest.TestCase):
    def test_automatic_dorks_can_be_disabled(self):
        self.assertEqual(
            _prepare_base_query("john doe", automatic_dorks=True),
            '"john doe"',
        )
        self.assertEqual(
            _prepare_base_query("john doe", automatic_dorks=False),
            "john doe",
        )
        self.assertEqual(
            _prepare_base_query('"john doe" site:example.com'),
            '"john doe" site:example.com',
        )

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


class SettingsSynchronizationTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_settings_change_is_consumed_from_i18n_bridge(self):
        tab = SimpleNamespace(
            evaluate=AsyncMock(return_value={"language": "de", "theme": "dark"})
        )

        settings = await _consume_settings_change(tab)

        self.assertEqual(settings, {"language": "de", "theme": "dark"})
        self.assertIn("consumeSettingsChange", tab.evaluate.await_args.args[0])

    async def test_settings_are_applied_only_to_other_synthesix_tabs(self):
        source = SimpleNamespace(url="file:///app/index.html", evaluate=AsyncMock())
        report = SimpleNamespace(url="file:///app/report.html", evaluate=AsyncMock())
        external = SimpleNamespace(
            url="https://example.com/",
            evaluate=AsyncMock(),
        )

        await _apply_settings_to_tabs(
            [source, report, external],
            {"language": "pt", "theme": "light"},
            source_tab=source,
        )

        source.evaluate.assert_not_awaited()
        external.evaluate.assert_not_awaited()
        report.evaluate.assert_awaited_once()
        script = report.evaluate.await_args.args[0]
        self.assertIn("applySettings", script)
        self.assertIn('"language": "pt"', script)
        self.assertIn('"theme": "light"', script)


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
    async def test_capture_evidence_records_png_only(self):
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            service = SimpleNamespace(
                get=Mock(return_value=SimpleNamespace(status="active")),
                save_page=Mock(
                    return_value=SimpleNamespace(
                        id="result-1",
                        url="https://example.com/",
                        title="Example",
                    )
                ),
                record_evidence_capture=Mock(
                    return_value=SimpleNamespace(capture_scope="viewport")
                ),
            )
            settings = SimpleNamespace(
                base_dir=base_dir,
                evidence_dir=base_dir / "data" / "evidence",
            )
            png = SimpleNamespace(
                sha256="a" * 64,
                byte_size=100,
                width=800,
                height=600,
            )
            captured_html = SimpleNamespace(
                sha256="b" * 64,
                byte_size=200,
            )
            capture_html_mock = AsyncMock(return_value=captured_html)
            capture_mhtml_mock = AsyncMock(return_value=captured_html)

            with (
                patch("main.capture_png", AsyncMock(return_value=png)),
                patch("main.capture_html", capture_html_mock),
                patch("main.capture_mhtml", capture_mhtml_mock),
            ):
                await _capture_evidence(
                    service,
                    settings,
                    object(),
                    "case-1",
                    {
                        "captureScope": "viewport",
                        "captureName": "Homepage",
                        "selection": {
                            "x": 0,
                            "y": 0,
                            "width": 800,
                            "height": 600,
                        },
                        "page": {"browserContext": {}},
                    },
                )

            recorded = service.record_evidence_capture.call_args.kwargs
            artifact_types = {
                artifact["artifact_type"]
                for artifact in recorded["artifacts"]
            }
            manifest = json.loads(
                (
                    base_dir
                    / recorded["manifest_path"]
                ).read_text(encoding="utf-8")
            )

        self.assertEqual(artifact_types, {"png"})
        self.assertEqual(recorded["capture_kind"], "screenshot")
        self.assertEqual(manifest["schema_version"], 3)
        self.assertEqual(manifest["capture"]["kind"], "screenshot")
        self.assertEqual(
            {artifact["type"] for artifact in manifest["artifacts"]},
            {"png"},
        )
        capture_html_mock.assert_not_awaited()
        capture_mhtml_mock.assert_not_awaited()

    async def test_archive_page_records_html_text_and_partial_mhtml(self):
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)

            def record_capture(**kwargs):
                return SimpleNamespace(
                    id=kwargs["capture_id"],
                    result_id=kwargs["result_id"],
                    source_url=kwargs["source_url"],
                    page_title=kwargs["page_title"],
                    captured_at=kwargs["captured_at"],
                    artifacts=tuple(
                        SimpleNamespace(**artifact)
                        for artifact in kwargs["artifacts"]
                    ),
                )

            service = SimpleNamespace(
                get=Mock(return_value=SimpleNamespace(status="active")),
                save_page=Mock(
                    return_value=SimpleNamespace(
                        id="result-1",
                        url="https://example.com/",
                        title="Example",
                    )
                ),
                record_evidence_capture=Mock(side_effect=record_capture),
                get_page_monitor_for_result=Mock(return_value=None),
            )
            settings = SimpleNamespace(
                base_dir=base_dir,
                evidence_dir=base_dir / "data" / "evidence",
            )

            async def capture_html_document(_tab, output_path):
                output_path.parent.mkdir(parents=True, exist_ok=True)
                content = "<html><body><h1>Example</h1></body></html>"
                output_path.write_text(content, encoding="utf-8")
                return SimpleNamespace(
                    sha256=hashlib.sha256(content.encode()).hexdigest(),
                    byte_size=len(content.encode()),
                )

            with (
                patch(
                    "main.capture_html",
                    AsyncMock(side_effect=capture_html_document),
                ),
                patch(
                    "main.capture_mhtml",
                    AsyncMock(side_effect=RuntimeError("unsupported")),
                ),
                patch(
                    "main._compare_page_archive",
                    AsyncMock(side_effect=RuntimeError("comparison failed")),
                ),
                patch("main.logger.error"),
            ):
                _, _, capture, comparison = await _archive_page(
                    service,
                    settings,
                    object(),
                    "case-1",
                    {"page": {"browserContext": {}}},
                )

            recorded = service.record_evidence_capture.call_args.kwargs
            manifest = json.loads(
                (base_dir / recorded["manifest_path"]).read_text(
                    encoding="utf-8"
                )
            )

        self.assertIsNone(comparison)
        self.assertEqual(capture.id, recorded["capture_id"])
        self.assertEqual(
            {artifact["artifact_type"] for artifact in recorded["artifacts"]},
            {"html", "text"},
        )
        self.assertEqual(recorded["capture_kind"], "page_archive")
        self.assertEqual(recorded["status"], "partial")
        self.assertIn("MHTML archive unavailable", recorded["error"])
        self.assertEqual(manifest["capture"]["kind"], "page_archive")

    async def test_verify_evidence_checks_every_artifact(self):
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            evidence_dir = base_dir / "data" / "evidence"
            capture_dir = evidence_dir / "case-1" / "capture-1"
            capture_dir.mkdir(parents=True)
            png_path = capture_dir / "capture.png"
            html_path = capture_dir / "page.html"
            png_path.write_bytes(b"original")
            html_path.write_bytes(b"<html>original</html>")
            service = SimpleNamespace(
                get_evidence_capture=lambda *_args: SimpleNamespace(
                    artifacts=(
                        SimpleNamespace(
                            artifact_type="png",
                            file_path=(
                                "data/evidence/case-1/capture-1/capture.png"
                            ),
                            sha256=hashlib.sha256(b"original").hexdigest(),
                        ),
                        SimpleNamespace(
                            artifact_type="html",
                            file_path=(
                                "data/evidence/case-1/capture-1/page.html"
                            ),
                            sha256=hashlib.sha256(
                                b"<html>original</html>"
                            ).hexdigest(),
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
            html_path.write_bytes(b"<html>modified</html>")
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

    async def test_delete_export_removes_directory_and_database_row(self):
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            export_dir = (
                base_dir
                / "data"
                / "exports"
                / "case-1"
                / "zeroneurone_1"
            )
            export_dir.mkdir(parents=True)
            paths = {}
            for name in (
                "zeroneurone.zip",
                "dossier.json",
                "investigation.graphml",
                "zeroneurone.csv",
                "nodes.csv",
                "edges.csv",
                "manifest.json",
            ):
                path = export_dir / name
                path.write_text("", encoding="utf-8")
                paths[name] = path.relative_to(base_dir).as_posix()
            service = SimpleNamespace(
                get_export=lambda *_args: SimpleNamespace(
                    archive_path=paths["zeroneurone.zip"],
                    dossier_path=paths["dossier.json"],
                    graphml_path=paths["investigation.graphml"],
                    csv_path=paths["zeroneurone.csv"],
                    nodes_csv_path=paths["nodes.csv"],
                    edges_csv_path=paths["edges.csv"],
                    manifest_path=paths["manifest.json"],
                ),
                delete_export=Mock(),
            )
            settings = SimpleNamespace(
                base_dir=base_dir,
                exports_dir=base_dir / "data" / "exports",
            )

            await _delete_investigation_export(
                service,
                settings,
                "case-1",
                "export-1",
            )

            self.assertFalse(export_dir.exists())
            service.delete_export.assert_called_once_with(
                "case-1",
                "export-1",
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
            {
                "id": "case-1",
                "title": "Case One",
                "tags": ["Prioritaire"],
                "graph_entities": [
                    {
                        "id": "entity-1",
                        "label": "Jane Doe",
                        "tags": ["Entreprise", "Source confidentielle"],
                        "properties": {"Alias": "JD"},
                    }
                ],
            },
        )

        self.assertTrue(_is_external_web_tab(tab))
        self.assertEqual(action["action"], "save_page_to_investigation")
        self.assertIn("__synthesix-save-overlay", tab.script)
        self.assertIn("SynthesixOverlay", tab.script)
        self.assertIn("sx-overlay-root", tab.script)
        self.assertIn("sx-overlay-action", tab.script)
        self.assertIn("sx-overlay-capture-menu", tab.script)
        self.assertIn("sx-overlay-selection-trigger", tab.script)
        self.assertIn("data-synthesix-overlay-root", tab.script)
        self.assertIn("data-synthesix-save-page", tab.script)
        self.assertIn("data-synthesix-archive", tab.script)
        self.assertIn("data-synthesix-capture", tab.script)
        self.assertIn("data-synthesix-capture-menu", tab.script)
        self.assertIn("synthesix-overlay-toggle", tab.script)
        self.assertIn("synthesix:external-overlay-collapsed", tab.script)
        self.assertIn("host.__synthesixSaveButton", tab.script)
        self.assertIn("Case One", tab.script)
        self.assertIn("Save page", tab.script)
        self.assertIn("observe_saved_page", tab.script)
        self.assertIn("M58 12 69 6l9 38-12 9-9-7z", tab.script)
        self.assertIn("Capture screenshot", tab.script)
        self.assertIn("Save page with HTML archive", tab.script)
        self.assertIn("archive_page_to_investigation", tab.script)
        self.assertIn("Capture name (optional)", tab.script)
        self.assertIn("captureName", tab.script)
        self.assertIn("screenshot_", tab.script)
        self.assertIn("Visible area", tab.script)
        self.assertIn("Select area", tab.script)
        self.assertIn("capture_evidence_to_investigation", tab.script)
        self.assertIn("__synthesix-evidence-selection", tab.script)
        # The entity tool is now the <sx-overlay-entity-menu> component; main.py
        # only creates it, wires the CDP actions, and injects the context data
        # (the panel internals/selection logic moved into the overlay bundle).
        self.assertIn("sx-overlay-entity-menu", tab.script)
        self.assertIn("tagsetProperties", tab.script)
        self.assertIn("create_graph_entity_from_selection", tab.script)
        self.assertIn("attach_selection_to_graph_entity", tab.script)
        self.assertIn("__synthesixSetGraphEntities", tab.script)
        self.assertIn("__synthesixSetEntityTagsets", tab.script)
        self.assertNotIn('document.addEventListener("contextmenu"', tab.script)
        self.assertIn("SIREN", tab.script)
        self.assertIn("Alias", tab.script)
        self.assertIn("Source confidentielle", tab.script)
        self.assertIn("Personne", tab.script)
        self.assertFalse(_is_external_web_tab(SimpleNamespace(url="file:///index.html")))

    def test_selection_entity_helper_saves_page_and_links_source(self):
        service = Mock()
        investigation = SimpleNamespace(id="case-1", status="active")
        saved = SimpleNamespace(
            id="result-1",
            url="https://example.com/profile",
            title="Profile",
        )
        service.get.return_value = investigation
        service.save_page.return_value = saved
        service.create_graph_entity_from_result.return_value = {
            "id": "entity-1",
            "label": "Jane Doe",
            "tags": ["Personne"],
            "linked_result_ids": ["result-1"],
        }

        returned_investigation, returned_saved, entity = (
            _create_graph_entity_from_selection(
                service,
                "case-1",
                {
                    "entity": {
                        "label": "Jane Doe",
                        "category": "Person",
                    },
                    "page": {
                        "url": "https://example.com/profile",
                        "title": "Profile",
                    },
                },
            )
        )

        self.assertIs(returned_investigation, investigation)
        self.assertIs(returned_saved, saved)
        self.assertEqual(entity["label"], "Jane Doe")
        service.save_page.assert_called_once_with(
            "case-1",
            {
                "url": "https://example.com/profile",
                "title": "Profile",
            },
        )
        service.create_graph_entity_from_result.assert_called_once_with(
            "case-1",
            "result-1",
            {
                "label": "Jane Doe",
                "category": "Person",
                "notes": (
                    "Created from selected text on "
                    "https://example.com/profile"
                ),
            },
        )

    def test_attach_selection_helper_links_source_and_appends_property(self):
        service = Mock()
        investigation = SimpleNamespace(id="case-1", status="active")
        saved = SimpleNamespace(
            id="result-1",
            url="https://example.com/profile",
            title="Profile",
        )
        service.get.return_value = investigation
        service.workspace_payload.return_value = {
            "graph_entities": [
                {
                    "id": "entity-1",
                    "label": "Jane Doe",
                    "properties": {"Alias": "J. Doe"},
                }
            ]
        }
        service.save_page.return_value = saved
        service.set_graph_entity_property.return_value = {
            "id": "entity-1",
            "label": "Jane Doe",
            "properties": {"Alias": "J. Doe; JD"},
        }

        returned_investigation, returned_saved, entity = (
            _attach_selection_to_graph_entity(
                service,
                "case-1",
                "entity-1",
                {
                    "property": {"key": "Alias", "value": "JD"},
                    "page": {"url": "https://example.com/profile"},
                },
            )
        )

        self.assertIs(returned_investigation, investigation)
        self.assertIs(returned_saved, saved)
        self.assertEqual(entity["properties"]["Alias"], "J. Doe; JD")
        service.link_result_to_graph_entity.assert_called_once_with(
            "case-1",
            "entity-1",
            "result-1",
        )
        service.set_graph_entity_property.assert_called_once_with(
            "case-1",
            "entity-1",
            {"key": "Alias", "value": "J. Doe; JD"},
        )

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

    async def test_home_page_action_is_returned_with_source_tab(self):
        class FakeTab:
            url = "file:///tmp/index.html"
            closed = False

            async def evaluate(self, _script):
                return {
                    "ready": True,
                    "action": {
                        "action": "suggest_query_variants",
                        "value": "anna lindberg",
                    },
                }

        tab = FakeTab()
        settings = SimpleNamespace(
            home_poll_interval=0,
            empty_tabs_grace_seconds=0,
            default_history_limit=25,
        )
        with (
            patch("main._open_tabs", return_value=[tab]),
            patch("main._cached_history_payload", return_value=("[]", "")),
        ):
            action = await wait_for_home_action(
                SimpleNamespace(stopped=False),
                "file:///tmp/index.html",
                settings=settings,
            )

        self.assertEqual(action["action"], "suggest_query_variants")
        self.assertIs(action["_source_tab"], tab)

    async def test_retry_search_combination_runs_only_selected_cell(self):
        settings = SimpleNamespace(
            default_engines={
                "google": True,
                "bing": True,
                "brave": True,
                "duckduckgo": True,
            },
            default_max_results=20,
        )
        with patch("main.perform_search", new=AsyncMock(return_value=None)) as search:
            message, is_error = await _retry_search_combination(
                {
                    "query": '"lindberg anna"',
                    "engine": "bing",
                    "originalQuery": "anna lindberg",
                    "filters": {"site": "example.com"},
                    "numResults": 7,
                    "investigationId": "case-1",
                },
                object(),
                settings,
                Mock(),
            )

        self.assertFalse(is_error)
        self.assertEqual(message, "Retry completed for Bing.")
        search.assert_awaited_once()
        call = search.await_args
        self.assertEqual(call.args[0], "anna lindberg")
        self.assertEqual(
            call.args[1],
            '"lindberg anna" site:example.com',
        )
        self.assertEqual(
            call.args[3],
            {
                "google": False,
                "bing": True,
                "brave": False,
                "duckduckgo": False,
            },
        )
        self.assertEqual(call.args[4], 7)
        self.assertEqual(call.kwargs["investigation_id"], "case-1")
        self.assertEqual(call.kwargs["query_variants"], ('"lindberg anna"',))

    async def test_retry_search_combination_rejects_unknown_engine(self):
        settings = SimpleNamespace(
            default_engines={"google": True},
            default_max_results=20,
        )
        with patch("main.perform_search", new=AsyncMock()) as search:
            message, is_error = await _retry_search_combination(
                {"query": "query", "engine": "unknown"},
                object(),
                settings,
                Mock(),
            )

        self.assertTrue(is_error)
        self.assertEqual(
            message,
            "The selected search engine cannot be retried.",
        )
        search.assert_not_awaited()

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
