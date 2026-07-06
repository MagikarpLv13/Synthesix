"""T-050: example tests for the shared FakeTab/FakeBrowser harness.

One test per documented use case (engine wait, home action loop, capture),
plus the fake-clock guarantee: timeouts are simulated without real time.
"""

import base64
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import observability
import search_engine as search_engine_module
from evidence.capture import capture_png
from main import wait_for_home_action
from search_engine import SearchEngine
from settings import get_settings
from tests.fakes import FakeBrowser, FakeElement, FakeTab, fake_clock

INDEX_URL = "file:///synthesix/index.html"


class ProbeEngine(SearchEngine):
    def __init__(self):
        super().__init__("Probe")

    def set_selector(self):
        self.selector = "#results"

    def construct_url(self):
        return "https://probe.example/search"

    def parse_results(self, raw_results):
        return []


class EngineWaitExampleTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        observability.reset()

    def tearDown(self):
        observability.reset()

    async def test_wait_for_page_load_success_without_real_time(self):
        engine = ProbeEngine()
        engine.set_selector()
        tab = FakeTab(url="https://probe.example/search")
        tab.program("query_selector", None, None, FakeElement())
        engine.tab = tab

        with fake_clock(search_engine_module) as clock:
            loaded = await engine.wait_for_page_load(timeout=30, interval=0.5)

        self.assertTrue(loaded)
        self.assertEqual(tab.journal.count("query_selector"), 3)
        self.assertEqual(clock.sleeps, [0.5, 0.5])

    async def test_wait_for_page_load_timeout_without_real_time(self):
        engine = ProbeEngine()
        engine.set_selector()
        engine.tab = FakeTab(url="https://probe.example/search")

        started = time.monotonic()
        with fake_clock(search_engine_module) as clock:
            loaded = await engine.wait_for_page_load(timeout=30, interval=0.5)
        real_elapsed = time.monotonic() - started

        self.assertFalse(loaded)
        self.assertGreaterEqual(clock.now, 30.0)
        # Acceptance: a 30 s timeout is simulated in well under 100 ms of
        # real time (generous bound to stay flake-free on slow machines).
        self.assertLess(real_elapsed, 1.0)
        self.assertEqual(engine.tab.journal.count("get_content"), 1)


class HomeActionExampleTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_home_action_is_consumed_from_fake_home_tab(self):
        actions = [None, {"action": "harness-probe"}]

        def home_scripts(script, *_args):
            if "consumeSettingsChange" in script:
                return None
            if "!!window.SynthesixOverlay" in script:
                return False
            if "setHistory" in script or "setInvestigations" in script:
                return None
            if "synthesixHome" in script and "consumeAction" in script:
                action = actions.pop(0) if actions else None
                return {
                    "ready": True,
                    "action": action,
                    "historyVersion": "",
                    "investigationsVersion": "",
                }
            return None

        home = FakeTab(url=INDEX_URL, target_id="home").on("evaluate", home_scripts)
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
                action = await wait_for_home_action(
                    browser, INDEX_URL, settings=settings
                )

        self.assertEqual(action["action"], "harness-probe")
        self.assertIs(action["_source_tab"], home)
        self.assertGreaterEqual(browser.journal.count("update_targets"), 1)
        self.assertGreaterEqual(browser.journal.count("evaluate"), 2)
        self.assertGreater(browser.journal.scripts_evaluated_bytes(), 0)


class CaptureExampleTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_capture_png_writes_decoded_screenshot(self):
        tab = FakeTab()
        tab.program("send", base64.b64encode(b"png-bytes").decode("ascii"))

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "shot.png"
            captured = await capture_png(
                tab,
                output_path,
                {"x": 0, "y": 0, "width": 32, "height": 16},
            )
            self.assertEqual(output_path.read_bytes(), b"png-bytes")

        self.assertEqual(captured.byte_size, len(b"png-bytes"))
        self.assertEqual(captured.width, 32.0)
        self.assertEqual(tab.journal.count("send"), 1)


class FakeTabBehaviourTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_programmed_exception_is_raised_then_defaults_resume(self):
        tab = FakeTab()
        tab.program("evaluate", RuntimeError("boom"), "value")

        with self.assertRaises(RuntimeError):
            await tab.evaluate("first()")
        self.assertEqual(await tab.evaluate("second()"), "value")
        self.assertIsNone(await tab.evaluate("third()"))

    async def test_navigation_and_close_update_state(self):
        browser = FakeBrowser()
        tab = await browser.get("https://example.com/a", new_tab=True)
        self.assertIs(browser.tabs[-1], tab)
        self.assertEqual(tab.url, "https://example.com/a")

        same_tab = await tab.get("https://example.com/b")
        self.assertIs(same_tab, tab)
        self.assertEqual(tab.url, "https://example.com/b")

        await tab.close()
        self.assertTrue(tab.closed)
        self.assertEqual(browser.journal.count("close"), 1)


if __name__ == "__main__":
    unittest.main()
