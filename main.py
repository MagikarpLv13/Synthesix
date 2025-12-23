import asyncio
from pathlib import Path
from brave import BraveSearchEngine
from google import GoogleSearchEngine
from bing import BingSearchEngine
import pandas as pd
import time
from browser_manager import HeadlessBrowserManager
from scoring import calculate_relevance
import zendriver as uc
import os       
from utils import is_advanced_query, smart_parse, generate_html_report, add_to_history, generate_history_html

query = ""

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
                        const numResults = parseInt(document.getElementById("num-results").value, 10) || 20;
                        resolve({ action: "search", value, engines: { google, bing, brave }, numResults });
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
                print(f"Parsing query to a smart query: {original_query}")
                parsed_query = smart_parse(original_query)
                print(f"Smart query: {parsed_query}")
            else:
                parsed_query = original_query
                
            # Perform the search
            engines = result.get("engines", {"google": True, "bing": True, "brave": True})
            num_results = result.get("numResults", 20)
            await perform_search(original_query, parsed_query, browser, engines, num_results)

    finally:
        await browser.stop()
        print("Goodbye!")

async def perform_search(original_query: str, parsed_query: str, browser: uc.Browser, engines: dict, num_results: int):
    print(f"\nSearch in progress for: {parsed_query}")

    # Launch searches in parallel
    start_time = time.time()

    tasks = []
    if engines.get("google"):
        tasks.append(("google", asyncio.create_task(GoogleSearchEngine().search(parsed_query, browser, num_results))))
    if engines.get("bing"):
        tasks.append(("bing", asyncio.create_task(BingSearchEngine().search(parsed_query, browser, num_results))))
    if engines.get("brave"):
        tasks.append(("brave", asyncio.create_task(BraveSearchEngine().search(parsed_query, browser, num_results))))

    results = await asyncio.gather(*(t[1] for t in tasks))
    engine_results = {engine: result for (engine, _), result in zip(tasks, results)}

    google_df = engine_results.get("google", pd.DataFrame())
    bing_df = engine_results.get("bing", pd.DataFrame())
    brave_df = engine_results.get("brave", pd.DataFrame())

    total_time = time.time() - start_time

    # Global execution time
    print("\n=== Global execution time ===")
    print(f"Total: {total_time:.2f} seconds")

    # Merge results
    combined_df = pd.concat([google_df, bing_df, brave_df])

    # Calculate relevance scores
    combined_df['relevance_score'] = combined_df.apply(lambda x: calculate_relevance(x, parsed_query), axis=1)
    combined_df = combined_df.sort_values('relevance_score', ascending=False)

    # Group by link and aggregate sources and other fields
    combined_df = (
        combined_df.groupby("link")
        .agg(
            {
                "title": lambda x: x[combined_df.loc[x.index, 'relevance_score'].idxmax()],  # Keep title with highest relevance
                "description": lambda x: x[combined_df.loc[x.index, 'relevance_score'].idxmax()],  # Keep description with highest relevance 
                "source": lambda x: ", ".join(sorted(x.unique())),  # Combine sources
                "relevance_score": "max"  # Keep highest relevance score
            }
        )
        .reset_index()
    )

    # Generate report with relevant results
    relevant_results = combined_df[combined_df['relevance_score'] > 0]
    nb_results = len(relevant_results)
    output_path = generate_html_report(relevant_results, parsed_query, total_time, nb_results)
    if output_path:
        print(f"✅ Generated report: {output_path}")
        result_tab = await browser.main_tab.get(f"file://{output_path}", new_tab=True)
        add_to_history(original_query, parsed_query, nb_results, output_path)
        generate_history_html()
        await result_tab.bring_to_front()
    else:
        print("Can't generate report.")

if __name__ == "__main__":
    asyncio.run(main())
