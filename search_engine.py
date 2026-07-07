from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
import hashlib
import json
import logging
import re
import time

import pandas as pd
import zendriver as uc

import observability
from exceptions import BrowserSessionError, SearchEngineError, SynthesixError
from settings import get_settings

logger = logging.getLogger(__name__)

# Target ids of tabs currently owned by a running engine search. Since
# searches run concurrently with the main poll loop (T-011), the loop must
# skip these tabs: no overlay injection or focus-guard arming mid-scrape.
ACTIVE_ENGINE_TAB_TARGETS: set[str] = set()

# Marker embedded in the probe expression so tests (and log readers) can tell
# probe evaluates apart from other scripts sent to an engine tab.
PROBE_MARKER = "__SYNTHESIX_ENGINE_PROBE__"

# Visible-text slice scanned in-page for challenge/no-results markers; those
# sit near the top of the page, far below this cap (T-012 risk note).
PROBE_TEXT_LIMIT = 20000
# documentElement.innerHTML slice scanned for raw challenge markers (e.g.
# Brave's blockRobots flag); challenge pages are small, so a bounded slice
# avoids serializing multi-MB result pages in-page on every iteration.
PROBE_HTML_LIMIT = 200000

_PROBE_DEFAULT_STATE = {
    "found": False,
    "ready": "",
    "body_length": 0,
    "result_count": 0,
    "challenge": False,
    "forbidden": False,
    "no_results": False,
    "url": "",
    "title": "",
    "text": "",
}

_PROBE_JS_TEMPLATE = r"""
(() => { /* __SYNTHESIX_ENGINE_PROBE__ */
    const config = __CONFIG__;
    const state = {
        found: false,
        ready: String(document.readyState || ""),
        bodyLength: 0,
        resultCount: 0,
        challenge: false,
        forbidden: false,
        noResults: false,
        url: String(location.href || ""),
        title: String(document.title || ""),
        text: "",
    };
    const countMatches = (selector) => {
        try {
            return document.querySelectorAll(selector).length;
        } catch (err) {
            return 0;
        }
    };
    if (config.selector) {
        state.resultCount = countMatches(config.selector);
        state.found = state.resultCount > 0;
    }
    if (document.body && document.body.innerHTML) {
        state.bodyLength = document.body.innerHTML.length;
    }
    if (config.challengeSelectors.some((selector) => countMatches(selector) > 0)) {
        state.challenge = true;
    }
    const path = String(location.pathname || "").toLowerCase();
    if (!state.challenge &&
        config.challengeUrlPathSubstrings.some((part) => path.includes(part))) {
        state.challenge = true;
    }
    const needText = config.includeText ||
        config.challengeTextPatterns.length > 0 ||
        config.noResultsTextPatterns.length > 0;
    let text = "";
    if (needText && document.body) {
        text = String(document.body.innerText || "").slice(0, config.textLimit);
    }
    const flatText = text.toLowerCase().replace(/\s+/g, " ");
    if (!state.challenge &&
        config.challengeTextPatterns.some((pattern) => flatText.includes(pattern))) {
        state.challenge = true;
    }
    if (!state.challenge && config.challengeHtmlMarkers.length > 0) {
        const rawHtml = String(document.documentElement.innerHTML || "")
            .slice(0, config.htmlLimit);
        if (config.challengeHtmlMarkers.some((marker) => rawHtml.includes(marker))) {
            state.challenge = true;
        }
    }
    if (config.forbiddenTitlePatterns.includes(state.title.trim().toLowerCase())) {
        state.forbidden = true;
    }
    if (!state.found &&
        config.noResultsTextPatterns.some((pattern) => flatText.includes(pattern))) {
        state.noResults = true;
    }
    if (config.includeText) {
        state.text = text;
    }
    return JSON.stringify(state);
})()
"""


