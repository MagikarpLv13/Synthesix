import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from lxml import html

from investigations.search_view import generate_local_search_page


class LocalSearchViewTestCase(unittest.TestCase):
    def test_generates_offline_report_with_investigation_link(self):
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            output_path = base_dir / "history" / "local_search.html"
            investigation_pages_dir = base_dir / "data" / "investigation_pages"

            generated = generate_local_search_page(
                [
                    {
                        "result_id": "result-1",
                        "investigation_id": "case-1",
                        "investigation_title": "Case <One>",
                        "title": "<script>Registry</script>",
                        "description": "Stored description",
                        "url": "https://example.com/registry",
                        "notes": "Verified locally",
                        "tags": ["registry"],
                        "sources": ["Google", "Bing"],
                        "analyst_status": "confirme",
                        "first_observed_at": "2026-06-09T10:00:00+00:00",
                        "last_observed_at": "2026-06-10T10:00:00+00:00",
                        "is_saved": True,
                        "evidence_count": 2,
                    }
                ],
                {
                    "query": "registry",
                    "investigation_title": "Case <One>",
                },
                output_path,
                base_dir=base_dir,
                investigation_pages_dir=investigation_pages_dir,
            )
            content = output_path.read_text(encoding="utf-8")
            tree = html.fromstring(content)

        self.assertEqual(generated, str(output_path))
        self.assertIn('src="../i18n.js"', content)
        self.assertIn(
            "No external search engine was contacted",
            " ".join(tree.text_content().split()),
        )
        self.assertIn("Already observed", content)
        self.assertIn("2 evidence capture(s)", content)
        self.assertIn("&lt;script&gt;Registry&lt;/script&gt;", content)
        self.assertNotIn("<script>Registry</script>", content)
        self.assertEqual(
            tree.xpath(
                "//a[contains(@href, 'case-1.html#result-result-1')]/text()"
            )[0],
            "Case <One>",
        )

    def test_rejects_non_http_result_links(self):
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            output_path = base_dir / "history" / "local_search.html"
            generate_local_search_page(
                [
                    {
                        "result_id": "result-1",
                        "title": "Unsafe",
                        "url": "javascript:alert(1)",
                    }
                ],
                {},
                output_path,
                base_dir=base_dir,
                investigation_pages_dir=base_dir / "cases",
            )
            content = output_path.read_text(encoding="utf-8")
            tree = html.fromstring(content)

        # the unsafe scheme is never rendered as a clickable link
        self.assertNotIn("javascript:", content)
        self.assertEqual(tree.xpath("//a[@data-triage-link]"), [])
        self.assertIn("Unsafe", content)


if __name__ == "__main__":
    unittest.main()
