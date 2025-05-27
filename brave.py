import requests
import re
import json
from html import unescape
from user_agents import get_useragent
import pandas as pd


def js_like_to_json(js_text):

    # Remplace void 0 par null
    js_text = js_text.replace("void 0", "null")

    js_text = re.sub(r"(^|\{|\[|,)\s*([a-zA-Z0-9_]+)\s*:", r'\1"\2":', js_text)

    # Enlève les chaines u003c
    js_text = js_text.replace("\\u003C", "<")
    js_text = js_text.replace("&quot;", "")
    js_text = unescape(js_text)

    # Enlève les balises html
    js_text = re.sub(r"<[^>]+>", "", js_text)

    # Ajoute [{ au début et }] à la fin
    js_text = "[{" + js_text + "}]"

    # Parse en JSON
    try:
        data = json.loads(js_text)
        return data
    except Exception as e:
        print("Erreur de parsing JSON:", e)
        return None


def extract_results(html):

    pattern = r"results:\s*\[\{(.*?)\}\],bo"
    match = re.search(pattern, html, re.DOTALL)

    if match:
        return js_like_to_json(match.group(1))
    else:
        print("Bloc 'results' non trouvé.")
        return None


def search_brave(query):
    url = "https://search.brave.com/search"
    params = {"q": query, "spellcheck": 0}

    # Use fake user-agent to avoid bot detection
    headers = {"User-Agent": get_useragent()}

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        # Extract the first result from the HTML response
        html = response.text
        data = extract_results(html)

        if data:
            print(f"Nombre de résultats: {len(data)}")
            res = []
            for item in data:
                title = item.get("title", "Titre non trouvé")
                link = item.get("url", "Lien non trouvé")
                description = item.get("description", "Description non trouvée")
                res.append({"title": title, "link": link, "description": description, "source": "Brave"})

            df = pd.DataFrame(res)
            return df

    else:
        print(f"Erreur HTTP {response.status_code}")
        return []


def search(term):
    search_brave(term)
