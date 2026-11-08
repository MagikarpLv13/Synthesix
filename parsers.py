import re
import json
import logging
from html import unescape
from lxml import html

logger = logging.getLogger(__name__)


def parse_with_xpath(raw_results, result_xpath, title_xpath, link_xpath, desc_xpath, source):
    """
    Parse generic search results from HTML using provided XPaths.
    Args:
        raw_results (str): HTML content.
        result_xpath (str): XPath to select each result block.
        title_xpath (str): XPath (relative to result) to select the title node(s).
        link_xpath (str): XPath (relative to result) to select the link node(s).
        desc_xpath (str): XPath (relative to result) to select the description node(s).
        source (str): Name of the search engine/source.
    Returns:
        list of dict: Each dict contains title, link, description, source.
    """
    res = []
    tree = html.fromstring(raw_results)
    results = tree.xpath(result_xpath)
    for result in results:
        try:
            a_tag = result.xpath(link_xpath)
            if not a_tag:
                continue
            title_tag = result.xpath(title_xpath)
            if not title_tag:
                continue
            desc_tag = result.xpath(desc_xpath)
            if not desc_tag:
                continue
            link = a_tag[0].get("href", "").strip()
            if not link:
                continue
            title = title_tag[0].text_content().strip()
            if not title:
                continue
            description = desc_tag[0].text_content().strip().replace('\xa0', ' ')
            if not description:
                continue
            res.append({
                "title": title,
                "link": link,
                "description": description,
                "source": source
            })
        except Exception:
            logger.debug("Error parsing %s result block.", source, exc_info=True)
            continue  
    return res



def js_like_to_json(js_text):
    """Convert a JS like text to a JSON object

    Args:
        js_text (str): The JS like text to convert

    Returns:
        dict: The JSON object
    """

    # Replace void 0 by null
    js_text = js_text.replace("void 0", "null")

    js_text = re.sub(r"(^|\{|\[|,)\s*([a-zA-Z0-9_]+)\s*:", r'\1"\2":', js_text)

    # Remove the u003c strings
    js_text = js_text.replace("\\u003C", "<")
    js_text = js_text.replace("&quot;", "")
    js_text = unescape(js_text)

    # Remove the html tags
    js_text = re.sub(r"<[^>]+>", "", js_text)

    # Add [{ at the beginning and }] at the end
    js_text = "[{" + js_text + "}]"

    # Parse to JSON
    try:
        data = json.loads(js_text)
        return data
    except json.JSONDecodeError:
        logger.debug("Unable to parse JavaScript-like JSON payload.", exc_info=True)
        return None

