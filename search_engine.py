from abc import ABC, abstractmethod
import pandas as pd
import time

class SearchEngine(ABC):
    def __init__(self, name, num_results=25):
        self.name = name
        self.results = []
        self.num_results = num_results

    @abstractmethod
    async def search(self, query, browser) -> pd.DataFrame:
        """
        Launch a search and return a DataFrame of results.
        """
        if query == "test" and browser is None:
            self.test()
            return
        start_time = time.time()
        self.results = await self.execute_search(query, browser)
        print(f"Temps d'exécution {self.name}: {time.time() - start_time:.2f} secondes")
        return pd.DataFrame(self.results)

    async def execute_search(self, query, browser):
        """Execute the search and return the results.
        """
        self.pre_execute_search()
        url = self.construct_url(query)
        tab = await browser.get(url, new_tab=True)
        await browser.wait(0.5)
        raw_results = await tab.get_content()
        res = self.parse_results(raw_results)
        self.post_execute_search()
        return res

    @abstractmethod
    async def construct_url(self, query) -> str:
        """
        Construct the URL for the search.
        """
        pass

    @abstractmethod
    def parse_results(self, raw_results):
        """
        Parse the raw HTML and return a list of structured results.
        """
        pass

    @abstractmethod
    def get_xpaths(self):
        """
        Return a dictionary with the XPaths necessary for parsing.
        """
        pass 

    def test(self):
        pass

    def post_execute_search(self):
        """Used to execute actions after the first search is executed. Mostly for search engine that need to
        click on a button to load more results.
        """
        pass

    def pre_execute_search(self):
        """Used to execute actions before the search is executed.
        """
        pass