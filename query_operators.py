from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Mapping
from urllib.parse import urlparse


FILTER_FIELDS = ("site", "exclude", "title", "url", "body", "filetype", "after", "before")


@dataclass(frozen=True)
class SearchFilters:
    site: str = ""
    exclude: str = ""
    title: str = ""
    url: str = ""
    body: str = ""
    filetype: str = ""
    after: str = ""
    before: str = ""

    @classmethod
    def from_payload(cls, payload: Mapping | None) -> "SearchFilters":
        if not isinstance(payload, Mapping):
            return cls()
        values = {}
        for field in FILTER_FIELDS:
            value = str(payload.get(field, "") or "").strip()
            values[field] = _normalize_date(value) if field in {"after", "before"} else value
        return cls(**values)

    def has_filters(self) -> bool:
        return any(getattr(self, field).strip() for field in FILTER_FIELDS)

    def to_payload(self) -> dict[str, str]:
        return {
            field: getattr(self, field)
            for field in FILTER_FIELDS
            if getattr(self, field).strip()
        }


def _split_values(value: str) -> list[str]:
    return [part.strip() for part in str(value or "").split(",") if part.strip()]


def _quote_operator_value(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if value.startswith('"') and value.endswith('"'):
        return value
    if any(char.isspace() for char in value):
        return f'"{value}"'
    return value


def _operator_terms(operator: str, values: str) -> list[str]:
    return [f"{operator}:{_quote_operator_value(value)}" for value in _split_values(values)]


def _negative_terms(values: str) -> list[str]:
    return [f"-{_quote_operator_value(value)}" for value in _split_values(values)]


def _plain_terms(values: str) -> list[str]:
    return [_quote_operator_value(value) for value in _split_values(values)]


def _normalize_date(value: str) -> str:
    value = str(value or "").strip()
    if not value:
        return ""
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        return ""


def _date_range(filters: SearchFilters) -> tuple[str, str]:
    after = _normalize_date(filters.after)
    before = _normalize_date(filters.before)
    if after and before and after > before:
        return "", ""
    return after, before


def build_engine_date_params(
    engine_name: str,
    filters: SearchFilters | Mapping | None = None,
    today: date | None = None,
) -> dict[str, str]:
    filters = SearchFilters.from_payload(filters) if not isinstance(filters, SearchFilters) else filters
    after, before = _date_range(filters)
    if not after and not before:
        return {}

    engine = engine_name.lower()
    if engine == "google":
        values = ["cdr:1"]
        if after:
            values.append(f"cd_min:{datetime.strptime(after, '%Y-%m-%d').strftime('%m/%d/%Y')}")
        if before:
            values.append(f"cd_max:{datetime.strptime(before, '%Y-%m-%d').strftime('%m/%d/%Y')}")
        return {"tbs": ",".join(values)}

    range_start = after or "1970-01-01"
    range_end = before or (today or date.today()).isoformat()
    if range_start > range_end:
        return {}
    if engine == "brave":
        return {"tf": f"{range_start}to{range_end}"}
    if engine == "duckduckgo":
        return {"df": f"{range_start}..{range_end}"}
    return {}


def build_display_query(base_query: str, filters: SearchFilters | Mapping | None = None) -> str:
    filters = SearchFilters.from_payload(filters) if not isinstance(filters, SearchFilters) else filters
    parts = [base_query.strip()] if base_query.strip() else []
    parts.extend(_operator_terms("site", filters.site))
    parts.extend(_negative_terms(filters.exclude))
    parts.extend(_operator_terms("intitle", filters.title))
    parts.extend(_operator_terms("inurl", filters.url))
    parts.extend(_operator_terms("inbody", filters.body))
    parts.extend(_operator_terms("filetype", filters.filetype))
    after, before = _date_range(filters)
    if after:
        parts.append(f"after:{after}")
    if before:
        parts.append(f"before:{before}")
    return " ".join(part for part in parts if part)


def build_engine_query(
    base_query: str,
    engine_name: str,
    filters: SearchFilters | Mapping | None = None,
) -> str:
    filters = SearchFilters.from_payload(filters) if not isinstance(filters, SearchFilters) else filters
    engine = engine_name.lower()
    parts = [base_query.strip()] if base_query.strip() else []

    parts.extend(_operator_terms("site", filters.site))
    parts.extend(_negative_terms(filters.exclude))
    parts.extend(_operator_terms("intitle", filters.title))

    if engine in {"google", "duckduckgo"}:
        parts.extend(_operator_terms("inurl", filters.url))
    else:
        parts.extend(_plain_terms(filters.url))

    if engine == "google":
        parts.extend(_operator_terms("intext", filters.body))
    elif engine in {"bing", "brave"}:
        parts.extend(_operator_terms("inbody", filters.body))
    else:
        parts.extend(_plain_terms(filters.body))

    parts.extend(_operator_terms("filetype", filters.filetype))
    return " ".join(part for part in parts if part)


def _domain_from_site_filter(value: str) -> str:
    value = value.strip().lower()
    if not value:
        return ""
    if "://" not in value:
        value = "https://" + value
    parsed = urlparse(value)
    return parsed.netloc.lower().removeprefix("www.")


def _link_matches_site(link: str, site_value: str) -> bool:
    site_domain = _domain_from_site_filter(site_value)
    if not site_domain:
        return True
    parsed = urlparse(str(link))
    link_domain = parsed.netloc.lower().removeprefix("www.")
    return link_domain == site_domain or link_domain.endswith("." + site_domain)


def _link_matches_filetype(link: str, filetype_value: str) -> bool:
    ext = filetype_value.strip().lower().lstrip(".")
    if not ext:
        return True
    return urlparse(str(link)).path.lower().endswith("." + ext)


def result_matches_filters(row: Mapping, filters: SearchFilters | Mapping | None = None) -> bool:
    filters = SearchFilters.from_payload(filters) if not isinstance(filters, SearchFilters) else filters
    if not filters.has_filters():
        return True

    title = str(row.get("title", "")).lower()
    description = str(row.get("description", "")).lower()
    link = str(row.get("link", ""))
    lower_link = link.lower()

    include_sites = _split_values(filters.site)
    if include_sites and not any(_link_matches_site(link, value) for value in include_sites):
        return False

    searchable_result = " ".join((title, description, lower_link))
    if any(value.lower() in searchable_result for value in _split_values(filters.exclude)):
        return False

    if any(value.lower() not in title for value in _split_values(filters.title)):
        return False

    if any(value.lower() not in lower_link for value in _split_values(filters.url)):
        return False

    filetypes = _split_values(filters.filetype)
    if filetypes and not any(_link_matches_filetype(link, value) for value in filetypes):
        return False

    return True
