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
        return f"https://search.brave.com/search?q={self.query}&spellcheck=0"

    def parse_results(self, raw_results):
        pattern = r"results:\s*\[\{(.*?)\}\],bo"
        match = re.search(pattern, raw_results, re.DOTALL)

        if match:
            res = js_like_to_json(match.group(1))
            if res is not None:
                for item in res:
                    if self.num_results < self.max_results:
                        self.results.append({
                            "title": item.get("title", "Titre non trouvé"),
                            "link": item.get("url", "Lien non trouvé"),
                            "description": item.get("description", "Description non trouvée"),
                            "source": self.name
                        })
                        self.num_results += 1
        else:
            print("Bloc 'results' non trouvé.")

        return self.results
    
    async def post_execute_search(self):
        while self.num_results < self.max_results:
            next_url = self.construct_url() + f"&offset={self.offset}"
            self.tab = await self.tab.get(next_url)
            await self.tab.wait(0.5)
            raw_results = await self.tab.get_content()
            self.parse_results(raw_results)
            self.offset += 1
