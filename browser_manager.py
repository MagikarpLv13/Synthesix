import zendriver as uc
import os
from zendriver.core.config import Config

class HeadlessBrowserManager:
    def __init__(self):
        self.browser : uc.Browser = None

    @classmethod
    async def create(cls):
        self = cls()
        custom_profile = os.path.join(os.getcwd(), "zendriver-profile")
        os.makedirs(custom_profile, exist_ok=True)

        config = Config()
        config.user_data_dir = custom_profile

        """⚠️ Headless mode is not working with Brave, instant flag as a robot 🤖.
        """
        # config.headless = True

        self.browser = await uc.start(config=config)
        return self

    async def quit(self):
        for tab in self.browser.tabs:
            await tab.close()
        await self.browser.stop()

    async def get_driver(self):
        return self.browser
