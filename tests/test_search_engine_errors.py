import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch

from brave import BraveSearchEngine
from exceptions import BrowserSessionError, RobotChallengeError, SearchEngineError
from search_engine import SearchEngine


class DummySearchEngine(SearchEngine):
    def __init__(self, parse_error=None):
        super().__init__("Dummy")
        self.parse_error = parse_error

    def set_selector(self):
        self.selector = "#results"

    def construct_url(self) -> str:
        return "https://example.com/search?q=dummy"

    def parse_results(self, raw_results):
        if self.parse_error:
            raise self.parse_error
        return [
            {
                "title": "Dummy title",
                "link": "https://example.com/dummy",
                "description": "Dummy description",
                "source": self.name,
            }
        ]


class LoadedTab:
    async def query_selector(self, _selector):
        return object()

    async def get_content(self):
        return "<html><div id='results'></div></html>"

    async def close(self):
        return None


class WorkingBrowser:
    main_tab = None

    async def get(self, _url, new_tab=True):
        return LoadedTab()


class FailingBrowser:
    main_tab = None

    async def get(self, _url, new_tab=True):
        raise RuntimeError("cdp disconnected")


class SearchEngineErrorTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_missing_browser_raises_browser_session_error(self):
        engine = DummySearchEngine()

        with self.assertRaises(BrowserSessionError):
            await engine.search("dummy")

    async def test_navigation_failure_raises_browser_session_error(self):
        engine = DummySearchEngine()

        with self.assertRaises(BrowserSessionError) as raised:
            await engine.search("dummy", FailingBrowser(), 5)

        self.assertEqual(raised.exception.url, "https://example.com/search?q=dummy")
        self.assertIsInstance(raised.exception.original_error, RuntimeError)

    async def test_parse_failure_raises_search_engine_error(self):
        engine = DummySearchEngine(parse_error=ValueError("bad html"))

        with self.assertRaises(SearchEngineError) as raised:
            await engine.search("dummy", WorkingBrowser(), 5)

        self.assertEqual(raised.exception.engine_name, "Dummy")
        self.assertEqual(raised.exception.query, "dummy")
        self.assertIsInstance(raised.exception.original_error, ValueError)


class BraveRobotChallengeErrorTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_unresolved_robot_challenge_raises_robot_challenge_error(self):
        class ChallengeTab:
            async def bring_to_front(self):
                return None

            async def get_content(self):
                return "<main>Verify you are human</main>"

            async def find(self, *_args, **_kwargs):
                return None

            async def evaluate(self, _expression):
                return None

        engine = BraveSearchEngine()
        engine.query = "dummy"
        engine.current_url = "https://search.brave.com/search?q=dummy"
        engine.tab = ChallengeTab()

        with TemporaryDirectory() as temp_dir:
            with patch.dict("os.environ", {"SYNTHESIX_BASE_DIR": temp_dir}, clear=True):
                with self.assertLogs("brave", level="WARNING"):
                    with self.assertRaises(RobotChallengeError) as raised:
                        await engine.robot_check()

        self.assertEqual(raised.exception.engine_name, "Brave")
        self.assertIn("html", raised.exception.captured_artifacts)
        self.assertIn("text", raised.exception.captured_artifacts)


if __name__ == "__main__":
    unittest.main()
