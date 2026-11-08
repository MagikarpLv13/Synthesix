import asyncio
import logging
from urllib.error import HTTPError
from urllib.parse import parse_qs, quote_plus, urlencode, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from browser import click_at, get_browser_service
from exceptions import RobotChallengeError
from parsers import parse_with_xpath
from query_operators import build_engine_date_params
from search_engine import SearchEngine
from search_regions import build_engine_region_params


logger = logging.getLogger(__name__)

_REDIRECT_CONCURRENCY = 4
_REDIRECT_REQUEST_TIMEOUT = 3.0
_REDIRECT_BATCH_TIMEOUT = 8.0


def _google_redirect_path(url: str) -> str:
    """Recognize only HTTPS wrappers on the Google Search origin."""
    try:
        parts = urlsplit(url)
        if (
            parts.scheme == "https"
            and parts.hostname in {"google.com", "www.google.com"}
            and parts.port in {None, 443}
            and parts.username is None
            and parts.password is None
            and parts.path in {"/goto", "/url"}
            and not any(ord(char) < 32 for char in url)
        ):
            return parts.path
    except ValueError:
        pass
    return ""


def _is_http_destination(url: str) -> bool:
    try:
        parts = urlsplit(url)
        return bool(
            parts.scheme in {"http", "https"}
            and parts.hostname
            and parts.port != 0
            and parts.username is None
            and parts.password is None
            and not any(ord(char) < 32 for char in url)
        )
    except ValueError:
        return False


def _unwrap_google_url(url: str) -> str:
    """Decode legacy /url destinations locally; /goto tokens are opaque."""
    if _google_redirect_path(url) == "/url":
        params = parse_qs(urlsplit(url).query)
        for key in ("q", "url"):
            target = (params.get(key) or [""])[0]
            if _is_http_destination(target):
                return target
    return url


class _NoGoogleRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Only Google's response headers are needed. Never visit the target.
        return None


def _resolve_google_goto(url: str) -> str:
    """Read Google's destination without following redirects or reading a body."""
    if _google_redirect_path(url) != "/goto":
        return url
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with build_opener(_NoGoogleRedirectHandler()).open(
            request, timeout=_REDIRECT_REQUEST_TIMEOUT,
        ):
            return url
    except HTTPError as error:
        with error:
            if error.code not in {301, 302, 303, 307, 308}:
                return url
            location = error.headers.get("Location", "")
            if not location or any(ord(char) < 32 for char in location):
                return url
            try:
                target = _unwrap_google_url(urljoin(url, location))
            except ValueError:
                return url
            if not _is_http_destination(target) or _google_redirect_path(target):
                return url
            parts = urlsplit(target)
            if parts.hostname in {"google.com", "www.google.com", "consent.google.com"}:
                # A Google interstitial is not the result's destination.
                return url
            return target
    except (OSError, ValueError):
        return url


async def resolve_google_result_links(results: list[dict]) -> None:
    """Resolve a batch before scoring/persistence, with bounded parallel I/O."""
    groups: dict[str, list[dict]] = {}
    for result in results:
        url = _unwrap_google_url(urljoin("https://www.google.com", result["link"]))
        result["link"] = url
        if _google_redirect_path(url) == "/goto":
            groups.setdefault(url, []).append(result)
    if not groups:
        return

    semaphore = asyncio.Semaphore(_REDIRECT_CONCURRENCY)

    async def resolve_one(url: str, rows: list[dict]) -> None:
        async with semaphore:
            try:
                target = await asyncio.to_thread(_resolve_google_goto, url)
            except Exception:
                logger.debug("Unable to resolve one Google result redirect.")
                return
            for row in rows:
                row["link"] = target

    try:
        await asyncio.wait_for(
            asyncio.gather(*(resolve_one(url, rows) for url, rows in groups.items())),
            timeout=_REDIRECT_BATCH_TIMEOUT,
        )
    except asyncio.TimeoutError:
        logger.debug("Google redirect resolution reached its time budget.")
    unresolved = sum(rows[0]["link"] == url for url, rows in groups.items())
    logger.info("Google result destinations: %d resolved, %d unresolved.",
                len(groups) - unresolved, unresolved)

# JS run in the top /sorry/ frame: locate the reCAPTCHA "I'm not a robot"
# checkbox and return its centre in top-viewport CSS pixels. Reaches into the
# anchor iframe when it is same-origin (google.com); otherwise falls back to
# the checkbox's usual offset inside the iframe. Returns null when no
# reCAPTCHA iframe is present.
_RECAPTCHA_CHECKBOX_COORDS_JS = """
(() => {
    const iframe = document.querySelector(
        'iframe[src*="/recaptcha/"][src*="anchor"], iframe[title="reCAPTCHA"]'
    );
    if (!iframe) return null;
    const ir = iframe.getBoundingClientRect();
    if (!ir.width || !ir.height) return null;
    try {
        const doc = iframe.contentDocument ||
            (iframe.contentWindow && iframe.contentWindow.document);
        if (doc) {
            const anchor = doc.querySelector(
                '#recaptcha-anchor, .recaptcha-checkbox, [role="checkbox"]'
            );
            if (anchor) {
                const ar = anchor.getBoundingClientRect();
                return {
                    x: ir.left + ar.left + ar.width / 2,
                    y: ir.top + ar.top + ar.height / 2
                };
            }
        }
    } catch (e) {}
    return { x: ir.left + 30, y: ir.top + ir.height / 2 };
})()
"""


