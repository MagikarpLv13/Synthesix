from selenium import webdriver
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
    driver = webdriver.Chrome(options=options)

    # Accès à Google
    driver.get("https://www.google.com/search?q="+query+"&num="+str(num_results*1.5)+"&start=0&filter=0&nfpr=1&udm=14")
    time.sleep(1)

    # Attente des résultats
    wait = WebDriverWait(driver, 10)
    try:
        results = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "[jscontroller][style='width:inherit']")
            )
        )
    except:
        # Si ça échoue, on réessaie sans le mode headless (C'est qu'on est flag comme robot 🤖)
        driver.quit()
        # Configuration des options Chrome
        options = Options()
        options.add_argument(f"--user-data-dir={profile_path}")
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.google.com/search?q="+query+"&num="+str(num_results*1.5)+"&start=0&filter=0&nfpr=1&udm=14")
        time.sleep(1)
        wait = WebDriverWait(driver, 10)
        results = wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "[jscontroller][style='width:inherit']")
            )
        )

    # Extraction des résultats
    for result in results:
        try:
            title = result.find_element(By.CSS_SELECTOR, "h3").text
            description = result.find_element(By.CSS_SELECTOR, ".VwiC3b").text
            link = result.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            res.append({"title": title, "link": link, "description": description, "source": "Google"})
        except:
            continue

    driver.quit()

    df = pd.DataFrame(res)
    return df
