import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from lxml import html

from investigations.view import generate_investigation_page


def workspace_payload(*, status="active"):
    return {
        "investigation": {
            "id": "case-123",
            "title": 'Case <Alpha> "test"',
            "reference": "REF-001",
            "description": "Investigation description",
            "tags": ["priority"],
            "status": status,
        },
        "results": [
            {
                "id": "result-123",
                "canonical_url": "https://example.com/page",
                "url": 'https://example.com/?q=<script>',
                "title": "<script>alert(1)</script>",
                "description": "Registry entry",
                "sources": ["Google", "Bing"],
                "first_observed_at": "2026-06-09T10:00:00+00:00",
                "last_observed_at": "2026-06-09T11:00:00+00:00",
                "latest_observed_at": "2026-06-09T11:00:00+00:00",
                "relevance_score": 8.5,
                "score_breakdown": [
                    {
                        "key": "exact_title",
                        "label": "Exact query term in title",
                        "score": 4.5,
                    },
                    {
                        "key": "engine_consensus",
                        "label": "Returned by 2 search engines",
                        "score": 1.0,
                    },
                ],
                "observation_count": 2,
                "analyst_status": "pertinent",
                "favorite": True,
                "notes": "Needs <verification>",
                "tags": ["registry"],
                "added_at": "2026-06-09T10:00:00+00:00",
                "updated_at": "2026-06-09T11:00:00+00:00",
                "discovery_method": "search_result",
                "discovery_query": "example company",
                "discovery_sources": ["Google", "Bing"],
                "discovery_report_path": "history/report.html",
                "discovery_observed_at": "2026-06-09T10:00:00+00:00",
                "discovery_referrer": "",
            }
        ],
        "searches": [
            {
                "id": "search-123",
                "original_query": "example company",
                "parsed_query": '"example company"',
                "filters": {},
                "engines": {"google": True, "bing": True},
                "requested_results": 20,
                "result_count": 1,
                "total_time": 0.5,
                "report_path": "history/report.html",
                "status": "completed",
                "engine_errors": {},
                "started_at": "2026-06-09T10:00:00+00:00",
                "completed_at": "2026-06-09T10:00:01+00:00",
            }
        ],
        "unassigned_searches": [
            {
                "id": "search-456",
                "original_query": "previous search",
                "parsed_query": '"previous search"',
                "filters": {},
                "engines": {"duckduckgo": True},
                "requested_results": 20,
                "result_count": 3,
                "total_time": 0.4,
                "report_path": "history/previous.html",
                "status": "completed",
                "engine_errors": {},
                "started_at": "2026-06-08T10:00:00+00:00",
                "completed_at": "2026-06-08T10:00:01+00:00",
            }
        ],
        "evidence": [
            {
                "id": "capture-123",
                "investigation_id": "case-123",
                "result_id": "result-123",
                "name": "Registry header",
                "source_url": "https://example.com/page",
                "page_title": "Example page",
                "capture_scope": "region",
                "selection": {
                    "x": 10,
                    "y": 20,
                    "width": 300,
                    "height": 200,
                },
                "manifest_path": "data/evidence/capture-123/manifest.json",
                "captured_at": "2026-06-10T10:00:00+00:00",
                "status": "completed",
                "error": "",
                "tool_version": "test",
                "artifacts": [
                    {
                        "id": "artifact-123",
                        "artifact_type": "png",
                        "file_path": "data/evidence/capture-123/capture.png",
                        "mime_type": "image/png",
                        "sha256": "a" * 64,
                        "byte_size": 123,
                        "created_at": "2026-06-10T10:00:00+00:00",
                    },
                    {
                        "id": "artifact-456",
                        "artifact_type": "html",
                        "file_path": "data/evidence/capture-123/page.html",
                        "mime_type": "text/html; charset=utf-8",
                        "sha256": "b" * 64,
                        "byte_size": 456,
                        "created_at": "2026-06-10T10:00:00+00:00",
                    },
                    {
                        "id": "artifact-789",
                        "artifact_type": "mhtml",
                        "file_path": "data/evidence/capture-123/page.mhtml",
                        "mime_type": "multipart/related",
                        "sha256": "c" * 64,
                        "byte_size": 789,
                        "created_at": "2026-06-10T10:00:00+00:00",
                    },
                ],
            }
        ],
    }


