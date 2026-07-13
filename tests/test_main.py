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
    _extension_overlay_context_payload,
    _slugify,
    _delete_evidence_capture,
    _delete_investigation_export,
    _install_and_consume_save_overlay,
    _investigation_payload,
    _is_external_web_tab,
    _normalize_dispatch_action,
    _overlay_injection_blocked,
    _log_level_from_args,
    _open_or_refresh_investigation_page,
    _reload_workspace_from_sidecar,
    _save_in_place,
    perform_search,
    _prepare_base_query,
    _retry_search_combination,
    _run_retry_search_action,
    _run_search_action,
    _search_task_running,
    _set_overlay_save_status,
    _start_search_task,
    _sync_extension_overlay_context,
    _verify_evidence_capture,
    apply_cli_runtime_overrides,
    configure_event_loop_policy,
    InvestigationPayloadCache,
    parse_cli_args,
    SearchBrowserProvider,
    wait_for_home_action,
)
from browser import BrowserService, get_browser_service
from exceptions import InvestigationValidationError, RobotChallengeError
from settings import get_settings


class OverlayInjectionGuardTestCase(unittest.TestCase):
    def test_blocks_lens_and_maps(self):
        self.assertTrue(
            _overlay_injection_blocked("https://lens.google.com/search")
        )
        self.assertTrue(
            _overlay_injection_blocked("https://maps.google.com/?q=x")
        )
        self.assertTrue(
            _overlay_injection_blocked("https://www.google.fr/maps/place/Paris")
        )

    def test_allows_regular_pages(self):
        self.assertFalse(
            _overlay_injection_blocked("https://example.com/article")
        )
        self.assertFalse(
            _overlay_injection_blocked("https://www.google.com/search?q=x")
        )

    def test_installer_skips_blocked_tab(self):
        tab = SimpleNamespace(url="https://lens.google.com/")
        self.assertIsNone(
            asyncio.run(
                _install_and_consume_save_overlay(BrowserService(None), tab)
            )
        )


