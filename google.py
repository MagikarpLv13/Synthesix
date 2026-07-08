import logging
from urllib.parse import quote_plus, urlencode, urlsplit

from browser import click_at, get_browser_service
from exceptions import RobotChallengeError
from parsers import parse_with_xpath
from query_operators import build_engine_date_params
from search_engine import SearchEngine
from search_regions import build_engine_region_params


logger = logging.getLogger(__name__)

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

    def parse_results(self, raw_results):
        xpaths = self.get_xpaths()
        return parse_with_xpath(
            raw_results,
            result_xpath=xpaths['result'],
            title_xpath=xpaths['title'],
            link_xpath=xpaths['link'],
            desc_xpath=xpaths['desc'],
            source=self.name
        )

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
