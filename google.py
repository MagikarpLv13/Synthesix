import pandas as pd
import time
import bs4
from reliq import reliq
import json
import pyquery
from parsers import parse_with_xpath
from search_engine import SearchEngine

class GoogleSearchEngine(SearchEngine):
    def __init__(self):
        super().__init__(name="Google")
        self.base_url = "https://www.google.com"

    def construct_url(self) -> str:
        return f"{self.base_url}/search?q={self.query}&num={self.max_results}&start=0&filter=0&nfpr=1&udm=14&safe=off"

    def parse_results(self, raw_results):
        xpaths = self.get_xpaths()
        return parse_with_xpath(
            raw_results,
            result_xpath=xpaths['result'],
            title_xpath=xpaths['title'],
            link_xpath=xpaths['link'],
            desc_xpath=xpaths['desc'],
            source=self.name
        )

    def get_xpaths(self):
        return {
            'result': ".//div[@jscontroller][@data-ved][@data-hveid]",
            'title': ".//a[@href]//h3",
            'link': ".//a[@href]",
            'desc': ".//*[contains(@class, 'VwiC3b')]"
        }

    def set_selector(self):
        self.selector = "#search"

    async def robot_check(self):
        button = await self.tab.find("#captcha-form", timeout=0.1)
        if button:
            print("Robot detected by Google, need to solve captcha")
            await self.tab.activate()
            await self.wait_for_page_load(timeout=100)
            return True

        # If the button is not found, we can assume that we are not a robot 🤖
        return False

    def test(self):
        with open("test_google.html", "r") as file:
            raw_results = file.read()
        begin_time = time.time()
        res = self.parse_results(raw_results)
        print(res)
        end_time = time.time()
        print(f"Temps d'exécution pour le parsing avec lxml: {end_time - begin_time:.2f} secondes")
        begin_time = time.time()
        parse_with_pyquery(raw_results)
        end_time = time.time()
        print(f"Temps d'exécution pour le parsing avec pyquery: {end_time - begin_time:.2f} secondes")
        begin_time = time.time()
        parse_with_bs4(raw_results)
        end_time = time.time()
        print(f"Temps d'exécution pour le parsing avec bs4: {end_time - begin_time:.2f} secondes")
        begin_time = time.time()
        parse_with_reliq(raw_results)
        end_time = time.time()
        print(f"Temps d'exécution pour le parsing avec reliq: {end_time - begin_time:.2f} secondes")


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

            desc_div = result.find(attrs={"class": "VwiC3b"})
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

    print(f"Nombre de lignes: {len(res)}")
    return res

# @TODO à améliorer
def parse_with_reliq(raw_results: str):
    res = []
    rq = reliq(raw_results)

    rqexpr = reliq.expr(
        r"""
        .searches * #search; div jscontroller ; {
            .description [0] div .VwiC3b ; span | "%i",
            [0] a href; {
                .link @ | "%(href)v",
                .title [0] h3 | "%i"
            }
        }  |
    """
    )

    try:
        items = rq.search(rqexpr)
        #print(items)
        json_items = json.loads(items)
        searches = json_items["searches"]
    except Exception as e:
        print("Erreur lors du parsing du JSON:", e)
        return res

    for search in searches:
        title = search["title"]
        if title == "":
            continue
        link = search["link"]
        if link == "":
            continue
        description = search["description"]
        if description == "":
            continue

        res.append({
            "title": search.get("title", ""),
            "link": search.get("link", ""),
            "description": search.get("description", ""),
            "source": "Google"
        })
        
    return res

def parse_with_pyquery(raw_results):
    res = []

    doc = pyquery.PyQuery(raw_results)
    search_div = doc("div#search")

    if not search_div:
        return res

    results = search_div.find("div[jscontroller][data-ved][data-hveid]")

    for result in results.items():
        try:
            a_tag = result.find("a[href]").eq(0)
            if not a_tag:
                continue
            link = a_tag.attr("href")

            h3_tag = a_tag.find("h3").eq(0)
            if not h3_tag:
                continue
            title = h3_tag.text()

            desc_div = result.find("[data-snf][data-sncf]").eq(0)
            if not desc_div:
                continue
            description = desc_div.text()

            res.append({
                "title": title,
                "link": link,
                "description": description,
                "source": "Google"
            })

        except Exception as e:
            print("Erreur lors du parsing d'un résultat:", e)
            continue

    print(f"Nombre de lignes: {len(res)}")
    return res
