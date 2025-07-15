from google import GoogleSearchEngine
from bing import BingSearchEngine
from brave import BraveSearchEngine
import asyncio

#asyncio.run(GoogleSearchEngine().search("test"))
#asyncio.run(BingSearchEngine().search("test"))
asyncio.run(BraveSearchEngine().search("test"))