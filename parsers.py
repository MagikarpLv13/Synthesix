from lxml import html

def parse_search_results(raw_results, result_xpath, title_xpath, link_xpath, desc_xpath, source):
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
        except Exception as e:
            print(f"Error parsing {source}: {e}")
            continue  
    return res 