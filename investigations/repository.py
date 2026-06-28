from __future__ import annotations

import hashlib
import json
import re
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
    ENTITY_STATUSES,
    ExtractedEntity,
    Investigation,
    InvestigationEntity,
    InvestigationExport,
    InvestigationResult,
    InvestigationSearchRun,
    LocalSearchFilters,
    LocalSearchResult,
    PageComparison,
    PageMonitor,
    UrlAnalysis,
)


LEGACY_IMPORT_KEY = "legacy_history_import_v1"
LOCAL_SEARCH_SEPARATOR = "\x1f"


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


def _fts_match_query(value: str) -> str:
    terms = re.findall(r"\w+", str(value or ""), flags=re.UNICODE)
    return " AND ".join(f'"{term}"*' for term in terms)


def _normalized_domain(value: str) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    if "://" not in text:
        text = f"https://{text}"
    try:
        return (urlsplit(text).hostname or "").lower().removeprefix("www.")
    except ValueError:
        return ""


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
            if 7 in applied:
                has_page_monitors = connection.execute(
                    """
                    SELECT 1
                    FROM sqlite_master
                    WHERE type = 'table' AND name = 'page_monitors'
                    """
                ).fetchone()
                if has_page_monitors is None:
                    connection.execute(
                        "DELETE FROM schema_migrations WHERE version = 7"
                    )
                    applied.remove(7)

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

        with self._connection() as connection:
            document_count = int(
                connection.execute(
                    "SELECT COUNT(*) AS count FROM local_search_documents"
                ).fetchone()["count"]
            )
            result_count = int(
                connection.execute(
                    "SELECT COUNT(*) AS count FROM results"
                ).fetchone()["count"]
            )
            if document_count == 0 and result_count:
                self._refresh_local_search_documents(connection)

    def schema_version(self) -> int:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT COALESCE(MAX(version), 0) AS version FROM schema_migrations"
            ).fetchone()
        return int(row["version"])

    def _refresh_local_search_documents(
        self,
        connection: sqlite3.Connection,
        result_ids: Iterable[str] | None = None,
    ) -> int:
        selected_ids = tuple(dict.fromkeys(
            str(result_id)
            for result_id in (result_ids or ())
            if str(result_id).strip()
        ))
        if result_ids is not None and not selected_ids:
            return 0

        params: list[str] = []
        result_filter = ""
        if selected_ids:
            placeholders = ", ".join("?" for _ in selected_ids)
            connection.execute(
                f"DELETE FROM local_search_documents "
                f"WHERE result_id IN ({placeholders})",
                selected_ids,
            )
            result_filter = f"WHERE r.id IN ({placeholders})"
            params.extend(selected_ids)
        else:
            connection.execute("DELETE FROM local_search_documents")

        rows = connection.execute(
            f"""
            WITH scopes AS (
                SELECT DISTINCT
                    o.result_id,
                    sr.investigation_id
                FROM search_result_observations o
                JOIN search_runs sr ON sr.id = o.search_run_id

                UNION

                SELECT
                    ir.result_id,
                    ir.investigation_id
                FROM investigation_results ir
                WHERE ir.is_saved = 1
            )
            SELECT
                r.id AS result_id,
                s.investigation_id,
                COALESCE(i.title, '') AS investigation_title,
                r.title,
                r.description,
                r.url,
                COALESCE(ir.notes, '') AS notes,
                COALESCE(ir.tags_json, '[]') AS tags_json,
                COALESCE(ir.analyst_status, '') AS analyst_status,
                COALESCE(ir.is_saved, 0) AS is_saved,
                r.first_observed_at,
                MAX(
                    r.last_observed_at,
                    COALESCE(MAX(o.observed_at), r.last_observed_at)
                ) AS last_observed_at,
                GROUP_CONCAT(o.source_json, char(31)) AS source_payloads,
                (
                    SELECT COUNT(*)
                    FROM evidence_captures ec
                    WHERE
                        ec.result_id = r.id
                        AND ec.investigation_id = s.investigation_id
                ) AS evidence_count
            FROM scopes s
            JOIN results r ON r.id = s.result_id
            LEFT JOIN investigations i ON i.id = s.investigation_id
            LEFT JOIN investigation_results ir
                ON ir.result_id = r.id
                AND ir.investigation_id = s.investigation_id
                AND ir.is_saved = 1
            LEFT JOIN search_result_observations o
                ON o.result_id = r.id
                AND EXISTS (
                    SELECT 1
                    FROM search_runs sr2
                    WHERE
                        sr2.id = o.search_run_id
                        AND (
                            (
                                s.investigation_id IS NULL
                                AND sr2.investigation_id IS NULL
                            )
                            OR (
                                s.investigation_id IS NOT NULL
                                AND (
                                    sr2.investigation_id = s.investigation_id
                                    OR (
                                        COALESCE(ir.is_saved, 0) = 1
                                        AND sr2.investigation_id IS NULL
                                    )
                                )
                            )
                        )
                )
            {result_filter}
            GROUP BY r.id, s.investigation_id
            """,
            params,
        ).fetchall()

        for row in rows:
            sources = set()
            for payload in str(row["source_payloads"] or "").split(
                LOCAL_SEARCH_SEPARATOR
            ):
                loaded = _json_load(payload, [])
                if isinstance(loaded, list):
                    sources.update(
                        str(source).strip()
                        for source in loaded
                        if str(source).strip()
                    )
            tags = _json_load(row["tags_json"], [])
            if not isinstance(tags, list):
                tags = []
            investigation_id = row["investigation_id"]
            document_key = (
                f"{row['result_id']}:{investigation_id or '__unassigned__'}"
            )
            connection.execute(
                """
                INSERT INTO local_search_documents(
                    document_key, result_id, investigation_id,
                    investigation_title, title, description, url, notes,
                    tags, sources, analyst_status, domain,
                    first_observed_at, last_observed_at, is_saved,
                    evidence_count
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document_key,
                    row["result_id"],
                    investigation_id,
                    row["investigation_title"],
                    row["title"],
                    row["description"],
                    row["url"],
                    row["notes"],
                    LOCAL_SEARCH_SEPARATOR.join(
                        str(tag).strip()
                        for tag in tags
                        if str(tag).strip()
                    ),
                    LOCAL_SEARCH_SEPARATOR.join(
                        sorted(sources, key=str.casefold)
                    ),
                    row["analyst_status"],
                    _normalized_domain(row["url"]),
                    row["first_observed_at"],
                    row["last_observed_at"],
                    int(row["is_saved"] or 0),
                    int(row["evidence_count"] or 0),
                ),
            )
        return len(rows)

    def rebuild_local_search_index(self) -> int:
        with self._connection() as connection:
            return self._refresh_local_search_documents(connection)

    def search_local_archive(
        self,
        filters: LocalSearchFilters,
    ) -> list[LocalSearchResult]:
        match_query = _fts_match_query(filters.query)
        params: list[str | int] = []
        conditions = []
        if match_query:
            from_clause = (
                "local_search_fts "
                "JOIN local_search_documents d "
                "ON d.id = local_search_fts.rowid"
            )
            rank_expression = (
                "bm25(local_search_fts, 6.0, 3.0, 2.0, 4.0, 3.0)"
            )
            conditions.append("local_search_fts MATCH ?")
            params.append(match_query)
        else:
            from_clause = "local_search_documents d"
            rank_expression = "0.0"

        if filters.investigation_id == "__unassigned__":
            conditions.append("d.investigation_id IS NULL")
        elif filters.investigation_id:
            conditions.append("d.investigation_id = ?")
            params.append(filters.investigation_id)
        if filters.source:
            conditions.append(
                "instr(char(31) || d.sources || char(31), "
                "char(31) || ? || char(31)) > 0"
            )
            params.append(filters.source)
        if filters.analyst_status:
            conditions.append("d.analyst_status = ?")
            params.append(filters.analyst_status)
        if filters.domain:
            domain = _normalized_domain(filters.domain)
            if not domain:
                return []
            conditions.append(
                "(d.domain = ? OR d.domain LIKE ?)"
            )
            params.extend((
                domain,
                f"%.{domain}",
            ))
        if filters.observed_after:
            conditions.append("substr(d.last_observed_at, 1, 10) >= ?")
            params.append(filters.observed_after)
        if filters.observed_before:
            conditions.append("substr(d.last_observed_at, 1, 10) <= ?")
            params.append(filters.observed_before)

        where_clause = (
            "WHERE " + " AND ".join(conditions)
            if conditions
            else ""
        )
        params.append(max(1, min(int(filters.limit), 500)))
        with self._connection() as connection:
            rows = connection.execute(
                f"""
                SELECT
                    d.*,
                    {rank_expression} AS rank
                FROM {from_clause}
                {where_clause}
                ORDER BY rank ASC, d.last_observed_at DESC, d.title ASC
                LIMIT ?
                """,
                params,
            ).fetchall()

        return [
            LocalSearchResult(
                result_id=row["result_id"],
                investigation_id=row["investigation_id"],
                investigation_title=(
                    row["investigation_title"] or "Unassigned searches"
                ),
                title=row["title"],
                description=row["description"],
                url=row["url"],
                notes=row["notes"],
                tags=tuple(
                    tag
                    for tag in str(row["tags"] or "").split(
                        LOCAL_SEARCH_SEPARATOR
                    )
                    if tag
                ),
                sources=tuple(
                    source
                    for source in str(row["sources"] or "").split(
                        LOCAL_SEARCH_SEPARATOR
                    )
                    if source
                ),
                analyst_status=row["analyst_status"],
                domain=row["domain"],
                first_observed_at=row["first_observed_at"],
                last_observed_at=row["last_observed_at"],
                is_saved=bool(row["is_saved"]),
                evidence_count=int(row["evidence_count"] or 0),
                rank=float(row["rank"] or 0),
            )
            for row in rows
        ]

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
            connection.execute(
                """
                UPDATE local_search_documents
                SET investigation_title = ?
                WHERE investigation_id = ?
                """,
                (title, investigation_id),
            )
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
                    ir.discovery_search_run_id,
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
                    discovery_search_run_id=row["discovery_search_run_id"],
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
            self._refresh_local_search_documents(connection, (result_id,))

        return next(
            result
            for result in self.list_investigation_results(investigation_id)
            if result.id == result_id
        )

    def get_saved_result_entity_sources(
        self,
        investigation_id: str,
        result_id: str,
    ) -> dict[str, str]:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT r.url, r.title, r.description, ir.notes
                FROM investigation_results ir
                JOIN results r ON r.id = ir.result_id
                WHERE
                    ir.investigation_id = ?
                    AND ir.result_id = ?
                    AND ir.is_saved = 1
                """,
                (investigation_id, result_id),
            ).fetchone()
        if row is None:
            raise InvestigationResultNotFoundError(
                investigation_id,
                result_id,
            )
        return {
            "url": str(row["url"] or ""),
            "title": str(row["title"] or ""),
            "description": str(row["description"] or ""),
            "notes": str(row["notes"] or ""),
        }

    def get_saved_result_url(
        self,
        investigation_id: str,
        result_id: str,
    ) -> str:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT r.url
                FROM investigation_results ir
                JOIN results r ON r.id = ir.result_id
                WHERE
                    ir.investigation_id = ?
                    AND ir.result_id = ?
                    AND ir.is_saved = 1
                """,
                (investigation_id, result_id),
            ).fetchone()
        if row is None:
            raise InvestigationResultNotFoundError(
                investigation_id,
                result_id,
            )
        return str(row["url"] or "")

    def record_url_analysis(
        self,
        investigation_id: str,
        result_id: str,
        analysis: Mapping,
    ) -> UrlAnalysis:
        self.get_saved_result_url(investigation_id, result_id)
        analysis_id = str(uuid4())
        analyzed_at = utc_now()
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO url_analyses(
                    id, investigation_id, result_id, requested_url, final_url,
                    final_domain_unicode, final_domain_punycode, status_code,
                    redirects_json, headers_json, content_type, content_length,
                    bytes_read, content_sha256, content_truncated, elapsed_ms,
                    tracking_parameters_json, cleaned_url, analyzed_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    analysis_id,
                    investigation_id,
                    result_id,
                    str(analysis.get("requested_url", "") or ""),
                    str(analysis.get("final_url", "") or ""),
                    str(analysis.get("final_domain_unicode", "") or ""),
                    str(analysis.get("final_domain_punycode", "") or ""),
                    int(analysis.get("status_code", 0) or 0),
                    _json_dump(analysis.get("redirects", [])),
                    _json_dump(analysis.get("headers", {})),
                    str(analysis.get("content_type", "") or ""),
                    analysis.get("content_length"),
                    int(analysis.get("bytes_read", 0) or 0),
                    str(analysis.get("content_sha256", "") or ""),
                    int(bool(analysis.get("content_truncated", False))),
                    int(analysis.get("elapsed_ms", 0) or 0),
                    _json_dump(analysis.get("tracking_parameters", [])),
                    str(analysis.get("cleaned_url", "") or ""),
                    analyzed_at,
                ),
            )
        return next(
            item
            for item in self.list_url_analyses(investigation_id)
            if item.id == analysis_id
        )

    def list_url_analyses(
        self,
        investigation_id: str,
    ) -> list[UrlAnalysis]:
        self.get_investigation(investigation_id)
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM url_analyses
                WHERE investigation_id = ?
                ORDER BY analyzed_at DESC, id DESC
                """,
                (investigation_id,),
            ).fetchall()
        analyses = []
        for row in rows:
            redirects = _json_load(row["redirects_json"], [])
            headers = _json_load(row["headers_json"], {})
            tracking_parameters = _json_load(
                row["tracking_parameters_json"],
                [],
            )
            analyses.append(
                UrlAnalysis(
                    id=row["id"],
                    investigation_id=row["investigation_id"],
                    result_id=row["result_id"],
                    requested_url=row["requested_url"],
                    final_url=row["final_url"],
                    final_domain_unicode=row["final_domain_unicode"],
                    final_domain_punycode=row["final_domain_punycode"],
                    status_code=int(row["status_code"]),
                    redirects=tuple(
                        dict(item)
                        for item in redirects
                        if isinstance(item, dict)
                    ),
                    headers={
                        str(key): str(value)
                        for key, value in headers.items()
                    }
                    if isinstance(headers, dict)
                    else {},
                    content_type=row["content_type"],
                    content_length=(
                        int(row["content_length"])
                        if row["content_length"] is not None
                        else None
                    ),
                    bytes_read=int(row["bytes_read"]),
                    content_sha256=row["content_sha256"],
                    content_truncated=bool(row["content_truncated"]),
                    elapsed_ms=int(row["elapsed_ms"]),
                    tracking_parameters=tuple(
                        str(value)
                        for value in tracking_parameters
                        if str(value).strip()
                    ),
                    cleaned_url=row["cleaned_url"],
                    analyzed_at=row["analyzed_at"],
                )
            )
        return analyses

    def create_investigation_entity(
        self,
        investigation_id: str,
        *,
        label: str,
        notes: str,
        tags: Iterable[str],
        properties: Mapping[str, str] | None = None,
    ) -> InvestigationEntity:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        entity_id = str(uuid4())
        now = utc_now()
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO investigation_entities(
                    id, investigation_id, label, notes, tags_json,
                    properties_json, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entity_id,
                    investigation_id,
                    label,
                    notes,
                    _json_dump(list(tags)),
                    _json_dump(dict(properties or {})),
                    now,
                    now,
                ),
            )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (now, investigation_id),
            )
        return next(
            entity
            for entity in self.list_investigation_entities(investigation_id)
            if entity.id == entity_id
        )

    def add_entity_relation(
        self,
        investigation_id: str,
        source_entity_id: str,
        target_entity_id: str,
        label: str,
        relation_id: str = "",
    ) -> dict:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        if not source_entity_id or not target_entity_id:
            raise InvestigationValidationError("Two entities are required.")
        if source_entity_id == target_entity_id:
            raise InvestigationValidationError(
                "An entity cannot be linked to itself."
            )
        known = {
            entity.id
            for entity in self.list_investigation_entities(investigation_id)
        }
        if source_entity_id not in known or target_entity_id not in known:
            raise InvestigationValidationError("Unknown entity.")
        relation_id = str(relation_id or "").strip() or str(uuid4())
        now = utc_now()
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO investigation_entity_relations(
                    id, investigation_id, source_entity_id,
                    target_entity_id, label, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    relation_id,
                    investigation_id,
                    source_entity_id,
                    target_entity_id,
                    label,
                    now,
                    now,
                ),
            )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (now, investigation_id),
            )
        return {
            "id": relation_id,
            "source_entity_id": source_entity_id,
            "target_entity_id": target_entity_id,
            "label": label,
        }

    def update_entity_relation(
        self,
        investigation_id: str,
        relation_id: str,
        label: str,
    ) -> None:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        now = utc_now()
        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE investigation_entity_relations
                SET label = ?, updated_at = ?
                WHERE id = ? AND investigation_id = ?
                """,
                (label, now, relation_id, investigation_id),
            )
            if cursor.rowcount == 0:
                raise InvestigationValidationError("Relation not found.")
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (now, investigation_id),
            )

    def delete_entity_relation(
        self,
        investigation_id: str,
        relation_id: str,
    ) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                DELETE FROM investigation_entity_relations
                WHERE id = ? AND investigation_id = ?
                """,
                (relation_id, investigation_id),
            )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (utc_now(), investigation_id),
            )

    def list_entity_relations_by_source(
        self,
        investigation_id: str,
    ) -> dict[str, list[dict]]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT r.id, r.source_entity_id, r.target_entity_id,
                       r.label, t.label AS target_label
                FROM investigation_entity_relations r
                JOIN investigation_entities t
                    ON t.id = r.target_entity_id
                WHERE r.investigation_id = ?
                ORDER BY r.created_at
                """,
                (investigation_id,),
            ).fetchall()
        grouped: dict[str, list[dict]] = {}
        for row in rows:
            grouped.setdefault(row["source_entity_id"], []).append(
                {
                    "id": row["id"],
                    "target_entity_id": row["target_entity_id"],
                    "target_label": row["target_label"],
                    "label": row["label"],
                }
            )
        return grouped

    def list_investigation_entities(
        self,
        investigation_id: str,
    ) -> list[InvestigationEntity]:
        self.get_investigation(investigation_id)
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM investigation_entities
                WHERE investigation_id = ?
                ORDER BY label COLLATE NOCASE, created_at
                """,
                (investigation_id,),
            ).fetchall()
            link_rows = connection.execute(
                """
                SELECT entity_id, result_id
                FROM investigation_entity_sources
                WHERE investigation_id = ?
                ORDER BY linked_at, result_id
                """,
                (investigation_id,),
            ).fetchall()
        linked_results: dict[str, list[str]] = {}
        for row in link_rows:
            linked_results.setdefault(row["entity_id"], []).append(
                row["result_id"]
            )
        entities = []
        for row in rows:
            tags = _json_load(row["tags_json"], [])
            properties = _json_load(row["properties_json"], {})
            entities.append(
                InvestigationEntity(
                    id=row["id"],
                    investigation_id=row["investigation_id"],
                    label=row["label"],
                    notes=row["notes"],
                    tags=tuple(
                        str(tag)
                        for tag in tags
                        if str(tag).strip()
                    ),
                    properties=(
                        {
                            str(key): str(value)
                            for key, value in properties.items()
                            if str(key).strip() and value is not None
                        }
                        if isinstance(properties, dict)
                        else {}
                    ),
                    linked_result_ids=tuple(
                        linked_results.get(row["id"], ())
                    ),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
            )
        return entities

    def update_investigation_entity(
        self,
        investigation_id: str,
        entity_id: str,
        *,
        label: str,
        notes: str,
        tags: Iterable[str],
    ) -> InvestigationEntity:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        now = utc_now()
        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE investigation_entities
                SET label = ?, notes = ?, tags_json = ?, updated_at = ?
                WHERE id = ? AND investigation_id = ?
                """,
                (
                    label,
                    notes,
                    _json_dump(list(tags)),
                    now,
                    entity_id,
                    investigation_id,
                ),
            )
            if cursor.rowcount == 0:
                raise InvestigationValidationError(
                    f"Investigation entity not found: {entity_id}"
                )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (now, investigation_id),
            )
        return next(
            entity
            for entity in self.list_investigation_entities(investigation_id)
            if entity.id == entity_id
        )

    def set_investigation_entity_property(
        self,
        investigation_id: str,
        entity_id: str,
        *,
        key: str,
        value: str | None,
    ) -> InvestigationEntity:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        now = utc_now()
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT properties_json
                FROM investigation_entities
                WHERE id = ? AND investigation_id = ?
                """,
                (entity_id, investigation_id),
            ).fetchone()
            if row is None:
                raise InvestigationValidationError(
                    f"Investigation entity not found: {entity_id}"
                )
            properties = _json_load(row["properties_json"], {})
            if not isinstance(properties, dict):
                properties = {}
            if value is None:
                properties.pop(key, None)
            else:
                properties[key] = value
            connection.execute(
                """
                UPDATE investigation_entities
                SET properties_json = ?, updated_at = ?
                WHERE id = ? AND investigation_id = ?
                """,
                (
                    _json_dump(properties),
                    now,
                    entity_id,
                    investigation_id,
                ),
            )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (now, investigation_id),
            )
        return next(
            entity
            for entity in self.list_investigation_entities(investigation_id)
            if entity.id == entity_id
        )

    def delete_investigation_entity(
        self,
        investigation_id: str,
        entity_id: str,
    ) -> None:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        now = utc_now()
        with self._connection() as connection:
            cursor = connection.execute(
                """
                DELETE FROM investigation_entities
                WHERE id = ? AND investigation_id = ?
                """,
                (entity_id, investigation_id),
            )
            if cursor.rowcount == 0:
                raise InvestigationValidationError(
                    f"Investigation entity not found: {entity_id}"
                )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (now, investigation_id),
            )

    def link_result_to_investigation_entity(
        self,
        investigation_id: str,
        entity_id: str,
        result_id: str,
    ) -> InvestigationEntity:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        now = utc_now()
        with self._connection() as connection:
            entity = connection.execute(
                """
                SELECT 1
                FROM investigation_entities
                WHERE id = ? AND investigation_id = ?
                """,
                (entity_id, investigation_id),
            ).fetchone()
            saved = connection.execute(
                """
                SELECT 1
                FROM investigation_results
                WHERE investigation_id = ? AND result_id = ? AND is_saved = 1
                """,
                (investigation_id, result_id),
            ).fetchone()
            if entity is None:
                raise InvestigationValidationError(
                    f"Investigation entity not found: {entity_id}"
                )
            if saved is None:
                raise InvestigationResultNotFoundError(
                    investigation_id,
                    result_id,
                )
            connection.execute(
                """
                INSERT OR IGNORE INTO investigation_entity_sources(
                    entity_id, investigation_id, result_id, linked_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (entity_id, investigation_id, result_id, now),
            )
            connection.execute(
                """
                UPDATE investigation_entities
                SET updated_at = ?
                WHERE id = ? AND investigation_id = ?
                """,
                (now, entity_id, investigation_id),
            )
        return next(
            item
            for item in self.list_investigation_entities(investigation_id)
            if item.id == entity_id
        )

    def unlink_result_from_investigation_entity(
        self,
        investigation_id: str,
        entity_id: str,
        result_id: str,
    ) -> None:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        now = utc_now()
        with self._connection() as connection:
            cursor = connection.execute(
                """
                DELETE FROM investigation_entity_sources
                WHERE
                    entity_id = ?
                    AND investigation_id = ?
                    AND result_id = ?
                """,
                (entity_id, investigation_id, result_id),
            )
            if cursor.rowcount == 0:
                raise InvestigationValidationError(
                    "The saved page is not linked to this entity."
                )
            connection.execute(
                """
                UPDATE investigation_entities
                SET updated_at = ?
                WHERE id = ? AND investigation_id = ?
                """,
                (now, entity_id, investigation_id),
            )

    def attach_extracted_entity_property(
        self,
        investigation_id: str,
        extracted_entity_id: str,
        investigation_entity_id: str | None,
        *,
        property_key: str,
    ) -> ExtractedEntity:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        now = utc_now()
        with self._connection() as connection:
            if investigation_entity_id is not None:
                parent = connection.execute(
                    """
                    SELECT 1
                    FROM investigation_entities
                    WHERE id = ? AND investigation_id = ?
                    """,
                    (investigation_entity_id, investigation_id),
                ).fetchone()
                if parent is None:
                    raise InvestigationValidationError(
                        "Investigation entity not found."
                    )
            cursor = connection.execute(
                """
                UPDATE extracted_entities
                SET
                    investigation_entity_id = ?,
                    property_key = ?,
                    status = CASE
                        WHEN ? IS NOT NULL THEN 'validated'
                        ELSE status
                    END,
                    reviewed_at = CASE
                        WHEN ? IS NOT NULL THEN ?
                        ELSE reviewed_at
                    END,
                    last_observed_at = ?
                WHERE id = ? AND investigation_id = ?
                """,
                (
                    investigation_entity_id,
                    property_key if investigation_entity_id else "",
                    investigation_entity_id,
                    investigation_entity_id,
                    now,
                    now,
                    extracted_entity_id,
                    investigation_id,
                ),
            )
            if cursor.rowcount == 0:
                raise InvestigationValidationError(
                    f"Extracted entity not found: {extracted_entity_id}"
                )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (now, investigation_id),
            )
        return next(
            entity
            for entity in self.list_extracted_entities(investigation_id)
            if entity.id == extracted_entity_id
        )

    def upsert_extracted_entities(
        self,
        investigation_id: str,
        result_id: str,
        candidates: Iterable[Mapping],
    ) -> list[ExtractedEntity]:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        now = utc_now()
        with self._connection() as connection:
            saved = connection.execute(
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
            if saved is None:
                raise InvestigationResultNotFoundError(
                    investigation_id,
                    result_id,
                )

            for candidate in candidates:
                entity_type = str(candidate.get("entity_type", "") or "")
                normalized_value = str(
                    candidate.get("normalized_value", "") or ""
                )
                if not entity_type or not normalized_value:
                    continue
                entity_id = str(
                    uuid5(
                        NAMESPACE_URL,
                        (
                            f"synthesix:entity:{investigation_id}:{result_id}:"
                            f"{entity_type}:{normalized_value}"
                        ),
                    )
                )
                connection.execute(
                    """
                    INSERT INTO extracted_entities(
                        id, investigation_id, result_id, entity_type,
                        suggested_type, custom_label,
                        value_original, value_normalized, source_field,
                        source_text, confidence, confidence_reasons_json,
                        attributes_json, status,
                        first_observed_at, last_observed_at
                    )
                    VALUES (
                        ?, ?, ?, ?, ?, '',
                        ?, ?, ?, ?, ?, ?, ?, 'proposed', ?, ?
                    )
                    ON CONFLICT(
                        investigation_id,
                        result_id,
                        suggested_type,
                        value_normalized
                    ) DO UPDATE SET
                        value_original = excluded.value_original,
                        source_field = excluded.source_field,
                        source_text = excluded.source_text,
                        confidence = excluded.confidence,
                        confidence_reasons_json =
                            excluded.confidence_reasons_json,
                        attributes_json = excluded.attributes_json,
                        last_observed_at = excluded.last_observed_at
                    """,
                    (
                        entity_id,
                        investigation_id,
                        result_id,
                        entity_type,
                        entity_type,
                        str(candidate.get("value", "") or ""),
                        normalized_value,
                        str(candidate.get("source_field", "") or ""),
                        str(candidate.get("source_text", "") or ""),
                        float(candidate.get("confidence", 0) or 0),
                        _json_dump(
                            list(candidate.get("confidence_reasons", ()) or ())
                        ),
                        _json_dump(
                            dict(candidate.get("attributes", {}) or {})
                        ),
                        now,
                        now,
                    ),
                )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (now, investigation_id),
            )
        return [
            entity
            for entity in self.list_extracted_entities(investigation_id)
            if entity.result_id == result_id
        ]

    def list_extracted_entities(
        self,
        investigation_id: str,
    ) -> list[ExtractedEntity]:
        self.get_investigation(investigation_id)
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM extracted_entities
                WHERE investigation_id = ?
                ORDER BY
                    CASE status
                        WHEN 'proposed' THEN 0
                        WHEN 'validated' THEN 1
                        ELSE 2
                    END,
                    entity_type,
                    value_normalized
                """,
                (investigation_id,),
            ).fetchall()
        return [
            ExtractedEntity(
                id=row["id"],
                investigation_id=row["investigation_id"],
                result_id=row["result_id"],
                entity_type=row["entity_type"],
                suggested_type=row["suggested_type"],
                custom_label=row["custom_label"],
                tags=tuple(
                    str(tag)
                    for tag in _json_load(row["tags_json"], [])
                    if str(tag).strip()
                ),
                investigation_entity_id=row["investigation_entity_id"],
                property_key=row["property_key"],
                value_original=row["value_original"],
                value_normalized=row["value_normalized"],
                source_field=row["source_field"],
                source_text=row["source_text"],
                confidence=float(row["confidence"] or 0),
                confidence_reasons=tuple(
                    str(reason)
                    for reason in _json_load(
                        row["confidence_reasons_json"],
                        [],
                    )
                    if str(reason).strip()
                ),
                attributes=(
                    {
                        str(key): value
                        for key, value in _json_load(
                            row["attributes_json"],
                            {},
                        ).items()
                    }
                    if isinstance(
                        _json_load(row["attributes_json"], {}),
                        dict,
                    )
                    else {}
                ),
                status=row["status"],
                first_observed_at=row["first_observed_at"],
                last_observed_at=row["last_observed_at"],
                reviewed_at=row["reviewed_at"],
            )
            for row in rows
        ]

    def update_extracted_entity_status(
        self,
        investigation_id: str,
        entity_id: str,
        status: str,
    ) -> ExtractedEntity:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        if status not in ENTITY_STATUSES:
            raise InvestigationValidationError(
                f"Unsupported entity status: {status}"
            )
        now = utc_now()
        reviewed_at = None if status == "proposed" else now
        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE extracted_entities
                SET status = ?, reviewed_at = ?
                WHERE id = ? AND investigation_id = ?
                """,
                (status, reviewed_at, entity_id, investigation_id),
            )
            if cursor.rowcount == 0:
                raise InvestigationValidationError(
                    f"Extracted entity not found: {entity_id}"
                )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (now, investigation_id),
            )
        return next(
            entity
            for entity in self.list_extracted_entities(investigation_id)
            if entity.id == entity_id
        )

    def update_extracted_entity_metadata(
        self,
        investigation_id: str,
        entity_id: str,
        *,
        entity_type: str,
        custom_label: str,
        tags: Iterable[str],
        property_type: str = "",
    ) -> ExtractedEntity:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        current = next(
            (
                entity
                for entity in self.list_extracted_entities(investigation_id)
                if entity.id == entity_id
            ),
            None,
        )
        if current is None:
            raise InvestigationValidationError(
                f"Extracted entity not found: {entity_id}"
            )
        attributes = dict(current.attributes)
        if property_type:
            attributes["property_type"] = property_type
        else:
            attributes.pop("property_type", None)
        now = utc_now()
        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE extracted_entities
                SET
                    entity_type = ?,
                    custom_label = ?,
                    tags_json = ?,
                    attributes_json = ?,
                    last_observed_at = ?
                WHERE id = ? AND investigation_id = ?
                """,
                (
                    entity_type,
                    custom_label,
                    _json_dump(list(tags)),
                    _json_dump(attributes),
                    now,
                    entity_id,
                    investigation_id,
                ),
            )
            if cursor.rowcount == 0:
                raise InvestigationValidationError(
                    f"Extracted entity not found: {entity_id}"
                )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (now, investigation_id),
            )
        return next(
            entity
            for entity in self.list_extracted_entities(investigation_id)
            if entity.id == entity_id
        )

    def set_extracted_entity_property_scope(
        self,
        investigation_id: str,
        entity_id: str,
        scope: str,
    ) -> ExtractedEntity:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        if scope not in {"page", "entity"}:
            raise InvestigationValidationError(
                f"Unsupported property scope: {scope}"
            )
        current = next(
            (
                entity
                for entity in self.list_extracted_entities(investigation_id)
                if entity.id == entity_id
            ),
            None,
        )
        if current is None:
            raise InvestigationValidationError(
                f"Extracted entity not found: {entity_id}"
            )
        attributes = dict(current.attributes)
        attributes["property_scope"] = scope
        now = utc_now()
        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE extracted_entities
                SET attributes_json = ?, last_observed_at = ?
                WHERE id = ? AND investigation_id = ?
                """,
                (
                    _json_dump(attributes),
                    now,
                    entity_id,
                    investigation_id,
                ),
            )
            if cursor.rowcount == 0:
                raise InvestigationValidationError(
                    f"Extracted entity not found: {entity_id}"
                )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (now, investigation_id),
            )
        return next(
            entity
            for entity in self.list_extracted_entities(investigation_id)
            if entity.id == entity_id
        )

    def update_extracted_entity_attributes(
        self,
        investigation_id: str,
        entity_id: str,
        attributes: Mapping,
    ) -> ExtractedEntity:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        current = next(
            (
                entity
                for entity in self.list_extracted_entities(investigation_id)
                if entity.id == entity_id
            ),
            None,
        )
        if current is None:
            raise InvestigationValidationError(
                f"Extracted entity not found: {entity_id}"
            )
        cleaned = {
            str(key): value
            for key, value in dict(attributes).items()
            if str(key).strip()
        }
        now = utc_now()
        with self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE extracted_entities
                SET attributes_json = ?, last_observed_at = ?
                WHERE id = ? AND investigation_id = ?
                """,
                (
                    _json_dump(cleaned),
                    now,
                    entity_id,
                    investigation_id,
                ),
            )
            if cursor.rowcount == 0:
                raise InvestigationValidationError(
                    f"Extracted entity not found: {entity_id}"
                )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (now, investigation_id),
            )
        return next(
            entity
            for entity in self.list_extracted_entities(investigation_id)
            if entity.id == entity_id
        )

    def delete_extracted_entity(
        self,
        investigation_id: str,
        entity_id: str,
    ) -> None:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        now = utc_now()
        with self._connection() as connection:
            cursor = connection.execute(
                """
                DELETE FROM extracted_entities
                WHERE id = ? AND investigation_id = ?
                """,
                (entity_id, investigation_id),
            )
            if cursor.rowcount == 0:
                raise InvestigationValidationError(
                    f"Extracted entity not found: {entity_id}"
                )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (now, investigation_id),
            )

    def record_investigation_export(
        self,
        investigation_id: str,
        *,
        archive_path: str,
        dossier_path: str,
        graphml_path: str,
        csv_path: str,
        nodes_csv_path: str,
        edges_csv_path: str,
        manifest_path: str,
        include_evidence: bool,
        include_unreviewed: bool,
        node_count: int,
        edge_count: int,
        asset_count: int,
        generated_at: str,
    ) -> InvestigationExport:
        self.get_investigation(investigation_id)
        export_id = str(uuid4())
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO investigation_exports(
                    id, investigation_id, export_type, archive_path,
                    dossier_path, graphml_path,
                    csv_path, nodes_csv_path, edges_csv_path, manifest_path,
                    include_evidence, include_unreviewed, node_count,
                    edge_count, asset_count, generated_at
                )
                VALUES (
                    ?, ?, 'zeroneurone', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    export_id,
                    investigation_id,
                    archive_path,
                    dossier_path,
                    graphml_path,
                    csv_path,
                    nodes_csv_path,
                    edges_csv_path,
                    manifest_path,
                    int(include_evidence),
                    int(include_unreviewed),
                    int(node_count),
                    int(edge_count),
                    int(asset_count),
                    generated_at,
                ),
            )
        return next(
            export
            for export in self.list_investigation_exports(investigation_id)
            if export.id == export_id
        )

    def list_investigation_exports(
        self,
        investigation_id: str,
    ) -> list[InvestigationExport]:
        self.get_investigation(investigation_id)
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM investigation_exports
                WHERE investigation_id = ?
                ORDER BY generated_at DESC, id DESC
                """,
                (investigation_id,),
            ).fetchall()
        return [
            InvestigationExport(
                id=row["id"],
                investigation_id=row["investigation_id"],
                export_type=row["export_type"],
                archive_path=row["archive_path"],
                dossier_path=row["dossier_path"],
                graphml_path=row["graphml_path"],
                csv_path=row["csv_path"],
                nodes_csv_path=row["nodes_csv_path"],
                edges_csv_path=row["edges_csv_path"],
                manifest_path=row["manifest_path"],
                include_evidence=bool(row["include_evidence"]),
                include_unreviewed=bool(row["include_unreviewed"]),
                node_count=int(row["node_count"] or 0),
                edge_count=int(row["edge_count"] or 0),
                asset_count=int(row["asset_count"] or 0),
                generated_at=row["generated_at"],
            )
            for row in rows
        ]

    def get_investigation_export(
        self,
        investigation_id: str,
        export_id: str,
    ) -> InvestigationExport:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        return next(
            (
                export
                for export in self.list_investigation_exports(investigation_id)
                if export.id == export_id
            ),
            None,
        ) or self._raise_export_not_found(export_id)

    @staticmethod
    def _raise_export_not_found(export_id: str):
        raise InvestigationValidationError(
            f"Investigation export not found: {export_id}"
        )

    def delete_investigation_export(
        self,
        investigation_id: str,
        export_id: str,
    ) -> None:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        with self._connection() as connection:
            cursor = connection.execute(
                """
                DELETE FROM investigation_exports
                WHERE id = ? AND investigation_id = ?
                """,
                (export_id, investigation_id),
            )
            if cursor.rowcount == 0:
                raise InvestigationValidationError(
                    f"Investigation export not found: {export_id}"
                )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (utc_now(), investigation_id),
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
            result_ids = [
                row["result_id"]
                for row in connection.execute(
                    """
                    SELECT result_id
                    FROM search_result_observations
                    WHERE search_run_id = ?
                    """,
                    (search_run_id,),
                )
            ]

            connection.execute(
                "UPDATE search_runs SET investigation_id = ? WHERE id = ?",
                (investigation_id, search_run_id),
            )
            connection.execute(
                "UPDATE investigations SET updated_at = ? WHERE id = ?",
                (now, investigation_id),
            )
            self._refresh_local_search_documents(connection, result_ids)

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
            self._refresh_local_search_documents(connection, (result_id,))

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
            self._refresh_local_search_documents(
                connection,
                (result["id"],),
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
            monitor = connection.execute(
                """
                SELECT 1
                FROM page_monitors
                WHERE investigation_id = ? AND result_id = ?
                LIMIT 1
                """,
                (investigation_id, result_id),
            ).fetchone()
            if monitor is not None:
                raise InvestigationValidationError(
                    "Stop monitoring this page before removing it."
                )
            connection.execute(
                """
                DELETE FROM evidence_captures
                WHERE investigation_id = ? AND result_id = ?
                """,
                (investigation_id, result_id),
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
            self._refresh_local_search_documents(connection, (result_id,))

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
        indexed_result_ids = []

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
                indexed_result_ids.append(result_id)

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
            self._refresh_local_search_documents(
                connection,
                indexed_result_ids,
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
            self._refresh_local_search_documents(connection)
        return search_count

    def _row_to_page_monitor(self, row: sqlite3.Row) -> PageMonitor:
        similarity = row["comparison_similarity"]
        return PageMonitor(
            id=row["id"],
            investigation_id=row["investigation_id"],
            result_id=row["result_id"],
            result_title=row["result_title"],
            result_url=row["result_url"],
            baseline_capture_id=row["baseline_capture_id"],
            last_capture_id=row["last_capture_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            archive_count=int(row["archive_count"] or 0),
            comparison_id=row["comparison_id"],
            comparison_status=row["comparison_status"],
            comparison_similarity=(
                float(similarity) if similarity is not None else None
            ),
            comparison_report_path=row["comparison_report_path"],
            comparison_generated_at=row["comparison_generated_at"],
        )

    def list_page_monitors(
        self,
        investigation_id: str,
    ) -> list[PageMonitor]:
        self.get_investigation(investigation_id)
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    monitor.*,
                    result.title AS result_title,
                    result.url AS result_url,
                    (
                        SELECT COUNT(*)
                        FROM evidence_captures capture
                        WHERE
                            capture.investigation_id = monitor.investigation_id
                            AND capture.result_id = monitor.result_id
                            AND capture.capture_kind = 'page_archive'
                    ) AS archive_count,
                    comparison.id AS comparison_id,
                    comparison.status AS comparison_status,
                    comparison.similarity AS comparison_similarity,
                    comparison.report_path AS comparison_report_path,
                    comparison.generated_at AS comparison_generated_at
                FROM page_monitors monitor
                JOIN results result ON result.id = monitor.result_id
                LEFT JOIN page_comparisons comparison
                    ON comparison.id = (
                        SELECT candidate.id
                        FROM page_comparisons candidate
                        WHERE candidate.monitor_id = monitor.id
                        ORDER BY candidate.generated_at DESC
                        LIMIT 1
                    )
                WHERE monitor.investigation_id = ?
                ORDER BY monitor.updated_at DESC, result.title COLLATE NOCASE
                """,
                (investigation_id,),
            ).fetchall()
        return [self._row_to_page_monitor(row) for row in rows]

    def get_page_monitor(
        self,
        investigation_id: str,
        monitor_id: str,
    ) -> PageMonitor:
        return next(
            (
                monitor
                for monitor in self.list_page_monitors(investigation_id)
                if monitor.id == monitor_id
            ),
            None,
        ) or self._raise_page_monitor_not_found(monitor_id)

    def get_page_monitor_for_result(
        self,
        investigation_id: str,
        result_id: str,
    ) -> PageMonitor | None:
        return next(
            (
                monitor
                for monitor in self.list_page_monitors(investigation_id)
                if monitor.result_id == result_id
            ),
            None,
        )

    @staticmethod
    def _raise_page_monitor_not_found(monitor_id: str):
        raise InvestigationValidationError(
            f"Page monitor not found: {monitor_id}"
        )

    def create_page_monitor(
        self,
        investigation_id: str,
        result_id: str,
    ) -> PageMonitor:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        existing = self.get_page_monitor_for_result(
            investigation_id,
            result_id,
        )
        if existing is not None:
            return existing

        now = utc_now()
        monitor_id = str(uuid4())
        with self._connection() as connection:
            saved = connection.execute(
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
            if saved is None:
                raise InvestigationResultNotFoundError(
                    investigation_id,
                    result_id,
                )
            latest_archive = connection.execute(
                """
                SELECT id
                FROM evidence_captures
                WHERE
                    investigation_id = ?
                    AND result_id = ?
                    AND capture_kind = 'page_archive'
                ORDER BY captured_at DESC
                LIMIT 1
                """,
                (investigation_id, result_id),
            ).fetchone()
            baseline_id = (
                latest_archive["id"] if latest_archive is not None else None
            )
            connection.execute(
                """
                INSERT INTO page_monitors(
                    id, investigation_id, result_id, baseline_capture_id,
                    last_capture_id, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    monitor_id,
                    investigation_id,
                    result_id,
                    baseline_id,
                    baseline_id,
                    now,
                    now,
                ),
            )
        return self.get_page_monitor(investigation_id, monitor_id)

    def delete_page_monitor(
        self,
        investigation_id: str,
        monitor_id: str,
    ) -> None:
        investigation = self.get_investigation(investigation_id)
        if investigation.status != "active":
            raise InvestigationValidationError(
                "Archived investigations are read-only."
            )
        with self._connection() as connection:
            cursor = connection.execute(
                """
                DELETE FROM page_monitors
                WHERE id = ? AND investigation_id = ?
                """,
                (monitor_id, investigation_id),
            )
            if cursor.rowcount == 0:
                self._raise_page_monitor_not_found(monitor_id)

    def advance_page_monitor(
        self,
        investigation_id: str,
        monitor_id: str,
        capture_id: str,
    ) -> PageMonitor:
        monitor = self.get_page_monitor(investigation_id, monitor_id)
        with self._connection() as connection:
            capture = connection.execute(
                """
                SELECT 1
                FROM evidence_captures
                WHERE
                    id = ?
                    AND investigation_id = ?
                    AND result_id = ?
                    AND capture_kind = 'page_archive'
                """,
                (capture_id, investigation_id, monitor.result_id),
            ).fetchone()
            if capture is None:
                raise InvestigationValidationError(
                    "The page monitor can only use a page archive."
                )
            now = utc_now()
            connection.execute(
                """
                UPDATE page_monitors
                SET
                    baseline_capture_id = COALESCE(
                        baseline_capture_id,
                        ?
                    ),
                    last_capture_id = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (capture_id, capture_id, now, monitor_id),
            )
        return self.get_page_monitor(investigation_id, monitor_id)

    def record_page_comparison(
        self,
        *,
        investigation_id: str,
        monitor_id: str,
        previous_capture_id: str | None,
        current_capture_id: str,
        status: str,
        similarity: float | None,
        previous_sha256: str,
        current_sha256: str,
        report_path: str | None,
        generated_at: str,
    ) -> PageComparison:
        if status not in {
            "unchanged",
            "minor_change",
            "changed",
            "inconclusive",
        }:
            raise InvestigationValidationError(
                "Unsupported page comparison status."
            )
        monitor = self.get_page_monitor(investigation_id, monitor_id)
        current_capture = self.get_evidence_capture(
            investigation_id,
            current_capture_id,
        )
        if (
            current_capture.result_id != monitor.result_id
            or current_capture.capture_kind != "page_archive"
        ):
            raise InvestigationValidationError(
                "The current snapshot does not belong to this page monitor."
            )
        if previous_capture_id:
            previous_capture = self.get_evidence_capture(
                investigation_id,
                previous_capture_id,
            )
            if (
                previous_capture.result_id != monitor.result_id
                or previous_capture.capture_kind != "page_archive"
            ):
                raise InvestigationValidationError(
                    "The previous snapshot does not belong to this page monitor."
                )
        comparison_id = str(uuid4())
        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO page_comparisons(
                    id, monitor_id, previous_capture_id, current_capture_id,
                    status, similarity, previous_sha256, current_sha256,
                    report_path, generated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    comparison_id,
                    monitor_id,
                    previous_capture_id,
                    current_capture_id,
                    status,
                    similarity,
                    previous_sha256,
                    current_sha256,
                    report_path,
                    generated_at,
                ),
            )
            connection.execute(
                """
                UPDATE page_monitors
                SET
                    baseline_capture_id = COALESCE(
                        baseline_capture_id,
                        ?
                    ),
                    last_capture_id = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    current_capture_id,
                    current_capture_id,
                    generated_at,
                    monitor_id,
                ),
            )
        return self.get_page_comparison(comparison_id)

    def get_page_comparison(self, comparison_id: str) -> PageComparison:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM page_comparisons
                WHERE id = ?
                """,
                (comparison_id,),
            ).fetchone()
        if row is None:
            raise InvestigationValidationError(
                f"Page comparison not found: {comparison_id}"
            )
        similarity = row["similarity"]
        return PageComparison(
            id=row["id"],
            monitor_id=row["monitor_id"],
            previous_capture_id=row["previous_capture_id"],
            current_capture_id=row["current_capture_id"],
            status=row["status"],
            similarity=float(similarity) if similarity is not None else None,
            previous_sha256=row["previous_sha256"],
            current_sha256=row["current_sha256"],
            report_path=row["report_path"],
            generated_at=row["generated_at"],
        )

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
        capture_kind: str = "screenshot",
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
        if capture_kind not in {"screenshot", "page_archive"}:
            raise InvestigationValidationError(
                "Unsupported evidence capture kind."
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
                    status, error, tool_version, capture_kind
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    capture_kind,
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
            self._refresh_local_search_documents(connection, (result_id,))

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
                capture_kind=row["capture_kind"],
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
            capture = connection.execute(
                """
                SELECT result_id
                FROM evidence_captures
                WHERE id = ? AND investigation_id = ?
                """,
                (capture_id, investigation_id),
            ).fetchone()
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
            self._refresh_local_search_documents(
                connection,
                (capture["result_id"],),
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
            "local_search_documents",
            "local_search_fts",
            "page_monitors",
            "page_comparisons",
            "extracted_entities",
            "investigation_entities",
            "investigation_entity_sources",
            "investigation_exports",
            "url_analyses",
        }
        if table_name not in allowed:
            raise ValueError("Unsupported table name")
        with self._connection() as connection:
            row = connection.execute(f"SELECT COUNT(*) AS count FROM {table_name}").fetchone()
        return int(row["count"])
