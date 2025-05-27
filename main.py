from brave import search_brave
from google import google_search
from bing import bing_search
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

# Demander à l'utilisateur le terme à rechercher
search_term = input("Entrez le terme à rechercher : ")


with ThreadPoolExecutor(max_workers=3) as executor:
    google_future = executor.submit(google_search, search_term)
    brave_future = executor.submit(search_brave, search_term)
    bing_future = executor.submit(bing_search, search_term)
    
    google_df = google_future.result()
    brave_df = brave_future.result() 
    bing_df = bing_future.result()


combined_df = pd.concat([google_df, brave_df, bing_df])

# Suppression des doublons de link
combined_df = combined_df.drop_duplicates(subset='link', keep='first')

# Calcul d'un score de pertinence en fonction du terme de recherche pour chaque résultat
# Fonction pour calculer le score de pertinence
def calculate_relevance(row, search_term):
    
    # Séparer les termes qui sont entre guillemets
    terms = []
    current_term = ""
    in_quotes = False
    score = 0
    
    for char in search_term:
        if char == '"':
            in_quotes = not in_quotes
            if not in_quotes and current_term:
                terms.append(current_term.strip())
                current_term = ""
        elif char == ' ' and not in_quotes:
            if current_term:
                terms.append(current_term.strip())
            current_term = ""
        else:
            current_term += char
            
    if current_term:
        terms.append(current_term.strip())
        
    # Filtrer les mots vides comme 'AND', 'OR'
    terms = [term for term in terms if term.upper() not in ['AND', 'OR']]

    
    for term in terms:
    
        # Retire les guillemets du terme de recherche
        clean_term = term.replace('"', '')

        # Vérifie la présence dans le titre (plus important)
        if clean_term.lower() in str(row['title']).lower():
            score += 4.5

        # Vérifie la présence dans la description
        if clean_term.lower() in str(row['description']).lower():
            score += 4.5

        # Vérifie la présence dans l'URL
        # Pour les termes avec espaces, vérifier avec différents séparateurs
        if ' ' in clean_term:
            # Vérifier avec tiret
            hyphenated_term = clean_term.replace(' ', '-')
            if hyphenated_term.lower() in str(row['link']).lower():
                score += 1

            # Vérifier sans espace
            spaced_term = clean_term.replace(' ', '')
            if spaced_term.lower() in str(row['link']).lower():
                score += 1

        if clean_term.lower() in str(row['link']).lower():
            score += 1

    return score

# Calcule le score pour chaque ligne
combined_df['relevance_score'] = combined_df.apply(lambda x: calculate_relevance(x, search_term), axis=1)

# Trie les résultats par score de pertinence décroissant
combined_df = combined_df.sort_values('relevance_score', ascending=False)

# Affiche les résultats, titre, link,source et score de pertinence
for index, row in combined_df.iterrows():
    print(f"Link: {row['link']}, Score de pertinence: {row['relevance_score']}")
    print("--------------------------------")
