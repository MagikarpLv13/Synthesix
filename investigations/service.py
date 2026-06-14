from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, Mapping

from analysis.entities import extract_entity_candidates
from exceptions import InvestigationValidationError
from investigations.models import (
    ANALYST_STATUSES,
    ENTITY_STATUSES,
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
        key = tag.casefold()
        if not tag or key in seen:
            continue
        tags.append(tag)
        seen.add(key)
        if len(tags) >= MAX_TAG_COUNT:
            break
    return tuple(tags)


class InvestigationService:
    def __init__(self, repository: InvestigationRepository):
        self.repository = repository

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
            "exports": [
                export.to_payload()
                for export in self.repository.list_investigation_exports(
                    investigation_id
                )
            ],
        }

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

    def delete_entity(
        self,
        investigation_id: str,
        entity_id: str,
    ) -> None:
        self.repository.delete_extracted_entity(
            investigation_id,
            entity_id,
        )

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
