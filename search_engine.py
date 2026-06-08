from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
import hashlib
import logging
import re
import time

import pandas as pd
import zendriver as uc

from exceptions import BrowserSessionError, SearchEngineError, SynthesixError
from settings import get_settings

logger = logging.getLogger(__name__)


class SearchEngine(ABC):
    def __init__(self, name):
        self.name = name
        self.results = []
        self.num_results = 0
        self.max_results = None
        self.tab : uc.Tab = None
        self.query = None
        self.browser = None
        self.selector = None
        self.current_url = None
        self.search_filters = {}
        self._debug_html_hashes = set()

    async def search(self, query, browser=None, max_results=None) -> pd.DataFrame:
        """
        Launch a search and return a DataFrame of results.
        """
        self.query = query
        self.browser = browser
        self.max_results = max_results if max_results is not None else get_settings().default_max_results
        self.results = []
        self.num_results = 0
        self._debug_html_hashes = set()
        self.set_selector()
        if self.query == "test" and self.browser is None:
            self.test()
            return pd.DataFrame(self.results)
        if self.browser is None:
            raise BrowserSessionError("A zendriver browser instance is required for live searches.")

        start_time = time.monotonic()
        try:
            await self.execute_search()
            return pd.DataFrame(self.results)
        except SynthesixError:
            raise
        except Exception as exc:
            raise SearchEngineError(
                self.name,
                f"{self.name} search failed.",
                query=self.query,
                url=self.current_url,
                original_error=exc,
            ) from exc
        finally:
            logger.info("Execution time %s: %.2f seconds", self.name, time.monotonic() - start_time)
            await self.close_tab()

    def capture_debug_html(self, raw_html: str, stage: str) -> str | None:
        settings = get_settings()
        if not settings.debug_html:
            return None

        raw_html = str(raw_html)
        content_hash = hashlib.sha256(raw_html.encode("utf-8", errors="replace")).hexdigest()
        if content_hash in self._debug_html_hashes:
            return None
        self._debug_html_hashes.add(content_hash)

        engine_slug = re.sub(r"[^a-z0-9]+", "_", self.name.lower()).strip("_") or "engine"
        stage_slug = re.sub(r"[^a-z0-9]+", "_", stage.lower()).strip("_") or "page"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        output_path = settings.debug_html_dir / f"{timestamp}_{engine_slug}_{stage_slug}.html"

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(raw_html, encoding="utf-8")
        except OSError:
            logger.warning("Unable to save debug HTML page: %s", output_path, exc_info=True)
            return None

        logger.info("Debug HTML captured for %s (%s): %s", self.name, stage, output_path)
        return str(output_path.resolve())

    async def read_page_content(self, stage: str) -> str:
        raw_html = await self.tab.get_content()
        self.capture_debug_html(raw_html, stage)
        return raw_html

    async def close_tab(self):
        if self.tab is None:
            return
        try:
            await self.tab.close()
        except Exception as exc:
            logger.warning("Unable to close %s tab: %s", self.name, exc)
        finally:
            self.tab = None

    async def execute_search(self):
        """Execute the search and return the results.
        """
        await self.pre_execute_search()
        await self.navigate()
        try:
            raw_results = await self.read_page_content("results")
        except Exception as exc:
            raise BrowserSessionError(
                f"Unable to read {self.name} page content.",
                url=self.current_url,
                original_error=exc,
            ) from exc

        try:
            self.results = self.parse_results(raw_results)
        except Exception as exc:
            raise SearchEngineError(
                self.name,
                f"Unable to parse {self.name} results.",
                query=self.query,
                url=self.current_url,
                original_error=exc,
            ) from exc

        self.num_results = len(self.results)
        await self.post_execute_search()

    async def navigate(self):
        """Navigate to the page
        """
        url = self.construct_url()
        self.current_url = url
        try:
            self.tab = await self.browser.get(url, new_tab=True)
        except Exception as exc:
            raise BrowserSessionError(
                f"Unable to open {self.name} search page.",
                url=url,
                original_error=exc,
            ) from exc
        
        # Stay focused on the main tab
        main_tab = getattr(self.browser, "main_tab", None)
        if main_tab and not getattr(main_tab, "closed", False):
            try:
                await main_tab.bring_to_front()
            except Exception:
                logger.debug("Unable to bring main tab to front", exc_info=True)
        if not await self.wait_for_page_load():
            raise SearchEngineError(
                self.name,
                f"{self.name} results did not load before timeout.",
                query=self.query,
                url=self.current_url,
            )

    @abstractmethod
    def set_selector(self):
        """Set the selector for the search engine.
        Selector used as a reference point to know when the page is loaded and to locate the results container
        Example:
        - Brave: "#results"
        - Google: "#search"
        - Bing: "#b_results"
        """
        pass

    @abstractmethod
    def construct_url(self) -> str:
        """
        Construct the URL for the search.
        """
        pass

    @abstractmethod
    def parse_results(self, raw_results):
        """
        Parse the raw HTML and return a list of structured results.
        """
        pass

    def get_xpaths(self):
        """
        Return a dictionary with the XPaths necessary for parsing.
        """
        pass 

    def test(self):
        pass

    async def post_execute_search(self):
        """Used to execute actions after the first search is executed. Mostly for search engine that need to
        click on a button to load more results.
        """
        pass

    async def pre_execute_search(self):
        """Used to execute actions before the search is executed.
        """
        pass

    async def wait_for_page_load(self, timeout=None, interval=None) -> bool:
        """Custom function to wait for the page to load.
        """
        settings = get_settings()
        timeout = settings.page_load_timeout if timeout is None else timeout
        interval = settings.page_load_interval if interval is None else interval
        start = time.monotonic()
        while (time.monotonic() - start) < timeout:
            try:
                results = await self.tab.query_selector(self.selector)
                if results:
                    return True
            except Exception:
                pass
            await asyncio.sleep(interval)

        try:
            await self.read_page_content("load_timeout")
        except Exception:
            logger.debug("Unable to capture page content after load timeout", exc_info=True)
        return bool(await self.robot_check())
            
    async def robot_check(self):
        """
        Check if we are flagged as a robot.
        """
        return False
