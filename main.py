import asyncio
from brave import BraveSearchEngine
from google import GoogleSearchEngine
from bing import BingSearchEngine
import pandas as pd
import time
from browser_manager import HeadlessBrowserManager
from scoring import calculate_relevance
import zendriver as uc
import os       
from utils import is_advanced_query, smart_parse, generate_html_report

query = ""

async def main():
    browser_manager = await HeadlessBrowserManager.create()
    browser = await browser_manager.get_driver()
    index_path = os.path.abspath("index.html")
    await browser.main_tab.get(index_path)
    await browser.main_tab.bring_to_front()

    try:
        while True:
            # Wait for either the search or quit button to be clicked
            result = await browser.main_tab.evaluate(
                """
                new Promise(resolve => {
                    const searchBtn = document.querySelector("#search-button");
                    const quitBtn = document.querySelector("#quit-button");
                    const searchHandler = () => {
                        const value = document.querySelector("#search-field").value;
                        resolve({ action: "search", value });
                        cleanup();
                    };
                    const quitHandler = () => {
                        resolve({ action: "quit" });
                        cleanup();
                    };
                    function cleanup() {
                        document.querySelector("#search-field").value = "";
                        searchBtn.removeEventListener("click", searchHandler);
                        quitBtn.removeEventListener("click", quitHandler);
                    }
                    searchBtn.addEventListener("click", searchHandler, { once: true });
                    quitBtn.addEventListener("click", quitHandler, { once: true });
                });
                """,
                await_promise=True,
            )

            if result["action"] == "quit":
                print("Goodbye!")
                await browser_manager.quit()
                break
            search_value = result["value"].strip()
            if not search_value:
                print("Goodbye!")
                break

            # If the query is not advanced, parse it to a smart query
            if not is_advanced_query(search_value):
                query = search_value
                print(f"Parsing query to a smart query: {search_value}")
                search_term = smart_parse(search_value)
                print(f"Smart query: {search_term}")
            else:
                query = search_value
                search_term = search_value

            # Perform the search
            await perform_search(search_term, browser)

    finally:
        await browser_manager.quit()

async def perform_search(search_term: str, browser: uc.Browser):
    print(f"\nSearch in progress for: {search_term}")

    # Launch searches in parallel
    start_time = time.time()

    google_task = asyncio.create_task(GoogleSearchEngine().search(search_term, browser))
    bing_task = asyncio.create_task(BingSearchEngine().search(search_term, browser))
    brave_task = asyncio.create_task(BraveSearchEngine().search(search_term, browser))

    google_res = await asyncio.gather(google_task)
    bing_res = await asyncio.gather(bing_task)
    brave_res = await asyncio.gather(brave_task)
    total_time = time.time() - start_time

    google_df = google_res[0]
    bing_df = bing_res[0]
    brave_df = brave_res[0]

    # Global execution time
    print("\n=== Global execution time ===")
    print(f"Total: {total_time:.2f} seconds")

    # Merge results
    combined_df = pd.concat([google_df, bing_df, brave_df])

    # Calculate relevance scores
    combined_df['relevance_score'] = combined_df.apply(lambda x: calculate_relevance(x, search_term), axis=1)
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

    # Display top 5 results with a relevance score > 0
    relevant_results = combined_df[combined_df['relevance_score'] > 0].head(10)
    if len(relevant_results) > 0:
        #print(f"\nRelevant results ({len(relevant_results)}):")
        #for _, row in relevant_results.iterrows():
        #    print(f"Title: {row['title']}")
        #    print(f"Description: {row['description']}")
        #    print(f"Link: {row['link']}")
        #    print(f"Source: {row['source']}")
        #    print(f"Relevance score: {row['relevance_score']:.2f}")
        #    print("-" * 50)
        output_path = generate_html_report(relevant_results, search_term, total_time)
        if output_path:
            print(f"✅ Rapport généré : {output_path}")
            result_tab = await browser.main_tab.get(f"file://{output_path}", new_tab=True)
            await result_tab.bring_to_front()
        else:
            print("❌ Aucun résultat pertinent trouvé.")
    else:
        print("No relevant results found.")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
