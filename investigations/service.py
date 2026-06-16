from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, Mapping

from analysis.entities import extract_entity_candidates
from analysis.urls import analyze_url
from exceptions import InvestigationValidationError
from exports.zeroneurone_tagsets import canonical_zeroneurone_tag
from investigations.models import (
    ANALYST_STATUSES,
    ENTITY_STATUSES,
    ENTITY_TYPES,
    Investigation,
    InvestigationExport,
    LocalSearchFilters,
    PageComparison,
    PageMonitor,
)
from investigations.repository import InvestigationRepository


MAX_TITLE_LENGTH = 120
MAX_REFERENCE_LENGTH = 120
MAX_DESCRIPTION_LENGTH = 4000
MAX_TAG_COUNT = 20
MAX_TAG_LENGTH = 50
MAX_RESULT_NOTES_LENGTH = 10000
MAX_PAGE_TITLE_LENGTH = 500
MAX_PAGE_DESCRIPTION_LENGTH = 4000
MAX_PAGE_URL_LENGTH = 8000
MAX_EVIDENCE_NAME_LENGTH = 120
MAX_LOCAL_SEARCH_QUERY_LENGTH = 500
MAX_LOCAL_SEARCH_DOMAIN_LENGTH = 253
MAX_ENTITY_CUSTOM_LABEL_LENGTH = 120
MAX_INVESTIGATION_ENTITY_LABEL_LENGTH = 200
MAX_INVESTIGATION_ENTITY_NOTES_LENGTH = 4000
MAX_ENTITY_PROPERTY_KEY_LENGTH = 100
MAX_ENTITY_PROPERTY_VALUE_LENGTH = 4000
MAX_ENTITY_SOURCE_BYTES = 2 * 1024 * 1024
MAX_ENTITY_SOURCE_TOTAL_CHARS = 2_000_000


def _default_property_key(entity_type: str) -> str:
    return {
        "email": "Email",
        "phone": "Téléphone",
        "url": "URL",
        "domain": "Domaine",
        "ipv4": "IP",
        "ipv6": "IP",
        "handle": "Compte en ligne",
        "identifier": "Identifiant",
        "coordinates": "Coordonnées",
        "address": "Adresse",
        "vat_number": "Numéro de TVA",
        "siret": "SIRET",
        "siren": "SIREN",
        "date": "Date/heure",
        "person": "Personne",
        "organization": "Entreprise",
        "place": "Lieu",
        "event": "Événement",
        "product": "Produit ou service",
    }.get(entity_type, "Information")


def _clean_text(value, *, max_length: int) -> str:
    return str(value or "").strip()[:max_length]


def _normalize_tags(value) -> tuple[str, ...]:
    if isinstance(value, str):
        candidates = value.split(",")
    elif isinstance(value, Iterable):
        candidates = value
    else:
        candidates = ()

    tags = []
    seen = set()
    for candidate in candidates:
        tag = str(candidate or "").strip()[:MAX_TAG_LENGTH]
        tag = canonical_zeroneurone_tag(tag)
        key = tag.casefold()
        if not tag or key in seen:
            continue
        tags.append(tag)
        seen.add(key)
        if len(tags) >= MAX_TAG_COUNT:
            break
    return tuple(tags)


