from parsers import parse_with_xpath
from search_engine import SearchEngine

class BingSearchEngine(SearchEngine):
    def __init__(self):
        super().__init__(name="Bing")
        self.base_url = "https://www.bing.com"
        
        
    async def post_execute_search(self):
        while self.num_results < self.max_results:
            try:
                next_button = await self.tab.xpath(".//a[contains(@class, 'sb_pagN') and @href]")
            except Exception as e:
                print(e)
                break
            if next_button:
                current_url = self.base_url + next_button[0].get("href")
            self.tab = await self.tab.get(current_url)
            await self.tab.wait(0.5)
            raw_results = await self.tab.get_content()
            self.results.extend(self.parse_results(raw_results))
            self.num_results = len(self.results)

    def construct_url(self) -> str:
        return f"{self.base_url}/search?q={self.query}"

    def parse_results(self, raw_results):
        xpaths = self.get_xpaths()
        return parse_with_xpath(
            raw_results,
            result_xpath=xpaths["result"],
            title_xpath=xpaths["title"],
            link_xpath=xpaths["link"],
            desc_xpath=xpaths["desc"],
            source=self.name,
        )

    def get_xpaths(self):
        return {
            'result': "//li[contains(@class, 'b_algo')]",
            'title': ".//h2",
            'link': ".//a[@href]",
            'desc': ".//div[contains(@class, 'b_caption')]"
        }
        
    def test(self):
        with open("test_bing.html", "r") as file:
            raw_results = file.read()

        res = self.parse_results(raw_results)
        print(res)