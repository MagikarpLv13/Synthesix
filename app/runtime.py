"""Application lifecycle and the narrow command bridge for the local home page."""

from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Mapping

from app.profiles import ProfileLauncher, validate_web_url
from app.search import SearchBrowserProvider, SearchRequest
from app.storage import BrowserStore
from browser import eval_js, get_browser_service
from browser_manager import HeadlessBrowserManager, _resolve_browser_executable
from exceptions import SearchEngineError
from query_operators import build_display_query
from search_orchestrator import SearchOrchestrator
from settings import AppSettings

logger = logging.getLogger(__name__)


class BrowserApplication:
    def __init__(self, settings: AppSettings, store: BrowserStore | None = None) -> None:
        self.settings = settings
        assets = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
        self.home_url = (assets / "index.html").as_uri()
        self.store = store or BrowserStore(settings.base_dir / "data" / "browser.sqlite")
        self.search_browser = SearchBrowserProvider(settings)
        self.manager: HeadlessBrowserManager | None = None
        self.service = None
        self.home_tab = None
        self._home_handles: dict[str, object] = {}
        self.launcher: ProfileLauncher | None = None
        self.search_task: asyncio.Task | None = None
        self._cancel_requested = False
        self._publish_lock = asyncio.Lock()
        self.model: dict = {"connected": True, "running": False, "results": [], "coverage": [], "profiles": [], "history": [], "status": "Ready to search.", "isError": False}
        self.model["request"] = {"queries": [], "engines": getattr(settings, "default_engines", {name: True for name in ("google", "bing", "brave", "duckduckgo")}), "filters": {}, "numResults": getattr(settings, "default_max_results", 20), "automaticDorks": True}

    async def publish(self, **patch) -> None:
        async with self._publish_lock:
            self.model.update(patch)
            if self.home_tab is None:
                return
            ready = await eval_js(self.home_tab, f"""(() => {{
                if (location.href !== {json.dumps(self.home_url)} || !window.synthesixHome) return false;
                const ready = window.synthesixHome.heartbeat();
                {f'window.synthesixHome.setState({json.dumps(patch, ensure_ascii=True)});' if patch else ''}
                return ready;
            }})()""", category="browser_app_ui")
            if ready is False:
                await eval_js(self.home_tab, f"""(() => {{
                    if (location.href === {json.dumps(self.home_url)} && window.synthesixHome)
                        window.synthesixHome.setState({json.dumps(self.model, ensure_ascii=True)});
                }})()""", category="browser_app_hydrate")

    async def refresh_lists(self) -> None:
        profiles, history = await asyncio.gather(asyncio.to_thread(self.store.profiles), asyncio.to_thread(self.store.history))
        await self.publish(profiles=profiles, history=history)

    async def trusted_source(self, source) -> bool:
        if source is None or self.home_tab is None or getattr(source, "target_id", None) != self.home_tab.target_id:
            return False
        # Check the live document, not only Zendriver's cached target URL.
        return await eval_js(source, "location.href", category="browser_app_origin") == self.home_url

    async def select_home(self, tabs) -> None:
        live_ids = {tab.target_id for tab in tabs}
        self._home_handles = {key: tab for key, tab in self._home_handles.items() if key in live_ids}
        candidate = next((tab for tab in tabs if str(tab.url) == self.home_url), None)
        if candidate is None:
            self.home_tab = None
            return
        if candidate.target_id not in self._home_handles:
            await self.service.arm_dispatch_binding(candidate)
            self._home_handles[candidate.target_id] = candidate
        self.home_tab = self._home_handles[candidate.target_id]

    async def dispatch(self, action: Mapping, source) -> None:
        if not isinstance(action, Mapping) or not await self.trusted_source(source):
            return
        name = action.get("action")
        try:
            if name == "search":
                if self.search_task is not None and not self.search_task.done():
                    raise ValueError("A search is already running. Cancel it or wait for it to finish.")
                request = SearchRequest.from_payload(action)
                self._cancel_requested = False
                await self.publish(running=True, results=[], coverage=[], request=request.to_payload(), status="Searching selected engines...", isError=False)
                self.search_task = asyncio.create_task(self.run_search(request))
            elif name == "cancel_search":
                if self.search_task is not None and not self.search_task.done() and not self._cancel_requested:
                    self._cancel_requested = True
                    self.search_task.cancel()
            elif name == "create_profile":
                await asyncio.to_thread(self.store.create_profile, action.get("name"))
                await self.publish(status="Browser profile created.", isError=False)
                await self.refresh_lists()
            elif name == "rename_profile":
                await asyncio.to_thread(self.store.rename_profile, action.get("profileId"), action.get("name"))
                await self.publish(status="Browser profile renamed.", isError=False)
                await self.refresh_lists()
            elif name in {"open_profile", "open_result"}:
                profile_id = action.get("profileId", "")
                url = validate_web_url(action.get("url")) if name == "open_result" else None
                if profile_id:
                    if self.launcher is None:
                        raise ValueError("Browser executable not found.")
                    await asyncio.to_thread(self.launcher.open, profile_id, url)
                elif url:
                    await self.service.open_tab(url)
                else:
                    raise ValueError("Unknown browser profile.")
                await self.publish(status="Browser opened.", isError=False)
            elif name == "load_search":
                if self.search_task is not None and not self.search_task.done():
                    raise ValueError("A search is already running. Cancel it or wait for it to finish.")
                saved = await asyncio.to_thread(self.store.search, action.get("id"))
                await self.publish(request=saved["request"], results=saved["results"], coverage=saved["coverage"], status="Saved search restored.", isError=False)
        except ValueError as exc:
            await self.publish(status=str(exc), isError=True)
        except Exception:
            logger.exception("Browser application action failed: %s", name)
            await self.publish(status="Action failed. Check the logs for details.", isError=True)

    async def run_search(self, request: SearchRequest) -> None:
        errors: dict[str, str] = {}

        async def progress(rows, coverage):
            await self.publish(results=list(rows), coverage=list(coverage))

        try:
            browser = await self.search_browser.get_browser()
            result = await SearchOrchestrator(settings=self.settings).collect(
                "\n".join(request.original_queries),
                build_display_query(request.queries[0], request.filters),
                browser, request.engines, request.num_results,
                filters=request.filters, base_query=request.queries[0],
                query_variants=request.queries, on_progress=progress,
            )
            errors = {key: type(error).__name__ for key, error in result.engine_errors.items()}
            await self.publish(results=list(result.results), coverage=list(result.coverage), status="Some engines could not finish. Available results are shown." if errors else "Search completed.", isError=bool(errors))
        except asyncio.CancelledError:
            errors = {"search": "cancelled"}
            await self.publish(status="Search cancelled.", isError=False)
            raise
        except Exception as exc:
            logger.exception("Search failed.")
            errors = {key: type(error).__name__ for key, error in exc.engine_errors.items()} if isinstance(exc, SearchEngineError) and exc.engine_errors else {"search": type(exc).__name__}
            await self.publish(status="Search failed. Check engine coverage and retry.", isError=True)
        finally:
            try:
                await asyncio.to_thread(self.store.save_search, request.to_payload(), self.model["results"], self.model["coverage"], errors)
                await self.refresh_lists()
            except Exception:
                logger.exception("Unable to save search history.")
                await self.publish(status="Results are available, but search history could not be saved.", isError=True)
            await self.publish(running=False)

    async def run(self, *, headless: bool = False) -> None:
        try:
            self.manager = await HeadlessBrowserManager.create(
                home_url=self.home_url, settings=self.settings,
                profile_dir=self.settings.base_dir / "data" / "browser-ui-profile",
                headless=headless,
            )
            browser = self.manager.browser
            self.service = get_browser_service(browser)
            home_tab = await self.service.open_tab(self.home_url)
            # Zendriver lazily prepares a target connection. Finish its first
            # CDP exchange before progress updates or other readers can use it.
            await self.service.arm_dispatch_binding(home_tab)
            self._home_handles[home_tab.target_id] = home_tab
            self.home_tab = home_tab
            await self.service.close_blank_tabs()
            executable = _resolve_browser_executable(self.settings)
            if executable is None:
                executable = Path(browser.config.browser_executable_path)
            self.launcher = ProfileLauncher(self.store, executable)
            await self.refresh_lists()
            last_sync = 0.0
            while True:
                tabs = await self.service.tabs()
                if tabs is None or not tabs:
                    break
                await self.select_home(tabs)
                if self.home_tab is not None:
                    await self.service.arm_dispatch_binding(self.home_tab)
                    if time.monotonic() - last_sync >= 2:
                        await self.publish()
                        action = await eval_js(self.home_tab, "window.synthesixHome?.consumeAction()", category="browser_app_fallback")
                        if action:
                            await self.dispatch(action, self.home_tab)
                        last_sync = time.monotonic()
                try:
                    action = await asyncio.wait_for(self.service.dispatch_queue.get(), timeout=0.5)
                except asyncio.TimeoutError:
                    continue
                await self.dispatch(action, action.get("_source_tab"))
        finally:
            if self.search_task is not None and not self.search_task.done():
                self.search_task.cancel()
                await asyncio.gather(self.search_task, return_exceptions=True)
            await self.search_browser.stop()
            if self.manager is not None:
                await self.manager.stop()
