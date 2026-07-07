import asyncio
import json
import logging
import re
import time
import unicodedata
from datetime import datetime
from html import unescape
from urllib.parse import quote_plus, urlencode, urlparse

from exceptions import RobotChallengeError
from parsers import parse_with_xpath
from query_operators import build_engine_date_params
from search_engine import SearchEngine
from search_regions import build_engine_region_params
from settings import get_settings
from utils import js_like_to_json

logger = logging.getLogger(__name__)


BRAVE_ROBOT_CHALLENGE_PATTERNS = (
    "i'm not a robot",
    "im not a robot",
    "i am not a robot",
    "je ne suis pas un robot",
    "verify you are human",
    "verifiez que vous etes humain",
    "checking if the site connection is secure",
    "performing security verification",
    "please wait while we verify",
    "please verify your identity",
    "verify your identity",
    "human verification",
    "complete the security check",
    "security check",
    "verifier",
    "captcha",
    "robot",
    "bot",
)

BRAVE_ROBOT_BUTTON_PATTERNS = (
    "i'm not a robot",
    "im not a robot",
    "i am not a robot",
    "je ne suis pas un robot",
    "verify you are human",
    "verifiez que vous etes humain",
    "verifier",
    "verify",
    "continue",
    "human",
)

BRAVE_ROBOT_RAW_MARKERS = (
    r"page\s*:\s*[\"']?/captcha[\"']?",
    r"[\"']page[\"']\s*:\s*[\"']/captcha[\"']",
    r"blockRobots\s*:\s*true",
    r"[\"']blockRobots[\"']\s*:\s*true",
    r"turnstile",
    r"cf-chl-",
    r"hcaptcha",
    r"recaptcha",
)

BRAVE_ROBOT_FIND_PATTERNS = (
    "i'm not a robot",
    "im not a robot",
    "i am not a robot",
    "je ne suis pas un robot",
    "verify you are human",
    "verifiez que vous etes humain",
)

# Probe-side challenge markers (T-012): the captcha interstitial path and the
# blockRobots flag, matched on a bounded innerHTML slice in-page. The looser
# text patterns above stay reserved for robot_check() on the full HTML.
BRAVE_CHALLENGE_URL_PATH_SUBSTRINGS = (
    "/captcha",
    "/challenge",
    "/verify",
)

BRAVE_CHALLENGE_HTML_MARKERS = (
    "blockRobots:true",
    '"blockRobots":true',
)


def _normalize_challenge_text(text: str) -> str:
    text = unescape(str(text))
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", text.lower()).strip()


