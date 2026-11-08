import base64
import binascii
import asyncio
import logging
import time
from urllib.parse import quote_plus, urlencode, urljoin, urlsplit, parse_qs

from parsers import parse_with_xpath
from search_engine import SearchEngine
from search_regions import build_engine_region_params
from settings import get_settings


logger = logging.getLogger(__name__)


def resolve_bing_redirect(url: str) -> str:
    """Resolve a Bing ``/ck/a`` redirect to the real destination URL.

    Bing wraps organic result links in ``https://www.bing.com/ck/a?...&u=a1<b64>``
    where the ``u`` parameter is the base64url-encoded target (prefixed with a
    two-character version marker, usually ``a1``). Leaving the wrapper in place
    breaks cross-engine de-duplication, which merges results on their URL.
    """
    if not url:
        return url
    try:
        parts = urlsplit(url)
    except ValueError:
        return url
    if "bing.com" not in parts.netloc.casefold() or "/ck/" not in parts.path:
        return url
    encoded = (parse_qs(parts.query).get("u") or [""])[0]
    if len(encoded) < 3 or not encoded[:2].isalnum():
        return url
    payload = encoded[2:]
    payload += "=" * (-len(payload) % 4)
    try:
        decoded = base64.urlsafe_b64decode(payload).decode("utf-8", "replace")
    except (binascii.Error, ValueError):
        return url
    return decoded if decoded.startswith(("http://", "https://")) else url


class BingSearchEngine(SearchEngine):
    def __init__(self):
        super().__init__(name="Bing")
        self.base_url = "https://www.bing.com"

    async def post_execute_search(self):
        if self.num_results >= self.max_results:
            return

        # If the number of results from the actual page is less than 10, we can assume that there are no more results
        if self.num_results < 10:
            return

        while self.num_results < self.max_results:
            try:
                next_button = await self.tab.xpath(".//a[contains(@class, 'sb_pagN') and @href]")
            except Exception:
                logger.debug("Unable to locate Bing next page button.", exc_info=True)
                break
            if not next_button:
                break

            href = next_button[0].get("href")
            if not href:
                break

            next_url = urljoin(self.base_url, href)

            if next_url == self.current_url:
                break
            else:
                self.current_url = next_url

            self.tab = await self.tab.get(next_url)
            await self.wait_for_page_load()
            raw_results = await self.read_page_content("pagination")
            results = self.parse_results(raw_results)
            self.results.extend(results)
            self.num_results = len(self.results)
            
            #@TODO: Not very efficient, we should find a better way to do this
            # If the number of results from the actual page is less than 5, we can assume that there are no more results
            if len(results) < 5:
                break

    def construct_url(self) -> str:
        count = min(50, int(self.max_results * 1.5 + 0.5))
        url = f"{self.base_url}/search?q={quote_plus(self.query)}&count={count}&adlt=off"
        region_params = build_engine_region_params("bing", self.search_filters)
        if region_params:
            url += "&" + urlencode(region_params)
        return url

    def parse_results(self, raw_results):
        xpaths = self.get_xpaths()
        results = parse_with_xpath(
            raw_results,
            result_xpath=xpaths["result"],
            title_xpath=xpaths["title"],
            link_xpath=xpaths["link"],
            desc_xpath=xpaths["desc"],
            source=self.name
        )
        for result in results:
            link = result.get("link")
            if link:
                result["link"] = resolve_bing_redirect(link)
        return results

    def set_selector(self):
        # Bing mounts ``#b_results`` before it hydrates its ``li.b_algo``
        # rows. Waiting on the container made a concurrent multi-engine run
        # occasionally scrape that empty shell; wait for the actual rows as
        # Brave already does for its client-rendered snippets.
        self.selector = "#b_results li.b_algo"

    async def wait_for_page_load(self, timeout=None, interval=None) -> bool:
        """Wait for Bing's hydrated organic rows, not its initial shell.

        Under a concurrent multi-engine search Bing can mount the page shell
        promptly but populate ``li.b_algo`` a few seconds later.  The generic
        2.5-second wait was therefore enough when Bing ran alone, yet brittle
        alongside the other engines.
        """
        settings = get_settings()
        timeout = (
            settings.bing_results_timeout if timeout is None else timeout
        )
        interval = (
            settings.bing_results_interval if interval is None else interval
        )
        start = time.monotonic()
        while (time.monotonic() - start) < timeout:
            if (await self.probe_page_state())["found"]:
                return True
            await asyncio.sleep(interval)

        try:
            await self.read_page_content("load_timeout")
        except Exception:
            logger.debug(
                "Unable to capture Bing content after load timeout",
                exc_info=True,
            )
        return bool(await self.robot_check())

    def get_xpaths(self):
        return {
            'result': "//li[contains(@class, 'b_algo')]",
            'title': ".//h2",
            'link': ".//a[@href]",
            'desc': ".//div[contains(@class, 'b_caption')]"
        }
