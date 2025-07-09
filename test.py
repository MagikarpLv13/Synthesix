from google import GoogleSearchEngine
from bing import BingSearchEngine
import asyncio

asyncio.run(GoogleSearchEngine().search("test"))
asyncio.run(BingSearchEngine().search("test"))