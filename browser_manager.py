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
        config.headless = True
        config.user_data_dir = custom_profile
        config.sandbox = True
        config.lang = None
        config.host = None
        config.port = None
        config.expert = None
        
        self.browser = await uc.start(config=config)
        await self.set_driver(self.browser)
        return self

    async def quit(self):
        self.browser.stop()
        
    async def get_driver(self):
        return self.browser
        
    async def set_driver(self, browser):
        self.browser = browser
        
        
        