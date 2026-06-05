import asyncio
import argparse
from pathlib import Path
import logging
import json
import time
import sys
from browser_manager import HeadlessBrowserManager
from exceptions import SynthesixError
from search_orchestrator import SearchOrchestrator
from settings import AppSettings, get_settings
import zendriver as uc
from utils import (
    is_advanced_query,
    load_search_history,
    smart_parse,
)

logger = logging.getLogger(__name__)
_MISSING_HISTORY_SIGNATURE = object()


def _normalize_tab_url(url: str | None) -> str:
    return (url or "").split("#", 1)[0]


def _is_open_tab(tab) -> bool:
    return not getattr(tab, "closed", False)


async def _open_tabs(browser: uc.Browser):
    try:
        targets = await browser._get_targets()
        live_page_ids = {target.target_id for target in targets if target.type_ == "page"}
        await browser.update_targets()
    except Exception:
        logger.debug("Unable to update browser targets", exc_info=True)
        return None

    return [
        tab
        for tab in browser.tabs
        if _is_open_tab(tab) and getattr(tab, "target_id", None) in live_page_ids
    ]


def _is_home_tab(tab, index_url: str) -> bool:
    return _normalize_tab_url(getattr(tab, "url", None)) == index_url


async def _consume_home_tab_action(tab, history_json: str, history_version: str):
    history_version_json = json.dumps(history_version)
    try:
        return await tab.evaluate(
            f"""
            (() => {{
                if (
                    !window.synthesixHome ||
                    typeof window.synthesixHome.consumeAction !== "function"
                ) {{
                    return {{ ready: false, action: null }};
                }}
                window.name = "synthesix-home";
                const nextHistoryVersion = {history_version_json};
                if (window.synthesixHome.historyVersion !== nextHistoryVersion) {{
                    window.synthesixHome.setHistory({history_json});
                    window.synthesixHome.historyVersion = nextHistoryVersion;
                }}
                return {{
                    ready: true,
                    action: window.synthesixHome.consumeAction()
                }};
            }})()
            """,
        )
    except Exception:
        logger.debug("Unable to read home tab action", exc_info=True)
        return None


def _history_signature(settings: AppSettings):
    try:
        stat = settings.history_json_path.stat()
    except OSError:
        return None
    return stat.st_mtime_ns, stat.st_size


def _cached_history_payload(settings: AppSettings, cache: dict) -> tuple[str, str]:
    signature = _history_signature(settings)
    if cache.get("signature", _MISSING_HISTORY_SIGNATURE) != signature:
        cache["signature"] = signature
        cache["json"] = json.dumps(load_search_history(limit=settings.default_history_limit))
        cache["version"] = "" if signature is None else f"{signature[0]}:{signature[1]}"
    return cache["json"], cache["version"]


def parse_cli_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Start Synthesix browser-driven multi-engine search.",
    )
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "--quiet",
        action="store_true",
        help="Only show warnings and errors.",
    )
    verbosity.add_argument(
        "--verbose",
        action="store_true",
        help="Show debug logs.",
    )
    return parser.parse_args(argv)


def _log_level_from_args(args) -> int:
    if args.verbose:
        return logging.DEBUG
    if args.quiet:
        return logging.WARNING
    return logging.INFO


def configure_logging(args) -> None:
    logging.basicConfig(
        level=_log_level_from_args(args),
        format="%(levelname)s:%(name)s:%(message)s",
    )


def configure_event_loop_policy() -> None:
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def _consume_page_tab_action(tab):
    try:
        return await tab.evaluate(
            """
            (() => {
                if (
                    !window.synthesixPage ||
                    typeof window.synthesixPage.consumeAction !== "function"
                ) {
                    return null;
                }
                return window.synthesixPage.consumeAction();
            })()
            """,
        )
    except Exception:
        logger.debug("Unable to read page tab action", exc_info=True)
        return None


