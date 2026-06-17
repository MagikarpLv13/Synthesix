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
        self.assertIn("Evidence", content)
        self.assertIn("2 capture(s)", content)
        self.assertIn("local-archive-result", content)
        self.assertIn("status-badge--confirmed", content)
        self.assertEqual(
            tree.xpath(
                "count(//*[contains(concat(' ', normalize-space(@class), ' '), "
                "' result-tag ')])"
            ),
            3.0,
        )
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
            tree = html.fromstring(output_path.read_text(encoding="utf-8"))

        self.assertEqual(
            tree.xpath("//a[contains(@class, 'result-title')]/@href"),
            ["#"],
        )

    def test_empty_report_uses_archive_empty_state(self):
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            output_path = base_dir / "history" / "local_search.html"
            generate_local_search_page(
                [],
                {},
                output_path,
                base_dir=base_dir,
                investigation_pages_dir=base_dir / "cases",
            )
            tree = html.fromstring(output_path.read_text(encoding="utf-8"))

        empty_states = tree.xpath("//*[contains(@class, 'local-search-empty')]")
        self.assertEqual(len(empty_states), 1)
        self.assertIn(
            "No stored observation matches these filters.",
            " ".join(empty_states[0].text_content().split()),
        )


if __name__ == "__main__":
    unittest.main()
