"""Offline parser golden tests.

To refresh a fixture after an engine changes:
1. Run Synthesix with ``SYNTHESIX_DEBUG_HTML=1`` and a neutral query.
2. Copy only the result markup needed by that engine parser into
   ``tests/fixtures/engines/<engine>_<YYYY-MM>.html``.
3. Remove cookies, tokens, account data, investigation data, and unrelated
   page chrome before committing the fixture.
"""

from pathlib import Path
from urllib.parse import urlparse
import unittest

from bing import BingSearchEngine
from brave import BraveSearchEngine
from duckduckgo import DuckDuckGoSearchEngine
from google import GoogleSearchEngine


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "engines"


class EngineGoldenParsingTestCase(unittest.TestCase):
    def test_engine_golden_fixtures_parse_public_results(self):
        cases = (
            (GoogleSearchEngine, "google_2026-06.html"),
            (BingSearchEngine, "bing_2026-06.html"),
            (DuckDuckGoSearchEngine, "duckduckgo_2026-06.html"),
            (BraveSearchEngine, "brave_2026-06.html"),
            (BraveSearchEngine, "brave_2026-07.html"),
        )

        for engine_cls, filename in cases:
            with self.subTest(engine=engine_cls.__name__, fixture=filename):
                engine = engine_cls()
                engine.max_results = 5
                results = engine.parse_results(
                    (FIXTURE_DIR / filename).read_text(encoding="utf-8")
                )

                self.assertGreaterEqual(len(results), 5)
                for result in results[:5]:
                    self.assertEqual(result["source"], engine.name)
                    self.assertTrue(result["title"].strip())
                    self.assertTrue(result["description"].strip())
                    parsed = urlparse(result["link"])
                    self.assertIn(parsed.scheme, {"http", "https"})
                    self.assertTrue(parsed.netloc)

                if engine.name == "Bing":
                    self.assertFalse(
                        any("bing.com/ck/" in result["link"] for result in results)
                    )
                if engine.name == "DuckDuckGo":
                    self.assertFalse(
                        any("duckduckgo.com/l/" in result["link"] for result in results)
                    )

    def test_brave_xpath_fallback_fixture_parses_when_json_is_absent(self):
        engine = BraveSearchEngine()
        engine.max_results = 5

        with self.assertLogs("brave", level="WARNING") as logs:
            results = engine.parse_results(
                (FIXTURE_DIR / "brave_xpath_2026-06.html").read_text(encoding="utf-8")
            )

        self.assertGreaterEqual(len(results), 5)
        self.assertEqual(engine.nb_results_per_page, 5)
        self.assertTrue(
            any("XPath fallback parsed 5 results" in message for message in logs.output)
        )


if __name__ == "__main__":
    unittest.main()
