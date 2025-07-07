import nodriver as uc
import os
import pandas as pd
from nodriver import Config
import time
import bs4
from reliq import reliq
from lxml import html
import json

async def google_search(query, num_results=25):
    """
    Perform a Google search and return the titles, descirptions and links of the results.

    Args:
        query (str): The search query.
        num_results (int): The number of results to return.

    Returns:
        dataframe: A pandas DataFrame containing the titles, descriptions, and links of the search results.
    """

    res = []

    custom_profile = os.path.join(os.getcwd(), "selenium-profile")
    os.makedirs(custom_profile, exist_ok=True)

    config = Config()
    config.headless = True
    config.user_data_dir=custom_profile

    # Démarrage du navigateur
    driver = await uc.start(config=config)

    url = "https://www.google.com/search?q="+query+"&num="+str(num_results)+"&start=0&filter=0&nfpr=1&udm=14"

    print(f"url: {url}")

    # Accès à la recherche
    tab = await driver.get(url)
    await driver.wait(0.33)
    raw_results = await tab.get_content()
    start_time = time.time()
    
    res = parse_with_reliq(raw_results)
    end_time = time.time()
    
    print(f"Temps d'exécution pour l'extraction des résultats: {end_time - start_time:.2f} secondes")

    if driver is not None:
        driver.stop()
    else:
        print("Driver is None, impossible d'arrêter le navigateur proprement.")

    df = pd.DataFrame(res)
    print(f"Nombre de lignes: {len(df)}")
    return df


def parse_with_lxml(raw_results):
    res = []
    tree = html.fromstring(raw_results)
    search_div = tree.xpath("//div[@id='search']")
    if not search_div:
        results = []
    else:
        results = search_div[0].xpath(".//div[@jscontroller][@data-ved][@data-hveid]")

    for result in results:
        try:
            a_tag = (
                result.xpath(".//a[@href]")[0] if result.xpath(".//a[@href]") else None
            )
            if a_tag is None:
                continue
            link = a_tag.get("href")

            h3_tag = a_tag.xpath(".//h3")[0] if a_tag.xpath(".//h3") else None
            if h3_tag is None:
                continue
            title = h3_tag.text_content().strip()

            desc_div = (
                result.xpath(".//*[@data-snf][@data-sncf]")[0]
                if result.xpath(".//*[@data-snf][@data-sncf]")
                else None
            )
            if desc_div is None:
                continue
            description = desc_div.text_content().strip()

            res.append(
                {
                    "title": title,
                    "link": link,
                    "description": description,
                    "source": "Google",
                }
            )

        except Exception as e:
            print("Erreur lors du parsing d'un résultat:", e)
            continue
    return res

def parse_with_bs4(raw_results):
    res = []
    soup = bs4.BeautifulSoup(raw_results, "html.parser")
    search_div = soup.find("div", id="search")
    if not search_div:
        results = []
    else:
        results = search_div.find_all(lambda tag: (
            tag.has_attr("jscontroller") and
            tag.has_attr("data-ved") and
            tag.has_attr("data-hveid")
        ))

    for result in results:
        try:
            a_tag = result.find("a", href=True)
            if not a_tag:
                continue
            link = a_tag["href"]

            h3_tag = a_tag.find("h3")
            if not h3_tag:
                continue
            title = h3_tag.get_text(strip=True)

            desc_div = result.find(attrs={"data-snf": True, "data-sncf": True})
            if not desc_div:
                continue
            description = desc_div.get_text(strip=True)

            res.append({
                "title": title,
                "link": link,
                "description": description,
                "source": "Google"
            })

        except Exception as e:
            print("Erreur lors du parsing d'un résultat:", e)
            continue

    return res

def parse_with_reliq(raw_results: str):
    res = []
    rq = reliq(raw_results)
    rel_expr = reliq.expr(r"""
        div .id=search; {
            div[jscontroller][data-ved][data-hveid]; {
            
            }
        }
    """)
    items = rq.search(rel_expr)
    print(len(items))
    for item in items:
        try:
            data = json.loads(item)
            res.append({
                "title": data.get("title", ""),
                "link": data.get("link", ""),
                "description": data.get("desc", ""),
                "source": "Google"
            })
        except Exception as e:
            print("Erreur lors du parsing reliq:", e)
            continue
    return res


# TODO: faire un parse avec Reliq-Python
# TODO: faire un parse avec PyQuery
# TODO: faire un parse avec nodriver
