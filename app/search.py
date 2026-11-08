"""Validated search requests and the lazily started, isolated search browser."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from browser import get_browser_service
from browser_manager import HeadlessBrowserManager
from query_operators import SearchFilters
from settings import AppSettings, ENGINE_NAMES
from query_syntax import is_advanced_query, smart_parse


@dataclass(frozen=True)
class SearchRequest:
    original_queries: tuple[str, ...]
    queries: tuple[str, ...]
    engines: dict[str, bool]
    filters: SearchFilters
    num_results: int
    automatic_dorks: bool

    @classmethod
    def from_payload(cls, payload: Mapping) -> "SearchRequest":
        if not isinstance(payload, Mapping):
            raise ValueError("Invalid search request.")
        queries = payload.get("queries")
        if not isinstance(queries, list) or not 1 <= len(queries) <= 20:
            raise ValueError("Enter between 1 and 20 queries, one per line.")
        if any(not isinstance(q, str) or not q.strip() or len(q.strip()) > 500 or any(ord(c) < 32 for c in q) for q in queries):
            raise ValueError("Each query must contain 1 to 500 characters.")
        engines = payload.get("engines")
        if not isinstance(engines, dict) or any(k not in ENGINE_NAMES or type(v) is not bool for k, v in engines.items()) or not any(engines.values()):
            raise ValueError("Select at least one search engine.")
        count = payload.get("numResults", 20)
        automatic = payload.get("automaticDorks", True)
        if type(count) is not int or not 1 <= count <= 100 or type(automatic) is not bool:
            raise ValueError("Invalid search options.")
        raw_filters = payload.get("filters", {})
        if not isinstance(raw_filters, dict) or any(not isinstance(v, str) or len(v) > 500 for v in raw_filters.values()):
            raise ValueError("Invalid search filters.")
        originals = tuple(dict.fromkeys(q.strip() for q in queries))
        prepared = tuple(smart_parse(q) if automatic and not is_advanced_query(q) else q for q in originals)
        return cls(originals, prepared, dict(engines), SearchFilters.from_payload(raw_filters), count, automatic)

    def to_payload(self) -> dict:
        return {"queries": list(self.original_queries), "engines": self.engines, "filters": self.filters.to_payload(), "numResults": self.num_results, "automaticDorks": self.automatic_dorks}


class SearchBrowserProvider:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.manager: HeadlessBrowserManager | None = None

    async def get_browser(self):
        if self.manager is not None:
            if await get_browser_service(self.manager.browser).ping():
                return self.manager.browser
            await self.stop()
        self.manager = await HeadlessBrowserManager.create_search(self.settings)
        return self.manager.browser

    async def stop(self) -> None:
        manager, self.manager = self.manager, None
        if manager is not None:
            await manager.stop()
