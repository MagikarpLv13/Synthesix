import logging
from urllib.parse import quote_plus, urlencode

from parsers import parse_with_xpath
from query_operators import build_engine_date_params
from search_engine import SearchEngine


logger = logging.getLogger(__name__)


class GoogleSearchEngine(SearchEngine):
    def __init__(self):
        super().__init__(name="Google")
        self.base_url = "https://www.google.com"

    def construct_url(self) -> str:
        url = f"{self.base_url}/search?q={quote_plus(self.query)}&num={self.max_results}&start=0&filter=0&nfpr=1&udm=14&safe=off"
        date_params = build_engine_date_params("google", self.search_filters)
        if date_params:
            url += "&" + urlencode(date_params)
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
        button = await self.tab.find("#captcha-form", timeout=0.1)
        if button:
            logger.warning("Robot detected by Google, captcha resolution is required.")
            await self.tab.activate()
            await self.wait_for_page_load(timeout=100)
            return True

        # If the button is not found, we can assume that we are not a robot 🤖
        return False
