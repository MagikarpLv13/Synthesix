"""Real Chrome smoke with synthetic data and disposable profiles only."""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.runtime import BrowserApplication
from browser import click_at
from browser import get_browser_service
from browser_manager import HeadlessBrowserManager
from settings import get_settings
from search_orchestrator import SearchOrchestrator
from tests.fakes import FakeBrowser
from zendriver import cdp


async def smoke():
    print("Starting real browser smoke", flush=True)
    output = Path("tmp_ui_render/browser-refocus")
    output.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory() as directory, patch.dict(os.environ, {"SYNTHESIX_BASE_DIR": directory}):
        application = BrowserApplication(get_settings())
        running = asyncio.create_task(application.run(headless=True))
        try:
            for _ in range(100):
                if running.done():
                    await running
                    raise AssertionError("Browser exited before the home became ready")
                if application.home_tab:
                    ready = await asyncio.wait_for(application.home_tab.evaluate("Boolean(document.querySelector('sx-browser-app')?.model.connected)"), 5)
                    if ready:
                        break
                await asyncio.sleep(.2)
            else:
                raise AssertionError("Home did not connect")
            tab = application.home_tab
            print("Home connected", flush=True)
            assert await tab.evaluate("Boolean(document.querySelector('sx-browser-app').shadowRoot.querySelector('textarea'))")

            async def click(selector):
                point = await tab.evaluate(f"""(() => {{ const el = document.querySelector('sx-browser-app').shadowRoot.querySelector({json.dumps(selector)}); el.scrollIntoView({{block:'center'}}); const r = el.getBoundingClientRect(); return {{x:r.x+r.width/2,y:r.y+r.height/2}}; }})()""")
                await click_at(tab, point["x"], point["y"])
                await asyncio.sleep(.25)

            # Real mouse and keyboard CDP input exercise the Lit form and push bridge.
            await click("nav button:nth-child(2)")
            await click(".inline-form input")
            await tab.send(cdp.input_.insert_text(text="Synthetic persona"))
            await click(".inline-form button")
            print("Profile form submitted", flush=True)
            for _ in range(30):
                if application.store.profiles():
                    break
                await asyncio.sleep(.1)
            assert len(application.store.profiles()) == 1
            assert application.store.profiles()[0]["name"] == "Synthetic persona"
            await click("nav button:first-child")

            class LocalEngine:
                def __init__(self, name):
                    self.name = name

                async def search(self, *_args):
                    await asyncio.sleep(.05)
                    return [{"title": "Synthetic domain", "description": "Synthetic domain result", "link": "https://example.com/shared", "source": self.name}]

            factories = {name.lower(): (lambda name=name: LocalEngine(name)) for name in ["Google", "Bing", "Brave", "DuckDuckGo"]}
            def local_orchestrator(**kwargs):
                return SearchOrchestrator(engine_factories=factories, **kwargs)

            with patch.object(application.search_browser, "get_browser", new=AsyncMock(return_value=FakeBrowser())), patch("app.runtime.SearchOrchestrator", side_effect=local_orchestrator):
                await click("textarea")
                await tab.send(cdp.input_.insert_text(text='synthetic\nsite:example.com "domain"'))
                assert await tab.evaluate("document.querySelector('sx-browser-app').shadowRoot.querySelector('textarea').value.includes('synthetic')")
                await click("aside button.primary")
                for _ in range(50):
                    if application.store.history() and not application.model["running"]:
                        break
                    await asyncio.sleep(.1)
                assert application.store.history(), application.model["status"]
                assert application.store.history()[0]["count"] == 1
                assert len(application.model["coverage"]) == 2
                assert len(application.model["results"][0]["query_variants"]) == 2
                assert len(application.model["results"][0]["source"].split(",")) == 4
                print("Search form -> CDP -> engines -> deduplication -> history OK", flush=True)

            rows = [{"title": "Synthetic result " + "long title " * 14, "link": "https://example.com/" + "long-path/" * 16, "description": "Synthetic text for layout verification. " * 10, "source": "Google, Bing", "relevance_score": 8.3, "query_variants": ['"synthetic"']}]
            await application.publish(results=rows, status="Search completed.")
            assert await tab.evaluate("document.querySelector('sx-browser-app').shadowRoot.querySelectorAll('article').length") == 1
            # The visual inspector reads light DOM. Export a synthetic static
            # view of the same shadow tree and its actual adopted stylesheets.
            snapshot = await tab.evaluate("""(() => { const root=document.querySelector('sx-browser-app').shadowRoot; return {html:root.innerHTML,css:[...root.adoptedStyleSheets].flatMap(s=>[...s.cssRules].map(r=>r.cssText)).join('\\n')}; })()""")
            assets = Path(__file__).resolve().parents[2]
            markup = snapshot["html"].replace('src="assets/', 'src="' + (assets / 'assets').as_uri() + '/')
            (output / "inspector.html").write_text('<!doctype html><html lang="fr"><head><meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="' + (assets / 'theme.css').as_uri() + '"><style>' + snapshot["css"].replace(":host", "body") + '</style></head><body>' + markup + '</body></html>', encoding="utf-8")
            for theme in ["light", "dark"]:
                for width in [1440, 768, 390]:
                    await tab.send(cdp.emulation.set_device_metrics_override(width=width, height=1000, device_scale_factor=1, mobile=False))
                    await tab.evaluate(f"window.synthesixTheme.setTheme('{theme}')")
                    await asyncio.sleep(.15)
                    assert await tab.evaluate("document.documentElement.scrollWidth <= innerWidth"), (theme, width)
                    await tab.save_screenshot(str(output / f"{theme}-{width}.png"), full_page=True)
            await application.publish(results=[], status="Ready to search.")
            await tab.save_screenshot(str(output / "empty.png"), full_page=True)
            # A reloaded home receives the complete state again.
            await tab.reload()
            await asyncio.sleep(2.5)
            assert await tab.evaluate("document.querySelector('sx-browser-app').model.profiles.length") == 1
            assert await tab.evaluate("document.documentElement.lang") == "fr"
            print("Chrome smoke OK: home, Lit, profile form, CDP push, reload, light/dark, narrow and long text")
            fixture = Path(directory) / "synthetic-storage.html"
            fixture.write_text("<!doctype html><title>Synthetic profile storage</title>", encoding="utf-8")
            first = application.store.profiles()[0]
            second = application.store.create_profile("Second synthetic persona")

            async def stored_marker(profile, value=None):
                manager = await HeadlessBrowserManager.create(settings=get_settings(), profile_dir=application.store.profile_path(profile["id"]), ensure_bookmark=False, headless=True)
                try:
                    page = await get_browser_service(manager.browser).open_tab(fixture.as_uri())
                    if value:
                        await page.evaluate(f"localStorage.setItem('synthetic-marker', {json.dumps(value)})")
                    return await page.evaluate("localStorage.getItem('synthetic-marker')")
                finally:
                    await manager.stop()

            assert await stored_marker(first, "synthetic-value") == "synthetic-value"
            assert await stored_marker(second) is None
            assert await stored_marker(first) == "synthetic-value"
            print("Real profile persistence and isolation OK (synthetic local storage only)", flush=True)
        finally:
            running.cancel()
            await asyncio.gather(running, return_exceptions=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(asyncio.wait_for(smoke(), 90))
