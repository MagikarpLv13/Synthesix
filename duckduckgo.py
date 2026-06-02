from urllib.parse import parse_qs, quote_plus, urljoin, urlparse

from lxml import html

from search_engine import SearchEngine


class DuckDuckGoSearchEngine(SearchEngine):
    def __init__(self):
        super().__init__(name="DuckDuckGo")
        self.base_url = "https://noai.duckduckgo.com/html/"

    def construct_url(self) -> str:
        params = {
            "q": quote_plus(self.query),
            "kp": "-2",  # Safe Search off
            "kz": "-1",  # Instant Answers off
            "kac": "-1",  # Auto-suggest off
            "k1": "-1",  # Ads off
            "kl": "wt-wt",  # No region
        }
        query_string = "&".join(f"{key}={value}" for key, value in params.items())
        return f"{self.base_url}?{query_string}"

    def parse_results(self, raw_results):
        tree = html.fromstring(raw_results)
        results = []
        seen_links = set()

        result_xpath = (
            "//div[contains(@class, 'result__body')]"
            " | "
            "//div[contains(@class, 'web-result') and not(.//div[contains(@class, 'result__body')])]"
        )
        for result in tree.xpath(result_xpath):
            parsed = self._parse_result_block(result)
            if parsed and parsed["link"] not in seen_links:
                results.append(parsed)
                seen_links.add(parsed["link"])
            if len(results) >= self.max_results:
                return results

        for result in tree.xpath("//tr[.//a[contains(@class, 'result-link')]]"):
            parsed = self._parse_lite_result_row(result)
            if parsed and parsed["link"] not in seen_links:
                results.append(parsed)
                seen_links.add(parsed["link"])
            if len(results) >= self.max_results:
                return results

        return results

    def _parse_result_block(self, result):
        link_nodes = result.xpath(".//a[contains(@class, 'result__a') and @href]")
        if not link_nodes:
            return None

        link_node = link_nodes[0]
        title = link_node.text_content().strip()
        link = self._clean_duckduckgo_url(link_node.get("href", ""))

        desc_nodes = result.xpath(".//*[contains(@class, 'result__snippet')]")
        description = desc_nodes[0].text_content().strip() if desc_nodes else ""

        return self._build_result(title, link, description)

    def _parse_lite_result_row(self, result):
        link_nodes = result.xpath(".//a[contains(@class, 'result-link') and @href]")
        if not link_nodes:
            return None

        link_node = link_nodes[0]
        title = link_node.text_content().strip()
        link = self._clean_duckduckgo_url(link_node.get("href", ""))

        desc_nodes = result.xpath("./following-sibling::tr[1]//*[contains(@class, 'result-snippet')]")
        description = desc_nodes[0].text_content().strip() if desc_nodes else ""

        return self._build_result(title, link, description)

    def _build_result(self, title: str, link: str, description: str):
        if not title or not link:
            return None
        return {
            "title": title,
            "link": link,
            "description": description,
            "source": self.name,
        }

    def _clean_duckduckgo_url(self, link: str) -> str:
        if not link:
            return ""

        absolute_link = urljoin("https://duckduckgo.com", link)
        parsed = urlparse(absolute_link)
        query = parse_qs(parsed.query)
        redirected = query.get("uddg")
        if redirected:
            return redirected[0]
        return absolute_link

    def set_selector(self):
        self.selector = ".result__body, .web-result, .result-link, #links"

    def test(self):
        return None
