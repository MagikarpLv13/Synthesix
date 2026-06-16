from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from datetime import date
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
    "siret": 9,
    "siren": 10,
    "vat_number": 11,
    "date": 12,
    "address": 13,
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
SIRET_PATTERN = re.compile(
    r"(?<!\d)(?:\d[\s.-]*){14}(?!\d)"
)
SIREN_PATTERN = re.compile(
    r"(?<!\d)(?:\d[\s.-]*){9}(?!\d)"
)
VAT_PATTERN = re.compile(
    r"(?<![A-Z0-9])"
    r"(AT|BE|BG|CY|CZ|DE|DK|EE|EL|ES|FI|FR|GR|HR|HU|IE|IT|LT|LU|LV|"
    r"MT|NL|PL|PT|RO|SE|SI|SK)"
    r"[\s.-]*(\d(?:[\s.-]*[A-Z0-9]){1,11})(?![A-Z0-9])",
    re.IGNORECASE,
)
NUMERIC_DATE_PATTERN = re.compile(
    r"(?<!\d)(?:(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})|"
    r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{2,4}))(?!\d)"
)
MONTH_NAMES = {
    "janvier": 1,
    "january": 1,
    "février": 2,
    "fevrier": 2,
    "february": 2,
    "mars": 3,
    "march": 3,
    "avril": 4,
    "april": 4,
    "mai": 5,
    "may": 5,
    "juin": 6,
    "june": 6,
    "juillet": 7,
    "july": 7,
    "août": 8,
    "aout": 8,
    "august": 8,
    "septembre": 9,
    "september": 9,
    "octobre": 10,
    "october": 10,
    "novembre": 11,
    "november": 11,
    "décembre": 12,
    "decembre": 12,
    "december": 12,
}
TEXT_DATE_PATTERN = re.compile(
    r"(?<!\w)(\d{1,2})(?:er|st|nd|rd|th)?\s+("
    + "|".join(sorted(MONTH_NAMES, key=len, reverse=True))
    + r")\s+(\d{4})(?!\d)",
    re.IGNORECASE,
)
ADDRESS_PATTERN = re.compile(
    r"(?<!\w)(\d{1,5}(?:\s*(?:bis|ter|quater))?)\s+"
    r"(rue|avenue|av\.?|boulevard|bd\.?|route|chemin|impasse|allée|allee|"
    r"place|quai|cours|passage)\s+"
    r"([A-Za-zÀ-ÖØ-öø-ÿ0-9'’ .-]{2,80}?)"
    r"(?:\s*[,;\n]\s*|\s+)"
    r"(\d{5})\s+([A-Za-zÀ-ÖØ-öø-ÿ'’ -]{2,60})"
    r"(?=$|[.,;\n])",
    re.IGNORECASE,
)
VAT_CONTEXT_PATTERN = re.compile(
    r"\b(?:tva|vat|vat\s+number|num(?:é|e)ro\s+de\s+tva|"
    r"intracommunautaire)\b",
    re.IGNORECASE,
)
SIREN_CONTEXT_PATTERN = re.compile(r"\bsiren\b", re.IGNORECASE)
SIRET_CONTEXT_PATTERN = re.compile(r"\bsiret\b", re.IGNORECASE)


@dataclass(frozen=True)
class EntityCandidate:
    entity_type: str
    value: str
    normalized_value: str
    source_field: str
    source_text: str
    confidence: float
    confidence_reasons: tuple[str, ...] = ()
    attributes: Mapping[str, object] | None = None


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
    confidence_reasons: tuple[str, ...] = (),
    attributes: Mapping[str, object] | None = None,
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
            confidence_reasons=confidence_reasons,
            attributes=attributes or {},
        )
    )


def _digits(value: str) -> str:
    return re.sub(r"\D", "", value)


def _luhn_valid(value: str) -> bool:
    if not value.isdigit():
        return False
    total = 0
    parity = len(value) % 2
    for index, character in enumerate(value):
        digit = int(character)
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def _siret_valid(value: str) -> bool:
    if len(value) != 14 or not value.isdigit():
        return False
    if value[:9] == "356000000":
        return sum(int(character) for character in value) % 5 == 0
    return _luhn_valid(value)


def _siren_valid(value: str) -> bool:
    return len(value) == 9 and _luhn_valid(value)


