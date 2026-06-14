from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from typing import Mapping
from urllib.parse import urlsplit, urlunsplit


MAX_SOURCE_TEXT_LENGTH = 240
ENTITY_TYPE_ORDER = {
    "email": 0,
    "phone": 1,
    "url": 2,
    "domain": 3,
    "ipv4": 4,
    "ipv6": 5,
    "handle": 6,
    "identifier": 7,
    "coordinates": 8,
}

EMAIL_PATTERN = re.compile(
    r"(?<![\w.+-])[\w.!#$%&'*+/=?^`{|}~-]+@"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,63}\b"
)
URL_PATTERN = re.compile(r"https?://[^\s<>'\"]+", re.IGNORECASE)
DOMAIN_PATTERN = re.compile(
    r"(?<![@\w-])"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"(?:[A-Za-z]{2,63}|xn--[A-Za-z0-9-]{2,59})"
    r"(?![\w@-])",
    re.IGNORECASE,
)
PHONE_PATTERN = re.compile(
    r"(?<![\w.])(?:\+\d{1,3}[\s().-]*)?"
    r"(?:\d[\s().-]*){6,14}\d(?![\d\s().-]*\d)"
)
HANDLE_PATTERN = re.compile(r"(?<![\w@])@[A-Za-z0-9_][A-Za-z0-9_.-]{1,31}\b")
UUID_PATTERN = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-"
    r"[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",
    re.IGNORECASE,
)
COORDINATE_PATTERN = re.compile(
    r"(?<![\d.])"
    r"([+-]?(?:90(?:\.0+)?|[0-8]?\d(?:\.\d+)?))"
    r"\s*[,;]\s*"
    r"([+-]?(?:180(?:\.0+)?|1[0-7]\d(?:\.\d+)?|"
    r"\d?\d(?:\.\d+)?))"
    r"(?!\d)"
)
IP_TOKEN_PATTERN = re.compile(
    r"(?<![\w])"
    r"(?:[0-9A-Fa-f:.]*:[0-9A-Fa-f:.]+|\d{1,3}(?:\.\d{1,3}){3})"
    r"(?![\w])"
)


@dataclass(frozen=True)
class EntityCandidate:
    entity_type: str
    value: str
    normalized_value: str
    source_field: str
    source_text: str
    confidence: float


def _source_passage(text: str, start: int, end: int) -> str:
    left = max(0, start - 80)
    right = min(len(text), end + 80)
    passage = " ".join(text[left:right].split())
    return passage[:MAX_SOURCE_TEXT_LENGTH]


def _normalized_url(value: str) -> str:
    cleaned = value.rstrip(".,;:!?)]}")
    try:
        parsed = urlsplit(cleaned)
    except ValueError:
        return ""
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        return ""
    hostname = parsed.hostname.lower()
    try:
        port = parsed.port
    except ValueError:
        return ""
    netloc = f"[{hostname}]" if ":" in hostname else hostname
    if port and not (
        (parsed.scheme.lower() == "http" and port == 80)
        or (parsed.scheme.lower() == "https" and port == 443)
    ):
        netloc = f"{netloc}:{port}"
    return urlunsplit(
        (
            parsed.scheme.lower(),
            netloc,
            parsed.path or "/",
            parsed.query,
            "",
        )
    )


def _normalized_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if not 8 <= len(digits) <= 15:
        return ""
    return f"+{digits}" if value.strip().startswith("+") else digits


def _append_match(
    candidates: list[EntityCandidate],
    *,
    entity_type: str,
    value: str,
    normalized_value: str,
    source_field: str,
    text: str,
    start: int,
    end: int,
    confidence: float,
) -> None:
    if not normalized_value:
        return
    candidates.append(
        EntityCandidate(
            entity_type=entity_type,
            value=value,
            normalized_value=normalized_value,
            source_field=source_field,
            source_text=_source_passage(text, start, end),
            confidence=confidence,
        )
    )


