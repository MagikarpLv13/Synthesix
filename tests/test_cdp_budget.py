"""T-006: lock the CDP call budget of the idle poll loop.

Simulates `wait_for_home_action` ticks against a fake browser exposing one
home tab, one external http(s) tab and one local investigation tab, then
asserts the exact number of instrumented calls per category. Any change that
adds CDP traffic to the hot loop must consciously update these numbers
(they are the measured baseline the optimization tasks drive down).
"""

import asyncio
import tempfile
import unittest
from unittest.mock import patch

import observability
from main import _OVERLAY_FOCUS_GUARD_ARMED_TARGETS, wait_for_home_action
from settings import get_settings

INDEX_URL = "file:///synthesix/index.html"


class FakeTab:
    def __init__(self, url, target_id, home_actions=None):
        self.url = url
        self.target_id = target_id
        self.closed = False
        self._home_actions = list(home_actions or [])

    async def evaluate(self, script):
        if "consumeSettingsChange" in script:
            return None
        if "!!window.SynthesixOverlay" in script:
            return False
        if "synthesixHome" in script:
            action = self._home_actions.pop(0) if self._home_actions else None
            return {"ready": True, "action": action}
        # Overlay install/consume and synthesixPage consume paths.
        return None

    async def send(self, command):
        return None

    async def bring_to_front(self):
        return None


class FakeBrowser:
    def __init__(self, tabs):
        self.tabs = tabs
        self.stopped = False

    async def update_targets(self):
        return None

    async def _get_targets(self):
        return [
            type("Target", (), {"target_id": tab.target_id, "type_": "page"})()
            for tab in self.tabs
        ]


class CdpBudgetTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        observability.reset()
        _OVERLAY_FOCUS_GUARD_ARMED_TARGETS.clear()

    def tearDown(self):
        observability.reset()
        _OVERLAY_FOCUS_GUARD_ARMED_TARGETS.clear()

    async def test_idle_tick_budget_is_locked(self):
        ticks = 3
        home = FakeTab(
            INDEX_URL,
            "home",
            home_actions=[None] * (ticks - 1) + [{"action": "budget-probe"}],
        )
        external = FakeTab("https://example.com/article", "ext")
        case_page = FakeTab("file:///synthesix/data/pages/case.html", "case")
        browser = FakeBrowser([home, external, case_page])

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(
                "os.environ",
                {
                    "SYNTHESIX_BASE_DIR": temp_dir,
                    "SYNTHESIX_HOME_POLL_INTERVAL": "0",
                },
            ):
                settings = get_settings()
                action = await asyncio.wait_for(
                    wait_for_home_action(browser, INDEX_URL, settings=settings),
                    timeout=10,
                )

        self.assertEqual(action["action"], "budget-probe")

        calls = observability.snapshot()["calls"]
        # Baseline measured on 2026-07-06 (see docs/tasks/T-006): one target
        # inventory per tick, one settings probe per local tab and one home
        # consume per tick; two overlay evaluates per external tab and one
        # page consume per tick — except on the final tick, where the home
        # action returns before the overlay/page loop runs.
        idle_ticks = ticks - 1
        self.assertEqual(calls.get("targets_poll", 0), ticks)
        self.assertEqual(calls.get("eval_settings", 0), 2 * ticks)
        self.assertEqual(calls.get("eval_home", 0), ticks)
        self.assertEqual(calls.get("eval_overlay", 0), 2 * idle_ticks)
        self.assertEqual(calls.get("eval_page", 0), idle_ticks)

        evaluates_per_idle_tick = (
            2  # settings probes (home + case page)
            + 1  # home consume
            + calls.get("eval_overlay", 0) / idle_ticks
            + calls.get("eval_page", 0) / idle_ticks
        )
        self.assertLessEqual(evaluates_per_idle_tick, 6)


if __name__ == "__main__":
    unittest.main()
