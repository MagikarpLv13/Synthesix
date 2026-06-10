import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from brave import BraveSearchEngine
from duckduckgo import DuckDuckGoSearchEngine
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
    async def test_debug_html_capture_keeps_unique_raw_pages(self):
        engine = DummySearchEngine()

        with TemporaryDirectory() as temp_dir:
            env = {
                "SYNTHESIX_BASE_DIR": temp_dir,
                "SYNTHESIX_DEBUG_HTML": "1",
            }
            with patch.dict("os.environ", env, clear=True):
                first_path = engine.capture_debug_html("<html>debug page</html>", "results")
                duplicate_path = engine.capture_debug_html("<html>debug page</html>", "load_timeout")

            self.assertIsNotNone(first_path)
            self.assertTrue(Path(first_path).exists())
            self.assertEqual(
                Path(first_path).read_text(encoding="utf-8"),
                "<html>debug page</html>",
            )
            self.assertIsNone(duplicate_path)

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
            url = "https://search.brave.com/challenge"

            async def bring_to_front(self):
                self.focused = True
                return None

            async def get_content(self):
                return "<main>Verify you are human</main>"

            async def find(self, *_args, **_kwargs):
                return None

            async def evaluate(self, _expression):
                return None

            async def query_selector(self, _selector):
                return None

            async def save_screenshot(self, filename, **_kwargs):
                Path(filename).write_bytes(b"png")

        engine = BraveSearchEngine()
        engine.query = "dummy"
        engine.current_url = "https://search.brave.com/search?q=dummy"
        engine.tab = ChallengeTab()

        with TemporaryDirectory() as temp_dir:
            env = {
                "SYNTHESIX_BASE_DIR": temp_dir,
                "SYNTHESIX_BRAVE_RESULTS_TIMEOUT": "0.01",
                "SYNTHESIX_BRAVE_RESULTS_INTERVAL": "0",
            }
            with patch.dict("os.environ", env, clear=True):
                with self.assertLogs("brave", level="WARNING"):
                    with self.assertRaises(RobotChallengeError) as raised:
                        await engine.robot_check()

        self.assertEqual(raised.exception.engine_name, "Brave")
        self.assertIn("html", raised.exception.captured_artifacts)
        self.assertIn("text", raised.exception.captured_artifacts)
        self.assertTrue(engine.tab.focused)

    async def test_unknown_brave_challenge_resumes_after_manual_resolution(self):
        class ChallengeTab:
            url = "https://search.brave.com/challenge"

            def __init__(self):
                self.query_checks = 0
                self.focused = False

            async def bring_to_front(self):
                self.focused = True

            async def get_content(self):
                return "<main>Please verify your identity</main>"

            async def find(self, *_args, **_kwargs):
                return None

            async def evaluate(self, _expression):
                return None

            async def query_selector(self, _selector):
                self.query_checks += 1
                return object() if self.query_checks >= 2 else None

            async def save_screenshot(self, filename, **_kwargs):
                Path(filename).write_bytes(b"png")

        engine = BraveSearchEngine()
        engine.query = "dummy"
        engine.current_url = "https://search.brave.com/challenge"
        engine.tab = ChallengeTab()

        with TemporaryDirectory() as temp_dir:
            env = {
                "SYNTHESIX_BASE_DIR": temp_dir,
                "SYNTHESIX_BRAVE_RESULTS_TIMEOUT": "1",
                "SYNTHESIX_BRAVE_RESULTS_INTERVAL": "0",
            }
            with patch.dict("os.environ", env, clear=True):
                resolved = await engine.robot_check()

        self.assertTrue(resolved)
        self.assertTrue(engine.tab.focused)


class DuckDuckGoRobotChallengeErrorTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_accepts_parseable_results_without_matching_selector(self):
        class ParseableTab:
            async def query_selector(self, _selector):
                return None

            async def get_content(self):
                return """
                    <article data-testid="result">
                        <a
                            data-testid="result-title-a"
                            href="https://example.com/result"
                        >Result</a>
                        <div data-result="snippet">Description</div>
                    </article>
                """

        engine = DuckDuckGoSearchEngine()
        engine.query = "dummy"
        engine.max_results = 10
        engine.current_url = engine.construct_url()
        engine.tab = ParseableTab()

        loaded = await engine.wait_for_page_load(timeout=0.1, interval=0)

        self.assertTrue(loaded)

    async def test_uses_html_fallback_when_main_page_has_no_results(self):
        class FallbackTab:
            def __init__(self):
                self.content = "<html><body>Loading</body></html>"
                self.loaded_urls = []

            async def query_selector(self, _selector):
                return None

            async def get_content(self):
                return self.content

            async def get(self, url):
                self.loaded_urls.append(url)
                self.content = """
                    <div class="result__body">
                        <a
                            class="result__a"
                            href="https://example.com/fallback"
                        >Fallback result</a>
                    </div>
                """
                return self

        engine = DuckDuckGoSearchEngine()
        engine.query = "dummy"
        engine.max_results = 10
        engine.current_url = engine.construct_url()
        engine.tab = FallbackTab()

        loaded = await engine.wait_for_page_load(timeout=0.01, interval=0)

        self.assertTrue(loaded)
        self.assertEqual(
            engine.tab.loaded_urls,
            [engine.construct_url(engine.fallback_base_url)],
        )

    async def test_forbidden_after_manual_challenge_reloads_original_query(self):
        class ChallengeThenForbiddenTab:
            content_calls = 0
            reloaded_url = None

            async def get_content(self):
                self.content_calls += 1
                if self.content_calls == 1:
                    return (
                        '<section class="anomaly-modal">'
                        '<h1 class="anomaly-modal__title">'
                        "Unfortunately, bots use DuckDuckGo too."
                        "</h1>"
                        "</section>"
                    )
                return "<html><head><title>403 Forbidden</title></head></html>"

            async def bring_to_front(self):
                return None

            async def save_screenshot(self, filename, **_kwargs):
                Path(filename).write_bytes(b"png")

            async def query_selector(self, _selector):
                return object() if self.reloaded_url else None

            async def get(self, url):
                self.reloaded_url = url
                return self

        engine = DuckDuckGoSearchEngine()
        engine.query = "dummy"
        engine.current_url = "https://noai.duckduckgo.com/html/?q=dummy"
        engine.tab = ChallengeThenForbiddenTab()

        with TemporaryDirectory() as temp_dir:
            env = {
                "SYNTHESIX_BASE_DIR": temp_dir,
                "SYNTHESIX_DUCKDUCKGO_ROBOT_TIMEOUT": "1",
                "SYNTHESIX_DUCKDUCKGO_ROBOT_INTERVAL": "0",
            }
            with patch.dict("os.environ", env, clear=True):
                with self.assertLogs("duckduckgo", level="INFO"):
                    resolved = await engine.robot_check()

                follow_up_html = engine._challenge_follow_up_captures["follow_up_html"]
                self.assertTrue(Path(follow_up_html).exists())

        self.assertTrue(resolved)
        self.assertEqual(engine.tab.reloaded_url, engine.current_url)

    async def test_robot_challenge_resumes_after_manual_resolution(self):
        class ChallengeTab:
            query_checks = 0

            async def get_content(self):
                return (
                    '<section class="anomaly-modal">'
                    '<h1 class="anomaly-modal__title">'
                    "Unfortunately, bots use DuckDuckGo too."
                    "</h1>"
                    "</section>"
                )

            async def bring_to_front(self):
                return None

            async def save_screenshot(self, filename, **_kwargs):
                Path(filename).write_bytes(b"png")

            async def query_selector(self, _selector):
                self.query_checks += 1
                return object() if self.query_checks >= 2 else None

        engine = DuckDuckGoSearchEngine()
        engine.query = "dummy"
        engine.current_url = "https://noai.duckduckgo.com/html/?q=dummy"
        engine.tab = ChallengeTab()

        with TemporaryDirectory() as temp_dir:
            env = {
                "SYNTHESIX_BASE_DIR": temp_dir,
                "SYNTHESIX_DUCKDUCKGO_ROBOT_TIMEOUT": "1",
                "SYNTHESIX_DUCKDUCKGO_ROBOT_INTERVAL": "0",
            }
            with patch.dict("os.environ", env, clear=True):
                with self.assertLogs("duckduckgo", level="INFO") as logs:
                    resolved = await engine.robot_check()

        self.assertTrue(resolved)
        self.assertTrue(any("resolved manually" in entry for entry in logs.output))

    async def test_unresolved_robot_challenge_is_captured_and_raises(self):
        class ChallengeTab:
            async def get_content(self):
                return (
                    '<section class="anomaly-modal">'
                    '<h1 class="anomaly-modal__title">'
                    "Unfortunately, bots use DuckDuckGo too."
                    "</h1>"
                    "<p>Please complete the following challenge.</p>"
                    "</section>"
                )

            async def bring_to_front(self):
                return None

            async def save_screenshot(self, filename, **_kwargs):
                Path(filename).write_bytes(b"png")

            async def query_selector(self, _selector):
                return None

        engine = DuckDuckGoSearchEngine()
        engine.query = "dummy"
        engine.current_url = "https://noai.duckduckgo.com/html/?q=dummy"
        engine.tab = ChallengeTab()

        with TemporaryDirectory() as temp_dir:
            env = {
                "SYNTHESIX_BASE_DIR": temp_dir,
                "SYNTHESIX_DUCKDUCKGO_ROBOT_TIMEOUT": "0.001",
                "SYNTHESIX_DUCKDUCKGO_ROBOT_INTERVAL": "0",
            }
            with patch.dict("os.environ", env, clear=True):
                with self.assertLogs("duckduckgo", level="WARNING"):
                    with self.assertRaises(RobotChallengeError) as raised:
                        await engine.robot_check()

                captured = raised.exception.captured_artifacts
                self.assertTrue(Path(captured["html"]).exists())
                self.assertTrue(Path(captured["text"]).exists())
                self.assertTrue(Path(captured["screenshot"]).exists())

        self.assertEqual(raised.exception.engine_name, "DuckDuckGo")


if __name__ == "__main__":
    unittest.main()
