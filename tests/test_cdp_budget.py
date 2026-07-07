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
from browser import get_browser_service
from main import wait_for_home_action
from settings import get_settings
from tests.fakes import FakeBrowser, FakeTab

INDEX_URL = "file:///synthesix/index.html"


def make_tab(url, target_id, home_actions=None, home_versions=("", "")):
    """FakeTab answering the home/overlay/page poll scripts (T-050 harness)."""
    tab = FakeTab(url=url, target_id=target_id)
    tab.pushed_payloads = 0
    actions = list(home_actions or [])

    def home_scripts(script, *_args):
        if "consumeSettingsChange" in script:
            return None
        if "!!window.SynthesixOverlay" in script:
            return False
        if "setHistory" in script or "setInvestigations" in script:
            tab.pushed_payloads += 1
            return None
        if "synthesixHome" in script and "consumeAction" in script:
            action = actions.pop(0) if actions else None
            return {
                "ready": True,
                "action": action,
                "historyVersion": home_versions[0],
                "investigationsVersion": home_versions[1],
            }
        # Overlay install/consume and synthesixPage consume paths.
        return None

    tab.on("evaluate", home_scripts)
    return tab


class CdpBudgetTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        observability.reset()

    def tearDown(self):
        observability.reset()

    async def test_idle_tick_budget_is_locked(self):
        ticks = 3
        home = make_tab(
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

        snapshot = observability.snapshot()
        calls = snapshot["calls"]
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

        # T-003: page versions match the backend, so no payload is embedded
        # in the steady state.
        self.assertEqual(snapshot["bytes"].get("eval_home", 0), 0)
        self.assertEqual(home.pushed_payloads, 0)

        evaluates_per_idle_tick = (
            2  # settings probes (home + case page)
            + 1  # home consume
            + calls.get("eval_overlay", 0) / idle_ticks
            + calls.get("eval_page", 0) / idle_ticks
        )
        self.assertLessEqual(evaluates_per_idle_tick, 6)

    async def test_stale_home_versions_trigger_payload_push(self):
        home = make_tab(
            INDEX_URL,
            "home",
            home_actions=[{"action": "budget-probe"}],
            home_versions=("stale-history", "stale-investigations"),
        )
        browser = FakeBrowser([home])

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(
                "os.environ",
                {
                    "SYNTHESIX_BASE_DIR": temp_dir,
                    "SYNTHESIX_HOME_POLL_INTERVAL": "0",
                },
            ):
                settings = get_settings()
                await asyncio.wait_for(
                    wait_for_home_action(browser, INDEX_URL, settings=settings),
                    timeout=10,
                )

        snapshot = observability.snapshot()
        # One probe plus one payload push on the single tick.
        self.assertEqual(snapshot["calls"].get("eval_home", 0), 2)
        self.assertEqual(home.pushed_payloads, 1)
        # Empty temp-dir data: "[]" history + "[]" investigations payloads.
        self.assertEqual(snapshot["bytes"].get("eval_home", 0), 4)

    async def test_focus_guard_registry_is_pruned_with_targets(self):
        home = make_tab(INDEX_URL, "home", home_actions=[{"action": "probe"}])
        browser = FakeBrowser([home])
        registry = get_browser_service(browser).armed_script_targets
        registry.update({"home", "closed-tab"})

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(
                "os.environ",
                {
                    "SYNTHESIX_BASE_DIR": temp_dir,
                    "SYNTHESIX_HOME_POLL_INTERVAL": "0",
                },
            ):
                settings = get_settings()
                await asyncio.wait_for(
                    wait_for_home_action(browser, INDEX_URL, settings=settings),
                    timeout=10,
                )

        self.assertEqual(registry, {"home"})

    async def test_unreachable_browser_quits_instead_of_looping(self):
        class DeadBrowser:
            stopped = False
            tabs = []

            async def update_targets(self):
                raise ConnectionError("chrome is gone")

            async def _get_targets(self):
                raise ConnectionError("chrome is gone")

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(
                "os.environ",
                {
                    "SYNTHESIX_BASE_DIR": temp_dir,
                    "SYNTHESIX_HOME_POLL_INTERVAL": "0",
                },
            ):
                settings = get_settings()
                with patch("main._BROWSER_UNREACHABLE_QUIT_SECONDS", 0.05):
                    action = await asyncio.wait_for(
                        wait_for_home_action(
                            DeadBrowser(), INDEX_URL, settings=settings
                        ),
                        timeout=10,
                    )

        self.assertEqual(action, {"action": "quit"})


if __name__ == "__main__":
    unittest.main()