def _html_to_visible_text(raw_html: str) -> str:
    text = re.sub(
        r"<(script|style)\b[^>]*>.*?</\1>",
        " ",
        raw_html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    text = re.sub(r"<[^>]+>", " ", text)
    return unescape(text)


def looks_like_brave_robot_challenge(raw_html: str) -> bool:
    raw_html = unescape(str(raw_html))
    if any(re.search(marker, raw_html, flags=re.IGNORECASE) for marker in BRAVE_ROBOT_RAW_MARKERS):
        return True
    text = _normalize_challenge_text(_html_to_visible_text(raw_html))
    return any(pattern in text for pattern in BRAVE_ROBOT_CHALLENGE_PATTERNS)


def looks_like_brave_challenge_url(url: str | None) -> bool:
    path = urlparse(str(url or "")).path.casefold()
    return any(
        marker in path
        for marker in ("/captcha", "/challenge", "/verify")
    )


def _challenge_excerpt(raw_html: str, max_length: int = 2000) -> str:
    text = re.sub(r"\s+", " ", _html_to_visible_text(raw_html)).strip()
    return text[:max_length]


class BraveSearchEngine(SearchEngine):
    def __init__(self):
        super().__init__(name="Brave")
        self.base_url = "https://search.brave.com"
        self.offset = 1
        self.query = None
        self.nb_results_per_page = 0
        self._empty_results_dumped = False

    def construct_url(self):
        url = f"{self.base_url}/search?q={quote_plus(self.construct_query(self.query))}&spellcheck=0"
        extra_params = build_engine_date_params("brave", self.search_filters)
        extra_params.update(build_engine_region_params("brave", self.search_filters))
        if extra_params:
            url += "&" + urlencode(extra_params)
        return url

    # There is some cases where Brave does not display the Title in the HTML
    def parse_results_old(self, raw_results):
        xpaths = self.get_xpaths()
        return parse_with_xpath(
            raw_results,
            result_xpath=xpaths["result"],
            title_xpath=xpaths["title"],
            link_xpath=xpaths["link"],
            desc_xpath=xpaths["desc"],
            source=self.name
        )

    def get_xpaths(self):
        return {
            "result": "//div[contains(@class, 'snippet') and @data-pos]",
            "title": ".//div[contains(@class, 'title')]",
            "link": ".//a[@href]",
            # Brave moved the description from `.snippet-description` to a
            # `.content` node inside `.generic-snippet`; accept both so older
            # captures and the current SERP markup both parse.
            "desc": ".//div[contains(@class, 'snippet-description') or contains(@class, 'generic-snippet')]",
        }

    def _parse_results_embedded_json(self, raw_results):
        pattern = r"['\"]?results['\"]?\s*:\s*\[\{(.*?)\}\],\s*[a-zA-Z_$]{1,3}\b"
        match = re.search(pattern, raw_results, re.DOTALL)
        results = []

        if match:
            res = js_like_to_json(match.group(1))
            if res is not None:
                for item in res:
                    if self.max_results is None or self.num_results < self.max_results:
                        title = item.get("title", None)
                        url = item.get("url", None)
                        description = item.get("description", None)
                        if title is None or url is None or description is None:
                            continue

                        results.append({
                            "title": title,
                            "link": url,
                            "description": description,
                            "source": self.name
                        })
                        self.num_results += 1
                        self.nb_results_per_page += 1
        else:
            logger.debug("Brave results block not found in page source.")

        return results

    def parse_results(self, raw_results):
        self.nb_results_per_page = 0

        results = self._parse_results_embedded_json(raw_results)
        if results:
            return results

        logger.warning(
            "Brave embedded results parsing returned no results; "
            "falling back to XPath parsing."
        )
        fallback_results = self.parse_results_old(raw_results)
        if self.max_results is not None:
            remaining = max(0, self.max_results - self.num_results)
            fallback_results = fallback_results[:remaining]

        self.num_results += len(fallback_results)
        self.nb_results_per_page = len(fallback_results)
        if fallback_results:
            logger.warning("Brave XPath fallback parsed %d results.", len(fallback_results))
        else:
            logger.warning("Brave parsing failed: embedded JSON and XPath fallback returned no results.")
            self._dump_empty_results_html(raw_results)
        return fallback_results

    def _dump_empty_results_html(self, raw_results) -> None:
        """Save the raw page once when Brave yields zero results, so its
        current markup can be inspected and the parser updated.

        Always dumps (guarded to one per search, independent of the
        ``SYNTHESIX_DEBUG_HTML`` flag): a silently empty Brave means the site
        layout drifted from both the embedded-JSON regex and the XPath
        fallback, and the raw page is the only way to diagnose it. It is NOT
        gated on ``looks_like_brave_robot_challenge`` — a fully rendered SERP
        routinely contains the bare words "bot"/"robot", which would false-
        positive and silently skip the capture we need most."""
        if self._empty_results_dumped:
            return
        raw_results = str(raw_results)
        self._empty_results_dumped = True
        try:
            capture_dir = get_settings().debug_html_dir
            capture_dir.mkdir(parents=True, exist_ok=True)
            stem = f"brave_empty_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            output_path = capture_dir / f"{stem}.html"
            output_path.write_text(raw_results, encoding="utf-8")
        except OSError:
            logger.debug("Unable to save the empty Brave results page", exc_info=True)
            return
        logger.warning(
            "Brave returned 0 results; saved the raw page for diagnosis: %s",
            output_path.resolve(),
        )

    async def post_execute_search(self):
        if self.num_results >= self.max_results:
            return

        while self.num_results < self.max_results:
            # By default, Brave returns 20 results per page
            # If the number of results from the actual page is less than 10, we can assume that there are no more results
            if self.nb_results_per_page < 10:
                break

            # Get the next page
            next_url = self.construct_url() + f"&offset={self.offset}"
            self.tab = await self.tab.get(next_url)
            self.offset += 1
            await self.wait_for_page_load()
            raw_results = await self.read_page_content("pagination")
            results = self.parse_results(raw_results)
            self.results.extend(results)

    def set_selector(self):
        self.selector = "#results"

    def get_probe_markers(self) -> dict:
        return {
            "challenge_url_path_substrings": BRAVE_CHALLENGE_URL_PATH_SUBSTRINGS,
            "challenge_html_markers": BRAVE_CHALLENGE_HTML_MARKERS,
        }

    def construct_query(self, query: str) -> str:
        """Construct the query for the search.
        """
        return query

    async def capture_robot_challenge(self, raw_content: str = "") -> dict:
        capture_dir = get_settings().robot_challenges_dir
        capture_dir.mkdir(parents=True, exist_ok=True)
        stem = f"brave_anti_robot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if not raw_content:
            try:
                raw_content = await self.read_page_content("robot_capture")
            except Exception as exc:
                raw_content = f"Unable to capture HTML content: {exc}"

        html_path = capture_dir / f"{stem}.html"
        text_path = capture_dir / f"{stem}.txt"
        screenshot_path = capture_dir / f"{stem}.png"

        html_path.write_text(raw_content, encoding="utf-8")
        text_path.write_text(_challenge_excerpt(raw_content), encoding="utf-8")

        captured = {
            "html": str(html_path.resolve()),
            "text": str(text_path.resolve()),
        }
        try:
            await self.tab.save_screenshot(
                filename=screenshot_path,
                format="png",
                full_page=True,
            )
            captured["screenshot"] = str(screenshot_path.resolve())
        except Exception as exc:
            captured["screenshot_error"] = str(exc)

        return captured

    async def _wait_for_results_container(self, timeout: float | None = None, interval: float | None = None) -> bool:
        settings = get_settings()
        timeout = settings.brave_results_timeout if timeout is None else timeout
        interval = settings.brave_results_interval if interval is None else interval
        start = time.monotonic()
        while (time.monotonic() - start) < timeout:
            state = await self.probe_page_state()
            if state["found"]:
                return True
            if state["challenge"]:
                # Stop waiting for results; let robot_check take over now
                # instead of burning the full results timeout on a captcha.
                return False
            await asyncio.sleep(interval)
        return False

    async def wait_for_page_load(self, timeout=None, interval=None) -> bool:
        """Wait for Brave's client-rendered results before reading.

        Brave (SvelteKit) ships an empty shell, hides the body behind a ~3s
        reveal animation, then injects the result snippets client-side. The
        base 2.5s ``page_load_timeout`` reads that shell (0 results), so wait
        on the results container with Brave's own budget, then let the
        snippets hydrate (``brave_results_settle``) before returning."""
        settings = get_settings()
        if await self._wait_for_results_container(timeout, interval):
            settle = settings.brave_results_settle
            if settle > 0:
                await asyncio.sleep(settle)
            return True

        try:
            await self.read_page_content("load_timeout")
        except Exception:
            logger.debug(
                "Unable to capture Brave content after load timeout",
                exc_info=True,
            )
        return bool(await self.robot_check())

    async def _click_robot_button_with_find(self):
        for text in BRAVE_ROBOT_FIND_PATTERNS:
            try:
                button = await self.tab.find(
                    text,
                    best_match=True,
                    timeout=get_settings().brave_robot_find_timeout,
                )
            except Exception:
                button = None
            if button:
                try:
                    await button.click()
                    return text
                except Exception as exc:
                    logger.debug(
                        "Unable to click Brave anti-robot candidate found by text %r: %s",
                        text,
                        exc,
                    )
        return None

    async def _click_robot_button_with_js(self):
        patterns_json = json.dumps(BRAVE_ROBOT_BUTTON_PATTERNS)
        expression = f"""
        (() => {{
            const patterns = {patterns_json};
            const normalize = (value) => String(value || "")
                .normalize("NFD")
                .replace(/[\\u0300-\\u036f]/g, "")
                .replace(/[\\u2018\\u2019]/g, "'")
                .toLowerCase()
                .replace(/\\s+/g, " ")
                .trim();
            const isVisibleAndEnabled = (element) => {{
                const style = window.getComputedStyle(element);
                const rect = element.getBoundingClientRect();
                return !element.disabled &&
                    style.visibility !== "hidden" &&
                    style.display !== "none" &&
                    rect.width > 0 &&
                    rect.height > 0;
            }};
            const pageLooksLikeCaptcha =
                location.pathname.includes("/captcha") ||
                document.documentElement.innerHTML.includes("blockRobots:true") ||
                document.documentElement.innerHTML.includes('"blockRobots":true');
            if (pageLooksLikeCaptcha) {{
                const primarySelectors = [
                    "button[data-sveltekit-reload][role='button']",
                    "button.full-width[role='button']",
                    "button[class*='full-width']",
                    "[role='button'][class*='full-width']",
                    "button[type='submit']",
                    "button"
                ];
                for (const selector of primarySelectors) {{
                    const element = Array.from(document.querySelectorAll(selector))
                        .find(isVisibleAndEnabled);
                    if (element) {{
                        const text = [
                            element.innerText,
                            element.textContent,
                            element.value,
                            element.getAttribute("aria-label"),
                            element.getAttribute("title")
                        ].filter(Boolean).join(" ");
                        element.click();
                        return text || selector;
                    }}
                }}
            }}
            const selectors = [
                "button",
                "input[type='button']",
                "input[type='submit']",
                "[role='button']",
                "label",
                "[tabindex]"
            ];
            const elements = Array.from(document.querySelectorAll(selectors.join(",")));
            for (const element of elements) {{
                const text = [
                    element.innerText,
                    element.textContent,
                    element.value,
                    element.getAttribute("aria-label"),
                    element.getAttribute("title")
                ].filter(Boolean).join(" ");
                const normalized = normalize(text);
                if (!normalized) {{
                    continue;
                }}
                if (isVisibleAndEnabled(element) && patterns.some((pattern) => normalized.includes(pattern))) {{
                    element.click();
                    return text || element.tagName;
                }}
            }}
            return null;
        }})()
        """
        try:
            return await self.tab.evaluate(expression)
        except Exception:
            return None

    async def _click_robot_button(self):
        clicked = await self._click_robot_button_with_find()
        if clicked:
            return clicked
        return await self._click_robot_button_with_js()

    async def robot_check(self):
        try:
            raw_content = await self.read_page_content("robot_check")
        except Exception:
            raw_content = ""

        challenge_detected = (
            looks_like_brave_robot_challenge(raw_content)
            or looks_like_brave_challenge_url(
                getattr(self.tab, "url", None) or self.current_url
            )
        )
        if not challenge_detected:
            return False

        try:
            await self.tab.bring_to_front()
        except Exception:
            logger.debug(
                "Unable to focus the Brave challenge tab",
                exc_info=True,
            )

        clicked = await self._click_robot_button() if challenge_detected else None
        captured = await self.capture_robot_challenge(raw_content)
        logger.warning("Brave anti-robot challenge captured: %s", captured)

        if clicked:
            logger.info("Brave anti-robot control clicked: %s", clicked)
        else:
            logger.warning(
                "Resolve the Brave challenge manually in the foreground tab; "
                "Synthesix will resume automatically."
            )

        if await self._wait_for_results_container():
            logger.info("Brave anti-robot challenge resolved.")
            return True

        raise RobotChallengeError(
            self.name,
            "Brave anti-robot challenge was not resolved before the timeout.",
            query=self.query,
            url=self.current_url,
            captured_artifacts=captured,
        )
