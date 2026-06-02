from google import GoogleSearchEngine
from bing import BingSearchEngine
from brave import BraveSearchEngine
import asyncio

if __name__ == "__main__":
    # asyncio.run(GoogleSearchEngine().search("test"))
    # asyncio.run(BingSearchEngine().search("test"))
    asyncio.run(BraveSearchEngine().search("test"))
