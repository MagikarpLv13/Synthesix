import pandas as pd
from lxml import html
import time
from parsers import parse_search_results

# Nombre maximum de résultats souhaités
MAX_RESULTS = 25
# Nombre de résultats trouvés
nb_results = 0

# Configuration de la recherche

async def bing_search(query, browser=None):
    start_time = time.time()
    global nb_results
    print(f"Starting Bing search")
    res = []
    if query == "test" and browser is None:
        test()
        return

    # Construction de l'URL Bing initiale
    base_url = f"https://www.bing.com"
    current_url = base_url + f"/search?q={query}"
    res = []

    tab = await browser.get(current_url, new_tab=True)
    await browser.wait(0.5)
    raw_results = await tab.get_content()

    # Write raw results to index.html for testing/debugging
    # with open("test_bing.html", "w", encoding="utf-8") as f:
    #     f.write(raw_results)

    res = parse_bing_results(raw_results)

    while nb_results < MAX_RESULTS:
        next_button = await tab.xpath(".//a[contains(@class, 'sb_pagN') and @href]")
        if next_button:
            current_url = base_url + next_button[0].get("href")
        else:
            break
        tab = await browser.get(current_url, new_tab=True)
        await browser.wait(0.5)
        raw_results = await tab.get_content()
        res.extend(parse_bing_results(raw_results))

    if tab is not None:
        await tab.close()
    else:
        print("Tab is None, impossible de fermer la tab.")

    df = pd.DataFrame(res)
    print(f"Nombre de résultats Bing: {len(df)}")
    print(f"Temps d'exécution Bing: {time.time() - start_time:.2f} secondes")
    return df

def parse_bing_results(raw_results):
    return parse_search_results(
            raw_results,
            "//li[contains(@class, 'b_algo')]",
            ".//h2",
            ".//a[@href]",
            ".//div[contains(@class, 'b_caption')]",
            "Bing",
        )

def test():
    with open("test_bing.html", "r") as file:
        raw_results = file.read()

    res = parse_bing_results(raw_results)
    print(res)