class OverlayBundleReuseTestCase(unittest.TestCase):
    def _last_eval_script(self, already_loaded):
        scripts = []

        class Tab:
            url = "https://example.com/article"

            async def evaluate(self, script):
                scripts.append(script)
                if "!!window.SynthesixOverlay" in script:
                    return already_loaded
                return None

        asyncio.run(
            _install_and_consume_save_overlay(BrowserService(None), Tab())
        )
        # The first eval is the cheap pre-check, the last is the install/poll.
        self.assertGreaterEqual(len(scripts), 2)
        self.assertIn("!!window.SynthesixOverlay", scripts[0])
        return scripts[-1]

    def test_skips_bundle_when_already_loaded(self):
        self.assertIn('const overlayBundle = ""', self._last_eval_script(True))

    def test_ships_bundle_when_not_loaded(self):
        self.assertNotIn(
            'const overlayBundle = ""', self._last_eval_script(False)
        )


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

    def test_slugify_normalizes_accents_and_punctuation(self):
        self.assertEqual(
            _slugify("Enquête Société Générale — Volet 1 !"),
            "enquete-societe-generale-volet-1",
        )
        self.assertEqual(_slugify(""), "export")
        self.assertEqual(_slugify("   "), "export")
        self.assertEqual(_slugify("调查报告"), "export")
        self.assertEqual(
            len(_slugify("a" * 200)),
            60,
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


class InvestigationPayloadCacheTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_payload_cache_uses_threaded_read_until_invalidated(self):
        class FakeService:
            mutation_version = 0

            def __init__(self):
                self.calls = 0
                self.payload = [{"id": "case-1", "title": "Case One"}]

            def list_payload(self, *, include_archived=False):
                self.calls += 1
                self.include_archived = include_archived
                return self.payload

        async def run_sync(func, *args, **kwargs):
            return func(*args, **kwargs)

        service = FakeService()
        cache = InvestigationPayloadCache(service)
        with patch("main.asyncio.to_thread", new=AsyncMock(side_effect=run_sync)):
            first = await cache.investigation_payload()
            second = await cache.investigation_payload()
            cache.invalidate()
            third = await cache.investigation_payload()

        self.assertEqual(first, second)
        self.assertEqual(first, third)
        self.assertTrue(service.include_archived)
        self.assertEqual(service.calls, 2)

    async def test_payload_cache_refreshes_when_service_version_changes(self):
        class FakeService:
            def __init__(self):
                self.mutation_version = 0
                self.payload = [{"id": "case-1", "title": "Case One"}]

            def list_payload(self, *, include_archived=False):
                return self.payload

            def mark_changed(self):
                self.mutation_version += 1

        async def run_sync(func, *args, **kwargs):
            return func(*args, **kwargs)

        service = FakeService()
        cache = InvestigationPayloadCache(service)
        with patch("main.asyncio.to_thread", new=AsyncMock(side_effect=run_sync)):
            payload, version = await cache.investigation_payload()
            service.payload = [{"id": "case-1", "title": "Renamed"}]
            service.mark_changed()
            changed_payload, changed_version = await cache.investigation_payload()

        self.assertNotEqual(changed_payload, payload)
        self.assertNotEqual(changed_version, version)


class ExtensionOverlayContextTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_context_sync_sends_only_when_payload_changes(self):
        service = SimpleNamespace(
            send_extension_backend_message=AsyncMock(return_value=True)
        )
        cache = {}
        payload = _extension_overlay_context_payload(
            {
                "id": "case-1",
                "title": "Case One",
                "tags": ["Prioritaire"],
                "graph_entities": [
                    {
                        "id": "entity-1",
                        "label": "Jane Doe",
                        "tags": ["Personne"],
                        "properties": {"Alias": "J. Doe"},
                    }
                ],
            }
        )

        first = await _sync_extension_overlay_context(
            service,
            "ext-1",
            payload,
            cache,
        )
        second = await _sync_extension_overlay_context(
            service,
            "ext-1",
            payload,
            cache,
        )

        self.assertTrue(first)
        self.assertFalse(second)
        service.send_extension_backend_message.assert_awaited_once()
        message = service.send_extension_backend_message.await_args.args[1]
        self.assertEqual(message["type"], "synthesix:context-update")
        self.assertEqual(message["payload"]["id"], "case-1")
        self.assertIn("Personne", message["payload"]["baseTagsets"])
        self.assertIn("Alias", message["payload"]["graphEntities"][0]["propertyKeys"])

    async def test_extension_save_status_uses_backend_message(self):
        tab = SimpleNamespace(evaluate=AsyncMock())
        service = SimpleNamespace(
            send_extension_backend_message=AsyncMock(return_value=True)
        )
        settings = SimpleNamespace(overlay_mode="extension")

        await _set_overlay_save_status(
            service,
            settings,
            "ext-1",
            {
                "_extension_tab_id": 42,
                "_source_tab": tab,
            },
            "Saved",
        )

        tab.evaluate.assert_not_awaited()
        service.send_extension_backend_message.assert_awaited_once()
        message = service.send_extension_backend_message.await_args.args[1]
        self.assertEqual(
            message,
            {
                "type": "synthesix:button-status",
                "tabId": 42,
                "kind": "save",
                "state": "saved",
                "message": "Saved",
            },
        )


class InvestigationPageRoutingTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_pushes_workspace_reload_to_current_investigation_tab(self):
        scripts = []

        class Tab:
            async def evaluate(self, script):
                scripts.append(script)

        await _reload_workspace_from_sidecar(Tab(), 7)

        self.assertEqual(len(scripts), 1)
        self.assertIn("reloadWorkspace(7)", scripts[0])
        self.assertIn("window.synthesixPage", scripts[0])

    async def test_in_place_save_marks_and_pushes_workspace_revision(self):
        service = SimpleNamespace(mark_changed=Mock())
        settings = SimpleNamespace()
        source_tab = object()

        with (
            patch(
                "main._refresh_investigation_page_file",
                AsyncMock(return_value=8),
            ) as refresh,
            patch(
                "main._reload_workspace_from_sidecar",
                AsyncMock(),
            ) as reload_workspace,
            patch("main._set_page_status", AsyncMock()) as set_status,
        ):
            await _save_in_place(service, settings, source_tab, "case-123")

        service.mark_changed.assert_called_once_with()
        refresh.assert_awaited_once_with(service, settings, "case-123")
        reload_workspace.assert_awaited_once_with(source_tab, 8)
        set_status.assert_awaited_once_with(source_tab, "Saved.")

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

    async def test_capture_evidence_attaches_to_entity_when_requested(self):
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
                    return_value=SimpleNamespace(
                        id="capture-1",
                        capture_scope="viewport",
                    )
                ),
                attach_evidence_capture_to_entity=Mock(),
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

            with patch("main.capture_png", AsyncMock(return_value=png)):
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
                        "attach": {
                            "entityId": "entity-1",
                            "propertyKey": "Capture écran",
                        },
                    },
                )

            service.attach_evidence_capture_to_entity.assert_called_once_with(
                "case-1",
                "capture-1",
                {
                    "graph_entity_id": "entity-1",
                    "property_key": "Capture écran",
                    "property_type": "",
                },
            )

    async def test_capture_evidence_ignores_attach_failure(self):
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
                    return_value=SimpleNamespace(
                        id="capture-1",
                        capture_scope="viewport",
                    )
                ),
                attach_evidence_capture_to_entity=Mock(
                    side_effect=InvestigationValidationError("stale entity")
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

            with patch("main.capture_png", AsyncMock(return_value=png)):
                investigation, saved, capture = await _capture_evidence(
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
                        "attach": {"entityId": "entity-1", "propertyKey": "X"},
                    },
                )

            # The capture itself still succeeds even if the attach failed.
            self.assertEqual(capture.id, "capture-1")

    async def test_archive_page_records_visual_text_and_partial_mhtml(self):
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
                    "main.capture_visual_page",
                    AsyncMock(
                        return_value=SimpleNamespace(
                            sha256="v" * 64,
                            byte_size=123,
                            width=800,
                            height=900,
                            tile_count=1,
                        )
                    ),
                ),
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
            {"visual", "text"},
        )
        self.assertEqual(recorded["capture_kind"], "page_archive")
        self.assertEqual(recorded["status"], "partial")
        self.assertIn("MHTML archive unavailable", recorded["error"])
        self.assertEqual(manifest["capture"]["kind"], "page_archive")
        self.assertFalse(
            (base_dir / "data" / "evidence" / "case-1" / capture.id / "page.html").exists()
        )
        visual = next(
            artifact for artifact in manifest["artifacts"]
            if artifact["type"] == "visual"
        )
        self.assertEqual(visual["visual"], {"width": 800, "height": 900, "tile_count": 1})

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
                ensure_evidence_capture_deletable=Mock(),
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
            service.ensure_evidence_capture_deletable.assert_called_once_with(
                "case-1",
                "capture-1",
            )
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
                if "!!window.SynthesixOverlay" in script:
                    return False
                return {
                    "action": "save_page_to_investigation",
                    "investigationId": "case-1",
                    "page": {"url": self.url},
                }

        tab = FakeTab()
        action = await _install_and_consume_save_overlay(
            BrowserService(None),
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
        self.assertIn("data-synthesix-overlay-drag-handle", tab.script)
        self.assertIn("data-synthesix-save-page", tab.script)
        self.assertIn("data-synthesix-archive", tab.script)
        self.assertIn("data-synthesix-capture", tab.script)
        self.assertIn("data-synthesix-capture-menu", tab.script)
        self.assertIn("synthesix-overlay-toggle", tab.script)
        self.assertIn("synthesix:external-overlay-collapsed", tab.script)
        self.assertIn("synthesix:external-overlay-position", tab.script)
        self.assertIn("menu-edge", tab.script)
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
        self.assertIn("tagsetPropertyTypes", tab.script)
        self.assertIn("property_type", tab.script)
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

    async def test_external_page_overlay_queues_actions_fifo(self):
        """T-001: clicks land in a FIFO queue instead of a clobberable scalar,
        and the poll drains exactly one action per call."""

        class FakeTab:
            url = "https://example.com/article"

            async def evaluate(self, script):
                self.script = script
                if "!!window.SynthesixOverlay" in script:
                    return False
                return None

        tab = FakeTab()
        await _install_and_consume_save_overlay(
            BrowserService(None),
            tab,
            {"id": "case-1", "title": "Case"},
        )

        self.assertIn("window.__synthesixActions", tab.script)
        self.assertIn("queueAction({", tab.script)
        self.assertIn("queued.shift()", tab.script)
        self.assertNotIn("__synthesixSavePageAction", tab.script)

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

    def test_attach_selection_helper_records_sourced_extracted_entity(self):
        service = Mock()
        investigation = SimpleNamespace(id="case-1", status="active")
        saved = SimpleNamespace(
            id="result-1",
            url="https://example.com/profile",
            title="Profile",
        )
        extracted = SimpleNamespace(id="extracted-1")
        graph_entity = {
            "id": "entity-1",
            "label": "Jane Doe",
            "properties": {"Alias": "J. Doe"},
        }
        service.get.return_value = investigation
        service.workspace_payload.return_value = {
            "graph_entities": [graph_entity]
        }
        service.save_page.return_value = saved
        service.record_selection_entity.return_value = extracted
        service.attach_extracted_property.return_value = {
            "id": "extracted-1",
            "property_key": "Alias",
        }

        returned_investigation, returned_saved, entity, attached = (
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
        # The graph entity (with its label) is returned for the status message.
        self.assertEqual(entity["label"], "Jane Doe")
        self.assertEqual(attached["id"], "extracted-1")
        service.link_result_to_graph_entity.assert_called_once_with(
            "case-1",
            "entity-1",
            "result-1",
        )
        # The selection is stored as a sourced extracted entity on the page...
        service.record_selection_entity.assert_called_once_with(
            "case-1",
            "result-1",
            value="JD",
            property_key="Alias",
            property_type="",
            entity_type="other",
        )
        # ...then attached to the graph entity as a property.
        service.attach_extracted_property.assert_called_once_with(
            "case-1",
            "extracted-1",
            {
                "graph_entity_id": "entity-1",
                "property_key": "Alias",
                "property_type": "",
            },
        )

    async def test_external_page_overlay_can_focus_home_without_active_case(self):
        class FakeTab:
            url = "https://example.com/profile"

            async def evaluate(self, script):
                self.script = script
                return {"action": "focus_home"}

        tab = FakeTab()
        action = await _install_and_consume_save_overlay(
            BrowserService(None), tab
        )

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

    async def test_extension_overlay_action_is_returned_with_source_tab(self):
        from tests.fakes import FakeBrowser, FakeTab

        tab = FakeTab(url="https://example.com/profile", target_id="external-1")
        tab.on(
            "evaluate",
            lambda script, *_args: (
                "synthesixOverlayToken" in script and '"token-1"' in script
            ),
        )
        browser = FakeBrowser([tab])
        service = get_browser_service(browser)
        service.dispatch_queue.put_nowait(
            {
                "v": 1,
                "action": "extension_overlay_action",
                "tabId": 42,
                "url": "https://example.com/profile",
                "payload": {
                    "message": {
                        "type": "synthesix:overlay-action",
                        "href": "https://example.com/profile",
                        "sourceToken": "token-1",
                        "action": {
                            "action": "save_page_to_investigation",
                            "investigationId": "case-1",
                            "page": {"url": "https://example.com/profile"},
                        },
                    },
                    "sender": {
                        "tabId": 42,
                        "tabUrl": "https://example.com/profile",
                    },
                },
            }
        )
        settings = SimpleNamespace(
            overlay_mode="extension",
            home_poll_interval=5,
            empty_tabs_grace_seconds=0,
            default_history_limit=25,
        )

        action = await asyncio.wait_for(
            wait_for_home_action(
                browser,
                "file:///tmp/index.html",
                settings=settings,
                extension_available=True,
                extension_id=None,
            ),
            timeout=1,
        )

        self.assertEqual(action["action"], "save_page_to_investigation")
        self.assertEqual(action["investigationId"], "case-1")
        self.assertIs(action["_source_tab"], tab)
        self.assertEqual(action["_extension_tab_id"], 42)

    async def test_extension_focus_home_does_not_require_source_tab(self):
        action = await _normalize_dispatch_action(
            {
                "v": 1,
                "action": "extension_overlay_action",
                "tabId": 42,
                "url": "https://example.com/profile",
                "payload": {
                    "message": {
                        "type": "synthesix:overlay-action",
                        "href": "https://example.com/profile",
                        "sourceToken": "token-1",
                        "action": {"action": "focus_home"},
                    },
                    "sender": {
                        "tabId": 42,
                        "tabUrl": "https://example.com/profile",
                    },
                },
            },
            tabs=[],
        )

        self.assertEqual(action, {"action": "focus_home"})

    async def test_extension_spike_message_is_ignored(self):
        action = await _normalize_dispatch_action(
            {
                "v": 1,
                "action": "extension_spike_message",
                "payload": {
                    "message": {
                        "type": "synthesix:spike",
                        "payload": {"ok": True},
                    },
                },
            },
            tabs=[],
        )

        self.assertIsNone(action)

    async def test_extension_focus_home_opens_home_without_source_tab(self):
        from tests.fakes import FakeBrowser, FakeTab

        tab = FakeTab(url="https://example.com/profile", target_id="external-1")
        browser = FakeBrowser([tab])
        service = get_browser_service(browser)
        service.dispatch_queue.put_nowait(
            {
                "v": 1,
                "action": "extension_overlay_action",
                "tabId": 42,
                "url": "https://example.com/profile",
                "payload": {
                    "message": {
                        "type": "synthesix:overlay-action",
                        "href": "https://example.com/profile",
                        "sourceToken": "unknown-token",
                        "action": {"action": "focus_home"},
                    },
                    "sender": {
                        "tabId": 42,
                        "tabUrl": "https://example.com/profile",
                    },
                },
            }
        )
        settings = SimpleNamespace(
            overlay_mode="extension",
            home_poll_interval=5,
            empty_tabs_grace_seconds=0,
            default_history_limit=25,
        )
        focus_home = AsyncMock()

        with patch("main._focus_or_open_home_tab", new=focus_home):
            with self.assertRaises(asyncio.TimeoutError):
                await asyncio.wait_for(
                    wait_for_home_action(
                        browser,
                        "file:///tmp/index.html",
                        settings=settings,
                        extension_available=True,
                        extension_id=None,
                    ),
                    timeout=0.05,
                )

        focus_home.assert_awaited_once()

    async def test_extension_spike_message_does_not_leave_action_loop(self):
        from tests.fakes import FakeBrowser, FakeTab

        tab = FakeTab(url="https://example.com/profile", target_id="external-1")
        browser = FakeBrowser([tab])
        service = get_browser_service(browser)
        service.dispatch_queue.put_nowait(
            {
                "v": 1,
                "action": "extension_spike_message",
                "payload": {
                    "message": {
                        "type": "synthesix:spike",
                        "payload": {"ok": True},
                    },
                },
            }
        )
        settings = SimpleNamespace(
            overlay_mode="extension",
            home_poll_interval=5,
            empty_tabs_grace_seconds=0,
            default_history_limit=25,
        )

        with self.assertRaises(asyncio.TimeoutError):
            await asyncio.wait_for(
                wait_for_home_action(
                    browser,
                    "file:///tmp/index.html",
                    settings=settings,
                    extension_available=True,
                    extension_id=None,
                ),
                timeout=0.05,
            )

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


class BackgroundSearchTaskTestCase(unittest.IsolatedAsyncioTestCase):
    """T-011: searches run as background tasks; the loop stays responsive."""

    async def test_search_task_running_states(self):
        self.assertFalse(_search_task_running(None))
        task = asyncio.create_task(asyncio.sleep(60))
        self.assertTrue(_search_task_running(task))
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        self.assertFalse(_search_task_running(task))

    async def test_run_search_action_reports_persistence_error(self):
        with (
            patch("main.perform_search", new=AsyncMock(return_value="save failed")),
            patch("main._set_home_status", new=AsyncMock()) as status,
            patch("main._set_home_search_running", new=AsyncMock()) as running,
        ):
            await _run_search_action(object(), "file:///index.html", {})

        status.assert_awaited_once()
        self.assertEqual(status.await_args.args[2], "save failed")
        self.assertTrue(status.await_args.kwargs["is_error"])
        running.assert_awaited_once()
        self.assertFalse(running.await_args.args[2])

    async def test_run_search_action_uses_separate_search_browser_for_engines(self):
        user_browser = object()
        search_browser = object()
        provider = SimpleNamespace(
            get_browser=AsyncMock(return_value=search_browser),
            cleanup_idle_tabs=AsyncMock(),
        )

        with (
            patch("main.perform_search", new=AsyncMock(return_value=None)) as search,
            patch("main._set_home_search_running", new=AsyncMock()),
        ):
            await _run_search_action(
                user_browser,
                "file:///index.html",
                {"original_query": "query"},
                provider,
            )

        search.assert_awaited_once()
        self.assertIs(search.await_args.kwargs["browser"], search_browser)
        self.assertIs(search.await_args.kwargs["report_browser"], user_browser)
        provider.cleanup_idle_tabs.assert_awaited_once()

    async def test_run_search_action_clears_running_before_cleanup(self):
        events: list[str] = []
        provider = SimpleNamespace(
            get_browser=AsyncMock(return_value=object()),
            cleanup_idle_tabs=AsyncMock(side_effect=lambda: events.append("cleanup")),
        )

        async def clear_running(*_args):
            events.append("running:false")

        with (
            patch("main.perform_search", new=AsyncMock(return_value=None)),
            patch(
                "main._set_home_search_running",
                new=AsyncMock(side_effect=clear_running),
            ),
        ):
            await _run_search_action(
                object(),
                "file:///index.html",
                {"original_query": "query"},
                provider,
            )

        self.assertEqual(events, ["running:false", "cleanup"])

    async def test_headless_robot_challenge_opens_captured_artifact(self):
        with TemporaryDirectory() as temp_dir:
            artifact_path = Path(temp_dir) / "history" / "robot_challenges" / "challenge.html"
            artifact_path.parent.mkdir(parents=True)
            artifact_path.write_text("<html>challenge</html>", encoding="utf-8")
            challenge = RobotChallengeError(
                "duckduckgo",
                "challenge",
                captured_artifacts={"html": str(artifact_path)},
            )
            searcher = SimpleNamespace(search=AsyncMock(side_effect=challenge))
            challenge_tab = SimpleNamespace(bring_to_front=AsyncMock())
            service = SimpleNamespace(open_tab=AsyncMock(return_value=challenge_tab))
            report_browser = object()

            with (
                patch.dict(
                    "os.environ",
                    {
                        "SYNTHESIX_BASE_DIR": temp_dir,
                        "SYNTHESIX_SEARCH_WINDOW_MODE": "headless",
                    },
                    clear=True,
                ),
                patch("main.SearchOrchestrator", return_value=searcher),
                patch("main.get_browser_service", return_value=service),
            ):
                message = await perform_search(
                    "query",
                    '"query"',
                    object(),
                    {"duckduckgo": True},
                    1,
                    report_browser=report_browser,
                )

        self.assertIn("anti-robot challenge", message)
        service.open_tab.assert_awaited_once_with(artifact_path.resolve().as_uri())
        challenge_tab.bring_to_front.assert_awaited_once()

    async def test_perform_search_records_search_in_thread_and_marks_changed(self):
        search_result = SimpleNamespace(
            output_path=None,
            total_time=1.25,
            engine_errors={},
            results=[{"title": "Result"}],
        )
        searcher = SimpleNamespace(search=AsyncMock(return_value=search_result))
        investigation_service = SimpleNamespace(
            record_search=Mock(),
            mark_changed=Mock(),
        )

        async def run_sync(func, *args, **kwargs):
            return func(*args, **kwargs)

        with (
            patch("main.SearchOrchestrator", return_value=searcher),
            patch(
                "main.asyncio.to_thread",
                new=AsyncMock(side_effect=run_sync),
            ) as to_thread,
        ):
            message = await perform_search(
                "query",
                '"query"',
                object(),
                {"google": True},
                5,
                investigation_service=investigation_service,
            )

        self.assertIsNone(message)
        self.assertIs(to_thread.await_args.args[0], investigation_service.record_search)
        investigation_service.record_search.assert_called_once()
        investigation_service.mark_changed.assert_called_once()

    async def test_search_browser_provider_cleanup_closes_blank_tabs(self):
        search_browser = object()
        service = SimpleNamespace(
            tabs=AsyncMock(
                return_value=[
                    SimpleNamespace(url="https://example.com/"),
                    SimpleNamespace(url="about:blank"),
                ]
            ),
            close_blank_tabs=AsyncMock(return_value=1),
        )
        search_manager = SimpleNamespace(browser=search_browser)
        provider = SearchBrowserProvider(
            SimpleNamespace(search_browser_mode="separate"),
            SimpleNamespace(),
        )
        provider.search_browser_manager = search_manager

        with patch("main.get_browser_service", return_value=service) as get_service:
            await provider.cleanup_idle_tabs()

        get_service.assert_called_once_with(search_browser)
        service.close_blank_tabs.assert_awaited_once()

    async def test_search_browser_provider_cleanup_stops_when_only_blank_tabs_remain(self):
        search_browser = object()
        # The initial about:blank tab never gets a websocket, so zendriver
        # reports it closed=True; the provider must still count it as live.
        service = SimpleNamespace(
            tabs=AsyncMock(
                return_value=[SimpleNamespace(url="about:blank", closed=True)]
            ),
            close_blank_tabs=AsyncMock(),
        )
        search_manager = SimpleNamespace(browser=search_browser, stop=AsyncMock())
        provider = SearchBrowserProvider(
            SimpleNamespace(search_browser_mode="separate"),
            SimpleNamespace(),
        )
        provider.search_browser_manager = search_manager

        with patch("main.get_browser_service", return_value=service):
            await provider.cleanup_idle_tabs()

        search_manager.stop.assert_awaited_once()
        service.close_blank_tabs.assert_not_awaited()
        self.assertIsNone(provider.search_browser_manager)

    async def test_search_browser_provider_cleanup_stops_unreachable_browser(self):
        service = SimpleNamespace(
            tabs=AsyncMock(return_value=None),
            close_blank_tabs=AsyncMock(),
        )
        search_manager = SimpleNamespace(browser=object(), stop=AsyncMock())
        provider = SearchBrowserProvider(
            SimpleNamespace(search_browser_mode="separate"),
            SimpleNamespace(),
        )
        provider.search_browser_manager = search_manager

        with patch("main.get_browser_service", return_value=service):
            await provider.cleanup_idle_tabs()

        search_manager.stop.assert_awaited_once()
        service.close_blank_tabs.assert_not_awaited()
        self.assertIsNone(provider.search_browser_manager)

    async def test_run_search_action_reports_unexpected_failure(self):
        with (
            patch(
                "main.perform_search",
                new=AsyncMock(side_effect=RuntimeError("boom")),
            ),
            patch("main._set_home_status", new=AsyncMock()) as status,
            patch("main._set_home_search_running", new=AsyncMock()) as running,
        ):
            with self.assertLogs("main", level="ERROR"):
                await _run_search_action(object(), "file:///index.html", {})

        self.assertIn("Search failed", status.await_args.args[2])
        running.assert_awaited_once()
        self.assertFalse(running.await_args.args[2])

    async def test_cancelled_search_clears_running_flag_without_status(self):
        started = asyncio.Event()

        async def hang(**_kwargs):
            started.set()
            await asyncio.sleep(60)

        with (
            patch("main.perform_search", new=hang),
            patch("main._set_home_status", new=AsyncMock()) as status,
            patch("main._set_home_search_running", new=AsyncMock()) as running,
        ):
            task = _start_search_task(
                _run_search_action(object(), "file:///index.html", {})
            )
            await started.wait()
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

        self.assertTrue(task.cancelled())
        status.assert_not_awaited()
        running.assert_awaited_once()
        self.assertFalse(running.await_args.args[2])

    async def test_search_browser_provider_shared_uses_user_browser(self):
        user_browser = object()
        user_manager = SimpleNamespace(get_driver=AsyncMock(return_value=user_browser))
        provider = SearchBrowserProvider(
            SimpleNamespace(search_browser_mode="shared"),
            user_manager,
        )

        browser = await provider.get_browser()

        self.assertIs(browser, user_browser)
        user_manager.get_driver.assert_awaited_once()

    async def test_search_browser_provider_separate_reuses_alive_browser(self):
        search_browser = SimpleNamespace(
            tabs=[],
            update_targets=AsyncMock(),
            _get_targets=AsyncMock(
                return_value=[SimpleNamespace(target_id="tab-1", type_="page")]
            ),
        )
        search_manager = SimpleNamespace(
            browser=search_browser,
            get_driver=AsyncMock(return_value=search_browser),
            stop=AsyncMock(),
        )
        user_manager = SimpleNamespace()
        provider = SearchBrowserProvider(
            SimpleNamespace(search_browser_mode="separate"),
            user_manager,
        )

        with patch(
            "main.HeadlessBrowserManager.create_search",
            new=AsyncMock(return_value=search_manager),
        ) as create_search:
            first = await provider.get_browser()
            second = await provider.get_browser()

        self.assertIs(first, search_browser)
        self.assertIs(second, search_browser)
        create_search.assert_awaited_once()
        search_browser.update_targets.assert_awaited_once()
        search_browser._get_targets.assert_awaited_once()

    async def test_search_browser_provider_clear_stops_and_clears_profile(self):
        search_manager = SimpleNamespace(browser=object(), stop=AsyncMock())
        provider = SearchBrowserProvider(
            SimpleNamespace(
                search_browser_mode="separate",
                search_profile_dir=Path("search-profile"),
            ),
            SimpleNamespace(),
        )
        provider.search_browser_manager = search_manager

        with patch("main.clear_browser_profile_data", return_value=4) as clear_profile:
            removed = await provider.clear_browser_data()

        self.assertEqual(removed, 4)
        search_manager.stop.assert_awaited_once()
        clear_profile.assert_called_once_with(Path("search-profile"))
        self.assertIsNone(provider.search_browser_manager)

    async def test_start_search_task_logs_unhandled_exception(self):
        async def broken():
            raise RuntimeError("wrapper bug")

        with self.assertLogs("main", level="ERROR") as logs:
            task = _start_search_task(broken())
            await asyncio.gather(task, return_exceptions=True)
            # The done callback runs on the next loop iteration.
            await asyncio.sleep(0)

        self.assertTrue(
            any("unhandled exception" in entry for entry in logs.output)
        )

    async def test_run_retry_search_action_reports_to_page_tab(self):
        tab = object()
        with (
            patch(
                "main._retry_search_combination",
                new=AsyncMock(return_value=("Retry completed for Bing.", False)),
            ),
            patch("main._set_page_status", new=AsyncMock()) as page_status,
            patch("main._set_home_search_running", new=AsyncMock()) as running,
        ):
            await _run_retry_search_action(
                {"_source_tab": tab},
                object(),
                "file:///index.html",
                SimpleNamespace(),
                Mock(),
            )

        page_status.assert_awaited_once_with(
            tab, "Retry completed for Bing.", is_error=False
        )
        running.assert_awaited_once()
        self.assertFalse(running.await_args.args[2])


class ActiveEngineTabSkipTestCase(unittest.IsolatedAsyncioTestCase):
    """T-011: the poll loop must not touch tabs owned by a running engine."""

    def setUp(self):
        from search_engine import ACTIVE_ENGINE_TAB_TARGETS

        ACTIVE_ENGINE_TAB_TARGETS.clear()
        self.registry = ACTIVE_ENGINE_TAB_TARGETS

    def tearDown(self):
        self.registry.clear()

    async def test_poll_loop_skips_registered_engine_tabs(self):
        from tests.fakes import CallJournal, FakeBrowser, FakeTab

        index_url = "file:///synthesix/index.html"
        home = FakeTab(url=index_url, target_id="home")
        home.on(
            "evaluate",
            lambda script, *_args: (
                {
                    "ready": True,
                    "action": {"action": "probe"},
                    "historyVersion": "",
                    "investigationsVersion": "",
                }
                if "synthesixHome" in script and "consumeAction" in script
                else None
            ),
        )
        engine_tab = FakeTab(
            url="https://www.google.com/search?q=x",
            target_id="engine-1",
        )
        browser = FakeBrowser([home, engine_tab])
        engine_tab.journal = CallJournal()
        self.registry.add("engine-1")

        with TemporaryDirectory() as temp_dir:
            with patch.dict(
                "os.environ",
                {
                    "SYNTHESIX_BASE_DIR": temp_dir,
                    "SYNTHESIX_HOME_POLL_INTERVAL": "0",
                },
            ):
                settings = get_settings()
                action = await asyncio.wait_for(
                    wait_for_home_action(browser, index_url, settings=settings),
                    timeout=10,
                )

        self.assertEqual(action["action"], "probe")
        self.assertEqual(engine_tab.journal.records, [])


if __name__ == "__main__":
    unittest.main()
