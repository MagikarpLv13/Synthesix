import nodriver as uc
from selenium.webdriver.chrome.options import Options
import os

class HeadlessBrowserManager:
    async def __init__(self):
        self.browser = await uc.start()
        
    async def quit(self):
        await self.browser.quit()
        
    async def get_driver(self):
        return self.browser
        
        
        
        