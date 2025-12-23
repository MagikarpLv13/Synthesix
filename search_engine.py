from abc import ABC, abstractmethod
import pandas as pd
import time
import zendriver as uc
import asyncio

class SearchEngine(ABC):
    def __init__(self, name):
        self.name = name
        self.results = []
        self.num_results = 0
        self.max_results = None
        self.tab : uc.Tab = None
        self.query = None
        self.browser = None
        self.selector = None
        self.current_url = None

    async def search(self, query, browser=None, max_results=20) -> pd.DataFrame:
        """
        Launch a search and return a DataFrame of results.
        """
        self.query = query
        self.browser = browser
        self.max_results = max_results
        self.set_selector()
        if self.query == "test" and self.browser is None:
            self.test()
            return
        start_time = time.time()
        await self.execute_search()
        print(f"Temps d'exécution {self.name}: {time.time() - start_time:.2f} secondes")
        await self.tab.close()
        return pd.DataFrame(self.results)

    async def execute_search(self):
        """Execute the search and return the results.
        """
        await self.pre_execute_search()
        await self.navigate()
        raw_results = await self.tab.get_content()
        self.results = self.parse_results(raw_results)

        self.num_results = len(self.results)
        await self.post_execute_search()

    async def navigate(self):
        """Navigate to the page
        """
        url = self.construct_url()
        self.current_url = url
        self.tab = await self.browser.get(url, new_tab=True)
        
        # Stay focused on the main tab
        await self.browser.main_tab.bring_to_front()
        await self.wait_for_page_load()

    @abstractmethod
    def set_selector(self):
        """Set the selector for the search engine.
        Selector used as a reference point to know when the page is loaded and to locate the results container
        Example:
        - Brave: "#results"
        - Google: "#search"
        - Bing: "#b_results"
        """
        pass

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

    async def wait_for_page_load(self, timeout=2.5, interval=0.1):
        """Custom function to wait for the page to load.
        """
        start = time.time()
        while (time.time() - start) < timeout:
            try :
                results = await self.tab.query_selector(self.selector)
                if results:
                    return
                await asyncio.sleep(interval)
            except :
                await asyncio.sleep(interval)
        await self.robot_check()
            
    async def robot_check(self):
        """
        Check if we are flagged as a robot.
        """
        pass