class EngineTabPool:
    """One reusable tab per engine for a whole search run (T-014).

    Query variants of the same engine navigate the same tab sequentially
    (the orchestrator serializes variants per engine). The pool owner must
    call :meth:`close_all` once the run is over, whatever the outcome.
    """

    def __init__(self, browser) -> None:
        self._browser = browser
        self._tabs: dict[str, uc.Tab] = {}

    def owns(self, tab) -> bool:
        return any(existing is tab for existing in self._tabs.values())

    async def navigate(self, engine_name: str, url: str) -> uc.Tab:
        tab = self._tabs.get(engine_name)
        if tab is not None and not getattr(tab, "closed", False):
            observability.count("engine_tab_reuse")
            await tab.get(url)
            return tab
        observability.count("engine_tab_open")
        tab = await self._browser.get(url, new_tab=True)
        self._tabs[engine_name] = tab
        return tab

    async def close_all(self) -> None:
        tabs, self._tabs = dict(self._tabs), {}
        for engine_name, tab in tabs.items():
            target_id = getattr(tab, "target_id", None)
            if target_id:
                ACTIVE_ENGINE_TAB_TARGETS.discard(str(target_id))
            if getattr(tab, "closed", False):
                continue
            try:
                # tab.close() sends Target.closeTarget then waits up to 10s
                # for the TargetDestroyed event; if that event is missed the
                # wait would stall cleanup and leave the tab visible. The close
                # command is already sent, so bound the confirmation wait.
                await asyncio.wait_for(tab.close(), timeout=5.0)
            except Exception as exc:
                logger.warning("Unable to close pooled %s tab cleanly: %s", engine_name, exc)


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
        self.tab_pool: EngineTabPool | None = None
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
            await self.release_tab()

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
        observability.count("get_content")
        raw_html = await self.tab.get_content()
        observability.observe_bytes("get_content", len(raw_html))
        self.capture_debug_html(raw_html, stage)
        return raw_html

    async def release_tab(self):
        """Hand a pooled tab back to the pool; close tabs the pool does not own."""
        if self.tab is None:
            return
        if self.tab_pool is not None and self.tab_pool.owns(self.tab):
            self.tab = None
            return
        await self.close_tab()

    async def close_tab(self):
        if self.tab is None:
            return
        target_id = getattr(self.tab, "target_id", None)
        if target_id:
            ACTIVE_ENGINE_TAB_TARGETS.discard(str(target_id))
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
            if self.tab_pool is not None:
                self.tab = await self.tab_pool.navigate(self.name, url)
            else:
                self.tab = await self.browser.get(url, new_tab=True)
        except Exception as exc:
            raise BrowserSessionError(
                f"Unable to open {self.name} search page.",
                url=url,
                original_error=exc,
            ) from exc
        target_id = getattr(self.tab, "target_id", None)
        if target_id:
            ACTIVE_ENGINE_TAB_TARGETS.add(str(target_id))

        # T-014: no main-tab refocus per navigation — the only legitimate
        # bring_to_front left is the manual anti-robot challenge resolution.
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

    def get_probe_markers(self) -> dict:
        """Per-engine markers consumed by :meth:`probe_page_state`.

        Optional keys:
        - ``challenge_selectors``: CSS selectors flagging an anti-robot page;
        - ``challenge_url_path_substrings``: ``location.pathname`` substrings;
        - ``challenge_text_patterns``: lowercase substrings of the visible text;
        - ``challenge_html_markers``: raw ``documentElement.innerHTML`` substrings;
        - ``forbidden_title_patterns``: exact lowercase ``document.title`` values;
        - ``no_results_text_patterns``: lowercase substrings of the visible text.
        """
        return {}

    def _build_probe_expression(self, include_text: bool) -> str:
        markers = self.get_probe_markers()
        config = {
            "selector": self.selector or "",
            "challengeSelectors": list(markers.get("challenge_selectors", ())),
            "challengeUrlPathSubstrings": list(
                markers.get("challenge_url_path_substrings", ())
            ),
            "challengeTextPatterns": list(
                markers.get("challenge_text_patterns", ())
            ),
            "challengeHtmlMarkers": list(
                markers.get("challenge_html_markers", ())
            ),
            "forbiddenTitlePatterns": list(
                markers.get("forbidden_title_patterns", ())
            ),
            "noResultsTextPatterns": list(
                markers.get("no_results_text_patterns", ())
            ),
            "includeText": bool(include_text),
            "textLimit": PROBE_TEXT_LIMIT,
            "htmlLimit": PROBE_HTML_LIMIT,
        }
        return _PROBE_JS_TEMPLATE.replace("__CONFIG__", json.dumps(config))

    async def probe_page_state(self, include_text: bool = False) -> dict:
        """Composite page-state probe: one lightweight ``Runtime.evaluate``.

        Returns a small dict (``found``, ``ready``, ``body_length``,
        ``result_count``, ``challenge``, ``forbidden``, ``no_results``,
        ``url``, ``title``, ``text``) so wait loops never ship the full page
        HTML per iteration (T-012). Failures degrade to the default
        "not found" state, matching the old swallowed ``query_selector``
        errors.
        """
        observability.count("eval_engine_wait")
        state = dict(_PROBE_DEFAULT_STATE)
        try:
            raw = await self.tab.evaluate(self._build_probe_expression(include_text))
        except Exception:
            logger.debug("Unable to probe %s page state", self.name, exc_info=True)
            return state
        if isinstance(raw, str):
            observability.observe_bytes("eval_engine_wait", len(raw))
            try:
                raw = json.loads(raw)
            except ValueError:
                logger.debug("Unreadable %s probe payload", self.name)
                return state
        if not isinstance(raw, dict):
            return state
        state.update(
            {
                "found": bool(raw.get("found")),
                "ready": str(raw.get("ready") or ""),
                "body_length": int(raw.get("bodyLength") or 0),
                "result_count": int(raw.get("resultCount") or 0),
                "challenge": bool(raw.get("challenge")),
                "forbidden": bool(raw.get("forbidden")),
                "no_results": bool(raw.get("noResults")),
                "url": str(raw.get("url") or ""),
                "title": str(raw.get("title") or ""),
                "text": str(raw.get("text") or ""),
            }
        )
        return state

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

        One composite probe per iteration (T-012); the full page HTML is only
        fetched after the timeout, for the debug capture and robot check.
        """
        settings = get_settings()
        timeout = settings.page_load_timeout if timeout is None else timeout
        interval = settings.page_load_interval if interval is None else interval
        start = time.monotonic()
        while (time.monotonic() - start) < timeout:
            state = await self.probe_page_state()
            if state["found"]:
                return True
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
