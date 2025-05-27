from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Configuration du navigateur
options = Options()
options.add_argument("--headless")  # exécution sans ouvrir une fenêtre
driver = webdriver.Chrome(options=options)

# Configuration de la recherche

def bing_search(query):

    max_results = 25  # Nombre maximum de résultats souhaités
    results_count = 0

    # Construction de l'URL Bing initiale
    base_url = f"https://www.bing.com/search?q={query}"
    current_url = base_url
    res = []

    while results_count < max_results:
        # Accès à la page
        driver.get(current_url)
        time.sleep(2)

        # Attente explicite pour les résultats
        wait = WebDriverWait(driver, 10)
        try:
            results = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.b_algo")))
        except:
            results = []

        # Traitement des résultats de la page courante
        for result in results:
            if results_count >= max_results:
                break

            try:
                title_element = result.find_element(By.CSS_SELECTOR, "h2 a")
                title = title_element.text
                desc = result.find_element(By.CLASS_NAME, "b_caption").text
                url = title_element.get_attribute("href")
                res.append({"title":title, "link":url, "description":desc, "source":"Bing"})
                results_count += 1
            except:
                continue
            
        # Recherche du lien "Page suivante"
        try:
            next_button = driver.find_element(By.CLASS_NAME, "sb_pagN")
            if next_button and next_button.get_attribute("href"):
                current_url = next_button.get_attribute("href")
                time.sleep(2)  # Pause entre les pages pour éviter d'être bloqué
            else:
                break
        except:
            break

    driver.quit()
    df = pd.DataFrame(res)
    return df


def search(query):
    bing_search(query)