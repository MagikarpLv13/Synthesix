from abc import ABC, abstractmethod
import pandas as pd
import time
import nodriver as uc

class SearchEngine(ABC):
    def __init__(self, name, max_results=25):
        self.name = name
        self.results = []
        self.num_results = 0
        self.max_results = max_results
        self.tab : uc.Tab = None
        self.query = None

    async def search(self, query, browser=None) -> pd.DataFrame:
        """
        Launch a search and return a DataFrame of results.
        """
        self.query = query
        if self.query == "test" and browser is None:
            self.test()
            return
        start_time = time.time()
        await self.execute_search(browser)
        print(f"Temps d'exécution {self.name}: {time.time() - start_time:.2f} secondes")
        await self.tab.close()
        return pd.DataFrame(self.results)

    async def execute_search(self, browser):
        """Execute the search and return the results.
        """
        await self.pre_execute_search()
        url = self.construct_url()
        self.tab = await browser.get(url, new_tab=True)
        await browser.wait(0.5)
        raw_results = await self.tab.get_content()
        self.results = self.parse_results(raw_results)
        self.num_results = len(self.results)
        await self.post_execute_search()

    @abstractmethod
    async def construct_url(self) -> str:
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

    def get_xpaths(self):
        """
        Return a dictionary with the XPaths necessary for parsing.
        """
        pass 

    def test(self):
        pass

    async def post_execute_search(self):
        """Used to execute actions after the first search is executed. Mostly for search engine that need to
        click on a button to load more results.
        """
        pass

    async def pre_execute_search(self):
        """Used to execute actions before the search is executed.
        """
        pass
