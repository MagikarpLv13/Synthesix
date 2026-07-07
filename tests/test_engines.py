import asyncio
import base64
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import brave as brave_module
from bing import BingSearchEngine, resolve_bing_redirect
from brave import (
    BraveSearchEngine,
    looks_like_brave_challenge_url,
    looks_like_brave_robot_challenge,
)
from duckduckgo import (
    DuckDuckGoSearchEngine,
    looks_like_duckduckgo_forbidden,
    looks_like_duckduckgo_no_results,
    looks_like_duckduckgo_robot_challenge,
)
from exceptions import RobotChallengeError
from google import GoogleSearchEngine
from query_operators import SearchFilters
from search_engine import PROBE_MARKER


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


class _GoogleRobotTab:
    def __init__(self, captcha_node=None, url="https://www.google.com/search?q=x"):
        self.captcha_node = captcha_node
        self.url = url
        self.activated = False
        # reCAPTCHA checkbox best-effort click (None => nothing to click).
        self.checkbox_coords = None
        self.clicks = 0

    async def query_selector(self, selector):
        assert selector == "#captcha-form"
        return self.captcha_node

    async def activate(self):
        self.activated = True

    async def evaluate(self, script):
        return self.checkbox_coords

    async def send(self, command, *args, **kwargs):
        # click_at dispatches mouseMoved + mousePressed + mouseReleased.
        self.clicks += 1
        return None


