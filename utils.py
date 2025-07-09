import re
import json
from html import unescape

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
