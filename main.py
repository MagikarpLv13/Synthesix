import asyncio
from brave import BraveSearchEngine
from google import GoogleSearchEngine
from bing import BingSearchEngine
import pandas as pd
import time
from browser_manager import HeadlessBrowserManager
from scoring import calculate_relevance
import nodriver as uc

async def main():
    browser_manager = await HeadlessBrowserManager.create()
    browser = await browser_manager.get_driver()
    await browser.main_tab.minimize()
    
    try:
        while True:
            # Ask for the search term
            search_term = input("\nEnter the search term (or 'quit' to quit): ")
            
            if search_term.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not search_term.strip():
                print("Please enter a valid search term.")
                continue
            
            # Perform the search
            await perform_search(search_term, browser)
            
            # Ask if the user wants to continue
            continue_search = input("\nDo you want to make another search? (y/n): ")
            if continue_search.lower() not in ['y', 'yes']:
                print("Goodbye!")
                break
                
    finally:
        browser_manager.quit()
        
async def perform_search(search_term: str, browser: uc.Browser):
    print(f"\nSearch in progress for: '{search_term}'")
    
    # Launch searches in parallel
    start_time = time.time()
    
    google_task = asyncio.create_task(GoogleSearchEngine().search(search_term, browser))
    brave_task = asyncio.create_task(BraveSearchEngine().search(search_term, browser))
    bing_task = asyncio.create_task(BingSearchEngine().search(search_term, browser))
    
    google_res = await asyncio.gather(google_task)
    bing_res = await asyncio.gather(bing_task)
    brave_res = await asyncio.gather(brave_task)
    total_time = time.time() - start_time
    
    # Minimize the browser
    await browser.main_tab.minimize()
    
    google_df = google_res[0]
    bing_df = bing_res[0]
    brave_df = brave_res[0]
    
    # Global execution time
    print("\n=== Global execution time ===")
    print(f"Total: {total_time:.2f} seconds")
    
    # Merge results
    combined_df = pd.concat([google_df, bing_df, brave_df])
    
    # Remove duplicates of link
    combined_df = combined_df.drop_duplicates(subset='link', keep='first')

    # Calculate relevance scores
    combined_df['relevance_score'] = combined_df.apply(lambda x: calculate_relevance(x, search_term), axis=1)
    combined_df = combined_df.sort_values('relevance_score', ascending=False)

    # Display top 5 results with a relevance score > 0
    relevant_results = combined_df[combined_df['relevance_score'] > 0].head(5)
    if len(relevant_results) > 0:
        print(f"\nRelevant results ({len(relevant_results)}):")
        for index, row in relevant_results.iterrows():
            print(f"Title: {row['title']}")
            print(f"Description: {row['description']}")
            print(f"Link: {row['link']}")
            print(f"Source: {row['source']}")
            print(f"Relevance score: {row['relevance_score']:.2f}")
            print("-" * 50)
    else:
        print("No relevant results found.")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
