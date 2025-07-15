import re
from search_engine import SearchEngine
from utils import js_like_to_json
from parsers import parse_with_xpath
import time

class BraveSearchEngine(SearchEngine):
    def __init__(self):
        super().__init__(name="Brave")
        self.base_url = "https://search.brave.com"
        self.offset = 1
        self.query = None
        self.nb_results_per_page = 0

    def construct_url(self):
        url = f"{self.base_url}/search?q={self.construct_query(self.query)}&spellcheck=0"
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

    async def robot_check(self):
        button = await self.tab.find("I'm not a robot", best_match=True, timeout=0.1)
        if button:
            await button.click()
            print("Button clicked")
            await self.wait_for_page_load(timeout=10)
            return True
        
        # If the button is not found, we can assume that we are not a robot 🤖
        return False

    def test(self):
        with open("test_brave.html", "r") as file:
            raw_results = file.read()
        begin_time = time.time()
        res = self.parse_results(raw_results)
        print(res)
        print(len(res))
        end_time = time.time()
        print(f"Temps d'exécution pour le parsing avec lxml: {end_time - begin_time:.2f} secondes")
        begin_time = time.time()
