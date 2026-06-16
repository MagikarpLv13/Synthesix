from __future__ import annotations

from dataclasses import dataclass
from typing import Any


INVESTIGATION_STATUSES = ("active", "archived")
ANALYST_STATUSES = ("a_verifier", "pertinent", "ecarte", "confirme")
ENTITY_STATUSES = ("proposed", "validated", "rejected")
ENTITY_TYPES = (
    "email",
    "phone",
    "url",
    "domain",
    "ipv4",
    "ipv6",
    "handle",
    "identifier",
    "coordinates",
    "address",
    "vat_number",
    "siret",
    "siren",
    "date",
    "person",
    "organization",
    "place",
    "event",
    "product",
    "other",
)


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
    discovery_search_run_id: str | None
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
            "discovery_search_run_id": self.discovery_search_run_id,
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
class ExtractedEntity:
    id: str
    investigation_id: str
    result_id: str
    entity_type: str
    suggested_type: str
    custom_label: str
    tags: tuple[str, ...]
    investigation_entity_id: str | None
    property_key: str
    value_original: str
    value_normalized: str
    source_field: str
    source_text: str
    confidence: float
    confidence_reasons: tuple[str, ...]
    attributes: dict[str, Any]
    status: str
    first_observed_at: str
    last_observed_at: str
    reviewed_at: str | None

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "investigation_id": self.investigation_id,
            "result_id": self.result_id,
            "entity_type": self.entity_type,
            "suggested_type": self.suggested_type,
            "custom_label": self.custom_label,
            "tags": list(self.tags),
            "investigation_entity_id": self.investigation_entity_id,
            "property_key": self.property_key,
            "value_original": self.value_original,
            "value_normalized": self.value_normalized,
            "source_field": self.source_field,
            "source_text": self.source_text,
            "confidence": self.confidence,
            "confidence_reasons": list(self.confidence_reasons),
            "attributes": dict(self.attributes),
            "status": self.status,
            "first_observed_at": self.first_observed_at,
            "last_observed_at": self.last_observed_at,
            "reviewed_at": self.reviewed_at,
        }


@dataclass(frozen=True)
class InvestigationEntity:
    id: str
    investigation_id: str
    label: str
    notes: str
    tags: tuple[str, ...]
    properties: dict[str, str]
    linked_result_ids: tuple[str, ...]
    created_at: str
    updated_at: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "investigation_id": self.investigation_id,
            "label": self.label,
            "notes": self.notes,
            "tags": list(self.tags),
            "properties": dict(self.properties),
            "linked_result_ids": list(self.linked_result_ids),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass(frozen=True)
class InvestigationExport:
    id: str
    investigation_id: str
    export_type: str
    archive_path: str
    dossier_path: str
    graphml_path: str
    csv_path: str
    nodes_csv_path: str
    edges_csv_path: str
    manifest_path: str
    include_evidence: bool
    include_unreviewed: bool
    node_count: int
    edge_count: int
    asset_count: int
    generated_at: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "investigation_id": self.investigation_id,
            "export_type": self.export_type,
            "archive_path": self.archive_path,
            "dossier_path": self.dossier_path,
            "graphml_path": self.graphml_path,
            "csv_path": self.csv_path,
            "nodes_csv_path": self.nodes_csv_path,
            "edges_csv_path": self.edges_csv_path,
            "manifest_path": self.manifest_path,
            "include_evidence": self.include_evidence,
            "include_unreviewed": self.include_unreviewed,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "asset_count": self.asset_count,
            "generated_at": self.generated_at,
        }


