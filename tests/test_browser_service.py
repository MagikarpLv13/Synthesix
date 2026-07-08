"""T-020: BrowserService unit tests + no-direct-CDP regression guard.

The guard test greps the migrated modules for raw CDP idioms so a future
edit cannot quietly reintroduce `tab.send(...)`/`browser._get_targets`
outside `browser/service.py`.
"""

import asyncio
import base64
import json
import re
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from zendriver import cdp

import observability
from browser import (
    BrowserService,
    eval_js,
    get_browser_service,
    mhtml,
    outer_html,
    screenshot,
)
from tests.fakes import FakeBrowser, FakeTab


class FakeWorkerConnection:
    """Extension service-worker CDP connection double.

    Answers the revision probe with ``revision`` and records every evaluated
    expression, so tests can assert whether ``chrome.runtime.reload()`` ran.
    """

    def __init__(self, revision: str = ""):
        self.revision = revision
        self.expressions: list[str] = []
        self.handlers: list = []

    def add_handler(self, event_type, handler) -> None:
        self.handlers.append((event_type, handler))

    async def send(self, command):
        # zendriver CDP commands are generators; the first yield is the
        # request dict ({"method": ..., "params": ...}).
        request = command.send(None)
        method = str(request.get("method", ""))
        if method != "Runtime.evaluate":
            return None
        expression = str(request.get("params", {}).get("expression", ""))
        self.expressions.append(expression)
        if "synthesixBackgroundRevision" in expression:
            return SimpleNamespace(value=self.revision), None
        return SimpleNamespace(value=True), None


class BrowserServiceTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        observability.reset()

    def tearDown(self):
        observability.reset()

    async def test_tabs_returns_live_page_tabs_and_prunes_registry(self):
        live = FakeTab("https://example.com", "live")
        browser = FakeBrowser([live])
        service = BrowserService(browser)
        service.armed_script_targets.update({"live", "closed"})

        tabs = await service.tabs()

        self.assertEqual(tabs, [live])
        self.assertEqual(service.armed_script_targets, {"live"})
        self.assertEqual(observability.snapshot()["calls"]["targets_poll"], 1)

    async def test_tabs_returns_none_when_browser_unreachable(self):
        class DeadBrowser:
            tabs = []

            async def update_targets(self):
                raise ConnectionError("chrome is gone")

        self.assertIsNone(await BrowserService(DeadBrowser()).tabs())

    async def test_tabs_reads_event_registry_between_resyncs(self):
        # T-022: a tab that appears in the event-maintained registry after
        # the first resync is returned without a fresh getTargets round-trip.
        live = FakeTab("https://example.com", "live")
        browser = FakeBrowser([live])
        service = BrowserService(browser)

        await service.tabs()  # first call: authoritative resync (last == 0)
        appeared = FakeTab("https://new.example", "new")
        appeared.journal = browser.journal
        browser.tabs.append(appeared)  # zendriver's TargetCreated handler
        tabs = await service.tabs()  # second call: reads registry, no resync

        self.assertEqual({tab.target_id for tab in tabs}, {"live", "new"})
        self.assertEqual(observability.snapshot()["calls"]["targets_poll"], 1)

    async def test_tabs_resyncs_after_interval(self):
        service = BrowserService(FakeBrowser([FakeTab(target_id="a")]))
        service.target_resync_interval = 0.0  # every call is due

        await service.tabs()
        await service.tabs()

        self.assertEqual(observability.snapshot()["calls"]["targets_poll"], 2)

    async def test_tabs_forces_resync_when_registry_empty(self):
        # An empty registry must never be trusted on its own (a transient
        # event gap would look like "all tabs closed" => quit): resync even
        # when the time-based interval is nowhere near due.
        service = BrowserService(FakeBrowser([]))
        service.target_resync_interval = 9999.0

        await service.tabs()
        await service.tabs()

        self.assertEqual(observability.snapshot()["calls"]["targets_poll"], 2)

    async def test_tabs_resyncs_when_browser_connection_dropped(self):
        # T-022 regression guard: when Chrome dies the event registry can go
        # stale (no TargetDestroyed), so a stopped browser-connection listener
        # must force an authoritative resync even mid-interval — otherwise the
        # "all tabs closed => quit" path never fires.
        browser = FakeBrowser([FakeTab("https://example.com", "live")])
        browser.connection = SimpleNamespace(
            listener=SimpleNamespace(running=False)
        )
        service = BrowserService(browser)
        service._last_target_resync = float("inf")  # time interval never due

        await service.tabs()

        self.assertEqual(observability.snapshot()["calls"]["targets_poll"], 1)

    async def test_tabs_none_when_dropped_connection_resync_fails(self):
        class DroppedBrowser:
            stopped = False
            # Stale registry entry a missed TargetDestroyed left behind.
            tabs = [SimpleNamespace(target_id="stale")]
            connection = SimpleNamespace(listener=SimpleNamespace(running=False))

            async def update_targets(self):
                raise ConnectionError("chrome is gone")

            async def _get_targets(self):
                raise ConnectionError("chrome is gone")

        service = BrowserService(DroppedBrowser())
        service._last_target_resync = float("inf")

        self.assertIsNone(await service.tabs())

    async def test_tabs_none_when_resync_hangs(self):
        # A dead Chrome makes zendriver's CDP send await a reply that never
        # arrives; the resync must time out to unreachable instead of freezing
        # the whole action loop (so the browser.stopped quit check is reached).
        class HangingBrowser:
            stopped = False
            tabs = [SimpleNamespace(target_id="stale")]
            connection = SimpleNamespace(listener=SimpleNamespace(running=False))

            async def update_targets(self):
                await asyncio.sleep(3600)  # never returns

            async def _get_targets(self):
                return []

        service = BrowserService(HangingBrowser())
        service.target_resync_timeout = 0.05
        service._last_target_resync = float("inf")

        self.assertIsNone(await service.tabs())

    async def test_eval_js_returns_value_and_counts_category(self):
        tab = FakeTab()
        tab.program("evaluate", {"ready": True})

        result = await eval_js(tab, "1 + 1", category="eval_page")

        self.assertEqual(result, {"ready": True})
        self.assertEqual(observability.snapshot()["calls"]["eval_page"], 1)

    async def test_eval_js_swallows_failures_as_none(self):
        tab = FakeTab()
        tab.program("evaluate", RuntimeError("detached"))

        self.assertIsNone(await eval_js(tab, "1 + 1", category="eval_page"))

    async def test_arm_new_document_script_is_idempotent_per_target(self):
        tab = FakeTab(target_id="tab-1")
        service = BrowserService(FakeBrowser([tab]))

        await service.arm_new_document_script(tab, "guard();")
        await service.arm_new_document_script(tab, "guard();")

        # One arming = Page.enable + addScriptToEvaluateOnNewDocument.
        self.assertEqual(tab.journal.count("send"), 2)
        self.assertEqual(service.armed_script_targets, {"tab-1"})

    async def test_arm_new_document_script_skips_tab_without_target(self):
        tab = SimpleNamespace(url="https://example.com")
        service = BrowserService(None)

        await service.arm_new_document_script(tab, "guard();")

        self.assertEqual(service.armed_script_targets, set())

    async def test_arm_new_document_script_failure_leaves_target_unarmed(self):
        tab = FakeTab(target_id="tab-1")
        tab.program("send", RuntimeError("no Page domain"))
        service = BrowserService(FakeBrowser([tab]))

        await service.arm_new_document_script(tab, "guard();")

        self.assertEqual(service.armed_script_targets, set())

    async def test_arm_dispatch_binding_is_idempotent_per_target(self):
        tab = FakeTab(target_id="tab-1")
        service = BrowserService(FakeBrowser([tab]))

        armed_first = await service.arm_dispatch_binding(tab)
        armed_second = await service.arm_dispatch_binding(tab)

        self.assertTrue(armed_first)
        self.assertTrue(armed_second)
        # One arming = Runtime.enable + Runtime.addBinding.
        self.assertEqual(tab.journal.count("send"), 2)
        self.assertEqual(service.armed_binding_targets, {"tab-1"})
        self.assertEqual(observability.snapshot()["calls"]["arm_binding"], 1)

    async def test_arm_dispatch_binding_skips_tab_without_target(self):
        tab = SimpleNamespace(url="https://example.com")
        service = BrowserService(None)

        armed = await service.arm_dispatch_binding(tab)

        self.assertFalse(armed)
        self.assertEqual(service.armed_binding_targets, set())

    async def test_arm_dispatch_binding_failure_leaves_target_unarmed(self):
        tab = FakeTab(target_id="tab-1")
        tab.program("send", RuntimeError("Runtime domain unavailable"))
        service = BrowserService(FakeBrowser([tab]))

        armed = await service.arm_dispatch_binding(tab)

        self.assertFalse(armed)
        self.assertEqual(service.armed_binding_targets, set())

    async def test_dispatch_binding_handler_enqueues_valid_payload(self):
        tab = FakeTab(target_id="tab-1")
        service = BrowserService(FakeBrowser([tab]))
        await service.arm_dispatch_binding(tab)

        event = SimpleNamespace(
            name="synthesixDispatch",
            payload=json.dumps({"action": "cancel_search"}),
        )
        await tab.fire(cdp.runtime.BindingCalled, event)

        action = service.dispatch_queue.get_nowait()
        self.assertEqual(action["action"], "cancel_search")
        self.assertIs(action["_source_tab"], tab)
        self.assertEqual(observability.snapshot()["calls"]["push_action"], 1)

    async def test_dispatch_binding_handler_ignores_other_bindings(self):
        tab = FakeTab(target_id="tab-1")
        service = BrowserService(FakeBrowser([tab]))
        await service.arm_dispatch_binding(tab)

        event = SimpleNamespace(
            name="someOtherBinding",
            payload=json.dumps({"action": "cancel_search"}),
        )
        await tab.fire(cdp.runtime.BindingCalled, event)

        self.assertTrue(service.dispatch_queue.empty())

    async def test_dispatch_binding_handler_discards_malformed_payload(self):
        tab = FakeTab(target_id="tab-1")
        service = BrowserService(FakeBrowser([tab]))
        await service.arm_dispatch_binding(tab)

        for payload in ("not json", "42", json.dumps({"no_action": True})):
            await tab.fire(
                cdp.runtime.BindingCalled,
                SimpleNamespace(name="synthesixDispatch", payload=payload),
            )

        self.assertTrue(service.dispatch_queue.empty())

    async def test_dispatch_binding_handler_discards_oversized_payload(self):
        tab = FakeTab(target_id="tab-1")
        service = BrowserService(FakeBrowser([tab]))
        await service.arm_dispatch_binding(tab)

        await tab.fire(
            cdp.runtime.BindingCalled,
            SimpleNamespace(
                name="synthesixDispatch",
                payload=json.dumps({"action": "cancel_search", "blob": "x" * 300000}),
            ),
        )

        self.assertTrue(service.dispatch_queue.empty())

    async def test_arm_extension_binding_warns_on_stale_worker(self):
        connection = FakeWorkerConnection(revision="old-revision")
        service = BrowserService(FakeBrowser([]))
        service._find_extension_service_worker_target = AsyncMock(  # type: ignore[method-assign]
            return_value=SimpleNamespace(target_id="worker-1")
        )
        service._extension_connection = Mock(return_value=connection)  # type: ignore[method-assign]

        with self.assertLogs("browser.service", level="WARNING") as logs:
            armed = await service.arm_extension_dispatch_binding(
                "ext-1", expected_revision="disk-revision"
            )

        # A stale worker is armed anyway (better than a dead overlay); the
        # mismatch is surfaced once so the operator restarts the browser.
        self.assertTrue(armed)
        self.assertIn("worker-1", service.armed_extension_binding_targets)
        self.assertIn("worker-1", service.stale_extension_worker_targets)
        self.assertTrue(any("old-revision" in line for line in logs.output))

    async def test_arm_extension_binding_arms_matching_revision(self):
        connection = FakeWorkerConnection(revision="disk-revision")
        service = BrowserService(FakeBrowser([]))
        service._find_extension_service_worker_target = AsyncMock(  # type: ignore[method-assign]
            return_value=SimpleNamespace(target_id="worker-1")
        )
        service._extension_connection = Mock(return_value=connection)  # type: ignore[method-assign]

        with self.assertNoLogs("browser.service", level="WARNING"):
            armed = await service.arm_extension_dispatch_binding(
                "ext-1", expected_revision="disk-revision"
            )

        self.assertTrue(armed)
        self.assertIn("worker-1", service.armed_extension_binding_targets)
        self.assertNotIn("worker-1", service.stale_extension_worker_targets)

    async def test_arm_extension_binding_warns_only_once_per_worker(self):
        connection = FakeWorkerConnection(revision="old-revision")
        service = BrowserService(FakeBrowser([]))
        service._find_extension_service_worker_target = AsyncMock(  # type: ignore[method-assign]
            return_value=SimpleNamespace(target_id="worker-1")
        )
        service._extension_connection = Mock(return_value=connection)  # type: ignore[method-assign]
        service.stale_extension_worker_targets.add("worker-1")

        with self.assertNoLogs("browser.service", level="WARNING"):
            armed = await service.arm_extension_dispatch_binding(
                "ext-1", expected_revision="disk-revision"
            )

        self.assertTrue(armed)
        self.assertIn("worker-1", service.armed_extension_binding_targets)

    async def test_arm_extension_binding_skips_revision_check_without_expectation(self):
        connection = FakeWorkerConnection(revision="anything")
        service = BrowserService(FakeBrowser([]))
        service._find_extension_service_worker_target = AsyncMock(  # type: ignore[method-assign]
            return_value=SimpleNamespace(target_id="worker-1")
        )
        service._extension_connection = Mock(return_value=connection)  # type: ignore[method-assign]

        armed = await service.arm_extension_dispatch_binding("ext-1")

        self.assertTrue(armed)
        self.assertEqual(connection.expressions, [])
        self.assertIn("worker-1", service.armed_extension_binding_targets)

    async def test_send_extension_backend_message_evaluates_in_worker(self):
        class FakeConnection:
            async def send(self, _command):
                return SimpleNamespace(value=True), None

        service = BrowserService(FakeBrowser([]))
        target = SimpleNamespace(target_id="worker-1")
        connection = FakeConnection()
        service._find_extension_service_worker_target = AsyncMock(  # type: ignore[method-assign]
            return_value=target
        )
        service._extension_connection = Mock(return_value=connection)  # type: ignore[method-assign]

        sent = await service.send_extension_backend_message(
            "ext-1",
            {"type": "synthesix:context-update", "payload": {"id": "case-1"}},
        )

        self.assertTrue(sent)
        self.assertIs(service.extension_worker_connections["worker-1"], connection)
        self.assertEqual(
            observability.snapshot()["calls"]["extension_backend_message"],
            1,
        )

    def test_extension_connection_is_not_browser_owned(self):
        service = BrowserService(FakeBrowser([]))
        service._target_websocket_url = Mock(return_value="ws://127.0.0.1/devtools/page/worker-1")  # type: ignore[method-assign]
        target = SimpleNamespace(
            target_id="worker-1",
            type_="service_worker",
            title="",
            url="chrome-extension://ext/background.js",
            attached=True,
        )

        connection = service._extension_connection(target, "worker-1")

        self.assertIsNone(connection._owner)
        self.assertEqual(connection.target_id, "worker-1")

    def test_inspector_worker_script_loaded_event_is_registered(self):
        event = cdp.util.parse_json_event(
            {
                "method": "Inspector.workerScriptLoaded",
                "params": {},
            }
        )

        self.assertEqual(type(event).__name__, "_InspectorWorkerScriptLoaded")

    async def test_open_tab_delegates_and_counts(self):
        browser = FakeBrowser()
        service = BrowserService(browser)

        tab = await service.open_tab("file:///index.html", new_tab=True)

        self.assertEqual(tab.url, "file:///index.html")
        self.assertEqual(observability.snapshot()["calls"]["open_tab"], 1)

    async def test_screenshot_decodes_base64_png(self):
        tab = FakeTab()
        tab.program("send", base64.b64encode(b"png-bytes").decode("ascii"))

        content = await screenshot(
            tab,
            {"x": 0.0, "y": 0.0, "width": 8.0, "height": 8.0, "scale": 1.0},
        )

        self.assertEqual(content, b"png-bytes")
        self.assertEqual(observability.snapshot()["calls"]["screenshot"], 1)

    async def test_mhtml_and_outer_html_return_documents(self):
        tab = FakeTab()
        tab.program("send", "mhtml-content")
        self.assertEqual(await mhtml(tab), "mhtml-content")

        tab.program("send", SimpleNamespace(node_id=1), "<html></html>")
        self.assertEqual(await outer_html(tab), "<html></html>")

        calls = observability.snapshot()["calls"]
        self.assertEqual(calls["capture_mhtml"], 1)
        self.assertEqual(calls["capture_html"], 1)

    def test_get_browser_service_caches_per_browser(self):
        browser = FakeBrowser()
        self.assertIs(
            get_browser_service(browser), get_browser_service(browser)
        )

    def test_get_browser_service_tolerates_non_weakref_doubles(self):
        browser = SimpleNamespace(tabs=[])
        service = get_browser_service(browser)
        self.assertIs(service.browser, browser)


class NoDirectCdpRegressionTestCase(unittest.TestCase):
    """T-020 step 4: raw CDP idioms must stay inside browser/service.py."""

    FORBIDDEN = (
        re.compile(r"\.send\("),
        re.compile(r"_get_targets"),
        re.compile(r"\buc\.cdp\."),
        re.compile(r"\bcdp\.(?!com)"),
        re.compile(r"await\s+\w+\.evaluate\("),
    )

    def assert_no_direct_cdp(self, module_path: Path) -> None:
        source = module_path.read_text(encoding="utf-8")
        for pattern in self.FORBIDDEN:
            self.assertIsNone(
                pattern.search(source),
                f"{module_path.name} contains direct CDP call "
                f"({pattern.pattern!r}); route it through browser/service.py",
            )

    def test_main_has_no_direct_cdp_calls(self):
        import main

        self.assert_no_direct_cdp(Path(main.__file__))

    def test_evidence_capture_has_no_direct_cdp_calls(self):
        from evidence import capture

        self.assert_no_direct_cdp(Path(capture.__file__))


if __name__ == "__main__":
    unittest.main()
