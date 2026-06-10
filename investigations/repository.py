from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping
from urllib.parse import urlsplit, urlunsplit
from uuid import NAMESPACE_URL, uuid4, uuid5

from exceptions import (
    InvestigationHasDataError,
    InvestigationNotFoundError,
    InvestigationResultNotFoundError,
    InvestigationValidationError,
    SearchRunNotFoundError,
)
from investigations.migrations import MIGRATIONS
from investigations.models import (
    ANALYST_STATUSES,
    EvidenceArtifact,
    EvidenceCapture,
    Investigation,
    InvestigationResult,
    InvestigationSearchRun,
)


LEGACY_IMPORT_KEY = "legacy_history_import_v1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def canonicalize_url(value: str) -> str:
    value = str(value or "").strip()
    if not value:
        return ""

    try:
        parsed = urlsplit(value)
        if not parsed.scheme or not parsed.hostname:
            return value

        scheme = parsed.scheme.lower()
        hostname = parsed.hostname.lower()
        try:
            port = parsed.port
        except ValueError:
            port = None
        if port and not (
            (scheme == "http" and port == 80)
            or (scheme == "https" and port == 443)
        ):
            netloc = f"{hostname}:{port}"
        else:
            netloc = hostname
        return urlunsplit((scheme, netloc, parsed.path or "/", parsed.query, ""))
    except (TypeError, ValueError):
        return value


def _json_dump(value) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _json_load(value: str, fallback):
    try:
        loaded = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return fallback
    return loaded


