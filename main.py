import asyncio
from pathlib import Path
import logging
from brave import BraveSearchEngine
from google import GoogleSearchEngine
from bing import BingSearchEngine
from duckduckgo import DuckDuckGoSearchEngine
import pandas as pd
import time
from browser_manager import HeadlessBrowserManager
from scoring import calculate_relevance
import zendriver as uc
from utils import is_advanced_query, smart_parse, generate_html_report, add_to_history, generate_history_html

logger = logging.getLogger(__name__)

async def main():
    browser_manager = await HeadlessBrowserManager.create()
    browser = await browser_manager.get_driver()
    # Use a file:// URL so navigation works across platforms
    index_url = Path("index.html").resolve().as_uri()
    await browser.main_tab.get(index_url)
    await browser.main_tab.bring_to_front()

    try:
        while True:
            # Wait for either the search or quit button to be clicked
            result = await browser.main_tab.evaluate(
                """
                new Promise(resolve => {
                    const searchBtn = document.querySelector("#search-button");
                    const searchField = document.querySelector("#search-field");
                    
                    const searchHandler = () => {
                        const value = searchField.value.trim();
                        if (!value) {
                            alert("Please enter a search term.");
                            return;
                        }
                        const google = document.getElementById("engine-google").checked;
                        const bing = document.getElementById("engine-bing").checked;
                        const brave = document.getElementById("engine-brave").checked;
                        const duckduckgo = document.getElementById("engine-duckduckgo").checked;
                        const numResults = parseInt(document.getElementById("num-results").value, 10) || 20;
                        resolve({ action: "search", value, engines: { google, bing, brave, duckduckgo }, numResults });
                        cleanup();
                    };
                    
                    const quitHandler = () => {
                        resolve({ action: "quit" });
                        cleanup();
                    };
                    
                    const enterHandler = (e) => {
                        if (e.key === "Enter") {
                            searchHandler();
                        }
                    };

                    function cleanup() {
                        searchField.value = "";
                        searchBtn.removeEventListener("click", searchHandler);
                        searchField.removeEventListener("keypress", enterHandler);
                        window.removeEventListener("beforeunload", quitHandler);
                    }
                    
                    searchBtn.addEventListener("click", searchHandler, { once: true });
                    searchField.addEventListener("keypress", enterHandler);
                    window.addEventListener("beforeunload", quitHandler);
                });

                """,
                await_promise=True,
            )

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
            engines = result.get("engines", {"google": True, "bing": True, "brave": True, "duckduckgo": True})
            num_results = result.get("numResults", 20)
            await perform_search(original_query, parsed_query, browser, engines, num_results)

    finally:
        await browser.stop()
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
        result_tab = await browser.main_tab.get(Path(output_path).resolve().as_uri(), new_tab=True)
        add_to_history(original_query, parsed_query, nb_results, output_path)
        generate_history_html()
        await result_tab.bring_to_front()
    else:
        logger.error("Can't generate report.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    asyncio.run(main())
