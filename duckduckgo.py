import asyncio
import logging
import re
import time
from datetime import datetime
from html import unescape
from urllib.parse import parse_qs, quote_plus, urljoin, urlparse

from lxml import html

from exceptions import RobotChallengeError
from query_operators import build_engine_date_params
from search_engine import SearchEngine
from search_regions import build_engine_region_params
from settings import get_settings


logger = logging.getLogger(__name__)

DUCKDUCKGO_ROBOT_CHALLENGE_PATTERNS = (
    "unfortunately, bots use duckduckgo too",
    "please complete the following challenge",
    "confirm this search was made by a human",
    "select all squares containing a duck",
)

DUCKDUCKGO_ROBOT_RAW_MARKERS = (
    "anomaly-modal",
    "anomaly-modal__title",
    "anomaly-modal__challenge",
    "anomaly.js",
)

DUCKDUCKGO_FORBIDDEN_PATTERNS = (
    "<title>403 forbidden</title>",
    "<title>forbidden</title>",
    ">403 forbidden<",
    ">forbidden<",
)


def _html_to_visible_text(raw_html: str) -> str:
    text = re.sub(
        r"<(script|style)\b[^>]*>.*?</\1>",
        " ",
        str(raw_html),
        flags=re.IGNORECASE | re.DOTALL,
    )
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def looks_like_duckduckgo_robot_challenge(raw_html: str) -> bool:
    raw_html = unescape(str(raw_html))
    lowered_html = raw_html.lower()
    if any(marker in lowered_html for marker in DUCKDUCKGO_ROBOT_RAW_MARKERS):
        return True
    visible_text = _html_to_visible_text(raw_html).lower()
    return any(pattern in visible_text for pattern in DUCKDUCKGO_ROBOT_CHALLENGE_PATTERNS)


def looks_like_duckduckgo_forbidden(raw_html: str) -> bool:
    lowered_html = str(raw_html).lower()
    return any(pattern in lowered_html for pattern in DUCKDUCKGO_FORBIDDEN_PATTERNS)


