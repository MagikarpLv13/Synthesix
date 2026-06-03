import asyncio
from pathlib import Path
import logging
import json
import time
from brave import BraveSearchEngine
from google import GoogleSearchEngine
from bing import BingSearchEngine
from duckduckgo import DuckDuckGoSearchEngine
import pandas as pd
from browser_manager import HeadlessBrowserManager
from scoring import calculate_relevance
import zendriver as uc
from utils import (
    add_to_history,
    generate_history_html,
    generate_html_report,
    is_advanced_query,
    load_search_history,
    smart_parse,
)

logger = logging.getLogger(__name__)
HOME_POLL_INTERVAL = 0.25
EMPTY_TABS_GRACE_SECONDS = 2.0
DEFAULT_ENGINES = {"google": True, "bing": True, "brave": True, "duckduckgo": True}


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


async def _consume_home_tab_action(tab, history_json: str):
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
                window.synthesixHome.setHistory({history_json});
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


async def _focus_or_open_home_tab(browser: uc.Browser, index_url: str, home_tabs=None):
    if home_tabs is None:
        tabs = await _open_tabs(browser) or []
        home_tabs = [tab for tab in tabs if _is_home_tab(tab, index_url)]

    for home_tab in home_tabs:
        try:
            await home_tab.bring_to_front()
            return home_tab
        except Exception:
            logger.debug("Unable to focus existing home tab", exc_info=True)

    home_tab = await browser.get(index_url, new_tab=True)
    await home_tab.bring_to_front()
    return home_tab


async def wait_for_home_action(browser: uc.Browser, index_url: str):
    empty_since = None

    while True:
        if getattr(browser, "stopped", False):
            return {"action": "quit"}

        tabs = await _open_tabs(browser)
        if tabs is None:
            await asyncio.sleep(HOME_POLL_INTERVAL)
            continue

        if not tabs:
            if empty_since is None:
                empty_since = time.monotonic()
            elif time.monotonic() - empty_since >= EMPTY_TABS_GRACE_SECONDS:
                return {"action": "quit"}
            await asyncio.sleep(HOME_POLL_INTERVAL)
            continue

        empty_since = None

        home_tabs = [tab for tab in tabs if _is_home_tab(tab, index_url)]
        if home_tabs:
            history_json = json.dumps(load_search_history())
            for tab in home_tabs:
                state = await _consume_home_tab_action(tab, history_json)
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

        await asyncio.sleep(HOME_POLL_INTERVAL)

async def main():
    # Use a file:// URL so navigation works across platforms
    index_url = Path("index.html").resolve().as_uri()
    browser_manager = await HeadlessBrowserManager.create(home_url=index_url)
    browser = await browser_manager.get_driver()
    home_tab = await _focus_or_open_home_tab(browser, index_url)
    await home_tab.bring_to_front()

    try:
        while True:
            result = await wait_for_home_action(browser, index_url)

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
            engines = result.get("engines", DEFAULT_ENGINES)
            num_results = result.get("numResults", 20)
            await perform_search(original_query, parsed_query, browser, engines, num_results)

    finally:
        await browser_manager.stop()
        logger.info("Goodbye!")

async def perform_search(original_query: str, parsed_query: str, browser: uc.Browser, engines: dict, num_results: int):
    logger.info("Search in progress for: %s", parsed_query)

    # Launch searches in parallel
    start_time = time.monotonic()

    tasks = []
    if engines.get("google"):
        tasks.append(("google", asyncio.create_task(GoogleSearchEngine().search(parsed_query, browser, num_results))))
    if engines.get("bing"):
        tasks.append(("bing", asyncio.create_task(BingSearchEngine().search(parsed_query, browser, num_results))))
    if engines.get("brave"):
        tasks.append(("brave", asyncio.create_task(BraveSearchEngine().search(parsed_query, browser, num_results))))
    if engines.get("duckduckgo"):
        tasks.append(("duckduckgo", asyncio.create_task(DuckDuckGoSearchEngine().search(parsed_query, browser, num_results))))

    if not tasks:
        logger.warning("No search engine selected.")

    results = await asyncio.gather(*(t[1] for t in tasks), return_exceptions=True)
    engine_results = {}
    for (engine, _), result in zip(tasks, results):
        if isinstance(result, Exception):
            logger.error(
                "%s search failed",
                engine,
                exc_info=(type(result), result, result.__traceback__),
            )
            engine_results[engine] = pd.DataFrame()
        else:
            engine_results[engine] = result

    total_time = time.monotonic() - start_time

    # Global execution time
    logger.info("Global execution time: %.2f seconds", total_time)

    # Merge results
    required_columns = ["title", "link", "description", "source"]
    required_column_set = set(required_columns)
    frames = []
    for engine, df in engine_results.items():
        if not isinstance(df, pd.DataFrame):
            logger.warning("%s results ignored; expected DataFrame, got %s", engine, type(df).__name__)
            continue
        if df.empty:
            continue
        missing_columns = required_column_set - set(df.columns)
        if missing_columns:
            logger.warning("%s results ignored; missing columns: %s", engine, sorted(missing_columns))
            continue
        frames.append(df)

    if frames:
        combined_df = pd.concat(frames, ignore_index=True)
    else:
        combined_df = pd.DataFrame(columns=[*required_columns, "relevance_score"])

    # Calculate relevance scores
    if not combined_df.empty:
        combined_df["relevance_score"] = combined_df.apply(lambda x: calculate_relevance(x, parsed_query), axis=1)
        combined_df = combined_df.sort_values("relevance_score", ascending=False)

    # Group by link and aggregate sources and other fields
        best_idx = combined_df.groupby("link")["relevance_score"].idxmax()
        best_rows = combined_df.loc[best_idx, ["link", "title", "description", "relevance_score"]]
        sources = combined_df.groupby("link")["source"].apply(lambda x: ", ".join(sorted(x.astype(str).unique())))
        combined_df = (
            best_rows
            .merge(sources.rename("source"), on="link", how="left")
            .sort_values("relevance_score", ascending=False)
        )

    # Generate report with relevant results
    relevant_results = combined_df[combined_df['relevance_score'] > 0]
    nb_results = len(relevant_results)
    output_path = generate_html_report(relevant_results, parsed_query, total_time, nb_results)
    if output_path:
        logger.info("Generated report: %s", output_path)
        result_tab = await browser.get(Path(output_path).resolve().as_uri(), new_tab=True)
        add_to_history(original_query, parsed_query, nb_results, output_path)
        generate_history_html()
        await result_tab.bring_to_front()
    else:
        logger.error("Can't generate report.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    asyncio.run(main())
