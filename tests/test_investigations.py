import json
import sqlite3
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from exceptions import InvestigationHasDataError, InvestigationValidationError
from investigations.migrations import MIGRATIONS
from investigations.repository import InvestigationRepository, canonicalize_url
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
        self.assertEqual(self.repository.schema_version(), 2)

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

            self.assertEqual(repository.schema_version(), 2)
            self.assertEqual(repository.table_count("investigation_results"), 1)
            self.assertEqual(repository.get_investigation("case-1").result_count, 0)
            self.assertEqual(repository.list_investigation_results("case-1"), [])

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
        self.assertEqual(created.tags, ("person", "priority"))
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
        self.assertEqual(updated.tags, ("company", "registry"))
        self.assertEqual(updated.sources, ("Bing", "Google"))
        self.assertEqual(updated.discovery_sources, ("Bing", "Google"))
        self.assertEqual(updated.discovery_query, "example company")
        self.assertEqual(updated.discovery_method, "search_result")
        self.assertEqual(updated.relevance_score, 8.5)
        self.assertEqual(updated.observation_count, 1)

        workspace = self.service.workspace_payload(investigation.id)
        self.assertEqual(workspace["results"][0]["analyst_status"], "confirme")
        self.assertEqual(workspace["searches"][0]["original_query"], "example company")

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
            return_value="2026-06-10T12:30:00.000000+00:00",
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
            "2026-06-10T12:30:00.000000+00:00",
        )
        self.assertEqual(
            refreshed.latest_observed_at,
            "2026-06-10T12:30:00.000000+00:00",
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
