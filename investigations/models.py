from __future__ import annotations

from dataclasses import dataclass
from typing import Any


INVESTIGATION_STATUSES = ("active", "archived")
ANALYST_STATUSES = ("a_verifier", "pertinent", "ecarte", "confirme")


@dataclass(frozen=True)
class Investigation:
    id: str
    title: str
    reference: str
    description: str
    tags: tuple[str, ...]
    status: str
    created_at: str
    updated_at: str
    archived_at: str | None = None
    search_count: int = 0
    result_count: int = 0

    def to_payload(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "reference": self.reference,
            "description": self.description,
            "tags": list(self.tags),
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "archived_at": self.archived_at,
            "search_count": self.search_count,
            "result_count": self.result_count,
        }


@dataclass(frozen=True)
class InvestigationResult:
    id: str
    canonical_url: str
    url: str
    title: str
    description: str
    sources: tuple[str, ...]
    first_observed_at: str
    last_observed_at: str
    latest_observed_at: str
    relevance_score: float
    score_breakdown: tuple[dict[str, Any], ...]
    observation_count: int
    analyst_status: str
    favorite: bool
    notes: str
    tags: tuple[str, ...]
    added_at: str
    updated_at: str
    discovery_method: str
    discovery_query: str
    discovery_sources: tuple[str, ...]
    discovery_report_path: str | None
    discovery_observed_at: str | None
    discovery_referrer: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "canonical_url": self.canonical_url,
            "url": self.url,
            "title": self.title,
            "description": self.description,
            "sources": list(self.sources),
            "first_observed_at": self.first_observed_at,
            "last_observed_at": self.last_observed_at,
            "latest_observed_at": self.latest_observed_at,
            "relevance_score": self.relevance_score,
            "score_breakdown": [dict(component) for component in self.score_breakdown],
            "observation_count": self.observation_count,
            "analyst_status": self.analyst_status,
            "favorite": self.favorite,
            "notes": self.notes,
            "tags": list(self.tags),
            "added_at": self.added_at,
            "updated_at": self.updated_at,
            "discovery_method": self.discovery_method,
            "discovery_query": self.discovery_query,
            "discovery_sources": list(self.discovery_sources),
            "discovery_report_path": self.discovery_report_path,
            "discovery_observed_at": self.discovery_observed_at,
            "discovery_referrer": self.discovery_referrer,
        }


@dataclass(frozen=True)
class InvestigationSearchRun:
    id: str
    original_query: str
    parsed_query: str
    filters: dict[str, Any]
    engines: dict[str, bool]
    requested_results: int
    result_count: int
    total_time: float
    report_path: str | None
    status: str
    engine_errors: dict[str, Any]
    started_at: str
    completed_at: str | None

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "original_query": self.original_query,
            "parsed_query": self.parsed_query,
            "filters": self.filters,
            "engines": self.engines,
            "requested_results": self.requested_results,
            "result_count": self.result_count,
            "total_time": self.total_time,
            "report_path": self.report_path,
            "status": self.status,
            "engine_errors": self.engine_errors,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


@dataclass(frozen=True)
class EvidenceArtifact:
    id: str
    artifact_type: str
    file_path: str
    mime_type: str
    sha256: str
    byte_size: int
    created_at: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "artifact_type": self.artifact_type,
            "file_path": self.file_path,
            "mime_type": self.mime_type,
            "sha256": self.sha256,
            "byte_size": self.byte_size,
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class EvidenceCapture:
    id: str
    investigation_id: str
    result_id: str
    name: str
    source_url: str
    page_title: str
    capture_scope: str
    selection: dict[str, Any]
    manifest_path: str
    captured_at: str
    status: str
    error: str
    tool_version: str
    artifacts: tuple[EvidenceArtifact, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "investigation_id": self.investigation_id,
            "result_id": self.result_id,
            "name": self.name,
            "source_url": self.source_url,
            "page_title": self.page_title,
            "capture_scope": self.capture_scope,
            "selection": self.selection,
            "manifest_path": self.manifest_path,
            "captured_at": self.captured_at,
            "status": self.status,
            "error": self.error,
            "tool_version": self.tool_version,
            "artifacts": [
                artifact.to_payload()
                for artifact in self.artifacts
            ],
        }
