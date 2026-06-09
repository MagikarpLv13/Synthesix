from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping

from exceptions import InvestigationValidationError
from investigations.models import Investigation
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

    def clear_search_history(self) -> int:
        return self.repository.clear_search_history()
