import nodriver as uc
import os
from nodriver.core.config import Config

class HeadlessBrowserManager:
    def __init__(self):
        self.browser = None

    @classmethod
    async def create(cls):
        self = cls()
        custom_profile = os.path.join(os.getcwd(), "nodriver-profile")
        os.makedirs(custom_profile, exist_ok=True)

        config = Config()
        config.user_data_dir = custom_profile

        """⚠️ Headless mode is not working with Brave, instant flag as a robot 🤖.
        """
        # config.headless = True

        self.browser = await uc.start(config=config)
        await self.set_driver(self.browser)
        return self

    async def quit(self):
        self.browser.stop()

    async def get_driver(self):
        return self.browser

    async def set_driver(self, browser):
        self.browser = browser