@dataclass(frozen=True)
class UrlAnalysis:
    id: str
    investigation_id: str
    result_id: str
    requested_url: str
    final_url: str
    final_domain_unicode: str
    final_domain_punycode: str
    status_code: int
    redirects: tuple[dict[str, Any], ...]
    headers: dict[str, str]
    content_type: str
    content_length: int | None
    bytes_read: int
    content_sha256: str
    content_truncated: bool
    elapsed_ms: int
    tracking_parameters: tuple[str, ...]
    cleaned_url: str
    analyzed_at: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "investigation_id": self.investigation_id,
            "result_id": self.result_id,
            "requested_url": self.requested_url,
            "final_url": self.final_url,
            "final_domain_unicode": self.final_domain_unicode,
            "final_domain_punycode": self.final_domain_punycode,
            "status_code": self.status_code,
            "redirects": [dict(item) for item in self.redirects],
            "headers": dict(self.headers),
            "content_type": self.content_type,
            "content_length": self.content_length,
            "bytes_read": self.bytes_read,
            "content_sha256": self.content_sha256,
            "content_truncated": self.content_truncated,
            "elapsed_ms": self.elapsed_ms,
            "tracking_parameters": list(self.tracking_parameters),
            "cleaned_url": self.cleaned_url,
            "analyzed_at": self.analyzed_at,
        }


@dataclass(frozen=True)
class LocalSearchFilters:
    query: str = ""
    investigation_id: str = ""
    source: str = ""
    analyst_status: str = ""
    domain: str = ""
    observed_after: str = ""
    observed_before: str = ""
    limit: int = 100


@dataclass(frozen=True)
class LocalSearchResult:
    result_id: str
    investigation_id: str | None
    investigation_title: str
    title: str
    description: str
    url: str
    notes: str
    tags: tuple[str, ...]
    sources: tuple[str, ...]
    analyst_status: str
    domain: str
    first_observed_at: str
    last_observed_at: str
    is_saved: bool
    evidence_count: int
    rank: float

    def to_payload(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "investigation_id": self.investigation_id,
            "investigation_title": self.investigation_title,
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "notes": self.notes,
            "tags": list(self.tags),
            "sources": list(self.sources),
            "analyst_status": self.analyst_status,
            "domain": self.domain,
            "first_observed_at": self.first_observed_at,
            "last_observed_at": self.last_observed_at,
            "is_saved": self.is_saved,
            "evidence_count": self.evidence_count,
            "rank": self.rank,
            "already_observed": True,
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
    capture_kind: str = "screenshot"

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
            "capture_kind": self.capture_kind,
            "artifacts": [
                artifact.to_payload()
                for artifact in self.artifacts
            ],
        }


@dataclass(frozen=True)
class PageMonitor:
    id: str
    investigation_id: str
    result_id: str
    result_title: str
    result_url: str
    baseline_capture_id: str | None
    last_capture_id: str | None
    created_at: str
    updated_at: str
    archive_count: int = 0
    comparison_id: str | None = None
    comparison_status: str | None = None
    comparison_similarity: float | None = None
    comparison_report_path: str | None = None
    comparison_generated_at: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "investigation_id": self.investigation_id,
            "result_id": self.result_id,
            "result_title": self.result_title,
            "result_url": self.result_url,
            "baseline_capture_id": self.baseline_capture_id,
            "last_capture_id": self.last_capture_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "archive_count": self.archive_count,
            "comparison_id": self.comparison_id,
            "comparison_status": self.comparison_status,
            "comparison_similarity": self.comparison_similarity,
            "comparison_report_path": self.comparison_report_path,
            "comparison_generated_at": self.comparison_generated_at,
        }


@dataclass(frozen=True)
class PageComparison:
    id: str
    monitor_id: str
    previous_capture_id: str | None
    current_capture_id: str
    status: str
    similarity: float | None
    previous_sha256: str
    current_sha256: str
    report_path: str | None
    generated_at: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "monitor_id": self.monitor_id,
            "previous_capture_id": self.previous_capture_id,
            "current_capture_id": self.current_capture_id,
            "status": self.status,
            "similarity": self.similarity,
            "previous_sha256": self.previous_sha256,
            "current_sha256": self.current_sha256,
            "report_path": self.report_path,
            "generated_at": self.generated_at,
        }