class InvestigationRepository:
    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)

    def _connect(self) -> sqlite3.Connection:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path, timeout=5.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        return connection

    @contextmanager
    def _connection(self):
        connection = self._connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        with self._connection() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                )
                """
            )
            applied = {
                int(row["version"])
                for row in connection.execute("SELECT version FROM schema_migrations")
            }

        for version, sql in MIGRATIONS:
            if version in applied:
                continue
            applied_at = utc_now().replace("'", "''")
            migration = (
                "BEGIN IMMEDIATE;\n"
                + sql
                + "\nINSERT INTO schema_migrations(version, applied_at) "
                + f"VALUES ({int(version)}, '{applied_at}');\n"
                + "COMMIT;"
            )
            connection = self._connect()
            try:
                connection.executescript(migration)
            except Exception:
                connection.rollback()
                raise
            finally:
                connection.close()

    def schema_version(self) -> int:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT COALESCE(MAX(version), 0) AS version FROM schema_migrations"
            ).fetchone()
        return int(row["version"])

    def _row_to_investigation(self, row: sqlite3.Row) -> Investigation:
        tags = _json_load(row["tags_json"], [])
        return Investigation(
            id=row["id"],
            title=row["title"],
            reference=row["reference"],
            description=row["description"],
            tags=tuple(str(tag) for tag in tags if str(tag).strip()),
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            archived_at=row["archived_at"],
            search_count=int(row["search_count"] or 0),
            result_count=int(row["result_count"] or 0),
        )

    def _row_to_search_run(self, row: sqlite3.Row) -> InvestigationSearchRun:
        filters = _json_load(row["filters_json"], {})
        engines = _json_load(row["engines_json"], {})
        engine_errors = _json_load(row["engine_errors_json"], {})
        return InvestigationSearchRun(
            id=row["id"],
            original_query=row["original_query"],
            parsed_query=row["parsed_query"],
            filters=filters if isinstance(filters, dict) else {},
            engines=engines if isinstance(engines, dict) else {},
            requested_results=int(row["requested_results"] or 0),
            result_count=int(row["result_count"] or 0),
            total_time=float(row["total_time"] or 0),
            report_path=row["report_path"],
            status=row["status"],
            engine_errors=engine_errors if isinstance(engine_errors, dict) else {},
            started_at=row["started_at"],
            completed_at=row["completed_at"],
        )

    def create_investigation(
        self,
        title: str,
        *,
        reference: str = "",
        description: str = "",
        tags: Iterable[str] = (),
    ) -> Investigation:
        investigation_id = str(uuid4())
        now = utc_now()
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO investigations(
                    id, title, reference, description, tags_json, status,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, 'active', ?, ?)
                """,
                (
                    investigation_id,
                    title,
                    reference,
                    description,
                    _json_dump(list(tags)),
                    now,
                    now,
                ),
            )
        return self.get_investigation(investigation_id)

    def get_investigation(self, investigation_id: str) -> Investigation:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT
                    i.*,
                    COUNT(DISTINCT sr.id) AS search_count,
                    COUNT(DISTINCT ir.result_id) AS result_count
                FROM investigations i
                LEFT JOIN search_runs sr ON sr.investigation_id = i.id
                LEFT JOIN investigation_results ir
                    ON ir.investigation_id = i.id
                    AND ir.is_saved = 1
                WHERE i.id = ?
                GROUP BY i.id
                """,
                (investigation_id,),
            ).fetchone()
        if row is None:
            raise InvestigationNotFoundError(investigation_id)
        return self._row_to_investigation(row)

    def list_investigations(self, *, include_archived: bool = False) -> list[Investigation]:
        where = "" if include_archived else "WHERE i.status = 'active'"
        with self._connection() as connection:
            rows = connection.execute(
                f"""
                SELECT
                    i.*,
                    COUNT(DISTINCT sr.id) AS search_count,
                    COUNT(DISTINCT ir.result_id) AS result_count
                FROM investigations i
                LEFT JOIN search_runs sr ON sr.investigation_id = i.id
                LEFT JOIN investigation_results ir
                    ON ir.investigation_id = i.id
                    AND ir.is_saved = 1
                {where}
                GROUP BY i.id
                ORDER BY
                    CASE i.status WHEN 'active' THEN 0 ELSE 1 END,
                    i.updated_at DESC,
                    i.title COLLATE NOCASE
                """
            ).fetchall()
        return [self._row_to_investigation(row) for row in rows]

    def update_investigation(
        self,
        investigation_id: str,
        *,
        title: str,
        reference: str,
        description: str,
        tags: Iterable[str],
    ) -> Investigation:
        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE investigations
                SET title = ?, reference = ?, description = ?, tags_json = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    title,
                    reference,
                    description,
                    _json_dump(list(tags)),
                    utc_now(),
                    investigation_id,
                ),
            )
            if cursor.rowcount == 0:
                raise InvestigationNotFoundError(investigation_id)
        return self.get_investigation(investigation_id)

    def archive_investigation(self, investigation_id: str) -> Investigation:
        now = utc_now()
        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE investigations
                SET status = 'archived', archived_at = ?, updated_at = ?
                WHERE id = ? AND status = 'active'
                """,
                (now, now, investigation_id),
            )
            if cursor.rowcount == 0:
                self.get_investigation(investigation_id)
        return self.get_investigation(investigation_id)

    def list_investigation_results(
        self,
        investigation_id: str,
    ) -> list[InvestigationResult]:
        self.get_investigation(investigation_id)
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    r.id,
                    r.canonical_url,
                    r.url,
                    r.title,
                    r.description,
                    r.first_observed_at,
                    r.last_observed_at,
                    ir.analyst_status,
                    ir.favorite,
                    ir.notes,
                    ir.tags_json,
                    ir.added_at,
                    ir.updated_at,
                    ir.discovery_method,
                    ir.discovery_query,
                    ir.discovery_sources_json,
                    ir.discovery_report_path,
                    ir.discovery_observed_at,
                    ir.discovery_referrer,
                    COALESCE(MAX(o.relevance_score), 0) AS relevance_score,
                    COALESCE(
                        (
                            SELECT o2.score_breakdown_json
                            FROM search_result_observations o2
                            JOIN search_runs sr2 ON sr2.id = o2.search_run_id
                            WHERE
                                o2.result_id = r.id
                                AND (
                                    sr2.investigation_id = ?
                                    OR sr2.investigation_id IS NULL
                                )
                            ORDER BY o2.relevance_score DESC, o2.observed_at DESC
                            LIMIT 1
                        ),
                        '[]'
                    ) AS score_breakdown_json,
                    MAX(
                        r.last_observed_at,
                        COALESCE(MAX(o.observed_at), r.last_observed_at)
                    ) AS latest_observed_at,
                    COUNT(DISTINCT o.search_run_id) AS observation_count,
                    GROUP_CONCAT(o.source_json, char(31)) AS source_payloads
                FROM investigation_results ir
                JOIN results r ON r.id = ir.result_id
                LEFT JOIN search_result_observations o
                    ON o.result_id = r.id
                    AND o.search_run_id IN (
                        SELECT id
                        FROM search_runs
                        WHERE
                            investigation_id = ?
                            OR investigation_id IS NULL
                    )
                WHERE ir.investigation_id = ? AND ir.is_saved = 1
                GROUP BY r.id, ir.investigation_id
                ORDER BY
                    ir.favorite DESC,
                    CASE ir.analyst_status
                        WHEN 'confirme' THEN 0
                        WHEN 'pertinent' THEN 1
                        WHEN 'a_verifier' THEN 2
                        ELSE 3
                    END,
                    latest_observed_at DESC
                """,
                (investigation_id, investigation_id, investigation_id),
            ).fetchall()

        results = []
        for row in rows:
            sources = set()
            for payload in str(row["source_payloads"] or "").split("\x1f"):
                loaded = _json_load(payload, [])
                if isinstance(loaded, list):
                    sources.update(str(source).strip() for source in loaded if str(source).strip())
            tags = _json_load(row["tags_json"], [])
            discovery_sources = _json_load(
                row["discovery_sources_json"],
                [],
            )
            score_breakdown = _json_load(row["score_breakdown_json"], [])
            if not isinstance(score_breakdown, list):
                score_breakdown = []
            results.append(
                InvestigationResult(
                    id=row["id"],
                    canonical_url=row["canonical_url"],
                    url=row["url"],
                    title=row["title"],
                    description=row["description"],
                    sources=tuple(sorted(sources, key=str.casefold)),
                    first_observed_at=row["first_observed_at"],
                    last_observed_at=row["last_observed_at"],
                    latest_observed_at=row["latest_observed_at"],
                    relevance_score=float(row["relevance_score"] or 0),
                    score_breakdown=tuple(
                        dict(component)
                        for component in score_breakdown
                        if isinstance(component, dict)
                    ),
                    observation_count=int(row["observation_count"] or 0),
                    analyst_status=row["analyst_status"],
                    favorite=bool(row["favorite"]),
                    notes=row["notes"],
                    tags=tuple(str(tag) for tag in tags if str(tag).strip()),
                    added_at=row["added_at"],
                    updated_at=row["updated_at"],
                    discovery_method=row["discovery_method"],
                    discovery_query=row["discovery_query"],
                    discovery_sources=tuple(
                        str(source)
                        for source in discovery_sources
                        if str(source).strip()
                    ),
                    discovery_report_path=row["discovery_report_path"],
                    discovery_observed_at=row["discovery_observed_at"],
                    discovery_referrer=row["discovery_referrer"],
                )
            )
        return results

    def list_investigation_searches(
        self,
        investigation_id: str,
    ) -> list[InvestigationSearchRun]:
        self.get_investigation(investigation_id)
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM search_runs
                WHERE investigation_id = ?
                ORDER BY started_at DESC, id DESC
                """,
                (investigation_id,),
            ).fetchall()
        return [self._row_to_search_run(row) for row in rows]

    def list_unassigned_searches(self, *, limit: int = 100) -> list[InvestigationSearchRun]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM search_runs
                WHERE investigation_id IS NULL
                ORDER BY started_at DESC, id DESC
                LIMIT ?
                """,
                (max(1, int(limit)),),
            ).fetchall()
        return [self._row_to_search_run(row) for row in rows]

    def update_investigation_result(
        self,
        investigation_id: str,
        result_id: str,
        *,
        analyst_status: str,
        favorite: bool,
        notes: str,
        tags: Iterable[str],
    ) -> InvestigationResult:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        if analyst_status not in ANALYST_STATUSES:
            raise InvestigationValidationError(
                f"Unsupported analyst status: {analyst_status}"
            )

        now = utc_now()
        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE investigation_results
                SET analyst_status = ?, favorite = ?, notes = ?,
                    tags_json = ?, updated_at = ?
                WHERE
                    investigation_id = ?
                    AND result_id = ?
                    AND is_saved = 1
                """,
                (
                    analyst_status,
                    int(bool(favorite)),
                    notes,
                    _json_dump(list(tags)),
                    now,
                    investigation_id,
                    result_id,
                ),
            )
            if cursor.rowcount == 0:
                raise InvestigationResultNotFoundError(
                    investigation_id,
                    result_id,
                )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (now, investigation_id),
            )

        return next(
            result
            for result in self.list_investigation_results(investigation_id)
            if result.id == result_id
        )

    def attach_search(
        self,
        investigation_id: str,
        search_run_id: str,
    ) -> InvestigationSearchRun:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )

        now = utc_now()
        with self._connection() as connection:
            search = connection.execute(
                "SELECT investigation_id FROM search_runs WHERE id = ?",
                (search_run_id,),
            ).fetchone()
            if search is None:
                raise SearchRunNotFoundError(search_run_id)
            if search["investigation_id"] is not None:
                raise InvestigationValidationError(
                    "This search is already attached to an investigation."
                )

            connection.execute(
                "UPDATE search_runs SET investigation_id = ? WHERE id = ?",
                (investigation_id, search_run_id),
            )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (now, investigation_id),
            )

        return next(
            search
            for search in self.list_investigation_searches(investigation_id)
            if search.id == search_run_id
        )

    def save_page(
        self,
        investigation_id: str,
        *,
        url: str,
        title: str,
        description: str,
        referrer: str,
    ) -> InvestigationResult:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )

        canonical_url = canonicalize_url(url)
        if not canonical_url:
            raise InvestigationValidationError("A valid page URL is required.")

        now = utc_now()
        with self._connection() as connection:
            result_row = connection.execute(
                """
                SELECT id, title, description
                FROM results
                WHERE canonical_url = ?
                """,
                (canonical_url,),
            ).fetchone()
            if result_row is None:
                result_id = str(uuid4())
                connection.execute(
                    """
                    INSERT INTO results(
                        id, canonical_url, url, title, description,
                        first_observed_at, last_observed_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        result_id,
                        canonical_url,
                        url,
                        title,
                        description,
                        now,
                        now,
                    ),
                )
            else:
                result_id = result_row["id"]
                retained_title = title or result_row["title"]
                retained_description = description or result_row["description"]
                connection.execute(
                    """
                    UPDATE results
                    SET url = ?, title = ?, description = ?, last_observed_at = ?
                    WHERE id = ?
                    """,
                    (
                        url,
                        retained_title,
                        retained_description,
                        now,
                        result_id,
                    ),
                )

            discovery = connection.execute(
                """
                SELECT
                    sr.id AS search_run_id,
                    sr.original_query,
                    sr.parsed_query,
                    sr.report_path,
                    o.source_json,
                    o.observed_at
                FROM search_result_observations o
                JOIN search_runs sr ON sr.id = o.search_run_id
                WHERE
                    o.result_id = ?
                    AND (
                        sr.investigation_id = ?
                        OR sr.investigation_id IS NULL
                    )
                ORDER BY
                    CASE
                        WHEN sr.investigation_id = ? THEN 0
                        ELSE 1
                    END,
                    o.observed_at DESC,
                    sr.started_at DESC
                LIMIT 1
                """,
                (result_id, investigation_id, investigation_id),
            ).fetchone()

            if discovery is None:
                discovery_method = "manual_browsing"
                discovery_search_run_id = None
                discovery_query = ""
                discovery_sources = []
                discovery_report_path = None
                discovery_observed_at = now
            else:
                discovery_method = "search_result"
                discovery_search_run_id = discovery["search_run_id"]
                discovery_query = (
                    discovery["original_query"]
                    or discovery["parsed_query"]
                    or ""
                )
                discovery_sources = _json_load(discovery["source_json"], [])
                discovery_report_path = discovery["report_path"]
                discovery_observed_at = discovery["observed_at"]

            connection.execute(
                """
                INSERT INTO investigation_results(
                    investigation_id, result_id, analyst_status,
                    favorite, notes, tags_json, added_at, updated_at,
                    is_saved, discovery_method, discovery_search_run_id,
                    discovery_query, discovery_sources_json,
                    discovery_report_path, discovery_observed_at,
                    discovery_referrer
                )
                VALUES (
                    ?, ?, 'a_verifier', 0, '', '[]', ?, ?,
                    1, ?, ?, ?, ?, ?, ?, ?
                )
                ON CONFLICT(investigation_id, result_id) DO UPDATE SET
                    is_saved = 1,
                    discovery_method = excluded.discovery_method,
                    discovery_search_run_id = excluded.discovery_search_run_id,
                    discovery_query = excluded.discovery_query,
                    discovery_sources_json = excluded.discovery_sources_json,
                    discovery_report_path = excluded.discovery_report_path,
                    discovery_observed_at = excluded.discovery_observed_at,
                    discovery_referrer = excluded.discovery_referrer,
                    updated_at = excluded.updated_at
                """,
                (
                    investigation_id,
                    result_id,
                    now,
                    now,
                    discovery_method,
                    discovery_search_run_id,
                    discovery_query,
                    _json_dump(discovery_sources),
                    discovery_report_path,
                    discovery_observed_at,
                    referrer,
                ),
            )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (now, investigation_id),
            )

        return next(
            result
            for result in self.list_investigation_results(investigation_id)
            if result.id == result_id
        )

    def observe_saved_page(
        self,
        investigation_id: str,
        *,
        url: str,
    ) -> bool:
        canonical_url = canonicalize_url(url)
        if not canonical_url:
            return False

        now = utc_now()
        with self._connection() as connection:
            result = connection.execute(
                """
                SELECT r.id
                FROM investigation_results ir
                JOIN results r ON r.id = ir.result_id
                WHERE
                    ir.investigation_id = ?
                    AND ir.is_saved = 1
                    AND r.canonical_url = ?
                """,
                (investigation_id, canonical_url),
            ).fetchone()
            if result is None:
                return False

            connection.execute(
                """
                UPDATE results
                SET url = ?, last_observed_at = ?
                WHERE id = ?
                """,
                (url, now, result["id"]),
            )
            connection.execute(
                """
                UPDATE investigation_results
                SET updated_at = ?
                WHERE investigation_id = ? AND result_id = ?
                """,
                (now, investigation_id, result["id"]),
            )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (now, investigation_id),
            )
        return True

    def remove_saved_page(
        self,
        investigation_id: str,
        result_id: str,
    ) -> None:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )

        with self._connection() as connection:
            evidence = connection.execute(
                """
                SELECT 1
                FROM evidence_captures
                WHERE investigation_id = ? AND result_id = ?
                LIMIT 1
                """,
                (investigation_id, result_id),
            ).fetchone()
            if evidence is not None:
                raise InvestigationValidationError(
                    "This page has captured evidence and cannot be removed."
                )

            cursor = connection.execute(
                """
                DELETE FROM investigation_results
                WHERE
                    investigation_id = ?
                    AND result_id = ?
                    AND is_saved = 1
                """,
                (investigation_id, result_id),
            )
            if cursor.rowcount == 0:
                raise InvestigationResultNotFoundError(
                    investigation_id,
                    result_id,
                )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (utc_now(), investigation_id),
            )

    def delete_investigation(self, investigation_id: str) -> None:
        investigation = self.get_investigation(investigation_id)
        if investigation.search_count or investigation.result_count:
            raise InvestigationHasDataError(
                investigation_id,
                search_count=investigation.search_count,
                result_count=investigation.result_count,
            )
        with self._connection() as connection:
            cursor = connection.execute(
                "DELETE FROM investigations WHERE id = ?",
                (investigation_id,),
            )
            if cursor.rowcount == 0:
                raise InvestigationNotFoundError(investigation_id)

    def record_search(
        self,
        *,
        investigation_id: str | None,
        original_query: str,
        parsed_query: str,
        filters: Mapping,
        engines: Mapping[str, bool],
        requested_results: int,
        report_path: str | None,
        total_time: float,
        engine_errors: Mapping[str, Exception],
        results: Iterable[Mapping],
        started_at: str | None = None,
    ) -> str:
        if investigation_id:
            investigation = self.get_investigation(investigation_id)
            if investigation.status != "active":
                raise InvestigationNotFoundError(investigation_id)

        search_id = str(uuid4())
        started_at = started_at or utc_now()
        completed_at = utc_now()
        result_rows = list(results)
        error_payload = {
            str(engine): {
                "type": type(error).__name__,
                "message": str(error),
            }
            for engine, error in engine_errors.items()
        }

        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO search_runs(
                    id, investigation_id, original_query, parsed_query,
                    filters_json, engines_json, requested_results, result_count,
                    total_time, report_path, status, engine_errors_json,
                    started_at, completed_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'completed', ?, ?, ?)
                """,
                (
                    search_id,
                    investigation_id,
                    original_query,
                    parsed_query,
                    _json_dump(dict(filters)),
                    _json_dump(dict(engines)),
                    int(requested_results),
                    len(result_rows),
                    float(total_time),
                    report_path,
                    _json_dump(error_payload),
                    started_at,
                    completed_at,
                ),
            )

            for result in result_rows:
                url = str(result.get("link", "") or "").strip()
                canonical_url = canonicalize_url(url)
                if not canonical_url:
                    continue

                title = str(result.get("title", "") or "")
                description = str(result.get("description", "") or "")
                result_row = connection.execute(
                    "SELECT id FROM results WHERE canonical_url = ?",
                    (canonical_url,),
                ).fetchone()
                if result_row is None:
                    result_id = str(uuid4())
                    connection.execute(
                        """
                        INSERT INTO results(
                            id, canonical_url, url, title, description,
                            first_observed_at, last_observed_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            result_id,
                            canonical_url,
                            url,
                            title,
                            description,
                            completed_at,
                            completed_at,
                        ),
                    )
                else:
                    result_id = result_row["id"]
                    connection.execute(
                        """
                        UPDATE results
                        SET url = ?, title = ?, description = ?, last_observed_at = ?
                        WHERE id = ?
                        """,
                        (url, title, description, completed_at, result_id),
                    )

                sources = [
                    source.strip()
                    for source in str(result.get("source", "") or "").split(",")
                    if source.strip()
                ]
                connection.execute(
                    """
                    INSERT INTO search_result_observations(
                        search_run_id, result_id, source_json, title,
                        description, relevance_score, score_breakdown_json,
                        observed_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        search_id,
                        result_id,
                        _json_dump(sorted(set(sources))),
                        title,
                        description,
                        float(result.get("relevance_score", 0) or 0),
                        _json_dump(
                            result.get("score_breakdown", [])
                            if isinstance(result.get("score_breakdown", []), list)
                            else []
                        ),
                        completed_at,
                    ),
                )

            if investigation_id:
                connection.execute(
                    "UPDATE investigations SET updated_at = ? WHERE id = ?",
                    (completed_at, investigation_id),
                )
        return search_id

    def import_legacy_history(self, entries: Iterable[Mapping]) -> int:
        with self._connection() as connection:
            marker = connection.execute(
                "SELECT value FROM app_metadata WHERE key = ?",
                (LEGACY_IMPORT_KEY,),
            ).fetchone()
            if marker is not None:
                return 0

            imported = 0
            for index, entry in enumerate(entries):
                original_query = str(entry.get("query", "") or "").strip()
                parsed_query = str(entry.get("smart_query", "") or "").strip()
                if not original_query and not parsed_query:
                    continue

                source_payload = _json_dump(
                    {
                        "date": entry.get("date", ""),
                        "timestamp": entry.get("timestamp", ""),
                        "query": original_query,
                        "smart_query": parsed_query,
                        "link": entry.get("link", ""),
                        "index": index,
                    }
                )
                source_key = hashlib.sha256(source_payload.encode("utf-8")).hexdigest()
                search_id = str(uuid5(NAMESPACE_URL, f"synthesix:{source_key}"))
                started_at = str(
                    entry.get("timestamp")
                    or entry.get("date")
                    or utc_now()
                )
                cursor = connection.execute(
                    """
                    INSERT OR IGNORE INTO search_runs(
                        id, investigation_id, original_query, parsed_query,
                        filters_json, engines_json, requested_results, result_count,
                        total_time, report_path, status, engine_errors_json, started_at,
                        completed_at, legacy_source_key
                    )
                    VALUES (?, NULL, ?, ?, ?, '{}', 0, ?, 0, ?, 'legacy', '{}', ?, ?, ?)
                    """,
                    (
                        search_id,
                        original_query,
                        parsed_query,
                        _json_dump(entry.get("filters", {})),
                        int(entry.get("nb_results", 0) or 0),
                        str(entry.get("link", "") or "") or None,
                        started_at,
                        started_at,
                        source_key,
                    ),
                )
                imported += max(0, cursor.rowcount)

            now = utc_now()
            connection.execute(
                """
                INSERT INTO app_metadata(key, value, updated_at)
                VALUES (?, ?, ?)
                """,
                (LEGACY_IMPORT_KEY, str(imported), now),
            )
        return imported

    def clear_search_history(self) -> int:
        with self._connection() as connection:
            search_count = int(
                connection.execute("SELECT COUNT(*) AS count FROM search_runs").fetchone()["count"]
            )
            connection.execute(
                "DELETE FROM investigation_results WHERE is_saved = 0"
            )
            connection.execute("DELETE FROM search_runs")
            connection.execute(
                """
                DELETE FROM results
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM search_result_observations observation
                    WHERE observation.result_id = results.id
                )
                AND NOT EXISTS (
                    SELECT 1
                    FROM investigation_results saved
                    WHERE
                        saved.result_id = results.id
                        AND saved.is_saved = 1
                )
                """
            )
        return search_count

    def record_evidence_capture(
        self,
        *,
        capture_id: str,
        investigation_id: str,
        result_id: str,
        name: str,
        source_url: str,
        page_title: str,
        capture_scope: str,
        selection: Mapping,
        manifest_path: str,
        captured_at: str,
        tool_version: str,
        artifacts: Iterable[Mapping],
        status: str = "completed",
        error: str = "",
    ) -> EvidenceCapture:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        if capture_scope not in {"viewport", "region"}:
            raise InvestigationValidationError(
                "Unsupported evidence capture scope."
            )

        artifact_rows = [dict(artifact) for artifact in artifacts]
        with self._connection() as connection:
            saved_result = connection.execute(
                """
                SELECT 1
                FROM investigation_results
                WHERE
                    investigation_id = ?
                    AND result_id = ?
                    AND is_saved = 1
                """,
                (investigation_id, result_id),
            ).fetchone()
            if saved_result is None:
                raise InvestigationResultNotFoundError(
                    investigation_id,
                    result_id,
                )

            connection.execute(
                """
                INSERT INTO evidence_captures(
                    id, investigation_id, result_id, name, source_url, page_title,
                    capture_scope, selection_json, manifest_path, captured_at,
                    status, error, tool_version
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    capture_id,
                    investigation_id,
                    result_id,
                    name,
                    source_url,
                    page_title,
                    capture_scope,
                    _json_dump(dict(selection)),
                    manifest_path,
                    captured_at,
                    status,
                    error,
                    tool_version,
                ),
            )
            for artifact in artifact_rows:
                connection.execute(
                    """
                    INSERT INTO evidence_artifacts(
                        id, capture_id, artifact_type, file_path, mime_type,
                        sha256, byte_size, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(artifact["id"]),
                        capture_id,
                        str(artifact["artifact_type"]),
                        str(artifact["file_path"]),
                        str(artifact["mime_type"]),
                        str(artifact["sha256"]),
                        int(artifact["byte_size"]),
                        str(artifact["created_at"]),
                    ),
                )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (captured_at, investigation_id),
            )

        return next(
            capture
            for capture in self.list_evidence_captures(investigation_id)
            if capture.id == capture_id
        )

    def list_evidence_captures(
        self,
        investigation_id: str,
    ) -> list[EvidenceCapture]:
        self.get_investigation(investigation_id)
        with self._connection() as connection:
            capture_rows = connection.execute(
                """
                SELECT *
                FROM evidence_captures
                WHERE investigation_id = ?
                ORDER BY captured_at DESC
                """,
                (investigation_id,),
            ).fetchall()
            artifact_rows = connection.execute(
                """
                SELECT artifact.*
                FROM evidence_artifacts artifact
                JOIN evidence_captures capture
                    ON capture.id = artifact.capture_id
                WHERE capture.investigation_id = ?
                ORDER BY artifact.created_at, artifact.artifact_type
                """,
                (investigation_id,),
            ).fetchall()

        artifacts_by_capture: dict[str, list[EvidenceArtifact]] = {}
        for row in artifact_rows:
            artifacts_by_capture.setdefault(row["capture_id"], []).append(
                EvidenceArtifact(
                    id=row["id"],
                    artifact_type=row["artifact_type"],
                    file_path=row["file_path"],
                    mime_type=row["mime_type"],
                    sha256=row["sha256"],
                    byte_size=int(row["byte_size"] or 0),
                    created_at=row["created_at"],
                )
            )

        return [
            EvidenceCapture(
                id=row["id"],
                investigation_id=row["investigation_id"],
                result_id=row["result_id"],
                name=row["name"],
                source_url=row["source_url"],
                page_title=row["page_title"],
                capture_scope=row["capture_scope"],
                selection=_json_load(row["selection_json"], {}),
                manifest_path=row["manifest_path"],
                captured_at=row["captured_at"],
                status=row["status"],
                error=row["error"],
                tool_version=row["tool_version"],
                artifacts=tuple(artifacts_by_capture.get(row["id"], ())),
            )
            for row in capture_rows
        ]

    def get_evidence_capture(
        self,
        investigation_id: str,
        capture_id: str,
    ) -> EvidenceCapture:
        return next(
            (
                capture
                for capture in self.list_evidence_captures(investigation_id)
                if capture.id == capture_id
            ),
            None,
        ) or self._raise_evidence_not_found(capture_id)

    @staticmethod
    def _raise_evidence_not_found(capture_id: str):
        raise InvestigationValidationError(
            f"Evidence capture not found: {capture_id}"
        )

    def delete_evidence_capture(
        self,
        investigation_id: str,
        capture_id: str,
    ) -> None:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        with self._connection() as connection:
            cursor = connection.execute(
                """
                DELETE FROM evidence_captures
                WHERE id = ? AND investigation_id = ?
                """,
                (capture_id, investigation_id),
            )
            if cursor.rowcount == 0:
                raise InvestigationValidationError(
                    f"Evidence capture not found: {capture_id}"
                )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (utc_now(), investigation_id),
            )

    def table_count(self, table_name: str) -> int:
        allowed = {
            "investigations",
            "search_runs",
            "results",
            "search_result_observations",
            "investigation_results",
            "evidence_captures",
            "evidence_artifacts",
        }
        if table_name not in allowed:
            raise ValueError("Unsupported table name")
        with self._connection() as connection:
            row = connection.execute(f"SELECT COUNT(*) AS count FROM {table_name}").fetchone()
        return int(row["count"])
