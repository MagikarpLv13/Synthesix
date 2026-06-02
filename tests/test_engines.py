import asyncio
import unittest

from bing import BingSearchEngine
from brave import BraveSearchEngine, looks_like_brave_robot_challenge
from duckduckgo import DuckDuckGoSearchEngine
from google import GoogleSearchEngine


class EngineUrlTestCase(unittest.TestCase):
    def test_google_url_encodes_advanced_query(self):
        engine = GoogleSearchEngine()
        engine.query = '"python async" AND cdp'
        engine.max_results = 20

        self.assertIn("q=%22python+async%22+AND+cdp", engine.construct_url())

    def test_bing_url_encodes_advanced_query(self):
        engine = BingSearchEngine()
        engine.query = '"python async" AND cdp'
        engine.max_results = 20

        self.assertIn("q=%22python+async%22+AND+cdp", engine.construct_url())

    def test_brave_url_encodes_advanced_query(self):
        engine = BraveSearchEngine()
        engine.query = '"python async" AND cdp'

        self.assertIn("q=%22python+async%22+AND+cdp", engine.construct_url())

    def test_duckduckgo_url_uses_noai_html_and_pure_search_params(self):
        engine = DuckDuckGoSearchEngine()
        engine.query = '"python async" AND cdp'

        url = engine.construct_url()

        self.assertTrue(url.startswith("https://noai.duckduckgo.com/html/?"))
        self.assertIn("q=%22python+async%22+AND+cdp", url)
        self.assertIn("kp=-2", url)
        self.assertIn("kz=-1", url)
        self.assertIn("kac=-1", url)
        self.assertIn("k1=-1", url)
        self.assertIn("kl=wt-wt", url)


class BingPaginationTestCase(unittest.TestCase):
    def test_post_execute_search_stops_when_next_button_is_missing(self):
        class TabWithoutNextButton:
            async def xpath(self, _selector):
                return []

        engine = BingSearchEngine()
        engine.tab = TabWithoutNextButton()
        engine.max_results = 20
        engine.num_results = 10

        asyncio.run(engine.post_execute_search())


class BraveRobotChallengeTestCase(unittest.TestCase):
    def test_detects_brave_robot_challenge_variants(self):
        self.assertTrue(looks_like_brave_robot_challenge("<main>Verify you are human</main>"))
        self.assertTrue(looks_like_brave_robot_challenge("<main>Complete the security check</main>"))
        self.assertTrue(looks_like_brave_robot_challenge("<main>V\u00e9rifiez que vous \u00eates humain</main>"))
        self.assertTrue(
            looks_like_brave_robot_challenge(
                '<button class="button svelte-na4a2u type size--medium type--filled '
                'theme--default full-width tooltip--bottom" role="button" '
                'rel="noopener" data-sveltekit-reload="true">'
                '<span class="svelte-na4a2u">V\u00e9rifier</span></button>'
            )
        )
        self.assertTrue(
            looks_like_brave_robot_challenge(
                '<script>{page:"/captcha",blockRobots:true}</script>'
                '<button class="button full-width" role="button" '
                'data-sveltekit-reload="true"><span>Verificar</span></button>'
            )
        )

    def test_does_not_detect_regular_results_page(self):
        self.assertFalse(
            looks_like_brave_robot_challenge(
                "<main><div id='results'>Search results for python asyncio</div></main>"
            )
        )

    def test_find_click_failures_are_ignored(self):
        class BrokenElement:
            async def click(self):
                raise Exception("could not find position")

        class TabWithBrokenFindResult:
            async def find(self, *_args, **_kwargs):
                return BrokenElement()

        engine = BraveSearchEngine()
        engine.tab = TabWithBrokenFindResult()

        self.assertIsNone(asyncio.run(engine._click_robot_button_with_find()))


class DuckDuckGoParsingTestCase(unittest.TestCase):
    def test_parse_html_results_and_decode_redirect_links(self):
        raw_html = """
        <html>
            <body>
                <div class="result results_links web-result">
                    <div class="result__body">
                        <h2 class="result__title">
                            <a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fpython%3Fa%3D1">
                                Python Example
                            </a>
                        </h2>
                        <a class="result__snippet">A result about Python.</a>
                    </div>
                </div>
            </body>
        </html>
        """
        engine = DuckDuckGoSearchEngine()
        engine.max_results = 10

        results = engine.parse_results(raw_html)

        self.assertEqual(
            results,
            [
                {
                    "title": "Python Example",
                    "link": "https://example.com/python?a=1",
                    "description": "A result about Python.",
                    "source": "DuckDuckGo",
                }
            ],
        )

    def test_parse_results_honors_max_results(self):
        raw_html = """
        <html><body>
            <div class="result__body">
                <a class="result__a" href="https://example.com/one">One</a>
                <a class="result__snippet">First</a>
            </div>
            <div class="result__body">
                <a class="result__a" href="https://example.com/two">Two</a>
                <a class="result__snippet">Second</a>
            </div>
        </body></html>
        """
        engine = DuckDuckGoSearchEngine()
        engine.max_results = 1

        results = engine.parse_results(raw_html)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "One")


if __name__ == "__main__":
    unittest.main()