def _extract_from_text(source_field: str, text: str) -> list[EntityCandidate]:
    candidates: list[EntityCandidate] = []
    phone_exclusions = [
        match.span()
        for pattern in (
            EMAIL_PATTERN,
            URL_PATTERN,
            UUID_PATTERN,
            COORDINATE_PATTERN,
            IP_TOKEN_PATTERN,
        )
        for match in pattern.finditer(text)
    ]

    for match in EMAIL_PATTERN.finditer(text):
        _append_match(
            candidates,
            entity_type="email",
            value=match.group(0),
            normalized_value=match.group(0).casefold(),
            source_field=source_field,
            text=text,
            start=match.start(),
            end=match.end(),
            confidence=0.99,
        )

    for match in URL_PATTERN.finditer(text):
        normalized = _normalized_url(match.group(0))
        _append_match(
            candidates,
            entity_type="url",
            value=match.group(0).rstrip(".,;:!?)]}"),
            normalized_value=normalized,
            source_field=source_field,
            text=text,
            start=match.start(),
            end=match.end(),
            confidence=0.99,
        )

    for match in DOMAIN_PATTERN.finditer(text):
        value = match.group(0)
        _append_match(
            candidates,
            entity_type="domain",
            value=value,
            normalized_value=value.casefold().removeprefix("www."),
            source_field=source_field,
            text=text,
            start=match.start(),
            end=match.end(),
            confidence=0.95,
        )

    for match in PHONE_PATTERN.finditer(text):
        if any(
            match.start() < end and match.end() > start
            for start, end in phone_exclusions
        ):
            continue
        normalized = _normalized_phone(match.group(0))
        _append_match(
            candidates,
            entity_type="phone",
            value=match.group(0).strip(),
            normalized_value=normalized,
            source_field=source_field,
            text=text,
            start=match.start(),
            end=match.end(),
            confidence=0.85,
        )

    for match in HANDLE_PATTERN.finditer(text):
        _append_match(
            candidates,
            entity_type="handle",
            value=match.group(0),
            normalized_value=match.group(0).casefold(),
            source_field=source_field,
            text=text,
            start=match.start(),
            end=match.end(),
            confidence=0.85,
        )

    for match in UUID_PATTERN.finditer(text):
        _append_match(
            candidates,
            entity_type="identifier",
            value=match.group(0),
            normalized_value=match.group(0).casefold(),
            source_field=source_field,
            text=text,
            start=match.start(),
            end=match.end(),
            confidence=0.99,
        )

    for match in COORDINATE_PATTERN.finditer(text):
        if "." not in match.group(1) and "." not in match.group(2):
            continue
        latitude = float(match.group(1))
        longitude = float(match.group(2))
        normalized = f"{latitude:.6f},{longitude:.6f}"
        _append_match(
            candidates,
            entity_type="coordinates",
            value=match.group(0),
            normalized_value=normalized,
            source_field=source_field,
            text=text,
            start=match.start(),
            end=match.end(),
            confidence=0.9,
        )

    for match in IP_TOKEN_PATTERN.finditer(text):
        value = match.group(0).strip("[](),;.")
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            continue
        _append_match(
            candidates,
            entity_type="ipv4" if address.version == 4 else "ipv6",
            value=value,
            normalized_value=address.compressed,
            source_field=source_field,
            text=text,
            start=match.start(),
            end=match.end(),
            confidence=0.99,
        )

    return candidates


def extract_entity_candidates(
    sources: Mapping[str, object],
) -> tuple[EntityCandidate, ...]:
    selected: dict[tuple[str, str], EntityCandidate] = {}
    for source_field in ("url", "title", "description", "notes"):
        text = str(sources.get(source_field, "") or "").strip()
        if not text:
            continue
        for candidate in _extract_from_text(source_field, text):
            key = (candidate.entity_type, candidate.normalized_value)
            current = selected.get(key)
            if current is None or candidate.confidence > current.confidence:
                selected[key] = candidate

    return tuple(
        sorted(
            selected.values(),
            key=lambda item: (
                ENTITY_TYPE_ORDER.get(item.entity_type, 99),
                item.normalized_value,
            ),
        )
    )
