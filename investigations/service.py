from __future__ import annotations

import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping

from analysis.entities import extract_entity_candidates
from analysis.urls import analyze_url
from exceptions import InvestigationValidationError
from exports.zeroneurone_tagsets import (
    canonical_zeroneurone_tag,
    zeroneurone_tagset_suggested_properties,
)
from investigations.models import (
    ANALYST_STATUSES,
    ENTITY_STATUSES,
    ENTITY_TYPES,
    Investigation,
    InvestigationExport,
    LocalSearchFilters,
    PageComparison,
    PageMonitor,
    EvidenceCapture,
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
PROPERTY_TYPES = {
    "text",
    "number",
    "date",
    "datetime",
    "boolean",
    "choice",
    "geo",
    "country",
    "link",
}

ARCHIVE_ARTIFACT_TYPES = {"html", "mhtml", "text", "txt"}


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


def _has_archive_artifact(capture: EvidenceCapture) -> bool:
    for artifact in capture.artifacts:
        artifact_type = str(artifact.artifact_type or "").casefold()
        mime_type = str(artifact.mime_type or "").casefold()
        if artifact_type in ARCHIVE_ARTIFACT_TYPES:
            return True
        if "html" in mime_type or mime_type.startswith("text/"):
            return True
    return False


def _capture_datetime(capture: EvidenceCapture) -> datetime:
    try:
        parsed = datetime.fromisoformat(
            str(capture.captured_at or "").replace("Z", "+00:00")
        )
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


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


def _tagset_default_properties(tags: Iterable[object]) -> dict[str, str]:
    properties: dict[str, str] = {}
    for tag in tags:
        for suggested in zeroneurone_tagset_suggested_properties(tag):
            key = _clean_text(
                suggested.get("key"),
                max_length=MAX_ENTITY_PROPERTY_KEY_LENGTH,
            )
            if key:
                properties.setdefault(key, "")
    return properties


def _append_property_value(current: object, value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return str(current or "").strip()
    values = [
        item.strip()
        for item in str(current or "").split(";")
        if item.strip()
    ]
    if text not in values:
        values.append(text)
    return "; ".join(values)


def _extracted_property_key(entity) -> str:
    custom_label = _clean_text(
        getattr(entity, "custom_label", ""),
        max_length=MAX_ENTITY_PROPERTY_KEY_LENGTH,
    )
    attributes = getattr(entity, "attributes", {})
    if not isinstance(attributes, Mapping):
        attributes = {}
    suggested = _clean_text(
        attributes.get("property_key") or attributes.get("field_label"),
        max_length=MAX_ENTITY_PROPERTY_KEY_LENGTH,
    )
    default = _default_property_key(str(getattr(entity, "entity_type", "") or ""))
    existing = _clean_text(
        getattr(entity, "property_key", ""),
        max_length=MAX_ENTITY_PROPERTY_KEY_LENGTH,
    )
    if custom_label and (
        not existing or existing in {suggested, default}
    ):
        return custom_label
    if existing:
        return existing
    if custom_label:
        return custom_label
    if suggested:
        return suggested
    return default


def _extracted_property_value(entity) -> str:
    return _clean_text(
        getattr(entity, "value_original", "")
        or getattr(entity, "value_normalized", ""),
        max_length=MAX_ENTITY_PROPERTY_VALUE_LENGTH,
    )


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
        relations_by_source = self.repository.list_entity_relations_by_source(
            investigation_id
        )
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
                {
                    **entity.to_payload(),
                    "relations": relations_by_source.get(entity.id, []),
                }
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
        tags = _normalize_tags(payload.get("tags", ()))
        return self.repository.create_investigation_entity(
            investigation_id,
            label=label,
            notes=_clean_text(
                payload.get("notes"),
                max_length=MAX_INVESTIGATION_ENTITY_NOTES_LENGTH,
            ),
            tags=tags,
            properties=_tagset_default_properties(tags),
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
            or _extracted_property_key(extracted),
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
        self.repository.link_result_to_investigation_entity(
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

    def add_graph_entity_relation(
        self,
        investigation_id: str,
        source_entity_id: str,
        target_entity_id: str,
        label: str,
        relation_id: str = "",
    ) -> dict:
        return self.repository.add_entity_relation(
            investigation_id,
            str(source_entity_id or "").strip(),
            str(target_entity_id or "").strip(),
            _clean_text(label, max_length=120),
            relation_id=str(relation_id or "").strip(),
        )

    def update_graph_entity_relation(
        self,
        investigation_id: str,
        relation_id: str,
        label: str,
    ) -> None:
        self.repository.update_entity_relation(
            investigation_id,
            str(relation_id or "").strip(),
            _clean_text(label, max_length=120),
        )

    def delete_graph_entity_relation(
        self,
        investigation_id: str,
        relation_id: str,
    ) -> None:
        self.repository.delete_entity_relation(
            investigation_id,
            str(relation_id or "").strip(),
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
        updated = self.repository.set_investigation_entity_property(
            investigation_id,
            entity_id,
            key=normalized_key,
            value=None,
        )
        normalized_key_fold = normalized_key.casefold()
        for extracted in self.repository.list_extracted_entities(investigation_id):
            if extracted.investigation_entity_id != entity_id:
                continue
            if extracted.property_key.casefold() != normalized_key_fold:
                continue
            self.repository.delete_extracted_entity(
                investigation_id,
                extracted.id,
            )
        return updated.to_payload()

    def link_result_to_graph_entity(
        self,
        investigation_id: str,
        entity_id: str,
        result_id: str,
    ) -> dict:
        linked = self.repository.link_result_to_investigation_entity(
            investigation_id,
            entity_id,
            result_id,
        )
        # Linking no longer auto-attaches the page's extracted candidates:
        # the analyst validates/attaches them explicitly (AI-20260622-002).
        return next(
            entity.to_payload()
            for entity in self.repository.list_investigation_entities(
                investigation_id
            )
            if entity.id == linked.id
        )

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
        property_type = str(payload.get("property_type", "") or "").strip()
        if property_type and property_type not in PROPERTY_TYPES:
            raise InvestigationValidationError(
                f"Unsupported property type: {property_type}"
            )
        duplicate_strategy = str(
            payload.get("duplicate_strategy", "append") or "append"
        ).strip()
        if duplicate_strategy not in {"append", "replace"}:
            raise InvestigationValidationError(
                f"Unsupported duplicate strategy: {duplicate_strategy}"
            )
        entity = self.repository.attach_extracted_entity_property(
            investigation_id,
            extracted_entity_id,
            graph_entity_id,
            property_key=property_key,
        )
        entity = self.repository.update_extracted_entity_metadata(
            investigation_id,
            entity.id,
            entity_type=entity.entity_type,
            custom_label=entity.custom_label,
            tags=entity.tags,
            property_type=property_type,
        )
        self._sync_extracted_property_to_graph_entity(
            investigation_id,
            graph_entity_id,
            entity,
            property_key,
            duplicate_strategy=duplicate_strategy,
        )
        return entity.to_payload()

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

    def record_selection_entity(
        self,
        investigation_id: str,
        result_id: str,
        *,
        value: str,
        property_key: str,
        property_type: str = "",
        entity_type: str = "other",
    ):
        """Persist an analyst-selected value as a validated extracted entity.

        Used by the overlay so that text attached to a graph entity also shows
        up under its source page's entities and links back to that page.
        """
        normalized_type = str(entity_type or "other").strip() or "other"
        if normalized_type not in ENTITY_TYPES:
            normalized_type = "other"
        text = str(value or "").strip()
        normalized_property_type = str(property_type or "").strip()
        if (
            normalized_property_type
            and normalized_property_type not in PROPERTY_TYPES
        ):
            raise InvestigationValidationError(
                f"Unsupported property type: {normalized_property_type}"
            )
        attributes = {"property_key": property_key} if property_key else {}
        if normalized_property_type:
            attributes["property_type"] = normalized_property_type
        candidate = {
            "entity_type": normalized_type,
            "value": text,
            "normalized_value": text,
            "source_field": "selection",
            "source_text": text,
            "confidence": 1.0,
            "confidence_reasons": ("Attached from page selection",),
            "attributes": attributes,
        }
        created = self.repository.upsert_extracted_entities(
            investigation_id,
            result_id,
            [candidate],
        )
        entity = next(
            (
                item
                for item in created
                if item.entity_type == normalized_type
                and item.value_normalized == text
            ),
            None,
        )
        if entity is None:
            return None
        return self.repository.update_extracted_entity_status(
            investigation_id,
            entity.id,
            "validated",
        )

    def set_extracted_entity_source_capture(
        self,
        investigation_id: str,
        extracted_entity_id: str,
        capture_id: str,
    ) -> dict:
        capture_id = str(capture_id or "").strip()
        if not capture_id:
            raise InvestigationValidationError("Evidence capture is required.")
        self.repository.get_evidence_capture(investigation_id, capture_id)
        current = next(
            (
                entity
                for entity in self.repository.list_extracted_entities(
                    investigation_id
                )
                if entity.id == extracted_entity_id
            ),
            None,
        )
        if current is None:
            raise InvestigationValidationError(
                f"Extracted entity not found: {extracted_entity_id}"
            )
        attributes = dict(current.attributes)
        attributes["source_capture_id"] = capture_id
        return self.repository.update_extracted_entity_attributes(
            investigation_id,
            extracted_entity_id,
            attributes,
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
        sources.pop("url", None)
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
        self.repository.upsert_extracted_entities(
            investigation_id,
            result_id,
            (asdict(candidate) for candidate in candidates),
        )
        # Extracted candidates stay "proposed" for explicit analyst triage;
        # no automatic attach/validation (see AI-20260622-002).
        return [
            entity.to_payload()
            for entity in self.repository.list_extracted_entities(
                investigation_id
            )
            if entity.result_id == result_id
        ]

    def _sync_extracted_property_to_graph_entity(
        self,
        investigation_id: str,
        graph_entity_id: str,
        extracted_entity,
        property_key: str,
        *,
        duplicate_strategy: str = "append",
    ) -> None:
        value = _extracted_property_value(extracted_entity)
        key = _clean_text(
            property_key or _extracted_property_key(extracted_entity),
            max_length=MAX_ENTITY_PROPERTY_KEY_LENGTH,
        )
        if not key or not value:
            return
        graph_entity = next(
            (
                entity
                for entity in self.repository.list_investigation_entities(
                    investigation_id
                )
                if entity.id == graph_entity_id
            ),
            None,
        )
        if graph_entity is None:
            return
        self.repository.set_investigation_entity_property(
            investigation_id,
            graph_entity_id,
            key=key,
            value=(
                value
                if duplicate_strategy == "replace"
                else _append_property_value(
                    graph_entity.properties.get(key),
                    value,
                )
            ),
        )

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
        property_type = str(payload.get("property_type", "") or "").strip()
        if property_type and property_type not in PROPERTY_TYPES:
            raise InvestigationValidationError(
                f"Unsupported property type: {property_type}"
            )
        return self.repository.update_extracted_entity_metadata(
            investigation_id,
            entity_id,
            entity_type=entity_type,
            custom_label=custom_label,
            tags=tags,
            property_type=property_type,
        ).to_payload()

    def set_entity_property_scope(
        self,
        investigation_id: str,
        entity_id: str,
        scope: str,
    ) -> dict:
        normalized_scope = str(scope or "").strip()
        if normalized_scope not in {"page", "entity"}:
            raise InvestigationValidationError(
                f"Unsupported property scope: {normalized_scope}"
            )
        return self.repository.set_extracted_entity_property_scope(
            investigation_id,
            entity_id,
            normalized_scope,
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

    def list_evidence_captures(
        self,
        investigation_id: str,
    ) -> list[EvidenceCapture]:
        return self.repository.list_evidence_captures(investigation_id)

    def get_evidence_capture(self, investigation_id: str, capture_id: str):
        return self.repository.get_evidence_capture(
            investigation_id,
            capture_id,
        )

    def latest_page_archive_for_result(
        self,
        investigation_id: str,
        result_id: str,
    ) -> EvidenceCapture | None:
        candidates = [
            capture
            for capture in self.repository.list_evidence_captures(
                investigation_id
            )
            if capture.result_id == result_id
            and capture.capture_kind == "page_archive"
            and _has_archive_artifact(capture)
        ]
        if not candidates:
            return None
        return max(candidates, key=_capture_datetime)

    def evidence_capture_reference_count(
        self,
        investigation_id: str,
        capture_id: str,
    ) -> int:
        capture = self.repository.get_evidence_capture(
            investigation_id,
            capture_id,
        )
        references = 0
        for entity in self.repository.list_extracted_entities(
            investigation_id
        ):
            if entity.attributes.get("source_capture_id") == capture_id:
                references += 1
        latest = self.latest_page_archive_for_result(
            investigation_id,
            capture.result_id,
        )
        if latest is not None and latest.id == capture_id:
            for entity in self.repository.list_investigation_entities(
                investigation_id
            ):
                if capture.result_id in entity.linked_result_ids:
                    references += 1
                    break
        return references

    def ensure_evidence_capture_deletable(
        self,
        investigation_id: str,
        capture_id: str,
    ) -> None:
        if self.evidence_capture_reference_count(investigation_id, capture_id):
            raise InvestigationValidationError(
                "Cette archive est utilisée comme preuve de provenance. "
                "Supprimez la page enregistrée pour retirer cette preuve."
            )

    def delete_evidence_capture(
        self,
        investigation_id: str,
        capture_id: str,
    ) -> None:
        self.ensure_evidence_capture_deletable(investigation_id, capture_id)
        self.repository.delete_evidence_capture(
            investigation_id,
            capture_id,
        )

    def clear_search_history(self) -> int:
        return self.repository.clear_search_history()