class BraveEmptyResultsDumpTestCase(unittest.TestCase):
    """A silently empty Brave (both embedded-JSON and XPath parsing miss)
    saves the raw page so the drifted markup can be diagnosed."""

    def _engine(self):
        engine = BraveSearchEngine()
        engine.max_results = 10
        engine.num_results = 0
        return engine

    def test_dumps_raw_page_when_zero_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = SimpleNamespace(debug_html_dir=Path(tmp))
            with patch.object(brave_module, "get_settings", lambda: fake):
                results = self._engine().parse_results(
                    "<html><body>totally different layout</body></html>"
                )
            self.assertEqual(results, [])
            dumped = list(Path(tmp).glob("brave_empty_results_*.html"))
            self.assertEqual(len(dumped), 1)

    def test_dumps_even_when_page_mentions_robot(self):
        # A fully rendered SERP routinely contains the bare word "robot"; the
        # dump must NOT be skipped for it (that hid the capture we needed).
        with tempfile.TemporaryDirectory() as tmp:
            fake = SimpleNamespace(debug_html_dir=Path(tmp))
            with patch.object(brave_module, "get_settings", lambda: fake):
                self._engine().parse_results(
                    "<html><body>result about a chatbot robot</body></html>"
                )
            self.assertEqual(len(list(Path(tmp).glob("*.html"))), 1)

    def test_dumps_only_once_per_search(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = SimpleNamespace(debug_html_dir=Path(tmp))
            engine = self._engine()
            with patch.object(brave_module, "get_settings", lambda: fake):
                engine.parse_results("<html><body>page one</body></html>")
                engine.parse_results("<html><body>page two</body></html>")
            self.assertEqual(len(list(Path(tmp).glob("*.html"))), 1)


class BraveResultsWaitTestCase(unittest.IsolatedAsyncioTestCase):
    """Brave renders results client-side after a reveal; the wait must hold
    for the results container (not the base 2.5s) and bail early on a captcha."""

    def _fake_settings(self):
        return SimpleNamespace(
            brave_results_timeout=5.0,
            brave_results_interval=0.01,
        )

    def _engine(self, probe_state):
        engine = BraveSearchEngine()
        engine.query = "x"
        engine.set_selector()

        class Tab:
            async def evaluate(self, expression):
                return json.dumps(probe_state)

        engine.tab = Tab()
        return engine

    async def test_wait_returns_once_results_container_present(self):
        engine = self._engine(
            {"found": True, "resultCount": 5, "challenge": False, "ready": "complete",
             "bodyLength": 10, "forbidden": False, "noResults": False, "url": "", "title": ""}
        )
        with patch.object(brave_module, "get_settings", self._fake_settings):
            self.assertTrue(await engine.wait_for_page_load())

    async def test_results_wait_bails_out_on_challenge(self):
        engine = self._engine(
            {"found": False, "resultCount": 0, "challenge": True, "ready": "complete",
             "bodyLength": 10, "forbidden": False, "noResults": False, "url": "", "title": ""}
        )
        with patch.object(brave_module, "get_settings", self._fake_settings):
            self.assertFalse(await engine._wait_for_results_container())

    def test_selector_targets_result_rows_not_container(self):
        # The wait must key on the result rows (which appear once Brave
        # hydrates), not the empty `#results` container that mounts first.
        engine = BraveSearchEngine()
        engine.set_selector()
        self.assertIn("data-pos", engine.selector)


class GoogleRobotCheckTestCase(unittest.IsolatedAsyncioTestCase):
    """T-004: captcha detection uses query_selector and the /sorry/ URL,
    and an unresolved captcha surfaces as RobotChallengeError (coverage
    status "challenge" instead of a silent empty result)."""

    def _engine(self, tab, wait_result):
        engine = GoogleSearchEngine()
        engine.query = "probe"
        engine.tab = tab

        async def fake_wait(timeout=None, interval=None):
            return wait_result

        engine.wait_for_page_load = fake_wait
        return engine

    async def test_no_marker_means_no_robot(self):
        engine = self._engine(_GoogleRobotTab(), wait_result=True)

        self.assertFalse(await engine.robot_check())

    async def test_captcha_form_detected_and_resolved(self):
        tab = _GoogleRobotTab(captcha_node=object())
        engine = self._engine(tab, wait_result=True)

        self.assertTrue(await engine.robot_check())
        self.assertTrue(tab.activated)

    async def test_sorry_url_detected_without_form(self):
        tab = _GoogleRobotTab(
            url="https://www.google.com/sorry/index?continue=https://www.google.com/search"
        )
        engine = self._engine(tab, wait_result=True)

        self.assertTrue(await engine.robot_check())

    async def test_unresolved_captcha_raises_challenge_error(self):
        tab = _GoogleRobotTab(captcha_node=object())
        engine = self._engine(tab, wait_result=False)

        with self.assertRaises(RobotChallengeError):
            await engine.robot_check()

    async def test_recaptcha_checkbox_clicked_when_located(self):
        tab = _GoogleRobotTab(captcha_node=object())
        tab.checkbox_coords = {"x": 40.0, "y": 300.0}
        engine = self._engine(tab, wait_result=True)

        self.assertTrue(await engine.robot_check())
        # A trusted click = mouseMoved + mousePressed + mouseReleased.
        self.assertEqual(tab.clicks, 3)

    async def test_no_checkbox_means_no_click(self):
        tab = _GoogleRobotTab(captcha_node=object())  # checkbox_coords None
        engine = self._engine(tab, wait_result=True)

        self.assertTrue(await engine.robot_check())
        self.assertEqual(tab.clicks, 0)


class ProbePageStateTestCase(unittest.IsolatedAsyncioTestCase):
    """T-012: composite probe replaces per-iteration query_selector polls
    and in-loop full-page reads in engine wait loops."""

    async def test_probe_state_normalizes_json_payload(self):
        engine = DuckDuckGoSearchEngine()
        engine.query = "dummy"
        engine.set_selector()
        captured = {}

        class Tab:
            async def evaluate(self, expression):
                captured["expression"] = expression
                return json.dumps(
                    {
                        "found": True,
                        "ready": "complete",
                        "bodyLength": 1234,
                        "resultCount": 7,
                        "challenge": False,
                        "forbidden": True,
                        "noResults": False,
                        "url": "https://duckduckgo.com/?q=dummy",
                        "title": "403 Forbidden",
                    }
                )

        engine.tab = Tab()
        state = await engine.probe_page_state()

        self.assertTrue(state["found"])
        self.assertEqual(state["ready"], "complete")
        self.assertEqual(state["body_length"], 1234)
        self.assertEqual(state["result_count"], 7)
        self.assertTrue(state["forbidden"])
        self.assertFalse(state["challenge"])
        # The engine markers travel inside the probe expression.
        self.assertIn(PROBE_MARKER, captured["expression"])
        self.assertIn("anomaly-modal", captured["expression"])
        self.assertIn(
            "unfortunately, bots use duckduckgo too", captured["expression"]
        )

    async def test_probe_failure_degrades_to_not_found(self):
        engine = BraveSearchEngine()
        engine.set_selector()

        class Tab:
            async def evaluate(self, _expression):
                raise RuntimeError("cdp gone")

        engine.tab = Tab()
        state = await engine.probe_page_state()

        self.assertFalse(state["found"])
        self.assertFalse(state["challenge"])
        self.assertEqual(state["result_count"], 0)

    def test_brave_probe_embeds_challenge_markers(self):
        engine = BraveSearchEngine()
        engine.set_selector()

        expression = engine._build_probe_expression(include_text=False)

        self.assertIn("#results", expression)
        self.assertIn("/captcha", expression)
        self.assertIn("blockRobots", expression)

    async def test_duckduckgo_wait_stops_on_no_results_without_full_read(self):
        engine = DuckDuckGoSearchEngine()
        engine.query = "dummy"
        engine.max_results = 10
        engine.set_selector()

        class Tab:
            content_calls = 0

            async def evaluate(self, _expression):
                return '{"noResults": true}'

            async def get_content(self):
                self.content_calls += 1
                return "<html></html>"

        engine.tab = Tab()
        loaded = await engine._wait_for_result_content(timeout=5, interval=0)

        self.assertFalse(loaded)
        self.assertEqual(engine.tab.content_calls, 0)

    async def test_brave_container_wait_uses_probe_without_full_read(self):
        engine = BraveSearchEngine()
        engine.set_selector()

        class Tab:
            probes = 0
            content_calls = 0

            async def evaluate(self, _expression):
                self.probes += 1
                return json.dumps({"found": self.probes >= 3})

            async def get_content(self):
                self.content_calls += 1
                return "<html></html>"

        engine.tab = Tab()
        found = await engine._wait_for_results_container(timeout=5, interval=0)

        self.assertTrue(found)
        self.assertEqual(engine.tab.probes, 3)
        self.assertEqual(engine.tab.content_calls, 0)


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


class BingRedirectTestCase(unittest.TestCase):
    def test_resolves_ck_redirect_to_target(self):
        target = "https://example.com/article?id=42&ref=x"
        encoded = "a1" + base64.urlsafe_b64encode(
            target.encode("utf-8")
        ).decode("ascii").rstrip("=")
        ck_url = (
            "https://www.bing.com/ck/a?!&&p=deadbeef&u="
            + encoded
            + "&ntb=1"
        )
        self.assertEqual(resolve_bing_redirect(ck_url), target)

    def test_leaves_direct_urls_untouched(self):
        direct = "https://example.org/profile"
        self.assertEqual(resolve_bing_redirect(direct), direct)
        # A bing.com URL that is not a /ck/ redirect is left as-is.
        self.assertEqual(
            resolve_bing_redirect("https://www.bing.com/search?q=x"),
            "https://www.bing.com/search?q=x",
        )

    def test_parse_results_decodes_links(self):
        target = "https://target.example/page"
        encoded = "a1" + base64.urlsafe_b64encode(
            target.encode("utf-8")
        ).decode("ascii").rstrip("=")
        html = (
            '<div id="b_results"><li class="b_algo"><h2>'
            f'<a href="https://www.bing.com/ck/a?u={encoded}">Title</a>'
            '</h2><div class="b_caption"><p>desc</p></div></li></div>'
        )
        engine = BingSearchEngine()
        results = engine.parse_results(html)
        self.assertTrue(results)
        self.assertEqual(results[0]["link"], target)


class DuckDuckGoNoResultsTestCase(unittest.TestCase):
    def test_detects_empty_result_state(self):
        self.assertTrue(
            looks_like_duckduckgo_no_results("<div>No results.</div>")
        )
        self.assertTrue(
            looks_like_duckduckgo_no_results(
                "<p>No results for &quot;foobar&quot;</p>"
            )
        )

    def test_does_not_flag_pages_with_results(self):
        self.assertFalse(
            looks_like_duckduckgo_no_results(
                '<a class="result__a">A real result link</a>'
            )
        )


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

    def test_detects_new_challenge_markers_and_urls(self):
        self.assertTrue(
            looks_like_brave_robot_challenge(
                "<main>Performing security verification</main>"
            )
        )
        self.assertTrue(
            looks_like_brave_robot_challenge(
                '<div class="cf-chl-widget">Please wait</div>'
            )
        )
        self.assertTrue(
            looks_like_brave_challenge_url(
                "https://search.brave.com/challenge?q=test"
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


class BraveParsingTestCase(unittest.TestCase):
    def test_parse_embedded_json_accepts_variable_suffix(self):
        raw_html = """
        <html><body><script>
        window.__brave = {
            results:[{
                title:"One",
                url:"https://example.com/one",
                description:"First result."
            },{
                title:"Two",
                url:"https://example.com/two",
                description:"Second result."
            }],xy:0
        };
        </script></body></html>
        """
        engine = BraveSearchEngine()
        engine.max_results = 10

        results = engine.parse_results(raw_html)

        self.assertEqual([result["title"] for result in results], ["One", "Two"])
        self.assertEqual(engine.num_results, 2)
        self.assertEqual(engine.nb_results_per_page, 2)

    def test_parse_falls_back_to_xpath_when_embedded_json_is_absent(self):
        raw_html = """
        <html><body><main id="results">
            <div class="snippet" data-pos="1">
                <a href="https://example.com/one">
                    <div class="title">One</div>
                </a>
                <div class="snippet-description">First result.</div>
            </div>
            <div class="snippet" data-pos="2">
                <a href="https://example.com/two">
                    <div class="title">Two</div>
                </a>
                <div class="snippet-description">Second result.</div>
            </div>
        </main></body></html>
        """
        engine = BraveSearchEngine()
        engine.max_results = 10

        with self.assertLogs("brave", level="WARNING") as logs:
            results = engine.parse_results(raw_html)

        self.assertEqual([result["title"] for result in results], ["One", "Two"])
        self.assertEqual(engine.num_results, 2)
        self.assertEqual(engine.nb_results_per_page, 2)
        self.assertTrue(
            any("XPath fallback parsed 2 results" in message for message in logs.output)
        )


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

            async def evaluate(self, _expression):
                return '{"resultCount": 2}'

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