def _nearby_context(text: str, start: int, end: int, radius: int = 50) -> str:
    return text[max(0, start - radius):min(len(text), end + radius)]


def _date_value(year: int, month: int, day: int) -> str | None:
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def _numeric_date_details(match: re.Match) -> tuple[str, float, tuple[str, ...], dict] | None:
    if match.group(1):
        normalized = _date_value(
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3)),
        )
        if normalized is None:
            return None
        return (
            normalized,
            0.98,
            ("ISO-like year-month-day format", "Calendar-valid date"),
            {"precision": "day", "ambiguous": False, "interpretations": [normalized]},
        )

    first = int(match.group(4))
    second = int(match.group(5))
    year = int(match.group(6))
    if year < 100:
        year += 2000 if year < 70 else 1900
    interpretations = []
    day_first = _date_value(year, second, first)
    month_first = _date_value(year, first, second)
    if day_first:
        interpretations.append(day_first)
    if month_first and month_first not in interpretations:
        interpretations.append(month_first)
    if not interpretations:
        return None
    ambiguous = len(interpretations) > 1
    normalized = (
        "ambiguous:" + "|".join(interpretations)
        if ambiguous
        else interpretations[0]
    )
    reasons = ["Calendar-valid numeric date"]
    if ambiguous:
        reasons.append("Day/month order is ambiguous")
    else:
        reasons.append("Day/month order determined by numeric range")
    return (
        normalized,
        0.65 if ambiguous else 0.92,
        tuple(reasons),
        {
            "precision": "day",
            "ambiguous": ambiguous,
            "interpretations": interpretations,
        },
    )


