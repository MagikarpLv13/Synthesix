import asyncio
from brave import search_brave
from google import google_search
from bing import bing_search
import pandas as pd
import nodriver as uc
import time
from browser_manager import HeadlessBrowserManager

async def main():
    search_term = input("Entrez le terme à rechercher : ")
    execution_times = {}

    # Lancer les recherches en parallèle
    start_time = time.time()
    google_task = asyncio.create_task(google_search(search_term))
    #brave_task = asyncio.create_task(search_brave(search_term))
    #bing_task = asyncio.create_task(bing_search(search_term))

    google_df, = await asyncio.gather(google_task)
    total_time = time.time() - start_time

    # Afficher les temps d'exécution (ici, temps global)
    print("\n=== Temps d'exécution des recherches ===")
    print(f"Total: {total_time:.2f} secondes")

    # Fusionner les résultats
    combined_df = pd.concat([google_df])
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

    #combined_df['relevance_score'] = combined_df.apply(lambda x: calculate_relevance(x, search_term), axis=1)
    #combined_df = combined_df.sort_values('relevance_score', ascending=False)
#
    #for index, row in combined_df[combined_df['relevance_score'] > 0].iterrows():
    #    print(f"Titre: {row['title']}, Description: {row['description']}, Link: {row['link']} , Source: {row['source']}, Score de pertinence: {row['relevance_score']}")
    #    print("--------------------------------")

if __name__ == "__main__":
    asyncio.run(main())
