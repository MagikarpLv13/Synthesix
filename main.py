import asyncio
from brave import BraveSearchEngine
from google import GoogleSearchEngine
from bing import BingSearchEngine
import pandas as pd
import time
from browser_manager import HeadlessBrowserManager

async def main():
    
    browser_manager = await HeadlessBrowserManager.create()
    browser = await browser_manager.get_driver()
    await browser.main_tab.minimize()
    
    try:
        search_term = input("Entrez le terme à rechercher : ")

        # Lancer les recherches en parallèle
        start_time = time.time()
        google_task = asyncio.create_task(GoogleSearchEngine().search(search_term, browser))
        brave_task = asyncio.create_task(BraveSearchEngine().search(search_term, browser))
        bing_task = asyncio.create_task(BingSearchEngine().search(search_term, browser))

        google_res = await asyncio.gather(google_task)
        bing_res = await asyncio.gather(bing_task)
        brave_res = await asyncio.gather(brave_task)
        total_time = time.time() - start_time
        
        google_df = google_res[0]
        bing_df = bing_res[0]
        brave_df = brave_res[0]


        # Afficher les temps d'exécution (ici, temps global)
        print("\n=== Temps d'exécution des recherches ===")
        print(f"Total: {total_time:.2f} secondes")

        # Fusionner les résultats   
        combined_df = pd.concat([google_df, bing_df, brave_df])
        # Suppression des doublons de link
        combined_df = combined_df.drop_duplicates(subset='link', keep='first')

        # Calcul d'un score de pertinence en fonction du terme de recherche pour chaque résultat
        def calculate_relevance(row, search_term):
            # Séparer les termes par AND et OR uniquement
            terms = []
            score = 0
            import re
            parts = re.split(r'\s+(AND|OR)\s+', search_term, flags=re.IGNORECASE)
            for part in parts:
                if part.upper() not in ['AND', 'OR']:
                    clean_term = part.strip().strip('"')
                    if clean_term:
                        terms.append(clean_term)
            for term in terms:
                clean_term = term.replace('"', '')
                if clean_term.lower() in str(row['title']).lower():
                    score += 4.5
                if clean_term.lower() in str(row['description']).lower():
                    score += 4.5
                if ' ' in clean_term:
                    hyphenated_term = clean_term.replace(' ', '-')
                    if hyphenated_term.lower() in str(row['link']).lower():
                        score += 1
                    spaced_term = clean_term.replace(' ', '')
                    if spaced_term.lower() in str(row['link']).lower():
                        score += 1
                if clean_term.lower() in str(row['link']).lower():
                    score += 1
            return score

        combined_df['relevance_score'] = combined_df.apply(lambda x: calculate_relevance(x, search_term), axis=1)
        combined_df = combined_df.sort_values('relevance_score', ascending=False)

        for index, row in combined_df[combined_df['relevance_score'] > 0].iterrows():
            print(f"Titre: {row['title']}, Description: {row['description']}, Link: {row['link']} , Source: {row['source']}, Score de pertinence: {row['relevance_score']}")
            print("--------------------------------")
        
    finally:
        await browser_manager.quit()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