async def _focus_or_open_home_tab(
    browser: uc.Browser,
    index_url: str,
    home_tabs=None,
    reuse_current_tab: bool = False,
):
    if home_tabs is None:
        tabs = await _open_tabs(browser) or []
        home_tabs = [tab for tab in tabs if _is_home_tab(tab, index_url)]

    for home_tab in home_tabs:
        try:
            await home_tab.bring_to_front()
            return home_tab
        except Exception:
            logger.debug("Unable to focus existing home tab", exc_info=True)

    home_tab = await browser.get(index_url, new_tab=not reuse_current_tab)
    await home_tab.bring_to_front()
    return home_tab


async def wait_for_home_action(browser: uc.Browser, index_url: str, settings: AppSettings | None = None):
    settings = settings or get_settings()
    empty_since = None
    history_cache = {}

    while True:
        if getattr(browser, "stopped", False):
            return {"action": "quit"}

        tabs = await _open_tabs(browser)
        if tabs is None:
            await asyncio.sleep(settings.home_poll_interval)
            continue

        if not tabs:
            if empty_since is None:
                empty_since = time.monotonic()
            elif time.monotonic() - empty_since >= settings.empty_tabs_grace_seconds:
                return {"action": "quit"}
            await asyncio.sleep(settings.home_poll_interval)
            continue

        empty_since = None

        home_tabs = [tab for tab in tabs if _is_home_tab(tab, index_url)]
        if home_tabs:
            history_json, history_version = _cached_history_payload(settings, history_cache)
            for tab in home_tabs:
                state = await _consume_home_tab_action(tab, history_json, history_version)
                if state and state.get("action"):
                    return state["action"]

        for tab in tabs:
            if tab in home_tabs:
                continue
            action = await _consume_page_tab_action(tab)
            if not action:
                continue
            if action.get("action") == "focus_home":
                await _focus_or_open_home_tab(browser, index_url, home_tabs)
                break

        await asyncio.sleep(settings.home_poll_interval)

async def main():
    settings = get_settings()
    # Use a file:// URL so navigation works across platforms
    index_url = (settings.base_dir / "index.html").resolve().as_uri()
    browser_manager = await HeadlessBrowserManager.create(home_url=index_url, settings=settings)
    browser = await browser_manager.get_driver()
    home_tab = await _focus_or_open_home_tab(browser, index_url, reuse_current_tab=True)
    await home_tab.bring_to_front()

    try:
        while True:
            result = await wait_for_home_action(browser, index_url, settings=settings)

            # Quit the browser if the user wants to
            if result["action"] == "quit":
                return
            # Get the search value
            original_query = result["value"].strip()
            # If the search value is empty, quit the browser
            if not original_query:
                return
            # If the query is not advanced, parse it to a smart query
            if not is_advanced_query(original_query):
                logger.info("Parsing query to a smart query: %s", original_query)
                parsed_query = smart_parse(original_query)
                logger.info("Smart query: %s", parsed_query)
            else:
                parsed_query = original_query
                
            # Perform the search
            engines = result.get("engines", settings.default_engines)
            num_results = result.get("numResults", settings.default_max_results)
            await perform_search(original_query, parsed_query, browser, engines, num_results)

    finally:
        await browser_manager.stop()
        logger.info("Goodbye!")

async def perform_search(original_query: str, parsed_query: str, browser: uc.Browser, engines: dict, num_results: int):
    try:
        search_result = await SearchOrchestrator().search(
            original_query,
            parsed_query,
            browser,
            engines,
            num_results,
        )
    except SynthesixError:
        logger.error("Search failed.", exc_info=True)
        return

    if search_result.output_path:
        result_tab = await browser.get(Path(search_result.output_path).resolve().as_uri(), new_tab=True)
        await result_tab.bring_to_front()

if __name__ == "__main__":
    cli_args = parse_cli_args()
    configure_logging(cli_args)
    configure_event_loop_policy()
    asyncio.run(main())