def _extract_from_text(source_field: str, text: str) -> list[EntityCandidate]:
    candidates: list[EntityCandidate] = []
    siret_like_spans = [
        match.span() for match in SIRET_PATTERN.finditer(text)
    ]
    vat_like_spans = [
        match.span() for match in VAT_PATTERN.finditer(text)
    ]
    protected_number_spans: list[tuple[int, int]] = [
        *siret_like_spans,
        *vat_like_spans,
    ]

    for match in SIRET_PATTERN.finditer(text):
        value = _digits(match.group(0))
        context = _nearby_context(text, match.start(), match.end())
        context_match = bool(SIRET_CONTEXT_PATTERN.search(context))
        if not _siret_valid(value):
            continue
        _append_match(
            candidates,
            entity_type="siret",
            value=match.group(0).strip(),
            normalized_value=value,
            source_field=source_field,
            text=text,
            start=match.start(),
            end=match.end(),
            confidence=0.99 if context_match else 0.95,
            confidence_reasons=(
                "Valid 14-digit SIRET checksum",
                "Nearby SIRET label" if context_match else "Unlabelled valid SIRET",
            ),
            attributes={
                "country": "FR",
                "siren": value[:9],
                "nic": value[9:],
                "checksum_valid": True,
            },
        )

    for match in SIREN_PATTERN.finditer(text):
        if any(
            match.start() < end and match.end() > start
            for start, end in (*siret_like_spans, *vat_like_spans)
        ):
            continue
        value = _digits(match.group(0))
        context = _nearby_context(text, match.start(), match.end())
        context_match = bool(SIREN_CONTEXT_PATTERN.search(context))
        if context_match:
            protected_number_spans.append(match.span())
        if not _siren_valid(value):
            continue
        if not context_match:
            protected_number_spans.append(match.span())
        _append_match(
            candidates,
            entity_type="siren",
            value=match.group(0).strip(),
            normalized_value=value,
            source_field=source_field,
            text=text,
            start=match.start(),
            end=match.end(),
            confidence=0.99 if context_match else 0.94,
            confidence_reasons=(
                "Valid 9-digit SIREN checksum",
                "Nearby SIREN label" if context_match else "Unlabelled valid SIREN",
            ),
            attributes={"country": "FR", "checksum_valid": True},
        )

    for match in VAT_PATTERN.finditer(text):
        country = match.group(1).upper()
        body = re.sub(r"[\s.-]", "", match.group(2)).upper()
        if not body or not body[0].isdigit():
            continue
        normalized = f"{country}{body}"
        context = _nearby_context(text, match.start(), match.end(), radius=70)
        has_context = bool(VAT_CONTEXT_PATTERN.search(context))
        checksum_valid = None
        if country == "FR" and len(body) == 11 and body[2:].isdigit():
            siren = body[2:]
            if body[:2].isdigit():
                expected_key = (12 + 3 * (int(siren) % 97)) % 97
                checksum_valid = int(body[:2]) == expected_key
            if checksum_valid is False or not _siren_valid(siren):
                continue
        elif not has_context:
            continue
        _append_match(
            candidates,
            entity_type="vat_number",
            value=match.group(0).strip(),
            normalized_value=normalized,
            source_field=source_field,
            text=text,
            start=match.start(),
            end=match.end(),
            confidence=0.99 if checksum_valid else 0.82,
            confidence_reasons=tuple(
                reason
                for reason in (
                    "Nearby VAT label" if has_context else "",
                    "French VAT key and SIREN are valid"
                    if checksum_valid
                    else "Country-prefixed VAT-like format",
                )
                if reason
            ),
            attributes={
                "country": country,
                "checksum_valid": checksum_valid,
                "siren": body[2:] if country == "FR" and len(body) == 11 else "",
            },
        )

    for match in NUMERIC_DATE_PATTERN.finditer(text):
        details = _numeric_date_details(match)
        if details is None:
            continue
        normalized, confidence, reasons, attributes = details
        protected_number_spans.append(match.span())
        _append_match(
            candidates,
            entity_type="date",
            value=match.group(0),
            normalized_value=normalized,
            source_field=source_field,
            text=text,
            start=match.start(),
            end=match.end(),
            confidence=confidence,
            confidence_reasons=reasons,
            attributes=attributes,
        )

    for match in TEXT_DATE_PATTERN.finditer(text):
        month = MONTH_NAMES[match.group(2).casefold()]
        normalized = _date_value(
            int(match.group(3)),
            month,
            int(match.group(1)),
        )
        if normalized is None:
            continue
        _append_match(
            candidates,
            entity_type="date",
            value=match.group(0),
            normalized_value=normalized,
            source_field=source_field,
            text=text,
            start=match.start(),
            end=match.end(),
            confidence=0.98,
            confidence_reasons=(
                "Explicit month name",
                "Calendar-valid date",
            ),
            attributes={
                "precision": "day",
                "ambiguous": False,
                "interpretations": [normalized],
            },
        )

    for match in ADDRESS_PATTERN.finditer(text):
        street_type = match.group(2).rstrip(".").casefold()
        normalized = " ".join(
            (
                match.group(1).casefold(),
                street_type,
                " ".join(match.group(3).split()).casefold(),
                match.group(4),
                " ".join(match.group(5).split()).casefold(),
            )
        )
        _append_match(
            candidates,
            entity_type="address",
            value=match.group(0).strip(),
            normalized_value=normalized,
            source_field=source_field,
            text=text,
            start=match.start(),
            end=match.end(),
            confidence=0.82,
            confidence_reasons=(
                "Street number and street type detected",
                "French postal code and locality detected",
            ),
            attributes={
                "country": "FR",
                "house_number": match.group(1),
                "street_type": street_type,
                "street_name": " ".join(match.group(3).split()),
                "postal_code": match.group(4),
                "locality": " ".join(match.group(5).split()),
            },
        )

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
    ] + protected_number_spans

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
            confidence_reasons=("Email syntax", "Domain syntax"),
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
            confidence_reasons=("Absolute HTTP(S) URL",),
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
            confidence_reasons=("Domain-name syntax",),
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
            confidence_reasons=("International-length digit sequence",),
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
            confidence_reasons=("Handle prefix and allowed characters",),
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
            confidence_reasons=("RFC 4122 UUID syntax",),
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
            confidence_reasons=("Explicit decimal latitude/longitude pair",),
            attributes={"latitude": latitude, "longitude": longitude},
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
            confidence_reasons=(f"Valid IPv{address.version} address",),
        )

    return candidates


def extract_entity_candidates(
    sources: Mapping[str, object],
) -> tuple[EntityCandidate, ...]:
    selected: dict[tuple[str, str], EntityCandidate] = {}
    preferred_fields = ("url", "title", "description", "notes")
    source_fields = [
        *preferred_fields,
        *(
            field
            for field in sources
            if field not in preferred_fields
        ),
    ]
    for source_field in source_fields:
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