class DuckDuckGoSearchEngine(SearchEngine):
    def __init__(self):
        super().__init__(name="DuckDuckGo")
        self.base_url = "https://duckduckgo.com/"
        self.fallback_base_url = "https://html.duckduckgo.com/html/"
        self._challenge_follow_up_captures = {}

    def construct_url(self, base_url: str | None = None) -> str:
        params = {
            "q": quote_plus(self.query),
            "ia": "web",  # Web results only
            "kp": "-2",  # Safe Search off
            "kz": "-1",  # Instant Answers off
            "kac": "-1",  # Auto-suggest off
            "k1": "-1",  # Ads off
            "kl": "wt-wt",  # No region
        }
        params.update(build_engine_date_params("duckduckgo", self.search_filters))
        params.update(build_engine_region_params("duckduckgo", self.search_filters))
        query_string = "&".join(f"{key}={value}" for key, value in params.items())
        return f"{base_url or self.base_url}?{query_string}"

    def parse_results(self, raw_results):
        tree = html.fromstring(raw_results)
        results = []
        seen_links = set()

        for result in tree.xpath("//*[@data-testid='result']"):
            parsed = self._parse_modern_result(result)
            if parsed and parsed["link"] not in seen_links:
                results.append(parsed)
                seen_links.add(parsed["link"])
            if len(results) >= self.max_results:
                return results

        result_xpath = (
            "//div[contains(@class, 'result__body')]"
            " | "
            "//div[contains(@class, 'web-result') and not(.//div[contains(@class, 'result__body')])]"
        )
        for result in tree.xpath(result_xpath):
            parsed = self._parse_result_block(result)
            if parsed and parsed["link"] not in seen_links:
                results.append(parsed)
                seen_links.add(parsed["link"])
            if len(results) >= self.max_results:
                return results

        for result in tree.xpath("//tr[.//a[contains(@class, 'result-link')]]"):
            parsed = self._parse_lite_result_row(result)
            if parsed and parsed["link"] not in seen_links:
                results.append(parsed)
                seen_links.add(parsed["link"])
            if len(results) >= self.max_results:
                return results

        return results

    async def post_execute_search(self):
        if self.num_results >= self.max_results:
            return

        for page_index in range(1, 6):
            try:
                buttons = await self.tab.xpath(
                    "//*[@id='more-results'] | //*[@data-testid='more-results']"
                )
            except Exception:
                logger.debug("Unable to locate DuckDuckGo more-results button", exc_info=True)
                break
            if not buttons:
                break

            try:
                await buttons[0].click()
            except Exception:
                try:
                    clicked = await self.tab.evaluate(
                        """
                        (() => {
                            const button = document.querySelector(
                                "#more-results, [data-testid='more-results']"
                            );
                            if (!button) {
                                return false;
                            }
                            button.click();
                            return true;
                        })()
                        """
                    )
                except Exception:
                    clicked = False
                if not clicked:
                    logger.debug("Unable to click DuckDuckGo more-results button", exc_info=True)
                    break

            if not await self._wait_for_additional_results(page_index):
                break
            if self.num_results >= self.max_results:
                break

    async def _wait_for_additional_results(self, page_index: int) -> bool:
        settings = get_settings()
        start = time.monotonic()
        existing_links = {result["link"] for result in self.results}

        while time.monotonic() - start < settings.page_load_timeout:
            await asyncio.sleep(settings.page_load_interval)
            try:
                raw_results = await self.read_page_content(f"pagination_{page_index}")
            except Exception:
                continue

            parsed_results = self.parse_results(raw_results)
            new_results = [
                result
                for result in parsed_results
                if result["link"] not in existing_links
            ]
            if not new_results:
                continue

            remaining = max(0, self.max_results - len(self.results))
            self.results.extend(new_results[:remaining])
            self.num_results = len(self.results)
            return True

        return False

    def _parse_modern_result(self, result):
        link_nodes = result.xpath(".//*[@data-testid='result-title-a' and @href]")
        if not link_nodes:
            return None

        link_node = link_nodes[0]
        title = link_node.text_content().strip()
        link = self._clean_duckduckgo_url(link_node.get("href", ""))

        desc_nodes = result.xpath(".//*[@data-result='snippet']")
        description = desc_nodes[0].text_content().strip() if desc_nodes else ""

        return self._build_result(title, link, description)

    def _parse_result_block(self, result):
        link_nodes = result.xpath(".//a[contains(@class, 'result__a') and @href]")
        if not link_nodes:
            return None

        link_node = link_nodes[0]
        title = link_node.text_content().strip()
        link = self._clean_duckduckgo_url(link_node.get("href", ""))

        desc_nodes = result.xpath(".//*[contains(@class, 'result__snippet')]")
        description = desc_nodes[0].text_content().strip() if desc_nodes else ""

        return self._build_result(title, link, description)

    def _parse_lite_result_row(self, result):
        link_nodes = result.xpath(".//a[contains(@class, 'result-link') and @href]")
        if not link_nodes:
            return None

        link_node = link_nodes[0]
        title = link_node.text_content().strip()
        link = self._clean_duckduckgo_url(link_node.get("href", ""))

        desc_nodes = result.xpath("./following-sibling::tr[1]//*[contains(@class, 'result-snippet')]")
        description = desc_nodes[0].text_content().strip() if desc_nodes else ""

        return self._build_result(title, link, description)

    def _build_result(self, title: str, link: str, description: str):
        if not title or not link or self._is_ad_link(link):
            return None
        return {
            "title": title,
            "link": link,
            "description": description,
            "source": self.name,
        }

    def _is_ad_link(self, link: str) -> bool:
        parsed = urlparse(link)
        return parsed.netloc.endswith("duckduckgo.com") and parsed.path in {"/y.js", "/y"}

    def _clean_duckduckgo_url(self, link: str) -> str:
        if not link:
            return ""

        absolute_link = urljoin("https://duckduckgo.com", link)
        parsed = urlparse(absolute_link)
        query = parse_qs(parsed.query)
        redirected = query.get("uddg")
        if redirected:
            return redirected[0]
        return absolute_link

    def set_selector(self):
        self.selector = "[data-testid='result'], .result__body, .web-result, .result-link, #links"

    async def _wait_for_result_content(
        self,
        *,
        timeout: float,
        interval: float,
    ) -> bool:
        start = time.monotonic()
        next_content_check = start
        content_interval = max(0.5, interval)
        while time.monotonic() - start < max(0.0, timeout):
            try:
                if await self.tab.query_selector(self.selector):
                    return True
            except Exception:
                logger.debug(
                    "Unable to inspect DuckDuckGo result selectors",
                    exc_info=True,
                )

            raw_content = ""
            now = time.monotonic()
            if now >= next_content_check:
                next_content_check = now + content_interval
                try:
                    raw_content = await self.read_page_content("results_wait")
                except Exception:
                    raw_content = ""

            if raw_content:
                if (
                    looks_like_duckduckgo_robot_challenge(raw_content)
                    or looks_like_duckduckgo_forbidden(raw_content)
                ):
                    return False
                try:
                    if self.parse_results(raw_content):
                        return True
                except Exception:
                    logger.debug(
                        "Unable to parse DuckDuckGo while waiting for results",
                        exc_info=True,
                    )

            await asyncio.sleep(max(0.01, interval))
        return False

    async def wait_for_page_load(
        self,
        timeout: float | None = None,
        interval: float | None = None,
    ) -> bool:
        settings = get_settings()
        timeout = (
            settings.duckduckgo_results_timeout
            if timeout is None
            else timeout
        )
        interval = (
            settings.page_load_interval
            if interval is None
            else interval
        )
        if await self._wait_for_result_content(
            timeout=timeout,
            interval=interval,
        ):
            return True

        try:
            if await self.robot_check():
                return True
        except RobotChallengeError:
            raise

        fallback_url = self.construct_url(self.fallback_base_url)
        if self.current_url != fallback_url:
            logger.info(
                "DuckDuckGo results were not ready; trying the HTML endpoint."
            )
            if await self._navigate_after_challenge(fallback_url):
                if await self._wait_for_result_content(
                    timeout=timeout,
                    interval=interval,
                ):
                    return True
                return bool(await self.robot_check())
        return False

    async def capture_robot_challenge(
        self,
        raw_content: str = "",
        capture_kind: str = "anti_robot",
    ) -> dict:
        capture_dir = get_settings().robot_challenges_dir
        capture_dir.mkdir(parents=True, exist_ok=True)
        stem = f"duckduckgo_{capture_kind}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        if not raw_content:
            try:
                raw_content = await self.read_page_content("robot_capture")
            except Exception as exc:
                raw_content = f"Unable to capture HTML content: {exc}"

        html_path = capture_dir / f"{stem}.html"
        text_path = capture_dir / f"{stem}.txt"
        screenshot_path = capture_dir / f"{stem}.png"

        html_path.write_text(raw_content, encoding="utf-8")
        text_path.write_text(_html_to_visible_text(raw_content)[:2000], encoding="utf-8")

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

    async def _capture_follow_up_page(self, raw_content: str, capture_kind: str) -> None:
        if self._challenge_follow_up_captures:
            return
        captured = await self.capture_robot_challenge(raw_content, capture_kind=capture_kind)
        self._challenge_follow_up_captures = {
            f"follow_up_{name}": value
            for name, value in captured.items()
        }
        logger.warning("DuckDuckGo follow-up page captured: %s", captured)

    async def _navigate_after_challenge(self, url: str) -> bool:
        try:
            self.tab = await self.tab.get(url)
            self.current_url = url
            return True
        except Exception:
            logger.warning("Unable to reload DuckDuckGo after the challenge", exc_info=True)
            return False

    async def _wait_for_manual_challenge_resolution(
        self,
        timeout: float | None = None,
        interval: float | None = None,
    ) -> bool:
        settings = get_settings()
        timeout = settings.duckduckgo_robot_timeout if timeout is None else timeout
        interval = settings.duckduckgo_robot_interval if interval is None else interval
        start = time.monotonic()
        original_url = self.current_url or self.construct_url()
        reloaded_urls = set()
        fallback_attempted = False

        while time.monotonic() - start < max(0.0, timeout):
            try:
                if await self.tab.query_selector(self.selector):
                    return True
            except Exception:
                logger.debug("Unable to inspect DuckDuckGo after manual challenge", exc_info=True)

            try:
                raw_content = await self.read_page_content("manual_challenge_wait")
            except Exception:
                raw_content = ""

            if looks_like_duckduckgo_robot_challenge(raw_content):
                await asyncio.sleep(max(0.0, interval))
                continue

            if looks_like_duckduckgo_forbidden(raw_content):
                await self._capture_follow_up_page(raw_content, "forbidden")

            current_search_url = self.current_url or original_url
            if current_search_url not in reloaded_urls:
                reloaded_urls.add(current_search_url)
                logger.info("Reloading the DuckDuckGo query after manual verification.")
                if await self._navigate_after_challenge(current_search_url):
                    continue

            if not fallback_attempted:
                fallback_attempted = True
                fallback_url = self.construct_url(self.fallback_base_url)
                logger.info("Trying the DuckDuckGo HTML fallback endpoint.")
                if await self._navigate_after_challenge(fallback_url):
                    continue

            await asyncio.sleep(max(0.0, interval))
        return False

    async def robot_check(self):
        self._challenge_follow_up_captures = {}
        try:
            raw_content = await self.read_page_content("robot_check")
        except Exception:
            raw_content = ""

        challenge_detected = looks_like_duckduckgo_robot_challenge(raw_content)
        if not challenge_detected and looks_like_duckduckgo_forbidden(raw_content):
            captured = await self.capture_robot_challenge(raw_content, capture_kind="forbidden")
            logger.warning("DuckDuckGo returned a Forbidden page: %s", captured)
            raise RobotChallengeError(
                self.name,
                "DuckDuckGo returned a Forbidden page before results loaded.",
                query=self.query,
                url=self.current_url,
                captured_artifacts=captured,
            )
        if not challenge_detected:
            return False

        try:
            await self.tab.bring_to_front()
        except Exception:
            logger.debug("Unable to focus the DuckDuckGo challenge tab", exc_info=True)

        captured = await self.capture_robot_challenge(raw_content)
        logger.warning(
            "DuckDuckGo anti-robot challenge captured. Complete it manually in the "
            "foreground tab; Synthesix will resume automatically: %s",
            captured,
        )
        if await self._wait_for_manual_challenge_resolution():
            logger.info("DuckDuckGo anti-robot challenge resolved manually.")
            return True

        raise RobotChallengeError(
            self.name,
            "DuckDuckGo anti-robot challenge was not resolved before the timeout.",
            query=self.query,
            url=self.current_url,
            captured_artifacts={**captured, **self._challenge_follow_up_captures},
        )

    def test(self):
        return None