class InvestigationViewTestCase(unittest.TestCase):
    def test_generates_filterable_analyst_workspace(self):
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            output_path = base_dir / "data" / "investigation_pages" / "case-123.html"

            generated = generate_investigation_page(
                workspace_payload(),
                output_path,
                base_dir=base_dir,
                history_report_path=base_dir / "history" / "history.html",
            )
            content = output_path.read_text(encoding="utf-8")
            tree = html.fromstring(content)

        self.assertEqual(generated, str(output_path))
        self.assertEqual(
            tree.xpath("//article[@data-result-id='result-123']/@data-status"),
            ["pertinent"],
        )
        self.assertEqual(
            tree.xpath("//option[@value='search-456']/text()")[0].strip().split(" - ")[-1],
            "previous search (3 results)",
        )
        self.assertIn('queueAction("update_investigation_result"', content)
        self.assertIn('queueAction("remove_saved_page"', content)
        self.assertIn('queueAction("attach_investigation_search"', content)
        self.assertIn("Found through search", content)
        self.assertIn("example company", content)
        self.assertIn("Exact query term in title", content)
        self.assertIn("Returned by 2 search engines", content)
        self.assertIn("not factual accuracy", content)
        self.assertIn("data-local-datetime", content)
        self.assertIn("Intl.DateTimeFormat", content)
        self.assertNotIn("First seen 2026-06-09 10:00:00 UTC", content)
        self.assertIn("Evidence (1)", content)
        self.assertIn("Registry header", content)
        self.assertIn("Selected area", content)
        self.assertIn('class="evidence-thumbnail"', content)
        self.assertIn('class="evidence-name"', content)
        self.assertIn('loading="lazy"', content)
        self.assertNotIn("Open PNG", content)
        self.assertIn('queueAction("delete_evidence_capture"', content)
        self.assertIn('queueAction("verify_evidence_capture"', content)
        self.assertIn("data-evidence-verification", content)
        self.assertIn(">HTML</a>", content)
        self.assertIn(">MHTML</a>", content)
        self.assertIn(">Manifest</a>", content)
        self.assertEqual(
            tree.xpath("//button[contains(@class, 'verify-evidence')]/@title"),
            [
                "Recalculate every artifact hash and compare it with the "
                "recorded SHA-256"
            ],
        )
        self.assertEqual(
            tree.xpath("//button[contains(@class, 'delete-evidence')]/@title"),
            ["Delete this capture and its local evidence files"],
        )
        self.assertEqual(
            tree.xpath("//button[contains(@class, 'remove-saved-page')]/@title"),
            ["Remove this saved page from the investigation"],
        )
        self.assertEqual(
            tree.xpath("//input[@data-result-favorite]/@type"),
            ["checkbox"],
        )
        self.assertEqual(
            tree.xpath("//input[@data-result-favorite]/@checked"),
            ["checked"],
        )
        self.assertEqual(
            len(tree.xpath("//*[contains(@class, 'favorite-star')]")),
            1,
        )
        self.assertNotIn("SHA-256 aaaaaaaaaaaaaaaa", content)
        self.assertIn("result-filter-status", content)
        self.assertIn("result-filter-source", content)
        self.assertIn("result-filter-tag", content)
        self.assertIn("result-filter-after", content)
        self.assertIn("result-filter-before", content)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", content)
        self.assertNotIn("<script>alert(1)</script>", content)
        self.assertIn("../../theme.css", content)

        inline_scripts = re.findall(
            r"<script(?:\s[^>]*)?>([\s\S]*?)</script>",
            content,
        )
        self.assertEqual(
            len([script for script in inline_scripts if script.strip()]),
            1,
        )

    def test_uses_discovery_source_when_observation_sources_are_empty(self):
        workspace = workspace_payload()
        result = workspace["results"][0]
        result["sources"] = []
        result["discovery_sources"] = ["DuckDuckGo"]

        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            output_path = base_dir / "investigation.html"
            generate_investigation_page(
                workspace,
                output_path,
                base_dir=base_dir,
                history_report_path=base_dir / "history.html",
            )
            content = output_path.read_text(encoding="utf-8")

        self.assertIn("DuckDuckGo", content)
        self.assertNotIn("Unknown source", content)
        self.assertIn(
            '<option value="duckduckgo">DuckDuckGo</option>',
            content,
        )

    def test_archived_workspace_disables_analyst_mutations(self):
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            output_path = base_dir / "data" / "investigation_pages" / "case-123.html"

            generate_investigation_page(
                workspace_payload(status="archived"),
                output_path,
                base_dir=base_dir,
                history_report_path=base_dir / "history" / "history.html",
            )
            tree = html.fromstring(output_path.read_text(encoding="utf-8"))

        self.assertEqual(
            tree.xpath("//select[@data-result-status]/@disabled"),
            ["disabled"],
        )
        self.assertEqual(
            tree.xpath("//button[contains(@class, 'save-result-metadata')]/@disabled"),
            ["disabled"],
        )
        self.assertEqual(len(tree.xpath("//*[contains(@class, 'archive-notice')]")), 1)


if __name__ == "__main__":
    unittest.main()
