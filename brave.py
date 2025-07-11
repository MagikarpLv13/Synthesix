import re
from search_engine import SearchEngine
from utils import js_like_to_json

class BraveSearchEngine(SearchEngine):
    def __init__(self):
        super().__init__(name="Brave")
        self.base_url = "https://search.brave.com"
        self.offset = 1
        self.query = None

    def construct_url(self):
        url = f"{self.base_url}/search?q={self.construct_query(self.query)}&spellcheck=0"
        return url

    def parse_results(self, raw_results):
        pattern = r"results:\s*\[\{(.*?)\}\],bo"
        match = re.search(pattern, raw_results, re.DOTALL)
        results = []

        if match:
            res = js_like_to_json(match.group(1))
            if res is not None:
                for item in res:
                    if self.num_results < self.max_results:
                        results.append({
                            "title": item.get("title", "Title not found"),
                            "link": item.get("url", "Link not found"),
                            "description": item.get("description", "Description not found"),
                            "source": self.name
                        })
                        self.num_results += 1
        else:
            print("Bloc 'results' non trouvé.")

        return results

    async def post_execute_search(self):
        try:
            flagged_as_robot = await self.im_a_robot()
        except Exception as e:
            print(f"Error: {e}")

        while self.num_results < self.max_results:
            print(f"Robot flagged: {flagged_as_robot}")

            # Get the results
            raw_results = await self.tab.get_content()
            results = self.parse_results(raw_results)
            self.results.extend(results)

            # By default, Brave returns 20 results per page
            # If the number of results is less than 10, we can assume that there are no more results
            if len(results) < 10:
                break

            # Get the next page
            next_url = self.construct_url() + f"&offset={self.offset}"
            self.tab = await self.tab.get(next_url)
            self.offset += 1
            await self.tab.wait(0.5)

    def construct_query(self, query: str) -> str:
        """Construct the query for the search.
        """
        return query

    async def im_a_robot(self):
        pre_button = await self.tab.find("Letting you in", best_match=True, timeout=0.1)
        if pre_button:
            button = await self.tab.find("I'm not a robot", best_match=True, timeout=1.5)
            if button:
                await button.click()
                # Wait 5 seconds to process the "I'm not a robot" request
                await self.tab.wait(5)
                return True
            else:
                return False
        return False
