"""T-020: BrowserService unit tests + no-direct-CDP regression guard.

The guard test greps the migrated modules for raw CDP idioms so a future
edit cannot quietly reintroduce `tab.send(...)`/`browser._get_targets`
outside `browser/service.py`.
"""

import base64
import json
import re
import unittest
from pathlib import Path
from types import SimpleNamespace

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
