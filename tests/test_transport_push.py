"""T-021: push transport for local pages (home, investigation/report tabs).

`wait_for_home_action` normally polls each local tab by `evaluate` every
tick. In `transport_mode="push"`, a `Runtime.addBinding` is armed on those
tabs instead (`BrowserService.arm_dispatch_binding`); actions arrive through
`BrowserService.dispatch_queue` (simulated here with `FakeTab.fire`), and the
per-tab poll evaluate is throttled to `home_push_fallback_interval` once the
binding is confirmed. `transport_mode="poll"` (or a settings double missing
the attribute, as in every other pre-T-021 test) must behave byte for byte
like before this task.
"""

import asyncio
import json
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from zendriver import cdp

import observability
from browser import get_browser_service
from main import wait_for_home_action
from tests.fakes import FakeBrowser, FakeTab

INDEX_URL = "file:///synthesix/index.html"


def _ready_state(action=None):
    return {
        "ready": True,
        "action": action,
        "historyVersion": "",
        "investigationsVersion": "",
    }


class PushTransportTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        observability.reset()

    def tearDown(self):
        observability.reset()

    async def test_push_action_delivered_via_queue_for_home_tab(self):
        tab = FakeTab(url=INDEX_URL, target_id="home")
        tab.on("evaluate", lambda script, *_a: None)
        browser = FakeBrowser([tab])
        service = get_browser_service(browser)

        # Arm and fire before the loop even starts: proves delivery comes
        # from the queue, not from a lucky poll tick.
        self.assertTrue(await service.arm_dispatch_binding(tab))
        await tab.fire(
            cdp.runtime.BindingCalled,
            SimpleNamespace(
                name="synthesixDispatch",
                payload=json.dumps({"action": "cancel_search"}),
            ),
        )

        settings = SimpleNamespace(
            transport_mode="push",
            # Deliberately large: if delivery fell back to polling, this
            # test would time out instead of returning quickly.
            home_poll_interval=5.0,
            home_push_fallback_interval=2.0,
            empty_tabs_grace_seconds=0,
            default_history_limit=25,
        )
        with patch("main._cached_history_payload", return_value=("[]", "")):
            action = await asyncio.wait_for(
                wait_for_home_action(browser, INDEX_URL, settings=settings),
                timeout=1,
            )

        self.assertEqual(action["action"], "cancel_search")
        self.assertIs(action["_source_tab"], tab)

    async def test_push_action_delivered_via_queue_for_local_page_tab(self):
        tab = FakeTab(url="file:///synthesix/data/pages/case.html", target_id="case")
        tab.on("evaluate", lambda script, *_a: None)
        browser = FakeBrowser([tab])
        service = get_browser_service(browser)

        self.assertTrue(await service.arm_dispatch_binding(tab))
        await tab.fire(
            cdp.runtime.BindingCalled,
            SimpleNamespace(
                name="synthesixDispatch",
                payload=json.dumps({"action": "update_investigation_result"}),
            ),
        )

        settings = SimpleNamespace(
            transport_mode="push",
            home_poll_interval=5.0,
            home_push_fallback_interval=2.0,
            empty_tabs_grace_seconds=0,
            default_history_limit=25,
        )
        action = await asyncio.wait_for(
            wait_for_home_action(browser, INDEX_URL, settings=settings),
            timeout=1,
        )

        self.assertEqual(action["action"], "update_investigation_result")
        self.assertIs(action["_source_tab"], tab)

    async def test_confirmed_binding_throttles_local_consume_evaluate(self):
        calls: list[int] = []

        def home_scripts(script, *_args):
            if "consumeSettingsChange" in script:
                return None
            calls.append(1)
            if len(calls) < 3:
                return _ready_state()
            return _ready_state({"action": "probe"})

        tab = FakeTab(url=INDEX_URL, target_id="home")
        tab.on("evaluate", home_scripts)
        browser = FakeBrowser([tab])

        settings = SimpleNamespace(
            transport_mode="push",
            home_poll_interval=0.01,
            home_push_fallback_interval=0.05,
            empty_tabs_grace_seconds=0,
            default_history_limit=25,
        )
        with patch("main._cached_history_payload", return_value=("[]", "")):
            action = await asyncio.wait_for(
                wait_for_home_action(browser, INDEX_URL, settings=settings),
                timeout=5,
            )

        self.assertEqual(action["action"], "probe")
        self.assertEqual(len(calls), 3)
        # More ticks happened than home consumes: the throttle skipped
        # several. The per-tick settings scan (`eval_settings`, one per local
        # tab, never throttled) is the tick counter here — `targets_poll` is
        # no longer one-per-tick since T-022 made discovery event-driven.
        self.assertGreater(
            observability.snapshot()["calls"].get("eval_settings", 0), len(calls)
        )

    async def test_home_ready_dispatch_clears_local_sync_throttle(self):
        def home_scripts(script, *_args):
            if "consumeSettingsChange" in script:
                return None
            return _ready_state({"action": "probe"})

        tab = FakeTab(url=INDEX_URL, target_id="home")
        tab.on("evaluate", home_scripts)
        browser = FakeBrowser([tab])
        service = get_browser_service(browser)

        self.assertTrue(await service.arm_dispatch_binding(tab))
        # Simulate a consume right before a reload: without `home_ready`, the
        # throttle below (30s fallback) would block the sync past the test
        # timeout, so a pass proves the dispatch cleared it.
        service.last_local_sync_at["home"] = time.monotonic()
        await tab.fire(
            cdp.runtime.BindingCalled,
            SimpleNamespace(
                name="synthesixDispatch",
                payload=json.dumps({"action": "home_ready"}),
            ),
        )

        settings = SimpleNamespace(
            transport_mode="push",
            home_poll_interval=0.01,
            home_push_fallback_interval=30.0,
            empty_tabs_grace_seconds=0,
            default_history_limit=25,
        )
        with patch("main._cached_history_payload", return_value=("[]", "")):
            action = await asyncio.wait_for(
                wait_for_home_action(browser, INDEX_URL, settings=settings),
                timeout=2,
            )

        self.assertEqual(action["action"], "probe")

    async def test_poll_mode_never_arms_binding(self):
        tab = FakeTab(url=INDEX_URL, target_id="home")
        tab.on(
            "evaluate",
            lambda script, *_a: (
                _ready_state({"action": "probe"})
                if "consumeAction" in script
                else None
            ),
        )
        browser = FakeBrowser([tab])
        # No `transport_mode` at all, like every pre-T-021 settings double.
        settings = SimpleNamespace(
            home_poll_interval=0,
            empty_tabs_grace_seconds=0,
            default_history_limit=25,
        )
        with patch("main._cached_history_payload", return_value=("[]", "")):
            action = await asyncio.wait_for(
                wait_for_home_action(browser, INDEX_URL, settings=settings),
                timeout=2,
            )

        self.assertEqual(action["action"], "probe")
        self.assertEqual(
            get_browser_service(browser).armed_binding_targets, set()
        )
        self.assertEqual(observability.snapshot()["calls"].get("arm_binding", 0), 0)


if __name__ == "__main__":
    unittest.main()
