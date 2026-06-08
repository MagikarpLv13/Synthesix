import asyncio
import unittest
from urllib.parse import parse_qs, urlparse

from bing import BingSearchEngine
from brave import BraveSearchEngine, looks_like_brave_robot_challenge
from duckduckgo import (
    DuckDuckGoSearchEngine,
    looks_like_duckduckgo_forbidden,
    looks_like_duckduckgo_robot_challenge,
)
from google import GoogleSearchEngine
from query_operators import SearchFilters


class EngineUrlTestCase(unittest.TestCase):
    def test_google_url_encodes_advanced_query(self):
        engine = GoogleSearchEngine()
        engine.query = '"python async" AND cdp'
        engine.max_results = 20

        self.assertIn("q=%22python+async%22+AND+cdp", engine.construct_url())

    def test_google_url_uses_custom_date_range(self):
        engine = GoogleSearchEngine()
        engine.query = '"python async"'
        engine.max_results = 20
        engine.search_filters = SearchFilters(after="2024-01-02", before="2024-03-04")

        params = parse_qs(urlparse(engine.construct_url()).query)

        self.assertEqual(params["tbs"], ["cdr:1,cd_min:01/02/2024,cd_max:03/04/2024"])

    def test_google_url_targets_selected_country(self):
        engine = GoogleSearchEngine()
        engine.query = '"python async"'
        engine.max_results = 20
        engine.search_filters = SearchFilters(country="Sweden")

        params = parse_qs(urlparse(engine.construct_url()).query)

        self.assertEqual(params["gl"], ["se"])

    def test_bing_url_encodes_advanced_query(self):
        engine = BingSearchEngine()
        engine.query = '"python async" AND cdp'
        engine.max_results = 20

        self.assertIn("q=%22python+async%22+AND+cdp", engine.construct_url())

    def test_bing_url_targets_selected_country(self):
        engine = BingSearchEngine()
        engine.query = '"python async"'
        engine.max_results = 20
        engine.search_filters = SearchFilters(country="Sweden")

        params = parse_qs(urlparse(engine.construct_url()).query)

        self.assertEqual(params["cc"], ["SE"])

    def test_brave_url_encodes_advanced_query(self):
        engine = BraveSearchEngine()
        engine.query = '"python async" AND cdp'

        self.assertIn("q=%22python+async%22+AND+cdp", engine.construct_url())

    def test_brave_url_uses_custom_date_range(self):
        engine = BraveSearchEngine()
        engine.query = '"python async"'
        engine.search_filters = SearchFilters(after="2024-01-02", before="2024-03-04")

        params = parse_qs(urlparse(engine.construct_url()).query)

        self.assertEqual(params["tf"], ["2024-01-02to2024-03-04"])

    def test_brave_url_targets_selected_country(self):
        engine = BraveSearchEngine()
        engine.query = '"python async"'
        engine.search_filters = SearchFilters(country="Sweden")

        params = parse_qs(urlparse(engine.construct_url()).query)

        self.assertEqual(params["country"], ["se"])

    def test_duckduckgo_url_uses_main_web_search_and_pure_search_params(self):
        engine = DuckDuckGoSearchEngine()
        engine.query = '"python async" AND cdp'

        url = engine.construct_url()

        self.assertTrue(url.startswith("https://duckduckgo.com/?"))
        self.assertIn("q=%22python+async%22+AND+cdp", url)
        self.assertIn("ia=web", url)
        self.assertIn("kp=-2", url)
        self.assertIn("kz=-1", url)
        self.assertIn("kac=-1", url)
        self.assertIn("k1=-1", url)
        self.assertIn("kl=wt-wt", url)

    def test_duckduckgo_url_uses_custom_date_range(self):
        engine = DuckDuckGoSearchEngine()
        engine.query = '"python async"'
        engine.search_filters = SearchFilters(after="2024-01-02", before="2024-03-04")

        params = parse_qs(urlparse(engine.construct_url()).query)

        self.assertEqual(params["df"], ["2024-01-02..2024-03-04"])

    def test_duckduckgo_url_targets_selected_country(self):
        engine = DuckDuckGoSearchEngine()
        engine.query = '"python async"'
        engine.search_filters = SearchFilters(country="Sweden")

        params = parse_qs(urlparse(engine.construct_url()).query)

        self.assertEqual(params["kl"], ["se-sv"])


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
    def test_detects_duckduckgo_robot_challenge_variants(self):
        self.assertTrue(
            looks_like_duckduckgo_robot_challenge(
                '<section class="anomaly-modal">'
                '<h1 class="anomaly-modal__title">Unfortunately, bots use DuckDuckGo too.</h1>'
                "</section>"
            )
        )
        self.assertTrue(
            looks_like_duckduckgo_robot_challenge(
                "<main>Please complete the following challenge to confirm this search "
                "was made by a human.</main>"
            )
        )

    def test_does_not_detect_regular_duckduckgo_results(self):
        self.assertFalse(
            looks_like_duckduckgo_robot_challenge(
                '<main><div class="result__body">Regular search result</div></main>'
            )
        )

    def test_detects_duckduckgo_forbidden_page(self):
        self.assertTrue(
            looks_like_duckduckgo_forbidden(
                "<html><head><title>403 Forbidden</title></head><body>Forbidden</body></html>"
            )
        )
        self.assertFalse(
            looks_like_duckduckgo_forbidden(
                '<div class="result__body">Forbidden Stories investigation</div>'
            )
        )

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

    def test_parse_modern_web_results_and_skip_ads(self):
        raw_html = """
        <html><body>
            <article data-testid="result">
                <a data-testid="result-title-a" href="https://example.com/python">
                    Python Example
                </a>
                <div data-result="snippet">A modern DuckDuckGo result.</div>
            </article>
            <article data-testid="result">
                <a data-testid="result-title-a" href="https://duckduckgo.com/y.js?ad_domain=example.org">
                    Sponsored result
                </a>
                <div data-result="snippet">Advertisement</div>
            </article>
        </body></html>
        """
        engine = DuckDuckGoSearchEngine()
        engine.max_results = 10

        results = engine.parse_results(raw_html)

        self.assertEqual(
            results,
            [
                {
                    "title": "Python Example",
                    "link": "https://example.com/python",
                    "description": "A modern DuckDuckGo result.",
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

    def test_post_execute_search_loads_additional_modern_results(self):
        class MoreResultsButton:
            async def click(self):
                return None

        class PaginatedTab:
            async def xpath(self, _selector):
                return [MoreResultsButton()]

            async def get_content(self):
                return """
                <html><body>
                    <article data-testid="result">
                        <a data-testid="result-title-a" href="https://example.com/one">One</a>
                        <div data-result="snippet">First</div>
                    </article>
                    <article data-testid="result">
                        <a data-testid="result-title-a" href="https://example.com/two">Two</a>
                        <div data-result="snippet">Second</div>
                    </article>
                </body></html>
                """

        engine = DuckDuckGoSearchEngine()
        engine.tab = PaginatedTab()
        engine.max_results = 2
        engine.results = [
            {
                "title": "One",
                "link": "https://example.com/one",
                "description": "First",
                "source": "DuckDuckGo",
            }
        ]
        engine.num_results = 1

        asyncio.run(engine.post_execute_search())

        self.assertEqual([result["title"] for result in engine.results], ["One", "Two"])


if __name__ == "__main__":
    unittest.main()
