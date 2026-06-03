import asyncio
import json
import logging
import re
import time
import unicodedata
from datetime import datetime
from html import unescape
from urllib.parse import quote_plus

from exceptions import RobotChallengeError
from parsers import parse_with_xpath
from search_engine import SearchEngine
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
)

BRAVE_ROBOT_FIND_PATTERNS = (
    "i'm not a robot",
    "im not a robot",
    "i am not a robot",
    "je ne suis pas un robot",
    "verify you are human",
    "verifiez que vous etes humain",
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

    def construct_url(self):
        url = f"{self.base_url}/search?q={quote_plus(self.construct_query(self.query))}&spellcheck=0"
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
            "desc": ".//div[contains(@class, 'snippet-description')]",
        }

    def parse_results(self, raw_results):
        pattern = r"results:\s*\[\{(.*?)\}\],bo"
        match = re.search(pattern, raw_results, re.DOTALL)
        results = []
        self.nb_results_per_page = 0

        if match:
            res = js_like_to_json(match.group(1))
            if res is not None:
                for item in res:
                    if self.num_results < self.max_results:
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
            print("'results' block not found.")

        return results

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
            raw_results = await self.tab.get_content()
            results = self.parse_results(raw_results)
            self.results.extend(results)

    def set_selector(self):
        self.selector = "#results"

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
                raw_content = await self.tab.get_content()
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
            try:
                if await self.tab.query_selector(self.selector):
                    return True
            except Exception:
                pass
            await asyncio.sleep(interval)
        return False

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
        # We need to focus the tab to be able to click on the button
        await self.tab.bring_to_front()

        try:
            raw_content = await self.tab.get_content()
        except Exception:
            raw_content = ""

        challenge_detected = looks_like_brave_robot_challenge(raw_content)
        clicked = await self._click_robot_button() if challenge_detected else None
        captured = {}
        if challenge_detected or clicked:
            captured = await self.capture_robot_challenge(raw_content)
            logger.warning("Brave anti-robot challenge captured: %s", captured)

        if clicked:
            logger.info("Brave anti-robot control clicked: %s", clicked)
            if await self._wait_for_results_container():
                return True
            raise RobotChallengeError(
                self.name,
                "Brave anti-robot challenge was clicked but results did not load.",
                query=self.query,
                url=self.current_url,
                captured_artifacts=captured,
            )
        
        if challenge_detected:
            raise RobotChallengeError(
                self.name,
                "Brave anti-robot challenge detected, but no known control was clickable.",
                query=self.query,
                url=self.current_url,
                captured_artifacts=captured,
            )

        # If the button is not found, we can assume that we are not a robot
        return False

    def test(self):
        with open("test_brave.html", "r", encoding="utf-8", errors="replace") as file:
            raw_results = file.read()
        begin_time = time.time()
        res = self.parse_results(raw_results)
        print(res)
        print(len(res))
        end_time = time.time()
        print(f"Temps d'exécution pour le parsing avec lxml: {end_time - begin_time:.2f} secondes")
        begin_time = time.time()
