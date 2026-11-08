import asyncio
from dataclasses import replace
from email.message import Message
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
import threading
import unittest
from unittest.mock import AsyncMock, patch
from urllib.error import HTTPError, URLError

from lxml import html

import google as google_module
from google import GoogleSearchEngine, resolve_google_result_links
from search_orchestrator import aggregate_search_results
from settings import get_settings
from utils import generate_html_report


WRAPPER = "https://www.google.com/goto?url=opaque_token-123"
TARGET = "https://example.com/article?q=a%2Bb&lang=fr#section"
GOOGLE_HTML = """
<div id="search"><div jscontroller="result" data-ved="1" data-hveid="2">
  <a href="/goto?url=opaque_token-123"><h3>Example article</h3></a>
  <div class="VwiC3b">Example article description</div>
</div></div>
"""


def redirect_error(location: str, code: int = 302) -> HTTPError:
    headers = Message()
    headers["Location"] = location
    return HTTPError(WRAPPER, code, "response", headers, BytesIO())


class GoogleRedirectTestCase(unittest.TestCase):
    def test_legacy_wrappers_decode_without_a_request(self):
        cases = (
            ("https://www.google.com/url?q=https%3A%2F%2Fexample.com%2Fpage%3Fa%3D1%26b%3D2", "https://example.com/page?a=1&b=2"),
            ("https://google.com/url?url=https%3A%2F%2Fexample.com%2Fpage", "https://example.com/page"),
            ("https://www.google.com/url?q=javascript%3Aalert(1)", None),
            ("https://www.google.com/url?q=http%3A%2F%2F", None),
            ("https://www.google.com/url?q=https%3A%2F%2Fexample.com%3Ainvalid", None),
            ("https://google.com.evil.test/url?q=https%3A%2F%2Fexample.com", None),
            (TARGET, None),
            (WRAPPER, None),
        )
        with patch.object(google_module, "build_opener") as opener:
            for url, expected in cases:
                with self.subTest(url=url):
                    self.assertEqual(google_module._unwrap_google_url(url), expected or url)
            opener.assert_not_called()

    def test_reads_location_without_following_or_reading_destination(self):
        for code in (301, 302, 303, 307, 308):
            with self.subTest(code=code):
                error = redirect_error(TARGET, code)
                with patch.object(google_module, "build_opener") as factory:
                    factory.return_value.open.side_effect = error
                    self.assertEqual(google_module._resolve_google_goto(WRAPPER), TARGET)
                    handler = factory.call_args.args[0]
                    self.assertIsInstance(handler, google_module._NoGoogleRedirectHandler)
                    self.assertIsNone(handler.redirect_request(None, None, code, "", None, TARGET))
                    request = factory.return_value.open.call_args.args[0]
                    self.assertEqual(request.full_url, WRAPPER)
                    self.assertEqual(request.get_method(), "GET")
                    self.assertEqual(factory.return_value.open.call_args.kwargs["timeout"], 3.0)
                    factory.return_value.open.assert_called_once()
                self.assertTrue(error.fp.closed)

    def test_never_requests_other_origins_or_unsafe_urls(self):
        urls = (
            TARGET, "/goto?url=opaque", "http://www.google.com/goto?url=opaque",
            "https://www.google.com.evil.test/goto?url=opaque",
            "https://www.google.com@evil.test/goto?url=opaque",
            "https://user@www.google.com/goto?url=opaque",
            "https://www.google.com:8080/goto?url=opaque",
            "https://www.google.com:invalid/goto?url=opaque",
            "https://www.google.com/search?q=example", "https://[broken",
            "https://www.google.com/goto?url=opaque\r\nx-test: value",
        )
        with patch.object(google_module, "build_opener") as factory:
            for url in urls:
                with self.subTest(url=url):
                    self.assertEqual(google_module._resolve_google_goto(url), url)
            factory.assert_not_called()

    def test_keeps_wrapper_when_location_is_invalid_or_an_interstitial(self):
        for location in (
            "", "javascript:alert(1)", "file:///private/file", "ftp://example.com/",
            "http://", "https://[broken", "https://example.com:invalid/page",
            "https://user:password@example.com/page", "/sorry/index",
            "https://consent.google.com/m", "/goto?url=another_opaque_token",
            "https://example.com/path\r\ninjected",
        ):
            with self.subTest(location=location):
                # Assign directly so the test can also exercise malformed header values.
                error = redirect_error(location)
                with patch.object(google_module, "build_opener") as factory:
                    factory.return_value.open.side_effect = error
                    self.assertEqual(google_module._resolve_google_goto(WRAPPER), WRAPPER)

    def test_decodes_a_legacy_wrapper_in_the_location_header(self):
        with patch.object(google_module, "build_opener") as factory:
            factory.return_value.open.side_effect = redirect_error(
                "/url?q=https%3A%2F%2Fexample.com%2Fpage"
            )
            self.assertEqual(google_module._resolve_google_goto(WRAPPER), "https://example.com/page")
            factory.return_value.open.assert_called_once()

    def test_network_errors_and_non_redirect_responses_preserve_the_link(self):
        for error in (URLError("offline"), TimeoutError(), redirect_error(TARGET, 429)):
            with self.subTest(error=type(error).__name__):
                with patch.object(google_module, "build_opener") as factory:
                    factory.return_value.open.side_effect = error
                    self.assertEqual(google_module._resolve_google_goto(WRAPPER), WRAPPER)
        with patch.object(google_module, "build_opener") as factory:
            response = factory.return_value.open.return_value.__enter__.return_value
            self.assertEqual(google_module._resolve_google_goto(WRAPPER), WRAPPER)
            response.read.assert_not_called()


class GoogleRedirectBatchTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_duplicate_wrappers_use_one_request_and_keep_direct_links(self):
        rows = [{"link": WRAPPER}, {"link": WRAPPER}, {"link": TARGET}]
        with patch.object(google_module, "_resolve_google_goto", return_value=TARGET) as resolve:
            await resolve_google_result_links(rows)
        resolve.assert_called_once_with(WRAPPER)
        self.assertEqual([row["link"] for row in rows], [TARGET] * 3)

    async def test_one_failure_does_not_discard_other_results(self):
        bad = WRAPPER + "-bad"
        rows = [{"link": WRAPPER}, {"link": bad}]

        def resolve(url):
            if url == bad:
                raise RuntimeError("isolated failure")
            return TARGET

        with patch.object(google_module, "_resolve_google_goto", side_effect=resolve):
            await resolve_google_result_links(rows)
        self.assertEqual([row["link"] for row in rows], [TARGET, bad])

    async def test_network_work_does_not_block_the_event_loop(self):
        released = threading.Event()
        caller_thread = threading.get_ident()

        def resolve(url):
            self.assertNotEqual(threading.get_ident(), caller_thread)
            self.assertTrue(released.wait(2.0))
            return TARGET

        rows = [{"link": WRAPPER}]
        with patch.object(google_module, "_resolve_google_goto", side_effect=resolve):
            task = asyncio.create_task(resolve_google_result_links(rows))
            try:
                await asyncio.sleep(0)
                released.set()
                await task
            finally:
                released.set()
        self.assertEqual(rows[0]["link"], TARGET)

    async def test_concurrency_is_bounded(self):
        active = maximum = 0

        async def offload(function, url):
            nonlocal active, maximum
            active += 1
            maximum = max(maximum, active)
            await asyncio.sleep(0)
            active -= 1
            return TARGET

        rows = [{"link": WRAPPER + str(i)} for i in range(12)]
        with patch.object(google_module.asyncio, "to_thread", side_effect=offload):
            await resolve_google_result_links(rows)
        self.assertEqual(maximum, google_module._REDIRECT_CONCURRENCY)
        self.assertTrue(all(row["link"] == TARGET for row in rows))

    async def test_batch_timeout_keeps_completed_destinations_and_remaining_links(self):
        blocked = WRAPPER + "-blocked"
        rows = [{"link": WRAPPER}, {"link": blocked}]

        async def offload(function, url):
            if url == blocked:
                await asyncio.Event().wait()
            return TARGET

        with patch.object(google_module.asyncio, "to_thread", side_effect=offload):
            with patch.object(google_module, "_REDIRECT_BATCH_TIMEOUT", 0.02):
                await resolve_google_result_links(rows)
        self.assertEqual([row["link"] for row in rows], [TARGET, blocked])

    async def test_cancellation_propagates(self):
        started = asyncio.Event()

        async def offload(function, url):
            started.set()
            await asyncio.Event().wait()

        rows = [{"link": WRAPPER}]
        with patch.object(google_module.asyncio, "to_thread", side_effect=offload):
            task = asyncio.create_task(resolve_google_result_links(rows))
            await asyncio.wait_for(started.wait(), timeout=1)
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
        self.assertEqual(rows[0]["link"], WRAPPER)

    async def test_engine_resolves_before_aggregation_and_report(self):
        engine = GoogleSearchEngine()
        engine.pre_execute_search = AsyncMock()
        engine.navigate = AsyncMock()
        engine.read_page_content = AsyncMock(return_value=GOOGLE_HTML)
        with patch.object(google_module, "_resolve_google_goto", return_value=TARGET):
            await engine.execute_search()
        self.assertEqual(engine.results[0]["link"], TARGET)
        combined = aggregate_search_results({
            "google": engine.results,
            "bing": [{**engine.results[0], "source": "Bing"}],
        }, "Example article")
        self.assertEqual(len(combined), 1)
        self.assertEqual(combined[0]["engine_count"], 2)
        with TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            settings = replace(get_settings(), base_dir=base, history_dir=base,
                               history_report_path=base / "history.html")
            with patch("utils.get_settings", return_value=settings):
                report = generate_html_report(combined, "Example article", 0.1, 1)
            tree = html.fromstring(Path(report).read_text(encoding="utf-8"))
        self.assertEqual(tree.xpath('//sx-result-card/a[@data-triage-link]/@href'), [TARGET])
        self.assertEqual(tree.xpath('//sx-result-card/span[@slot="source"]/text()'), ["example.com"])
        self.assertNotIn("google.com/goto", html.tostring(tree, encoding="unicode"))


if __name__ == "__main__":
    unittest.main()
