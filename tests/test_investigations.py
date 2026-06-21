import json
import sqlite3
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from exceptions import InvestigationHasDataError, InvestigationValidationError
from investigations.migrations import MIGRATIONS
from investigations.repository import InvestigationRepository, canonicalize_url, utc_now
from investigations.service import InvestigationService


class InvestigationRepositoryTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "data" / "synthesix.db"
        self.repository = InvestigationRepository(self.database_path)
        self.service = InvestigationService(self.repository)
        self.service.initialize()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initializes_versioned_schema(self):
        self.assertTrue(self.database_path.exists())
        self.assertEqual(self.repository.schema_version(), 14)

    def test_v1_automatic_result_links_are_hidden_after_migration(self):
        with TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "legacy.db"
            connection = sqlite3.connect(database_path)
            try:
                connection.executescript(
                    """
                    CREATE TABLE schema_migrations (
                        version INTEGER PRIMARY KEY,
                        applied_at TEXT NOT NULL
                    );
                    """
                    + MIGRATIONS[0][1]
                )
                connection.execute(
                    "INSERT INTO schema_migrations(version, applied_at) VALUES (1, ?)",
                    ("2026-06-09T00:00:00+00:00",),
                )
                connection.execute(
                    """
                    INSERT INTO investigations(
                        id, title, reference, description, tags_json, status,
                        created_at, updated_at
                    )
                    VALUES ('case-1', 'Legacy case', '', '', '[]', 'active', ?, ?)
                    """,
                    (
                        "2026-06-09T00:00:00+00:00",
                        "2026-06-09T00:00:00+00:00",
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO results(
                        id, canonical_url, url, title, description,
                        first_observed_at, last_observed_at
                    )
                    VALUES ('result-1', 'https://example.com/', 'https://example.com/',
                            'Example', '', ?, ?)
                    """,
                    (
                        "2026-06-09T00:00:00+00:00",
                        "2026-06-09T00:00:00+00:00",
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO investigation_results(
                        investigation_id, result_id, analyst_status, favorite,
                        notes, tags_json, added_at, updated_at
                    )
                    VALUES ('case-1', 'result-1', 'a_verifier', 0, '', '[]', ?, ?)
                    """,
                    (
                        "2026-06-09T00:00:00+00:00",
                        "2026-06-09T00:00:00+00:00",
                    ),
                )
                connection.commit()
            finally:
                connection.close()

            repository = InvestigationRepository(database_path)
            service = InvestigationService(repository)
            service.initialize()

            self.assertEqual(repository.schema_version(), 14)
            self.assertEqual(repository.table_count("investigation_results"), 1)
            self.assertEqual(repository.get_investigation("case-1").result_count, 0)
            self.assertEqual(repository.list_investigation_results("case-1"), [])

    def test_v5_data_is_indexed_when_fts_migration_runs(self):
        with TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "legacy-v5.db"
            connection = sqlite3.connect(database_path)
            try:
                connection.execute(
                    """
                    CREATE TABLE schema_migrations (
                        version INTEGER PRIMARY KEY,
                        applied_at TEXT NOT NULL
                    )
                    """
                )
                for version, sql in MIGRATIONS[:5]:
                    connection.executescript(sql)
                    connection.execute(
                        """
                        INSERT INTO schema_migrations(version, applied_at)
                        VALUES (?, ?)
                        """,
                        (version, "2026-06-09T00:00:00+00:00"),
                    )
                connection.execute(
                    """
                    INSERT INTO investigations(
                        id, title, reference, description, tags_json, status,
                        created_at, updated_at
                    )
                    VALUES (
                        'case-1', 'Legacy indexed case', '', '', '[]', 'active',
                        ?, ?
                    )
                    """,
                    (
                        "2026-06-09T00:00:00+00:00",
                        "2026-06-09T00:00:00+00:00",
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO search_runs(
                        id, investigation_id, original_query, parsed_query,
                        filters_json, engines_json, requested_results,
                        result_count, total_time, report_path, status,
                        engine_errors_json, started_at, completed_at
                    )
                    VALUES (
                        'search-1', 'case-1', 'legacy archive',
                        '"legacy archive"', '{}', '{"google":true}', 10, 1,
                        0.5, 'report.html', 'completed', '{}', ?, ?
                    )
                    """,
                    (
                        "2026-06-09T00:00:00+00:00",
                        "2026-06-09T00:00:01+00:00",
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO results(
                        id, canonical_url, url, title, description,
                        first_observed_at, last_observed_at
                    )
                    VALUES (
                        'result-1', 'https://example.com/legacy',
                        'https://example.com/legacy', 'Legacy archive page',
                        'Stored before FTS5', ?, ?
                    )
                    """,
                    (
                        "2026-06-09T00:00:01+00:00",
                        "2026-06-09T00:00:01+00:00",
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO search_result_observations(
                        search_run_id, result_id, source_json, title,
                        description, relevance_score, score_breakdown_json,
                        observed_at
                    )
                    VALUES (
                        'search-1', 'result-1', '["Google"]',
                        'Legacy archive page', 'Stored before FTS5', 5, '[]', ?
                    )
                    """,
                    ("2026-06-09T00:00:01+00:00",),
                )
                connection.commit()
            finally:
                connection.close()

            service = InvestigationService(
                InvestigationRepository(database_path)
            )
            service.initialize()

            self.assertEqual(service.repository.schema_version(), 14)
            results = service.search_local_archive({"query": "legacy"})
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["investigation_title"], "Legacy indexed case")

    def test_repairs_pre_release_v7_without_page_monitor_tables(self):
        with TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "pre-release-v7.db"
            connection = sqlite3.connect(database_path)
            try:
                connection.execute(
                    """
                    CREATE TABLE schema_migrations (
                        version INTEGER PRIMARY KEY,
                        applied_at TEXT NOT NULL
                    )
                    """
                )
                for version, sql in MIGRATIONS[:6]:
                    connection.executescript(sql)
                    connection.execute(
                        """
                        INSERT INTO schema_migrations(version, applied_at)
                        VALUES (?, ?)
                        """,
                        (version, "2026-06-10T00:00:00+00:00"),
                    )
                connection.execute(
                    """
                    INSERT INTO schema_migrations(version, applied_at)
                    VALUES (7, ?)
                    """,
                    ("2026-06-10T01:00:00+00:00",),
                )
                connection.commit()
            finally:
                connection.close()

            repository = InvestigationRepository(database_path)
            repository.initialize()

            self.assertEqual(repository.schema_version(), 14)
            self.assertEqual(repository.table_count("page_monitors"), 0)
            repaired = sqlite3.connect(database_path)
            try:
                columns = {
                    row[1]
                    for row in repaired.execute(
                        "PRAGMA table_info(evidence_captures)"
                    )
                }
            finally:
                repaired.close()
            self.assertIn("capture_kind", columns)

    def test_creates_updates_and_archives_investigation(self):
        created = self.service.create(
            {
                "title": "Case Alpha",
                "reference": "REF-001",
                "description": "Initial scope",
                "tags": "person, priority, PERSON",
            }
        )

        self.assertEqual(created.title, "Case Alpha")
        self.assertEqual(created.tags, ("Personne", "priority"))
        self.assertEqual(self.service.list_payload()[0]["id"], created.id)

        updated = self.service.update(
            created.id,
            {
                "title": "Case Alpha Updated",
                "reference": "REF-002",
                "description": "Updated scope",
                "tags": ["updated"],
            },
        )
        self.assertEqual(updated.title, "Case Alpha Updated")
        self.assertEqual(updated.tags, ("updated",))

        archived = self.service.archive(created.id)
        self.assertEqual(archived.status, "archived")
        self.assertEqual(self.service.list_investigations(), [])
        self.assertEqual(
            self.service.list_investigations(include_archived=True)[0].id,
            created.id,
        )

    def test_rejects_empty_title(self):
        with self.assertRaises(InvestigationValidationError):
            self.service.create({"title": "  "})

    def test_deletes_only_empty_investigations(self):
        empty = self.service.create({"title": "Empty"})
        self.service.delete(empty.id)
        self.assertEqual(self.service.list_investigations(), [])

        populated = self.service.create({"title": "Populated"})
        self.service.record_search(
            investigation_id=populated.id,
            original_query="query",
            parsed_query='"query"',
            filters={},
            engines={"google": True},
            requested_results=10,
            report_path="report.html",
            total_time=0.5,
            engine_errors={},
            results=[
                {
                    "title": "Result",
                    "link": "https://example.com/page",
                    "description": "Description",
                    "source": "Google",
                    "relevance_score": 5,
                }
            ],
        )

        with self.assertRaises(InvestigationHasDataError):
            self.service.delete(populated.id)

    def test_records_observations_and_deduplicates_canonical_urls(self):
        investigation = self.service.create({"title": "Case"})
        common = {
            "investigation_id": investigation.id,
            "original_query": "query",
            "parsed_query": '"query"',
            "filters": {},
            "engines": {"google": True},
            "requested_results": 10,
            "report_path": "report.html",
            "total_time": 0.5,
            "engine_errors": {},
        }
        self.service.record_search(
            **common,
            results=[
                {
                    "title": "First title",
                    "link": "HTTPS://Example.COM:443/page#section",
                    "description": "First description",
                    "source": "Google",
                    "relevance_score": 5,
                }
            ],
        )
        self.service.record_search(
            **common,
            results=[
                {
                    "title": "Updated title",
                    "link": "https://example.com/page",
                    "description": "Updated description",
                    "source": "Bing, Google",
                    "relevance_score": 7,
                }
            ],
        )

        self.assertEqual(self.repository.table_count("search_runs"), 2)
        self.assertEqual(self.repository.table_count("results"), 1)
        self.assertEqual(self.repository.table_count("search_result_observations"), 2)
        self.assertEqual(self.repository.table_count("investigation_results"), 0)

        refreshed = self.repository.get_investigation(investigation.id)
        self.assertEqual(refreshed.search_count, 2)
        self.assertEqual(refreshed.result_count, 0)

    def test_local_search_indexes_content_and_metadata_filters(self):
        investigation = self.service.create({"title": "Registry case"})
        self.service.record_search(
            investigation_id=investigation.id,
            original_query="example company",
            parsed_query='"example company"',
            filters={},
            engines={"google": True, "bing": True},
            requested_results=10,
            report_path="report.html",
            total_time=0.5,
            engine_errors={},
            started_at="2026-06-09T09:00:00+00:00",
            results=[
                {
                    "title": "Example Company Registry",
                    "link": "https://records.example.com/company/42",
                    "description": "Official incorporation record.",
                    "source": "Google, Bing",
                    "relevance_score": 8.5,
                }
            ],
        )
        saved = self.service.save_page(
            investigation.id,
            {
                "url": "https://records.example.com/company/42",
                "title": "Example Company Registry",
                "description": "Official incorporation record.",
                "referrer": "file:///report.html",
            },
        )
        self.service.update_result(
            investigation.id,
            saved.id,
            {
                "analyst_status": "confirme",
                "favorite": False,
                "notes": "Validated against the chamber of commerce.",
                "tags": "corporate, registry",
            },
        )

        by_title = self.service.search_local_archive({"query": "Company"})
        by_notes = self.service.search_local_archive({"query": "chamber"})
        by_url = self.service.search_local_archive({"query": "company 42"})
        filtered = self.service.search_local_archive(
            {
                "investigation_id": investigation.id,
                "source": "Bing",
                "analyst_status": "confirme",
                "domain": "example.com",
                "observed_after": "2026-06-09",
                "observed_before": utc_now()[:10],
            }
        )

        self.assertEqual(by_title[0]["result_id"], saved.id)
        self.assertEqual(by_notes[0]["notes"], "Validated against the chamber of commerce.")
        self.assertEqual(by_url[0]["domain"], "records.example.com")
        self.assertEqual(filtered[0]["investigation_title"], "Registry case")
        self.assertEqual(filtered[0]["sources"], ["Bing", "Google"])
        self.assertEqual(filtered[0]["tags"], ["corporate", "registry"])
        self.assertTrue(filtered[0]["already_observed"])
        self.assertTrue(filtered[0]["is_saved"])
        self.assertEqual(self.repository.table_count("local_search_documents"), 1)
        self.assertEqual(self.repository.table_count("local_search_fts"), 1)

    def test_local_search_rebuilds_and_moves_attached_search_scope(self):
        investigation = self.service.create({"title": "Case"})
        search_id = self.service.record_search(
            investigation_id=None,
            original_query="offline archive",
            parsed_query='"offline archive"',
            filters={},
            engines={"duckduckgo": True},
            requested_results=10,
            report_path="report.html",
            total_time=0.5,
            engine_errors={},
            results=[
                {
                    "title": "Offline archive result",
                    "link": "https://example.org/archive",
                    "description": "Previously collected material.",
                    "source": "DuckDuckGo",
                    "relevance_score": 5,
                }
            ],
        )

        unassigned = self.service.search_local_archive(
            {
                "query": "offline",
                "investigation_id": "__unassigned__",
            }
        )
        self.assertEqual(len(unassigned), 1)

        self.service.attach_search(investigation.id, search_id)
        self.assertEqual(
            self.service.search_local_archive(
                {
                    "query": "offline",
                    "investigation_id": "__unassigned__",
                }
            ),
            [],
        )
        attached = self.service.search_local_archive(
            {
                "query": "offline",
                "investigation_id": investigation.id,
            }
        )
        self.assertEqual(len(attached), 1)

        with self.repository._connection() as connection:
            connection.execute("DELETE FROM local_search_documents")
        self.assertEqual(self.service.search_local_archive({"query": "offline"}), [])
        self.assertEqual(self.service.rebuild_local_search_index(), 1)
        self.assertEqual(len(self.service.search_local_archive({"query": "offline"})), 1)

    def test_clear_history_preserves_investigation_shells(self):
        investigation = self.service.create({"title": "Case"})
        self.service.record_search(
            investigation_id=investigation.id,
            original_query="query",
            parsed_query='"query"',
            filters={},
            engines={"google": True},
            requested_results=10,
            report_path="report.html",
            total_time=0.5,
            engine_errors={},
            results=[
                {
                    "title": "Saved result",
                    "link": "https://example.com/saved",
                    "description": "Description",
                    "source": "Google",
                    "relevance_score": 5,
                }
            ],
        )
        saved = self.service.save_page(
            investigation.id,
            {
                "url": "https://example.com/saved",
                "title": "Saved result",
                "description": "Description",
                "referrer": "https://www.google.com/",
            },
        )

        removed = self.service.clear_search_history()

        self.assertEqual(removed, 1)
        self.assertEqual(self.repository.table_count("search_runs"), 0)
        self.assertEqual(self.repository.table_count("investigation_results"), 1)
        self.assertEqual(self.repository.table_count("results"), 1)
        self.assertEqual(len(self.service.list_investigations()), 1)
        preserved = self.repository.list_investigation_results(investigation.id)[0]
        self.assertEqual(preserved.id, saved.id)
        local_results = self.service.search_local_archive({"query": "saved"})
        self.assertEqual(len(local_results), 1)
        self.assertTrue(local_results[0]["is_saved"])
        self.assertEqual(preserved.discovery_query, "query")
        self.assertEqual(preserved.discovery_sources, ("Google",))

    def test_updates_and_reads_analyst_metadata(self):
        investigation = self.service.create({"title": "Case"})
        self.service.record_search(
            investigation_id=investigation.id,
            original_query="example company",
            parsed_query='"example company"',
            filters={},
            engines={"google": True, "bing": True},
            requested_results=10,
            report_path="report.html",
            total_time=0.5,
            engine_errors={},
            results=[
                {
                    "title": "Example company registry",
                    "link": "https://example.com/company",
                    "description": "Registry entry.",
                    "source": "Google, Bing",
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
                }
            ],
        )
        result = self.service.save_page(
            investigation.id,
            {
                "url": "https://example.com/company",
                "title": "Example company registry",
                "description": "Registry entry.",
                "referrer": "file:///report.html",
            },
        )

        updated = self.service.update_result(
            investigation.id,
            result.id,
            {
                "analyst_status": "confirme",
                "favorite": True,
                "notes": "Confirmed against the registry.",
                "tags": "company, registry, COMPANY",
            },
        )

        self.assertEqual(updated.analyst_status, "confirme")
        self.assertTrue(updated.favorite)
        self.assertEqual(updated.notes, "Confirmed against the registry.")
        self.assertEqual(updated.tags, ("Entreprise", "registry"))
        self.assertEqual(updated.sources, ("Bing", "Google"))
        self.assertEqual(updated.discovery_sources, ("Bing", "Google"))
        self.assertEqual(updated.discovery_query, "example company")
        self.assertEqual(updated.discovery_method, "search_result")
        self.assertEqual(updated.relevance_score, 8.5)
        self.assertEqual(
            [component["key"] for component in updated.score_breakdown],
            ["exact_title", "engine_consensus"],
        )
        self.assertEqual(updated.observation_count, 1)

        workspace = self.service.workspace_payload(investigation.id)
        self.assertEqual(workspace["results"][0]["analyst_status"], "confirme")
        self.assertEqual(workspace["searches"][0]["original_query"], "example company")

    def test_builds_curated_entity_from_saved_source_and_extracted_property(self):
        investigation = self.service.create({"title": "Company case"})
        saved = self.service.save_page(
            investigation.id,
            {
                "url": "https://www.pappers.fr/entreprise/acme-732829320",
                "title": "ACME SAS - Pappers",
                "description": "SIRET 732 829 320 00074",
                "referrer": "https://www.google.com/",
            },
        )
        graph_entity = self.service.create_graph_entity(
            investigation.id,
            {
                "label": "ACME SAS",
                "tags": "Company",
                "notes": "Company retained from the registry result.",
            },
        )
        self.service.link_result_to_graph_entity(
            investigation.id,
            graph_entity["id"],
            saved.id,
        )
        self.service.set_graph_entity_property(
            investigation.id,
            graph_entity["id"],
            {"key": "Forme juridique", "value": "SAS"},
        )
        extracted = self.service.extract_entities(
            investigation.id,
            saved.id,
        )
        siret = next(
            entity
            for entity in extracted
            if entity["entity_type"] == "siret"
        )
        attached = self.service.attach_extracted_property(
            investigation.id,
            siret["id"],
            {
                "graph_entity_id": graph_entity["id"],
                "property_key": "SIRET",
            },
        )

        workspace = self.service.workspace_payload(investigation.id)
        curated = workspace["graph_entities"][0]
        self.assertEqual(curated["label"], "ACME SAS")
        self.assertEqual(curated["tags"], ["Entreprise"])
        self.assertEqual(curated["properties"]["Forme juridique"], "SAS")
        self.assertEqual(curated["properties"]["SIREN"], "")
        self.assertEqual(curated["properties"]["SIRET"], "732 829 320 00074")
        self.assertEqual(curated["properties"]["Date de création"], "")
        self.assertEqual(curated["linked_result_ids"], [saved.id])
        self.assertEqual(attached["status"], "validated")
        self.assertEqual(
            attached["investigation_entity_id"],
            graph_entity["id"],
        )
        self.assertEqual(attached["property_key"], "SIRET")

        self.service.detach_extracted_property(
            investigation.id,
            siret["id"],
        )
        detached = next(
            entity
            for entity in self.service.workspace_payload(
                investigation.id
            )["entities"]
            if entity["id"] == siret["id"]
        )
        self.assertIsNone(detached["investigation_entity_id"])
        self.assertEqual(detached["property_key"], "")

    def test_record_selection_entity_creates_validated_sourced_fact(self):
        investigation = self.service.create({"title": "Selection case"})
        saved = self.service.save_page(
            investigation.id,
            {
                "url": "https://www.750g.com/sandwich-au-poulet",
                "title": "Recette Sandwich au poulet",
                "description": "Sandwich au poulet en 10 minutes.",
            },
        )
        entity = self.service.create_graph_entity(
            investigation.id, {"label": "Justine Le Pottier"}
        )

        recorded = self.service.record_selection_entity(
            investigation.id,
            saved.id,
            value="sandwich au poulet",
            property_key="Sandwich",
        )
        self.assertIsNotNone(recorded)
        self.assertEqual(recorded.status, "validated")
        self.assertEqual(recorded.result_id, saved.id)
        self.assertEqual(recorded.value_original, "sandwich au poulet")
        self.assertEqual(recorded.entity_type, "other")

        self.service.attach_extracted_property(
            investigation.id,
            recorded.id,
            {"graph_entity_id": entity["id"], "property_key": "Sandwich"},
        )

        workspace = self.service.workspace_payload(investigation.id)
        # The selection shows up as a (validated) extracted entity on the page...
        page_entities = [
            item
            for item in workspace["entities"]
            if item["result_id"] == saved.id
        ]
        self.assertEqual(len(page_entities), 1)
        self.assertEqual(page_entities[0]["status"], "validated")
        self.assertEqual(
            page_entities[0]["investigation_entity_id"], entity["id"]
        )
        # ...and the curated entity carries the property value.
        curated = workspace["graph_entities"][0]
        self.assertEqual(curated["properties"]["Sandwich"], "sandwich au poulet")

    def test_builtin_tags_seed_default_entity_properties(self):
        investigation = self.service.create({"title": "Legal case"})

        lawyer = self.service.create_graph_entity(
            investigation.id,
            {
                "label": "Me Dupont",
                "tags": "Avocat",
            },
        )

        self.assertEqual(lawyer["tags"], ["Avocat"])
        self.assertEqual(
            lawyer["properties"],
            {
                "Barreau": "",
                "Spécialité": "",
                "Cabinet": "",
                "Date d'inscription": "",
            },
        )

    def test_custom_graph_entity_tag_is_preserved_without_default_properties(self):
        investigation = self.service.create({"title": "Custom tag case"})

        entity = self.service.create_graph_entity(
            investigation.id,
            {
                "label": "Custom target",
                "tags": "Source confidentielle",
            },
        )

        self.assertEqual(entity["tags"], ["Source confidentielle"])
        self.assertEqual(entity["properties"], {})

    def test_creates_graph_entities_directly_from_results_and_properties(self):
        investigation = self.service.create({"title": "Quick entities"})
        saved = self.service.save_page(
            investigation.id,
            {
                "url": "https://www.pappers.fr/entreprise/acme-732829320",
                "title": "ACME SAS - Pappers",
                "description": "SIRET 732 829 320 00074",
                "referrer": "https://www.google.com/",
            },
        )

        site_entity = self.service.create_graph_entity_from_result(
            investigation.id,
            saved.id,
            {
                "label": "Pappers",
                "category": "Website",
            },
        )
        self.assertEqual(site_entity["tags"], ["Site web"])
        self.assertEqual(site_entity["linked_result_ids"], [saved.id])

        extracted = self.service.extract_entities(
            investigation.id,
            saved.id,
        )
        siret = next(
            entity
            for entity in extracted
            if entity["entity_type"] == "siret"
        )
        company = self.service.create_graph_entity_from_extracted(
            investigation.id,
            siret["id"],
            {
                "label": "ACME SAS",
                "category": "Company",
                "property_key": "SIRET",
            },
        )

        self.assertEqual(company["tags"], ["Entreprise"])
        self.assertEqual(company["linked_result_ids"], [saved.id])
        attached = next(
            entity
            for entity in self.service.workspace_payload(
                investigation.id
            )["entities"]
            if entity["id"] == siret["id"]
        )
        self.assertEqual(
            attached["investigation_entity_id"],
            company["id"],
        )
        self.assertEqual(attached["property_key"], "SIRET")
        self.assertEqual(attached["status"], "validated")

    def test_analyst_label_overrides_inferred_property_key(self):
        investigation = self.service.create({"title": "Property labels"})
        saved = self.service.save_page(
            investigation.id,
            {
                "url": "https://example.org/company",
                "title": "ACME SAS",
                "description": "Date de création : 2025-06-14",
                "referrer": "",
            },
        )
        date_entity = next(
            entity
            for entity in self.service.extract_entities(
                investigation.id,
                saved.id,
            )
            if entity["entity_type"] == "date"
        )
        self.service.update_entity_metadata(
            investigation.id,
            date_entity["id"],
            {
                "entity_type": "date",
                "custom_label": "Créée le",
                "tags": "",
            },
        )

        company = self.service.create_graph_entity_from_extracted(
            investigation.id,
            date_entity["id"],
            {
                "label": "ACME SAS",
                "category": "Company",
            },
        )
        attached = next(
            entity
            for entity in self.service.workspace_payload(
                investigation.id
            )["entities"]
            if entity["id"] == date_entity["id"]
        )

        self.assertEqual(attached["property_key"], "Créée le")
        self.assertEqual(company["properties"]["Créée le"], "2025-06-14")

    def test_extracts_and_reviews_entities_without_resetting_analyst_status(self):
        investigation = self.service.create({"title": "Entity case"})
        saved = self.service.save_page(
            investigation.id,
            {
                "url": "https://example.org/profile",
                "title": "Public profile",
                "description": "Contact jane@example.org or @jane_public.",
                "referrer": "https://example.org/directory",
            },
        )
        self.service.update_result(
            investigation.id,
            saved.id,
            {
                "analyst_status": "pertinent",
                "notes": "Server 192.0.2.10.",
            },
        )

        extracted = self.service.extract_entities(
            investigation.id,
            saved.id,
        )
        self.assertNotIn("url", {entity["entity_type"] for entity in extracted})
        email = next(
            entity
            for entity in extracted
            if entity["entity_type"] == "email"
        )
        reviewed = self.service.update_entity_status(
            investigation.id,
            email["id"],
            "rejected",
        )
        relabeled = self.service.update_entity_metadata(
            investigation.id,
            email["id"],
            {
                "entity_type": "person",
                "custom_label": "Primary contact",
                "tags": "Person, Suspect, custom role",
            },
        )

        self.assertEqual(reviewed["status"], "rejected")
        self.assertIsNotNone(reviewed["reviewed_at"])
        self.assertEqual(relabeled["entity_type"], "person")
        self.assertEqual(relabeled["suggested_type"], "email")
        self.assertEqual(relabeled["custom_label"], "Primary contact")
        self.assertEqual(
            relabeled["tags"],
            ["Personne", "Suspect", "custom role"],
        )
        extracted_again = self.service.extract_entities(
            investigation.id,
            saved.id,
        )
        email_again = next(
            entity
            for entity in extracted_again
            if entity["id"] == email["id"]
        )
        self.assertEqual(email_again["status"], "rejected")
        self.assertEqual(
            self.repository.table_count("extracted_entities"),
            len(extracted),
        )
        workspace = self.service.workspace_payload(investigation.id)
        self.assertEqual(
            next(
                entity["status"]
                for entity in workspace["entities"]
                if entity["id"] == email["id"]
            ),
            "rejected",
        )
        self.service.remove_saved_page(investigation.id, saved.id)
        self.assertEqual(
            self.repository.table_count("extracted_entities"),
            0,
        )

    def test_extracts_entities_from_saved_archive_text(self):
        investigation = self.service.create({"title": "Archive entities"})
        saved = self.service.save_page(
            investigation.id,
            {
                "url": "https://example.org/company",
                "title": "Company",
                "description": "",
                "referrer": "",
            },
        )
        text_path = (
            Path(self.temp_dir.name)
            / "data"
            / "evidence"
            / "capture-entity"
            / "page.txt"
        )
        text_path.parent.mkdir(parents=True)
        text_path.write_text(
            "SIRET 732 829 320 00074. "
            "Siège social : 10 rue de la Paix, 75002 Paris.",
            encoding="utf-8",
        )
        self.service.record_evidence_capture(
            capture_id="capture-entity",
            investigation_id=investigation.id,
            result_id=saved.id,
            name="Company archive",
            source_url=saved.url,
            page_title=saved.title,
            capture_scope="viewport",
            selection={},
            manifest_path=(
                "data/evidence/capture-entity/manifest.json"
            ),
            captured_at="2026-06-15T10:00:00+00:00",
            tool_version="test",
            capture_kind="page_archive",
            artifacts=[
                {
                    "id": "artifact-entity-text",
                    "artifact_type": "text",
                    "file_path": (
                        "data/evidence/capture-entity/page.txt"
                    ),
                    "mime_type": "text/plain; charset=utf-8",
                    "sha256": "a" * 64,
                    "byte_size": text_path.stat().st_size,
                    "created_at": "2026-06-15T10:00:00+00:00",
                }
            ],
        )
        company = self.service.create_graph_entity(
            investigation.id,
            {
                "label": "ACME SAS",
                "tags": "Company",
            },
        )
        self.service.link_result_to_graph_entity(
            investigation.id,
            company["id"],
            saved.id,
        )

        extracted = self.service.extract_entities(
            investigation.id,
            saved.id,
        )

        self.assertIn("siret", {item["entity_type"] for item in extracted})
        address = next(
            item
            for item in extracted
            if item["entity_type"] == "address"
        )
        self.assertTrue(
            address["source_field"].startswith("archive_text:")
        )
        self.assertEqual(address["property_key"], "Siège social")
        self.assertEqual(address["investigation_entity_id"], company["id"])
        self.assertEqual(address["attributes"]["postal_code"], "75002")
        refreshed_company = next(
            entity
            for entity in self.service.workspace_payload(
                investigation.id
            )["graph_entities"]
            if entity["id"] == company["id"]
        )
        self.assertEqual(
            refreshed_company["properties"]["SIRET"],
            "732 829 320 00074",
        )
        self.assertEqual(
            refreshed_company["properties"]["Siège social"],
            "10 rue de la Paix, 75002 Paris",
        )

    def test_archived_investigation_rejects_entity_extraction(self):
        investigation = self.service.create({"title": "Archived case"})
        saved = self.service.save_page(
            investigation.id,
            {
                "url": "https://example.org/profile",
                "title": "Profile",
                "description": "Contact jane@example.org.",
                "referrer": "",
            },
        )
        self.service.archive(investigation.id)

        with self.assertRaises(InvestigationValidationError):
            self.service.extract_entities(investigation.id, saved.id)

    def test_analyzes_and_histories_saved_url(self):
        investigation = self.service.create({"title": "URL analysis"})
        saved = self.service.save_page(
            investigation.id,
            {
                "url": "https://example.org/profile?utm_source=test",
                "title": "Profile",
                "description": "",
                "referrer": "",
            },
        )
        payload = {
            "requested_url": saved.url,
            "final_url": "https://example.org/profile?utm_source=test",
            "final_domain_unicode": "example.org",
            "final_domain_punycode": "example.org",
            "status_code": 200,
            "redirects": [],
            "headers": {"content-type": "text/html"},
            "content_type": "text/html",
            "content_length": 123,
            "bytes_read": 123,
            "content_sha256": "a" * 64,
            "content_truncated": False,
            "elapsed_ms": 25,
            "tracking_parameters": ["utm_source"],
            "cleaned_url": "https://example.org/profile",
        }
        analyzer_result = Mock()
        analyzer_result.to_payload.return_value = payload

        with patch(
            "investigations.service.analyze_url",
            return_value=analyzer_result,
        ):
            first = self.service.analyze_result_url(
                investigation.id,
                saved.id,
            )
            second = self.service.analyze_result_url(
                investigation.id,
                saved.id,
            )

        self.assertNotEqual(first["id"], second["id"])
        self.assertEqual(
            self.repository.table_count("url_analyses"),
            2,
        )
        workspace = self.service.workspace_payload(investigation.id)
        self.assertEqual(len(workspace["url_analyses"]), 2)
        self.assertEqual(
            workspace["url_analyses"][0]["tracking_parameters"],
            ["utm_source"],
        )

        self.service.remove_saved_page(investigation.id, saved.id)
        self.assertEqual(self.repository.table_count("url_analyses"), 0)

    def test_deletes_extracted_entity(self):
        investigation = self.service.create({"title": "Entity deletion"})
        saved = self.service.save_page(
            investigation.id,
            {
                "url": "https://example.org/profile",
                "title": "Profile",
                "description": "Contact jane@example.org.",
                "referrer": "",
            },
        )
        entity = next(
            item
            for item in self.service.extract_entities(
                investigation.id,
                saved.id,
            )
            if item["entity_type"] == "email"
        )

        self.service.delete_entity(investigation.id, entity["id"])

        entity_ids = {
            item["id"]
            for item in self.service.workspace_payload(
                investigation.id
            )["entities"]
        }
        self.assertNotIn(entity["id"], entity_ids)

    def test_records_zeroneurone_export_in_workspace(self):
        investigation = self.service.create({"title": "Export case"})

        recorded = self.service.record_export(
            investigation.id,
            archive_path="data/exports/case/export/zeroneurone.zip",
            dossier_path="data/exports/case/export/dossier.json",
            graphml_path="data/exports/case/export/investigation.graphml",
            csv_path="data/exports/case/export/zeroneurone.csv",
            nodes_csv_path="data/exports/case/export/nodes.csv",
            edges_csv_path="data/exports/case/export/edges.csv",
            manifest_path="data/exports/case/export/manifest.json",
            include_evidence=False,
            include_unreviewed=False,
            node_count=4,
            edge_count=3,
            asset_count=2,
            generated_at="2026-06-12T12:00:00+00:00",
        )

        self.assertEqual(recorded["node_count"], 4)
        self.assertEqual(recorded["asset_count"], 2)
        workspace = self.service.workspace_payload(investigation.id)
        self.assertEqual(workspace["exports"][0]["id"], recorded["id"])
        self.assertEqual(
            self.repository.table_count("investigation_exports"),
            1,
        )

        self.service.delete_export(investigation.id, recorded["id"])

        self.assertEqual(
            self.repository.table_count("investigation_exports"),
            0,
        )

    def test_manual_page_save_records_referrer_without_search_noise(self):
        investigation = self.service.create({"title": "Case"})

        saved = self.service.save_page(
            investigation.id,
            {
                "url": "https://example.org/profile",
                "title": "Profile",
                "description": "Public profile",
                "referrer": "https://example.org/directory",
            },
        )

        self.assertEqual(saved.discovery_method, "manual_browsing")
        self.assertEqual(saved.discovery_query, "")
        self.assertEqual(saved.discovery_sources, ())
        self.assertEqual(
            saved.discovery_referrer,
            "https://example.org/directory",
        )
        self.assertEqual(
            self.repository.get_investigation(investigation.id).result_count,
            1,
        )

        self.service.remove_saved_page(investigation.id, saved.id)

        self.assertEqual(
            self.repository.list_investigation_results(investigation.id),
            [],
        )
        self.assertEqual(self.repository.table_count("results"), 1)

    def test_page_save_preserves_existing_metadata_when_page_fields_are_empty(self):
        investigation = self.service.create({"title": "Case"})
        self.service.record_search(
            investigation_id=investigation.id,
            original_query="profile",
            parsed_query='"profile"',
            filters={},
            engines={"google": True},
            requested_results=10,
            report_path="profile.html",
            total_time=0.1,
            engine_errors={},
            results=[
                {
                    "title": "Known profile",
                    "link": "https://example.org/profile",
                    "description": "Description from the search result.",
                    "source": "Google",
                    "relevance_score": 10,
                }
            ],
        )

        saved = self.service.save_page(
            investigation.id,
            {
                "url": "https://example.org/profile",
                "title": "",
                "description": "",
                "referrer": "",
            },
        )

        self.assertEqual(saved.title, "Known profile")
        self.assertEqual(saved.description, "Description from the search result.")

    def test_revisiting_saved_page_updates_latest_seen(self):
        investigation = self.service.create({"title": "Case"})
        self.service.record_search(
            investigation_id=investigation.id,
            original_query="profile",
            parsed_query='"profile"',
            filters={},
            engines={"google": True},
            requested_results=10,
            report_path="profile.html",
            total_time=0.1,
            engine_errors={},
            results=[
                {
                    "title": "Known profile",
                    "link": "https://example.org/profile",
                    "description": "Description",
                    "source": "Google",
                    "relevance_score": 10,
                }
            ],
            started_at="2026-06-09T10:00:00+00:00",
        )
        saved = self.service.save_page(
            investigation.id,
            {
                "url": "https://example.org/profile",
                "title": "Known profile",
                "description": "Description",
                "referrer": "",
            },
        )

        with patch(
            "investigations.repository.utc_now",
            return_value="2027-06-10T12:30:00.000000+00:00",
        ):
            observed = self.service.observe_saved_page(
                investigation.id,
                {"url": "https://example.org/profile#details"},
            )

        refreshed = self.repository.list_investigation_results(
            investigation.id
        )[0]
        self.assertTrue(observed)
        self.assertEqual(refreshed.id, saved.id)
        self.assertEqual(
            refreshed.last_observed_at,
            "2027-06-10T12:30:00.000000+00:00",
        )
        self.assertEqual(
            refreshed.latest_observed_at,
            "2027-06-10T12:30:00.000000+00:00",
        )

    def test_visiting_unsaved_page_does_not_create_case_result(self):
        investigation = self.service.create({"title": "Case"})

        observed = self.service.observe_saved_page(
            investigation.id,
            {"url": "https://example.org/not-saved"},
        )

        self.assertFalse(observed)
        self.assertEqual(
            self.repository.list_investigation_results(investigation.id),
            [],
        )

    def test_records_evidence_for_saved_page(self):
        investigation = self.service.create({"title": "Case"})
        saved = self.service.save_page(
            investigation.id,
            {
                "url": "https://example.org/profile",
                "title": "Profile",
                "description": "",
                "referrer": "",
            },
        )

        capture = self.service.record_evidence_capture(
            capture_id="capture-1",
            investigation_id=investigation.id,
            result_id=saved.id,
            name="Profile header",
            source_url=saved.url,
            page_title=saved.title,
            capture_scope="region",
            selection={"x": 10, "y": 20, "width": 300, "height": 200},
            manifest_path="data/evidence/capture-1/manifest.json",
            captured_at="2026-06-10T10:00:00.000000+00:00",
            tool_version="test",
            artifacts=[
                {
                    "id": "artifact-1",
                    "artifact_type": "png",
                    "file_path": "data/evidence/capture-1/capture.png",
                    "mime_type": "image/png",
                    "sha256": "a" * 64,
                    "byte_size": 123,
                    "created_at": "2026-06-10T10:00:00.000000+00:00",
                }
            ],
        )

        self.assertEqual(capture.capture_scope, "region")
        self.assertEqual(capture.name, "Profile header")
        self.assertEqual(capture.result_id, saved.id)
        self.assertEqual(capture.selection["width"], 300)
        self.assertEqual(capture.artifacts[0].sha256, "a" * 64)
        workspace = self.service.workspace_payload(investigation.id)
        self.assertEqual(workspace["evidence"][0]["id"], "capture-1")
        self.assertEqual(self.repository.table_count("evidence_captures"), 1)
        self.assertEqual(self.repository.table_count("evidence_artifacts"), 1)
        indexed = self.service.search_local_archive({"query": "profile"})
        self.assertEqual(indexed[0]["evidence_count"], 1)
        with self.assertRaises(InvestigationValidationError):
            self.service.remove_saved_page(investigation.id, saved.id)

        self.service.delete_evidence_capture(
            investigation.id,
            capture.id,
        )
        self.assertEqual(self.repository.table_count("evidence_captures"), 0)
        self.assertEqual(self.repository.table_count("evidence_artifacts"), 0)
        indexed = self.service.search_local_archive({"query": "profile"})
        self.assertEqual(indexed[0]["evidence_count"], 0)
        self.service.remove_saved_page(investigation.id, saved.id)

    def test_page_monitor_tracks_archive_comparisons(self):
        investigation = self.service.create({"title": "Watch page"})
        saved = self.service.save_page(
            investigation.id,
            {
                "url": "https://example.org/watch",
                "title": "Watched page",
                "description": "",
                "referrer": "",
            },
        )
        monitor = self.service.create_page_monitor(
            investigation.id,
            saved.id,
        )
        self.assertIsNone(monitor.last_capture_id)

        def record_archive(capture_id: str, captured_at: str):
            return self.service.record_evidence_capture(
                capture_id=capture_id,
                investigation_id=investigation.id,
                result_id=saved.id,
                name=capture_id,
                source_url=saved.url,
                page_title=saved.title,
                capture_scope="viewport",
                selection={},
                manifest_path=f"data/evidence/{capture_id}/manifest.json",
                captured_at=captured_at,
                tool_version="test",
                capture_kind="page_archive",
                artifacts=[
                    {
                        "id": f"artifact-{capture_id}",
                        "artifact_type": "text",
                        "file_path": f"data/evidence/{capture_id}/page.txt",
                        "mime_type": "text/plain; charset=utf-8",
                        "sha256": "a" * 64,
                        "byte_size": 10,
                        "created_at": captured_at,
                    }
                ],
            )

        first = record_archive(
            "archive-1",
            "2026-06-10T10:00:00.000000+00:00",
        )
        self.service.advance_page_monitor(
            investigation.id,
            monitor.id,
            first.id,
        )
        second = record_archive(
            "archive-2",
            "2026-06-11T10:00:00.000000+00:00",
        )
        comparison = self.service.record_page_comparison(
            investigation_id=investigation.id,
            monitor_id=monitor.id,
            previous_capture_id=first.id,
            current_capture_id=second.id,
            status="changed",
            similarity=0.5,
            previous_sha256="a" * 64,
            current_sha256="b" * 64,
            report_path="data/evidence/archive-2/comparison.html",
            generated_at="2026-06-11T10:00:00.000000+00:00",
        )

        workspace = self.service.workspace_payload(investigation.id)
        refreshed = workspace["page_monitors"][0]
        self.assertEqual(refreshed["archive_count"], 2)
        self.assertEqual(refreshed["last_capture_id"], second.id)
        self.assertEqual(refreshed["comparison_status"], "changed")
        self.assertEqual(
            self.repository.table_count("page_comparisons"),
            1,
        )
        self.assertEqual(comparison.current_capture_id, second.id)

        self.service.delete_page_monitor(investigation.id, monitor.id)
        self.assertEqual(self.repository.table_count("page_monitors"), 0)
        self.assertEqual(self.repository.table_count("page_comparisons"), 0)

    def test_attaches_unassigned_search_and_results(self):
        investigation = self.service.create({"title": "Case"})
        search_id = self.service.record_search(
            investigation_id=None,
            original_query="unassigned query",
            parsed_query='"unassigned query"',
            filters={"site": "example.com"},
            engines={"google": True},
            requested_results=10,
            report_path="unassigned.html",
            total_time=0.25,
            engine_errors={},
            results=[
                {
                    "title": "Unassigned query result",
                    "link": "https://example.com/unassigned",
                    "description": "Description",
                    "source": "Google",
                    "relevance_score": 5,
                }
            ],
        )

        before = self.service.workspace_payload(investigation.id)
        self.assertEqual(before["results"], [])
        self.assertEqual(before["unassigned_searches"][0]["id"], search_id)

        attached = self.service.attach_search(investigation.id, search_id)
        after = self.service.workspace_payload(investigation.id)

        self.assertEqual(attached.id, search_id)
        self.assertEqual(after["searches"][0]["id"], search_id)
        self.assertEqual(after["results"], [])
        self.assertEqual(after["unassigned_searches"], [])

        saved = self.service.save_page(
            investigation.id,
            {
                "url": "https://example.com/unassigned",
                "title": "Unassigned query result",
                "description": "Description",
                "referrer": "",
            },
        )
        self.assertEqual(saved.discovery_query, "unassigned query")
        self.assertEqual(saved.discovery_sources, ("Google",))

    def test_saved_page_uses_unassigned_search_provenance_and_observations(self):
        investigation = self.service.create({"title": "Case"})
        self.service.record_search(
            investigation_id=None,
            original_query="salmon pasta",
            parsed_query='"salmon pasta"',
            filters={},
            engines={"duckduckgo": True},
            requested_results=10,
            report_path="unassigned.html",
            total_time=0.25,
            engine_errors={},
            results=[
                {
                    "title": "Salmon pasta",
                    "link": "https://example.com/salmon-pasta",
                    "description": "Recipe collection",
                    "source": "DuckDuckGo",
                    "relevance_score": 7,
                }
            ],
        )

        saved = self.service.save_page(
            investigation.id,
            {
                "url": "https://example.com/salmon-pasta",
                "title": "Salmon pasta",
                "description": "Recipe collection",
                "referrer": "",
            },
        )

        self.assertEqual(saved.sources, ("DuckDuckGo",))
        self.assertEqual(saved.discovery_method, "search_result")
        self.assertEqual(saved.discovery_query, "salmon pasta")
        self.assertEqual(saved.discovery_sources, ("DuckDuckGo",))
        self.assertEqual(saved.observation_count, 1)
        self.assertEqual(saved.relevance_score, 7)

    def test_imports_legacy_history_only_once(self):
        second_temp = TemporaryDirectory()
        try:
            history_path = Path(second_temp.name) / "history.json"
            history_path.write_text(
                json.dumps(
                    [
                        {
                            "date": "09/06/2026 12:00",
                            "query": "legacy query",
                            "smart_query": '"legacy query"',
                            "nb_results": 3,
                            "link": "legacy.html",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            repository = InvestigationRepository(
                Path(second_temp.name) / "database" / "synthesix.db"
            )
            service = InvestigationService(repository)

            self.assertEqual(service.initialize(history_path), 1)
            self.assertEqual(service.initialize(history_path), 0)
            self.assertEqual(repository.table_count("search_runs"), 1)
        finally:
            second_temp.cleanup()

    def test_canonicalize_url_removes_fragment_credentials_and_default_port(self):
        self.assertEqual(
            canonicalize_url("HTTPS://user:pass@Example.COM:443/path?q=1#fragment"),
            "https://example.com/path?q=1",
        )


if __name__ == "__main__":
    unittest.main()