class InvestigationService:
    def __init__(
        self,
        repository: InvestigationRepository,
        *,
        base_dir: Path | None = None,
    ):
        self.repository = repository
        self.base_dir = (
            Path(base_dir).resolve()
            if base_dir is not None
            else repository.database_path.resolve().parent.parent
        )

    def initialize(self, history_path: Path | None = None) -> int:
        self.repository.initialize()
        if history_path is None or not history_path.exists():
            return self.repository.import_legacy_history(())

        try:
            entries = json.loads(history_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            entries = []
        if not isinstance(entries, list):
            entries = []
        return self.repository.import_legacy_history(
            entry for entry in entries if isinstance(entry, Mapping)
        )

    def list_investigations(self, *, include_archived: bool = False) -> list[Investigation]:
        return self.repository.list_investigations(include_archived=include_archived)

    def get(self, investigation_id: str) -> Investigation:
        return self.repository.get_investigation(investigation_id)

    def list_payload(self, *, include_archived: bool = False) -> list[dict]:
        return [
            investigation.to_payload()
            for investigation in self.list_investigations(include_archived=include_archived)
        ]

    def create(self, payload: Mapping) -> Investigation:
        title = _clean_text(payload.get("title"), max_length=MAX_TITLE_LENGTH)
        if not title:
            raise InvestigationValidationError("Investigation title is required.")
        return self.repository.create_investigation(
            title,
            reference=_clean_text(
                payload.get("reference"),
                max_length=MAX_REFERENCE_LENGTH,
            ),
            description=_clean_text(
                payload.get("description"),
                max_length=MAX_DESCRIPTION_LENGTH,
            ),
            tags=_normalize_tags(payload.get("tags", ())),
        )

    def update(self, investigation_id: str, payload: Mapping) -> Investigation:
        title = _clean_text(payload.get("title"), max_length=MAX_TITLE_LENGTH)
        if not title:
            raise InvestigationValidationError("Investigation title is required.")
        return self.repository.update_investigation(
            investigation_id,
            title=title,
            reference=_clean_text(
                payload.get("reference"),
                max_length=MAX_REFERENCE_LENGTH,
            ),
            description=_clean_text(
                payload.get("description"),
                max_length=MAX_DESCRIPTION_LENGTH,
            ),
            tags=_normalize_tags(payload.get("tags", ())),
        )

    def archive(self, investigation_id: str) -> Investigation:
        return self.repository.archive_investigation(investigation_id)

    def delete(self, investigation_id: str) -> None:
        self.repository.delete_investigation(investigation_id)

    def record_search(self, **kwargs) -> str:
        return self.repository.record_search(**kwargs)

    def search_local_archive(self, payload: Mapping) -> list[dict]:
        observed_after = _clean_text(
            payload.get("observed_after"),
            max_length=10,
        )
        observed_before = _clean_text(
            payload.get("observed_before"),
            max_length=10,
        )
        for value in (observed_after, observed_before):
            if value and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                raise InvestigationValidationError(
                    "Observation dates must use YYYY-MM-DD."
                )
        if observed_after and observed_before and observed_after > observed_before:
            raise InvestigationValidationError(
                "Observed after must be earlier than or equal to observed before."
            )

        analyst_status = _clean_text(
            payload.get("analyst_status"),
            max_length=30,
        )
        if analyst_status and analyst_status not in ANALYST_STATUSES:
            raise InvestigationValidationError(
                f"Unsupported analyst status: {analyst_status}"
            )

        investigation_id = _clean_text(
            payload.get("investigation_id"),
            max_length=100,
        )
        if investigation_id and investigation_id != "__unassigned__":
            self.get(investigation_id)

        try:
            limit = int(payload.get("limit", 100) or 100)
        except (TypeError, ValueError):
            limit = 100
        filters = LocalSearchFilters(
            query=_clean_text(
                payload.get("query"),
                max_length=MAX_LOCAL_SEARCH_QUERY_LENGTH,
            ),
            investigation_id=investigation_id,
            source=_clean_text(payload.get("source"), max_length=50),
            analyst_status=analyst_status,
            domain=_clean_text(
                payload.get("domain"),
                max_length=MAX_LOCAL_SEARCH_DOMAIN_LENGTH,
            ).lower(),
            observed_after=observed_after,
            observed_before=observed_before,
            limit=max(1, min(limit, 500)),
        )
        return [
            result.to_payload()
            for result in self.repository.search_local_archive(filters)
        ]

    def rebuild_local_search_index(self) -> int:
        return self.repository.rebuild_local_search_index()

    def workspace_payload(self, investigation_id: str) -> dict:
        investigation = self.get(investigation_id)
        return {
            "investigation": investigation.to_payload(),
            "results": [
                result.to_payload()
                for result in self.repository.list_investigation_results(
                    investigation_id
                )
            ],
            "searches": [
                search.to_payload()
                for search in self.repository.list_investigation_searches(
                    investigation_id
                )
            ],
            "unassigned_searches": [
                search.to_payload()
                for search in self.repository.list_unassigned_searches()
            ],
            "page_monitors": [
                monitor.to_payload()
                for monitor in self.repository.list_page_monitors(
                    investigation_id
                )
            ],
            "evidence": [
                capture.to_payload()
                for capture in self.repository.list_evidence_captures(
                    investigation_id
                )
            ],
            "entities": [
                entity.to_payload()
                for entity in self.repository.list_extracted_entities(
                    investigation_id
                )
            ],
            "graph_entities": [
                entity.to_payload()
                for entity in self.repository.list_investigation_entities(
                    investigation_id
                )
            ],
            "exports": [
                export.to_payload()
                for export in self.repository.list_investigation_exports(
                    investigation_id
                )
            ],
            "url_analyses": [
                analysis.to_payload()
                for analysis in self.repository.list_url_analyses(
                    investigation_id
                )
            ],
        }

    def create_graph_entity(
        self,
        investigation_id: str,
        payload: Mapping,
    ) -> dict:
        label = _clean_text(
            payload.get("label"),
            max_length=MAX_INVESTIGATION_ENTITY_LABEL_LENGTH,
        )
        if not label:
            raise InvestigationValidationError("Entity name is required.")
        return self.repository.create_investigation_entity(
            investigation_id,
            label=label,
            notes=_clean_text(
                payload.get("notes"),
                max_length=MAX_INVESTIGATION_ENTITY_NOTES_LENGTH,
            ),
            tags=_normalize_tags(payload.get("tags", ())),
        ).to_payload()

    def create_graph_entity_from_result(
        self,
        investigation_id: str,
        result_id: str,
        payload: Mapping,
    ) -> dict:
        self.repository.get_saved_result_entity_sources(
            investigation_id,
            result_id,
        )
        entity_payload = {
            **dict(payload),
            "tags": (
                payload.get("category")
                or payload.get("tags", ())
            ),
        }
        entity = self.create_graph_entity(
            investigation_id,
            entity_payload,
        )
        return self.link_result_to_graph_entity(
            investigation_id,
            str(entity["id"]),
            result_id,
        )

    def create_graph_entity_from_extracted(
        self,
        investigation_id: str,
        extracted_entity_id: str,
        payload: Mapping,
    ) -> dict:
        extracted = next(
            (
                entity
                for entity in self.repository.list_extracted_entities(
                    investigation_id
                )
                if entity.id == extracted_entity_id
            ),
            None,
        )
        if extracted is None:
            raise InvestigationValidationError(
                f"Extracted entity not found: {extracted_entity_id}"
            )
        property_key = _clean_text(
            payload.get("property_key")
            or _default_property_key(extracted.entity_type),
            max_length=MAX_ENTITY_PROPERTY_KEY_LENGTH,
        )
        entity_payload = {
            **dict(payload),
            "tags": (
                payload.get("category")
                or payload.get("tags", ())
            ),
        }
        entity = self.create_graph_entity(
            investigation_id,
            entity_payload,
        )
        entity_id = str(entity["id"])
        self.link_result_to_graph_entity(
            investigation_id,
            entity_id,
            extracted.result_id,
        )
        self.attach_extracted_property(
            investigation_id,
            extracted_entity_id,
            {
                "graph_entity_id": entity_id,
                "property_key": property_key,
            },
        )
        return next(
            item.to_payload()
            for item in self.repository.list_investigation_entities(
                investigation_id
            )
            if item.id == entity_id
        )

    def update_graph_entity(
        self,
        investigation_id: str,
        entity_id: str,
        payload: Mapping,
    ) -> dict:
        label = _clean_text(
            payload.get("label"),
            max_length=MAX_INVESTIGATION_ENTITY_LABEL_LENGTH,
        )
        if not label:
            raise InvestigationValidationError("Entity name is required.")
        return self.repository.update_investigation_entity(
            investigation_id,
            entity_id,
            label=label,
            notes=_clean_text(
                payload.get("notes"),
                max_length=MAX_INVESTIGATION_ENTITY_NOTES_LENGTH,
            ),
            tags=_normalize_tags(payload.get("tags", ())),
        ).to_payload()

    def delete_graph_entity(
        self,
        investigation_id: str,
        entity_id: str,
    ) -> None:
        self.repository.delete_investigation_entity(
            investigation_id,
            entity_id,
        )

    def set_graph_entity_property(
        self,
        investigation_id: str,
        entity_id: str,
        payload: Mapping,
    ) -> dict:
        key = _clean_text(
            payload.get("key"),
            max_length=MAX_ENTITY_PROPERTY_KEY_LENGTH,
        )
        value = _clean_text(
            payload.get("value"),
            max_length=MAX_ENTITY_PROPERTY_VALUE_LENGTH,
        )
        if not key:
            raise InvestigationValidationError("Property name is required.")
        if not value:
            raise InvestigationValidationError("Property value is required.")
        return self.repository.set_investigation_entity_property(
            investigation_id,
            entity_id,
            key=key,
            value=value,
        ).to_payload()

    def delete_graph_entity_property(
        self,
        investigation_id: str,
        entity_id: str,
        key: str,
    ) -> dict:
        normalized_key = _clean_text(
            key,
            max_length=MAX_ENTITY_PROPERTY_KEY_LENGTH,
        )
        if not normalized_key:
            raise InvestigationValidationError("Property name is required.")
        return self.repository.set_investigation_entity_property(
            investigation_id,
            entity_id,
            key=normalized_key,
            value=None,
        ).to_payload()

    def link_result_to_graph_entity(
        self,
        investigation_id: str,
        entity_id: str,
        result_id: str,
    ) -> dict:
        return self.repository.link_result_to_investigation_entity(
            investigation_id,
            entity_id,
            result_id,
        ).to_payload()

    def unlink_result_from_graph_entity(
        self,
        investigation_id: str,
        entity_id: str,
        result_id: str,
    ) -> None:
        self.repository.unlink_result_from_investigation_entity(
            investigation_id,
            entity_id,
            result_id,
        )

    def attach_extracted_property(
        self,
        investigation_id: str,
        extracted_entity_id: str,
        payload: Mapping,
    ) -> dict:
        graph_entity_id = _clean_text(
            payload.get("graph_entity_id"),
            max_length=100,
        )
        property_key = _clean_text(
            payload.get("property_key"),
            max_length=MAX_ENTITY_PROPERTY_KEY_LENGTH,
        )
        if not graph_entity_id:
            raise InvestigationValidationError(
                "Select an investigation entity."
            )
        if not property_key:
            raise InvestigationValidationError("Property name is required.")
        return self.repository.attach_extracted_entity_property(
            investigation_id,
            extracted_entity_id,
            graph_entity_id,
            property_key=property_key,
        ).to_payload()

    def detach_extracted_property(
        self,
        investigation_id: str,
        extracted_entity_id: str,
    ) -> dict:
        return self.repository.attach_extracted_entity_property(
            investigation_id,
            extracted_entity_id,
            None,
            property_key="",
        ).to_payload()

    def update_result(
        self,
        investigation_id: str,
        result_id: str,
        payload: Mapping,
    ):
        analyst_status = str(
            payload.get("analyst_status", "a_verifier") or "a_verifier"
        ).strip()
        notes = _clean_text(
            payload.get("notes"),
            max_length=MAX_RESULT_NOTES_LENGTH,
        )
        return self.repository.update_investigation_result(
            investigation_id,
            result_id,
            analyst_status=analyst_status,
            favorite=bool(payload.get("favorite", False)),
            notes=notes,
            tags=_normalize_tags(payload.get("tags", ())),
        )

    def attach_search(self, investigation_id: str, search_run_id: str):
        return self.repository.attach_search(investigation_id, search_run_id)

    def extract_entities(
        self,
        investigation_id: str,
        result_id: str,
    ) -> list[dict]:
        sources = self.repository.get_saved_result_entity_sources(
            investigation_id,
            result_id,
        )
        remaining_chars = MAX_ENTITY_SOURCE_TOTAL_CHARS
        captures = self.repository.list_evidence_captures(investigation_id)
        for capture in captures:
            if capture.result_id != result_id:
                continue
            for artifact in capture.artifacts:
                if artifact.artifact_type != "text" or remaining_chars <= 0:
                    continue
                path = Path(artifact.file_path)
                if not path.is_absolute():
                    path = self.base_dir / path
                try:
                    resolved = path.resolve()
                    resolved.relative_to(self.base_dir)
                    if (
                        not resolved.is_file()
                        or resolved.stat().st_size > MAX_ENTITY_SOURCE_BYTES
                    ):
                        continue
                    content = resolved.read_text(
                        encoding="utf-8",
                        errors="replace",
                    )[:remaining_chars]
                except (OSError, ValueError):
                    continue
                if content.strip():
                    sources[f"archive_text:{capture.id}"] = content
                    remaining_chars -= len(content)
        candidates = extract_entity_candidates(sources)
        return [
            entity.to_payload()
            for entity in self.repository.upsert_extracted_entities(
                investigation_id,
                result_id,
                (asdict(candidate) for candidate in candidates),
            )
        ]

    def update_entity_status(
        self,
        investigation_id: str,
        entity_id: str,
        status: str,
    ) -> dict:
        normalized_status = str(status or "").strip()
        if normalized_status not in ENTITY_STATUSES:
            raise InvestigationValidationError(
                f"Unsupported entity status: {normalized_status}"
            )
        return self.repository.update_extracted_entity_status(
            investigation_id,
            entity_id,
            normalized_status,
        ).to_payload()

    def update_entity_metadata(
        self,
        investigation_id: str,
        entity_id: str,
        payload: Mapping,
    ) -> dict:
        entity_type = _clean_text(
            payload.get("entity_type"),
            max_length=40,
        )
        if entity_type not in ENTITY_TYPES:
            raise InvestigationValidationError(
                f"Unsupported entity type: {entity_type}"
            )
        custom_label = _clean_text(
            payload.get("custom_label"),
            max_length=MAX_ENTITY_CUSTOM_LABEL_LENGTH,
        )
        tags = _normalize_tags(payload.get("tags", ()))
        return self.repository.update_extracted_entity_metadata(
            investigation_id,
            entity_id,
            entity_type=entity_type,
            custom_label=custom_label,
            tags=tags,
        ).to_payload()

    def delete_entity(
        self,
        investigation_id: str,
        entity_id: str,
    ) -> None:
        self.repository.delete_extracted_entity(
            investigation_id,
            entity_id,
        )

    def analyze_result_url(
        self,
        investigation_id: str,
        result_id: str,
    ) -> dict:
        url = self.repository.get_saved_result_url(
            investigation_id,
            result_id,
        )
        analysis = analyze_url(url)
        return self.repository.record_url_analysis(
            investigation_id,
            result_id,
            analysis.to_payload(),
        ).to_payload()

    def record_export(self, investigation_id: str, **kwargs) -> dict:
        return self.repository.record_investigation_export(
            investigation_id,
            **kwargs,
        ).to_payload()

    def get_export(
        self,
        investigation_id: str,
        export_id: str,
    ) -> InvestigationExport:
        return self.repository.get_investigation_export(
            investigation_id,
            export_id,
        )

    def delete_export(
        self,
        investigation_id: str,
        export_id: str,
    ) -> None:
        self.repository.delete_investigation_export(
            investigation_id,
            export_id,
        )

    def save_page(self, investigation_id: str, payload: Mapping):
        return self.repository.save_page(
            investigation_id,
            url=_clean_text(
                payload.get("url"),
                max_length=MAX_PAGE_URL_LENGTH,
            ),
            title=_clean_text(
                payload.get("title"),
                max_length=MAX_PAGE_TITLE_LENGTH,
            ),
            description=_clean_text(
                payload.get("description"),
                max_length=MAX_PAGE_DESCRIPTION_LENGTH,
            ),
            referrer=_clean_text(
                payload.get("referrer"),
                max_length=MAX_PAGE_URL_LENGTH,
            ),
        )

    def observe_saved_page(self, investigation_id: str, payload: Mapping) -> bool:
        return self.repository.observe_saved_page(
            investigation_id,
            url=_clean_text(
                payload.get("url"),
                max_length=MAX_PAGE_URL_LENGTH,
            ),
        )

    def remove_saved_page(self, investigation_id: str, result_id: str) -> None:
        self.repository.remove_saved_page(investigation_id, result_id)

    def create_page_monitor(
        self,
        investigation_id: str,
        result_id: str,
    ) -> PageMonitor:
        return self.repository.create_page_monitor(
            investigation_id,
            result_id,
        )

    def get_page_monitor(
        self,
        investigation_id: str,
        monitor_id: str,
    ) -> PageMonitor:
        return self.repository.get_page_monitor(
            investigation_id,
            monitor_id,
        )

    def get_page_monitor_for_result(
        self,
        investigation_id: str,
        result_id: str,
    ) -> PageMonitor | None:
        return self.repository.get_page_monitor_for_result(
            investigation_id,
            result_id,
        )

    def delete_page_monitor(
        self,
        investigation_id: str,
        monitor_id: str,
    ) -> None:
        self.repository.delete_page_monitor(
            investigation_id,
            monitor_id,
        )

    def advance_page_monitor(
        self,
        investigation_id: str,
        monitor_id: str,
        capture_id: str,
    ) -> PageMonitor:
        return self.repository.advance_page_monitor(
            investigation_id,
            monitor_id,
            capture_id,
        )

    def record_page_comparison(self, **kwargs) -> PageComparison:
        return self.repository.record_page_comparison(**kwargs)

    def record_evidence_capture(self, **kwargs):
        kwargs["name"] = _clean_text(
            kwargs.get("name"),
            max_length=MAX_EVIDENCE_NAME_LENGTH,
        )
        return self.repository.record_evidence_capture(**kwargs)

    def get_evidence_capture(self, investigation_id: str, capture_id: str):
        return self.repository.get_evidence_capture(
            investigation_id,
            capture_id,
        )

    def delete_evidence_capture(
        self,
        investigation_id: str,
        capture_id: str,
    ) -> None:
        self.repository.delete_evidence_capture(
            investigation_id,
            capture_id,
        )

    def clear_search_history(self) -> int:
        return self.repository.clear_search_history()
