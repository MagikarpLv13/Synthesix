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
        "page_monitors": [
            {
                "id": "monitor-123",
                "investigation_id": "case-123",
                "result_id": "result-123",
                "result_title": "Example page",
                "result_url": "https://example.com/page",
                "baseline_capture_id": "capture-100",
                "last_capture_id": "capture-123",
                "archive_count": 2,
                "comparison_id": "comparison-123",
                "comparison_status": "changed",
                "comparison_similarity": 0.75,
                "comparison_report_path": (
                    "data/evidence/capture-123/comparison.html"
                ),
                "comparison_generated_at": "2026-06-10T10:00:00+00:00",
            }
        ],
        "entities": [
            {
                "id": "entity-123",
                "investigation_id": "case-123",
                "result_id": "result-123",
                "entity_type": "email",
                "suggested_type": "email",
                "custom_label": "Primary contact",
                "investigation_entity_id": "",
                "property_key": "Email",
                "value_original": "analyst@example.com",
                "value_normalized": "analyst@example.com",
                "source_field": "notes",
                "source_text": "Contact analyst@example.com for verification.",
                "confidence": 0.99,
                "confidence_reasons": ["Email syntax", "Domain syntax"],
                "attributes": {
                    "domain": "example.com",
                    "field_label": "Email",
                    "property_key": "Email",
                },
                "status": "proposed",
                "first_observed_at": "2026-06-10T10:00:00+00:00",
                "last_observed_at": "2026-06-10T10:00:00+00:00",
                "reviewed_at": None,
            }
        ],
        "graph_entities": [
            {
                "id": "graph-entity-123",
                "investigation_id": "case-123",
                "label": "Example SAS",
                "notes": "Primary company",
                "tags": ["Entreprise", "Source confidentielle"],
                "properties": {
                    "SIREN": "732829320",
                    "Forme juridique": "SAS",
                },
                "linked_result_ids": ["result-123"],
                "created_at": "2026-06-10T10:00:00+00:00",
                "updated_at": "2026-06-10T10:00:00+00:00",
            }
        ],
        "exports": [
            {
                "id": "export-123",
                "investigation_id": "case-123",
                "export_type": "zeroneurone",
                "archive_path": "data/exports/case-123/export/zeroneurone.zip",
                "dossier_path": "data/exports/case-123/export/dossier.json",
                "graphml_path": (
                    "data/exports/case-123/export/investigation.graphml"
                ),
                "csv_path": "data/exports/case-123/export/zeroneurone.csv",
                "nodes_csv_path": "data/exports/case-123/export/nodes.csv",
                "edges_csv_path": "data/exports/case-123/export/edges.csv",
                "manifest_path": "data/exports/case-123/export/manifest.json",
                "include_evidence": False,
                "include_unreviewed": False,
                "node_count": 4,
                "edge_count": 3,
                "asset_count": 2,
                "generated_at": "2026-06-12T12:00:00+00:00",
            }
        ],
        "url_analyses": [
            {
                "id": "analysis-123",
                "investigation_id": "case-123",
                "result_id": "result-123",
                "requested_url": "https://example.com/start",
                "final_url": "https://example.com/page?utm_source=test",
                "final_domain_unicode": "example.com",
                "final_domain_punycode": "example.com",
                "status_code": 200,
                "redirects": [
                    {
                        "url": "https://example.com/start",
                        "status_code": 301,
                        "location": "https://example.com/page?utm_source=test",
                    }
                ],
                "headers": {
                    "content-type": "text/html",
                    "x-frame-options": "DENY",
                },
                "content_type": "text/html",
                "content_length": 512,
                "bytes_read": 512,
                "content_sha256": "d" * 64,
                "content_truncated": False,
                "elapsed_ms": 42,
                "tracking_parameters": ["utm_source"],
                "cleaned_url": "https://example.com/page",
                "analyzed_at": "2026-06-14T10:00:00+00:00",
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
                "capture_kind": "screenshot",
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
        self.assertNotIn("toggle-result-details", content)
        self.assertNotIn("collapsedStorageKey", content)
        self.assertNotIn("setResultCollapsed", content)
        self.assertIn('queueAction("remove_saved_page"', content)
        self.assertIn('queueAction("attach_investigation_search"', content)
        self.assertIn('queueAction("delete_page_monitor"', content)
        self.assertIn('queueAction("extract_result_entities"', content)
        self.assertIn('queueAction("analyze_result_url"', content)
        self.assertIn('queueAction("update_entity_status"', content)
        self.assertIn('queueAction("update_entity_metadata"', content)
        self.assertIn('queueAction("create_graph_entity"', content)
        self.assertIn(
            '"create_graph_entity_from_extracted"',
            content,
        )
        self.assertIn('queueAction("update_graph_entity"', content)
        self.assertIn('queueAction("link_result_to_graph_entity"', content)
        self.assertIn('queueAction("attach_extracted_property"', content)
        self.assertNotIn("Créer une entité depuis ce site", content)
        self.assertNotIn("create_graph_entity_from_result", content)
        self.assertIn("Promouvoir en entité", content)
        self.assertIn('queueAction("export_zeroneurone"', content)
        self.assertIn('queueAction("delete_zeroneurone_export"', content)
        self.assertIn("Significant change", content)
        self.assertIn("75.00% text similarity", content)
        self.assertEqual(
            tree.xpath("//nav[contains(@class, 'investigation-nav')]/a/@href"),
            [
                "#overview",
                "#entities",
                "#saved-pages",
                "#page-monitoring",
                "#exports",
                "#attach-search",
                "#search-runs",
            ],
        )
        self.assertNotIn("Found through search", content)
        self.assertIn("example company", content)
        self.assertIn("Open Wayback Machine", content)
        self.assertIn("web.archive.org/web/*/https://example.com/", content)
        self.assertNotIn("Exact query term in title", content)
        self.assertNotIn("Returned by 2 search engines", content)
        self.assertNotIn("not factual accuracy", content)
        self.assertNotIn("score-breakdown", content)
        self.assertIn("data-local-datetime", content)
        self.assertIn("Intl.DateTimeFormat", content)
        self.assertIn('src="../../i18n.js"', content)
        self.assertNotIn("First seen 2026-06-09 10:00:00 UTC", content)
        self.assertIn("Evidence (1)", content)
        self.assertIn("Entities (1)", content)
        self.assertIn(">Entités</h3>", content)
        self.assertNotIn("Final graph", content)
        self.assertNotIn("Final graph node", content)
        self.assertIn("Example SAS", content)
        self.assertIn("Forme juridique", content)
        self.assertIn("Linked entities", content)
        self.assertIn("Lier à une entité", content)
        self.assertIn("analyst@example.com", content)
        self.assertIn('class="info-tip"', content)
        self.assertIn("Primary contact", content)
        self.assertEqual(
            tree.xpath("//input[@data-entity-custom-label]/@value"),
            ["Primary contact"],
        )
        self.assertIn("Suggested Email", content)
        self.assertIn("from notes", content)
        self.assertIn("Email syntax", content)
        self.assertIn("example.com", content)
        self.assertIn("Technical URL analysis (1)", content)
        self.assertIn("HTTP 200", content)
        self.assertIn("1 redirect(s)", content)
        self.assertIn("SHA-256 " + ("d" * 64), content)
        self.assertIn("x-frame-options", content)
        self.assertIn("without known tracking parameters", content)
        self.assertIn("ZeroNeurone export", content)
        self.assertIn("Export GraphML and CSV", content)
        self.assertIn(">GraphML</a>", content)
        self.assertIn(">ZeroNeurone ZIP</a>", content)
        self.assertIn(">Dossier JSON</a>", content)
        self.assertIn(">ZeroNeurone CSV</a>", content)
        self.assertIn(">Manifest</a>", content)
        self.assertIn("2 assets", content)
        self.assertIn("Delete export</button>", content)
        self.assertEqual(tree.xpath("//select[@data-entity-status]"), [])
        self.assertTrue(
            tree.xpath(
                "//*[contains(@class, 'entity-chip-row')]"
                "[contains(@class, 'entity-item--proposed')]"
            )
        )
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
        saved_page_card = tree.xpath("//article[@data-result-id='result-123']")[0]
        self.assertFalse(
            saved_page_card.xpath(".//*[contains(@class, 'result-evidence')]")
        )
        self.assertFalse(
            saved_page_card.xpath(".//*[contains(@class, 'result-entity-links')]")
        )
        self.assertTrue(
            saved_page_card.xpath(".//textarea[@data-result-notes][@hidden]")
        )
        self.assertTrue(
            saved_page_card.xpath(".//input[@data-result-tags][@type='hidden']")
        )
        remove_page = saved_page_card.xpath(
            ".//button[contains(@class, 'remove-saved-page')]"
        )[0]
        self.assertEqual(remove_page.text_content().strip(), "")
        self.assertTrue(remove_page.xpath(".//*[local-name()='svg']"))
        wayback = saved_page_card.xpath(
            ".//a[contains(@href, 'web.archive.org') and "
            "contains(@class, 'icon-action')]"
        )
        self.assertEqual(len(wayback), 1)
        self.assertEqual(wayback[0].get("aria-label"), "Open Wayback Machine")
        self.assertFalse(
            saved_page_card.xpath(".//*[contains(@class, 'result-provenance')]")
        )
        inspector = tree.xpath("//*[@data-inspector-panel='result-123']")[0]
        self.assertTrue(inspector.xpath(".//*[contains(@class, 'result-evidence')]"))
        self.assertTrue(
            inspector.xpath(".//*[contains(@class, 'result-entity-links')]")
        )
        self.assertFalse(
            inspector.xpath(
                ".//*[contains(concat(' ', normalize-space(@class), ' '), "
                "' link-result-entity ')]"
            )
        )
        self.assertTrue(inspector.xpath(".//select[@data-link-graph-entity]"))
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
        self.assertEqual(
            len(tree.xpath("//*[@id='result-filters'][@hidden]")),
            1,
        )
        self.assertEqual(
            tree.xpath("//*[@id='toggle-result-filters']/@aria-expanded"),
            ["false"],
        )
        self.assertIn('id="tag-suggestions"', content)
        self.assertIn('<option value="Personne"></option>', content)
        self.assertIn('<option value="Offshore"></option>', content)
        self.assertIn('<option value="Source confidentielle"></option>', content)
        self.assertIn('list="tag-suggestions"', content)
        self.assertNotIn("data-result-tag-suggestion", content)
        self.assertNotIn("add-result-tag", content)
        self.assertNotIn("ZeroNeurone TagSets are suggested", content)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", content)
        self.assertNotIn("<script>alert(1)</script>", content)
        self.assertIn("../../theme.css", content)
        self.assertEqual(
            tree.xpath(
                "//article[@data-result-id='result-123']"
                "/div[contains(@class, 'result-body')]/@id"
            ),
            ["result-body-result-123"],
        )

        inline_scripts = re.findall(
            r"<script(?:\s[^>]*)?>([\s\S]*?)</script>",
            content,
        )
        self.assertEqual(
            len([script for script in inline_scripts if script.strip()]),
            1,
        )

    def test_overview_shows_next_actions_worklist(self):
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            output_path = base_dir / "investigation.html"
            generate_investigation_page(
                workspace_payload(),
                output_path,
                base_dir=base_dir,
            history_report_path=base_dir / "history.html",
            )
            content = output_path.read_text(encoding="utf-8")
            tree = html.fromstring(content)

        worklist = tree.xpath(
            "//aside[contains(@class, 'workspace__rail')]"
            "//*[contains(@class, 'focus-summary')]"
        )
        self.assertEqual(len(worklist), 1)
        items = tree.xpath(
            "//*[contains(@class, 'focus-summary')]"
            "/*[contains(@class, 'focus-item')]"
        )
        self.assertEqual(len(items), 4)
        # 0 to review (pertinent), 1 monitored change, 1 proposed entity, 1 capture
        self.assertEqual(
            tree.xpath("//*[contains(@class, 'focus-item')]/strong/text()"),
            ["0", "1", "1", "1"],
        )
        self.assertEqual(
            tree.xpath("//*[contains(@class, 'focus-item')]/span/text()"),
            [
                "pages to review",
                "monitored changes",
                "proposed entities",
                "captures",
            ],
        )
        self.assertIn("Triage saved pages before exporting.", content := tree.text_content())
        self.assertIn("Open changed pages and compare archives.", content)

    def test_rail_inspector_panel_summarizes_each_saved_page(self):
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            output_path = base_dir / "investigation.html"
            generate_investigation_page(
                workspace_payload(),
                output_path,
                base_dir=base_dir,
                history_report_path=base_dir / "history.html",
            )
            tree = html.fromstring(output_path.read_text(encoding="utf-8"))

        panels = tree.xpath(
            "//aside[contains(@class, 'workspace__rail')]"
            "//*[@data-inspector-panel='result-123']"
        )
        self.assertEqual(len(panels), 1)
        panel = panels[0]
        # Hidden until a saved-page card is clicked.
        self.assertIsNotNone(panel.get("hidden"))
        panel_text = panel.text_content()
        self.assertNotIn("Score", panel_text)
        self.assertNotIn("Observations", panel_text)
        self.assertFalse(panel.xpath(".//*[contains(@class, 'inspector-stats')]"))
        self.assertIn("Relevant", panel_text)
        goto = panel.xpath(".//*[@data-inspector-goto='result-123']")
        self.assertEqual(len(goto), 1)

    def test_entities_are_compact_rows_with_management_card_in_rail(self):
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            output_path = base_dir / "investigation.html"
            generate_investigation_page(
                workspace_payload(),
                output_path,
                base_dir=base_dir,
                history_report_path=base_dir / "history.html",
            )
            content = output_path.read_text(encoding="utf-8")
            tree = html.fromstring(content)

        # Compact, clickable row in the main-column entity list.
        rows = tree.xpath(
            "//*[contains(@class, 'graph-entity-list')]"
            "//button[@data-entity-select='graph-entity-123']"
        )
        self.assertEqual(len(rows), 1)
        self.assertTrue(
            rows[0].xpath(".//*[contains(@class, 'entity-row__meta')]/span")
        )
        self.assertIn("example sas", rows[0].get("data-entity-search"))
        create_form = tree.xpath("//*[@id='graph-entity-create-form']")[0]
        self.assertEqual(
            tree.xpath("//*[@id='open-entity-create']/text()"),
            ["+ Entité"],
        )
        self.assertEqual(
            tree.xpath(
                "//aside[contains(@class, 'workspace__rail')]"
                "//*[@id='graph-entity-create-form'][@hidden]/@data-inspector-create-entity"
            ),
            [""],
        )
        self.assertEqual(
            create_form.xpath(".//input[@aria-label='Entity name']/@placeholder"),
            ["Nom de l'entité"],
        )
        self.assertEqual(
            create_form.xpath(".//*[@data-create-tags-editor]//input/@class"),
            ["tag-editor__input"],
        )
        self.assertIn("gatherCreateTags().join", content)
        self.assertIn(
            'createTagInput?.addEventListener("change", commitCreateTags)',
            content,
        )
        self.assertEqual(
            tree.xpath("//*[@id='entity-filter-query']/@placeholder"),
            ["Filtrer les entités..."],
        )
        self.assertEqual(
            len(tree.xpath("//*[contains(@class, 'entity-search__icon')]")),
            1,
        )
        # Full management card lives (hidden) in the rail inspector.
        cards = tree.xpath(
            "//aside[contains(@class, 'workspace__rail')]"
            "//article[@data-inspector-entity='graph-entity-123']"
        )
        self.assertEqual(len(cards), 1)
        self.assertIsNotNone(cards[0].get("hidden"))
        # Editable identity fields live at the top (auto-saved, no Save button).
        self.assertEqual(
            len(cards[0].xpath(".//*[@data-graph-entity-label]")),
            1,
        )
        self.assertEqual(
            len(cards[0].xpath(".//*[contains(@class, 'save-graph-entity')]")),
            0,
        )
        # Destructive actions are icon buttons, not text labels.
        delete = cards[0].xpath(
            ".//button[contains(@class, 'delete-graph-entity')]"
        )
        self.assertEqual(len(delete), 1)
        self.assertTrue(delete[0].xpath(".//*[local-name()='svg']"))
        self.assertEqual((delete[0].text or "").strip(), "")
        self.assertEqual(delete[0].get("aria-label"), "Delete entity")

    def test_overview_metrics_are_compact_tooltip_chips(self):
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            output_path = base_dir / "investigation.html"
            generate_investigation_page(
                workspace_payload(),
                output_path,
                base_dir=base_dir,
                history_report_path=base_dir / "history.html",
            )
            content = output_path.read_text(encoding="utf-8")
            tree = html.fromstring(content)

        chips = tree.xpath(
            "//*[contains(@class, 'investigation-metrics')]"
            "//*[contains(concat(' ', normalize-space(@class), ' '), ' metric-chip ')]"
        )
        self.assertEqual(len(chips), 5)
        self.assertIn("Searches: 1", chips[0].get("title"))
        self.assertEqual(chips[0].xpath(".//strong/text()"), ["1"])

    def test_inspector_starts_hidden_with_a_back_control(self):
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            output_path = base_dir / "investigation.html"
            generate_investigation_page(
                workspace_payload(),
                output_path,
                base_dir=base_dir,
                history_report_path=base_dir / "history.html",
            )
            tree = html.fromstring(output_path.read_text(encoding="utf-8"))

        # Next actions visible by default; inspector hidden until a selection.
        self.assertEqual(
            len(tree.xpath("//*[@id='rail-next-actions'][@hidden]")),
            0,
        )
        self.assertEqual(
            len(tree.xpath("//*[@id='inspector-detail'][@hidden]")),
            1,
        )
        # A back control returns to the actions view.
        self.assertEqual(
            len(tree.xpath("//*[@id='inspector-detail']//*[@data-inspector-close]")),
            1,
        )

    def test_entity_properties_show_type_badges_without_add_form(self):
        workspace = workspace_payload()
        workspace["graph_entities"][0]["properties"] = {
            "Forme juridique": "SAS",
            "Sandwich": "sandwich au poulet",
        }

        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            output_path = base_dir / "investigation.html"
            generate_investigation_page(
                workspace,
                output_path,
                base_dir=base_dir,
                history_report_path=base_dir / "history.html",
            )
            tree = html.fromstring(output_path.read_text(encoding="utf-8"))

        card = tree.xpath(
            "//article[@data-inspector-entity='graph-entity-123']"
        )[0]
        # Known property keys carry a small zeroneurone-style type chip.
        badges = card.xpath(".//*[contains(@class, 'prop-type')]/text()")
        self.assertGreaterEqual(
            [text.strip() for text in badges].count("Texte"),
            2,
        )
        # Property authoring belongs to zeroneurone: no manual add form here.
        self.assertEqual(card.xpath(".//*[@data-new-property-key]"), [])
        self.assertEqual(
            card.xpath(".//*[@data-graph-property-suggestion]"), []
        )

    def test_property_links_back_to_its_extracted_source(self):
        workspace = workspace_payload()
        entity = workspace["graph_entities"][0]
        entity["properties"] = {"Email": "analyst@example.com"}
        extracted = workspace["entities"][0]
        extracted["investigation_entity_id"] = entity["id"]
        extracted["property_key"] = "Email"
        extracted["status"] = "validated"
        extracted["result_id"] = workspace["results"][0]["id"]

        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            output_path = base_dir / "investigation.html"
            generate_investigation_page(
                workspace,
                output_path,
                base_dir=base_dir,
                history_report_path=base_dir / "history.html",
            )
            tree = html.fromstring(output_path.read_text(encoding="utf-8"))

        card = tree.xpath(
            "//article[@data-inspector-entity='graph-entity-123']"
        )[0]
        links = card.xpath(
            ".//a[contains(@class, 'graph-property-source')]/@href"
        )
        self.assertEqual(links, [workspace["results"][0]["url"]])
        refs = card.xpath(
            ".//a[contains(@class, 'graph-property-source')]"
            "//span[contains(@class, 'source-ref')]/text()"
        )
        self.assertEqual([text.strip() for text in refs], ["1"])
        source_refs = card.xpath(
            ".//ul[contains(@class, 'entity-source-list')]"
            "//span[contains(@class, 'source-ref')]/text()"
        )
        self.assertEqual([text.strip() for text in source_refs], ["1"])

    def test_extracted_row_carries_property_type_without_a_type_select(self):
        workspace = workspace_payload()
        workspace["entities"][0]["attributes"]["property_type"] = "text"

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
            tree = html.fromstring(content)

        row = tree.xpath(
            "//*[contains(@class, 'entity-chip-row')]"
            "[@data-entity-id='entity-123']"
        )[0]
        # Type is carried on the row for export, not editable here (no select).
        self.assertEqual(row.get("data-property-type"), "text")
        self.assertEqual(tree.xpath("//select[@data-property-type]"), [])
        self.assertIn("property_type: row.dataset.propertyType", content)

    def test_entity_tag_editor_renders_chips_and_an_add_input(self):
        workspace = workspace_payload()
        workspace["graph_entities"][0]["tags"] = []

        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            output_path = base_dir / "investigation.html"
            generate_investigation_page(
                workspace,
                output_path,
                base_dir=base_dir,
                history_report_path=base_dir / "history.html",
            )
            tree = html.fromstring(output_path.read_text(encoding="utf-8"))

        card = tree.xpath(
            "//article[@data-inspector-entity='graph-entity-123']"
        )[0]
        # No tags -> no chips, but the add input (with tagset suggestions) stays.
        self.assertFalse(card.xpath(".//*[contains(@class, 'tag-chip')]"))
        self.assertEqual(
            card.xpath(".//input[@data-tag-input]/@list"),
            ["entity-tagsets"],
        )
        # Notes is an always-editable textarea, not a masked paragraph.
        self.assertEqual(
            len(card.xpath(".//textarea[@data-graph-entity-notes]")),
            1,
        )

    def test_hides_raw_archive_text_source_in_entity_summary(self):
        workspace = workspace_payload()
        workspace["entities"][0]["source_field"] = "archive_text:capture-123"

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

        self.assertIn("Suggested Email", content)
        self.assertNotIn("from archive_text", content)

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

    def test_compacts_long_urls_without_changing_link_target(self):
        workspace = workspace_payload()
        long_url = (
            "https://www.google.com/maps/@48.2368593,2.3635355,3a,15y/"
            + ("data=!3m7!1e1!" * 30)
            + "?entry=ttu&ucbcb=1"
        )
        workspace["results"][0]["url"] = long_url
        workspace["url_analyses"][0]["final_url"] = long_url

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
            tree = html.fromstring(content)

        self.assertEqual(
            tree.xpath(
                "//article[@data-result-id='result-123']"
                "//a[contains(@class, 'result-title')]/@href"
            ),
            [long_url],
        )
        displayed_urls = tree.xpath(
            "//article[@data-result-id='result-123']"
            "//div[contains(@class, 'result-url')]/text()"
        )
        self.assertTrue(all(len(value.strip()) <= 160 for value in displayed_urls))
        self.assertTrue(any("..." in value for value in displayed_urls))
        self.assertTrue(
            all(
                value == long_url
                for value in tree.xpath(
                    "//article[@data-result-id='result-123']"
                    "//div[contains(@class, 'result-url')]/@title"
                )
            )
        )

    def test_page_monitor_can_be_enabled_from_saved_page(self):
        workspace = workspace_payload()
        workspace["page_monitors"] = []
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

        self.assertIn("Monitor changes", content)
        self.assertIn('queueAction("create_page_monitor"', content)
        self.assertIn("Screenshots are not compared automatically", content)

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
        self.assertFalse(
            tree.xpath("//button[contains(@class, 'save-result-metadata')]")
        )
        self.assertEqual(
            tree.xpath(
                "//button[contains(@class, 'extract-result-entities')]/@disabled"
            ),
            ["disabled"],
        )
        self.assertEqual(
            tree.xpath(
                "//button[contains(@class, 'analyze-result-url')]/@disabled"
            ),
            ["disabled"],
        )
        self.assertEqual(
            tree.xpath("//input[@data-entity-custom-label]/@disabled"),
            ["disabled"],
        )
        self.assertTrue(
            tree.xpath(
                "//button[contains(@class, 'entity-validate')]/@disabled"
            )
        )
        self.assertTrue(
            tree.xpath(
                "//button[contains(@class, 'entity-reject')]/@disabled"
            )
        )
        self.assertFalse(tree.xpath("//select[@data-result-tag-suggestion]"))
        self.assertFalse(tree.xpath("//button[contains(@class, 'add-result-tag')]"))
        self.assertTrue(
            tree.xpath(
                "//button[contains(@class, 'stop-page-monitor')]/@disabled"
            )
        )
        self.assertEqual(len(tree.xpath("//*[contains(@class, 'archive-notice')]")), 1)


if __name__ == "__main__":
    unittest.main()