class GoogleSearchEngine(SearchEngine):
    def __init__(self):
        super().__init__(name="Google")
        self.base_url = "https://www.google.com"

    def construct_url(self) -> str:
        url = f"{self.base_url}/search?q={quote_plus(self.query)}&num={self.max_results}&start=0&filter=0&nfpr=1&udm=14&safe=off"
        extra_params = build_engine_date_params("google", self.search_filters)
        extra_params.update(build_engine_region_params("google", self.search_filters))
        if extra_params:
            url += "&" + urlencode(extra_params)
        return url

    def parse_results(self, raw_results: str) -> list[dict[str, str]]:
        xpaths = self.get_xpaths()
        results = parse_with_xpath(
            raw_results,
            result_xpath=xpaths['result'],
            title_xpath=xpaths['title'],
            link_xpath=xpaths['link'],
            desc_xpath=xpaths['desc'],
            source=self.name
        )
        for result in results:
            result["link"] = _unwrap_google_url(urljoin(self.base_url, result["link"]))
        return results

    async def post_execute_search(self) -> None:
        await resolve_google_result_links(self.results)

    def get_xpaths(self):
        return {
            'result': ".//div[@jscontroller][@data-ved][@data-hveid]",
            'title': ".//a[@href]//h3",
            'link': ".//a[@href]",
            'desc': ".//*[contains(@class, 'VwiC3b')]"
        }

    def set_selector(self):
        self.selector = "#search"

    async def robot_check(self):
        # T-004: tab.find() text-searches the DOM (DOM.performSearch), so
        # matching the "#captcha-form" CSS selector through it was never
        # guaranteed. Probe the selector directly and fall back on Google's
        # interstitial URL (/sorry/) as a second marker.
        captcha_form = None
        try:
            captcha_form = await self.tab.query_selector("#captcha-form")
        except Exception:
            logger.debug(
                "Unable to inspect the Google page for a captcha form",
                exc_info=True,
            )

        current_url = str(getattr(self.tab, "url", "") or self.current_url or "")
        challenge_url = "/sorry/" in urlsplit(current_url).path
        if not captcha_form and not challenge_url:
            # Neither marker present: we can assume we are not a robot 🤖
            return False

        # wait_for_page_load() calls robot_check() again when it times out;
        # without this guard an unresolved captcha would nest 100s waits
        # forever instead of failing once.
        if getattr(self, "_challenge_wait_active", False):
            raise RobotChallengeError(
                self.name,
                "Google captcha was not resolved before the timeout.",
                query=self.query,
                url=self.current_url,
            )

        logger.warning("Robot detected by Google, captcha resolution is required.")
        try:
            await get_browser_service(self.browser).show_tab_window_for_manual_interaction(
                self.tab
            )
        except Exception:
            logger.debug("Unable to focus the Google challenge tab", exc_info=True)

        await self._try_click_recaptcha_checkbox()

        self._challenge_wait_active = True
        try:
            resolved = await self.wait_for_page_load(timeout=100)
        finally:
            self._challenge_wait_active = False

        if resolved:
            logger.info("Google captcha resolved; results are available.")
            return True

        raise RobotChallengeError(
            self.name,
            "Google captcha was not resolved before the timeout.",
            query=self.query,
            url=self.current_url,
        )

    async def _try_click_recaptcha_checkbox(self) -> None:
        """Best-effort: click the reCAPTCHA "I'm not a robot" checkbox with a
        trusted mouse event, once, before waiting on the challenge.

        If Google accepts it, the page reloads to results and
        :meth:`wait_for_page_load` picks it up. If Google shows an image
        challenge instead, the user solves it manually (unchanged behavior).
        Any failure is swallowed — this must never break captcha handling."""
        try:
            coords = await self.tab.evaluate(_RECAPTCHA_CHECKBOX_COORDS_JS)
        except Exception:
            logger.debug("Unable to locate the reCAPTCHA checkbox", exc_info=True)
            return
        if not isinstance(coords, dict):
            return
        x, y = coords.get("x"), coords.get("y")
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            return
        logger.info("Attempting to tick the reCAPTCHA checkbox automatically.")
        await click_at(self.tab, float(x), float(y))
