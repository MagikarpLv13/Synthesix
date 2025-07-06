from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import pandas as pd


def google_search(query, num_results=25):
    """
    Perform a Google search and return the titles, descirptions and links of the results.

    Args:
        query (str): The search query.
        num_results (int): The number of results to return.

    Returns:
        dataframe: A pandas DataFrame containing the titles, descriptions, and links of the search results.
    """

    res = []

    # Créer un chemin fixe pour le profil utilisateur Selenium
    profile_path = os.path.join(os.getcwd(), "selenium-profile")
    os.makedirs(profile_path, exist_ok=True)

    # Configuration des options Chrome
    options = Options()
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--headless")

    # Démarrage du navigateur
    driver = uc.Chrome(options=options)

    # Accès à Google
    driver.get("https://www.google.com/search?q="+query+"&num="+str(num_results*1.5)+"&start=0&filter=0&nfpr=1&udm=14")
    time.sleep(1)

    # Attente des résultats
    wait = WebDriverWait(driver, 10)
    try:
        results = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "[jscontroller][data-ved]")
            )
        )
    except:
        # Si ça échoue, on réessaie sans le mode headless (C'est qu'on est flag comme robot 🤖)
        driver.quit()
        # Configuration des options Chrome
        options = Options()
        options.add_argument(f"--user-data-dir={profile_path}")
        driver = uc.Chrome(options=options)
        driver.get("https://www.google.com/search?q="+query+"&num="+str(num_results*1.5)+"&start=0&filter=0&nfpr=1&udm=14")
        time.sleep(1)
        wait = WebDriverWait(driver, 600)
        results = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "[jscontroller][data-ved]")
            )
        )

    # Extraction des résultats
    for result in results:
        try:
            # Cherche le lien qui contient un <h3> (le titre)
            try:
                h3_tag = result.find_element(By.CSS_SELECTOR, "h3")
            except Exception as e:
                continue

            a_tag = h3_tag.find_element(By.XPATH, "./ancestor::a")
            link = a_tag.get_attribute("href")
            title = h3_tag.text

            # Cherche la description : premier div descendant
            description = ""
            desc_divs = result.find_elements(By.CSS_SELECTOR, "[data-snf] span")
            if desc_divs:
                description = desc_divs[0].text

            res.append({"title": title, "link": link, "description": description, "source": "Google"})
        except Exception as e:
            print("Erreur lors du parsing d'un résultat:", e)
            continue

    driver.quit()

    df = pd.DataFrame(res)
    return df
