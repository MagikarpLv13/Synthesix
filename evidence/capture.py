from __future__ import annotations

import asyncio
import base64
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from lxml import html as lxml_html
from zendriver import cdp

from evidence.hashing import sha256_bytes


MIN_CAPTURE_SIZE = 8.0
MAX_CAPTURE_DIMENSION = 32768.0
MAX_CAPTURE_AREA = 100_000_000.0
REDACTED_VALUE = "[REDACTED]"
SENSITIVE_HEADERS = frozenset(
    {
        "authentication-info",
        "authorization",
        "cookie",
        "proxy-authentication-info",
        "proxy-authorization",
        "set-cookie",
        "x-api-key",
        "x-auth-token",
        "x-csrf-token",
        "x-xsrf-token",
    }
)
SENSITIVE_AUTOCOMPLETE_VALUES = frozenset(
    {
        "cc-csc",
        "cc-number",
        "current-password",
        "new-password",
        "one-time-code",
    }
)
SENSITIVE_FIELD_FRAGMENTS = (
    "apikey",
    "authorization",
    "authtoken",
    "clientsecret",
    "cookie",
    "credential",
    "csrf",
    "password",
    "passwd",
    "passcode",
    "refreshtoken",
    "secret",
    "session",
    "token",
    "xsrf",
)
_HEADER_PATTERN = re.compile(r"^([!#$%&'*+\-.^_`|~0-9A-Za-z]+)\s*:")
_ATTRIBUTE_PATTERN = re.compile(
    r"""(?P<name>[^\s=/>]+)(?:\s*=\s*(?:"(?P<double>[^"]*)"|"""
    r"""'(?P<single>[^']*)'|(?P<bare>[^\s"'=<>`]+)))?""",
    re.DOTALL,
)
_SENSITIVE_TAG_PATTERN = re.compile(
    r"""<(?P<tag>input|meta)\b"""
    r"""(?P<attrs>(?:[^>"']|"[^"]*"|'[^']*')*)>""",
    re.IGNORECASE | re.DOTALL,
)
_TEXTAREA_PATTERN = re.compile(
    r"""(?P<start><textarea\b"""
    r"""(?P<attrs>(?:[^>"']|"[^"]*"|'[^']*')*)>)"""
    r"""(?P<content>.*?)"""
    r"""(?P<end></textarea\s*>)""",
    re.IGNORECASE | re.DOTALL,
)


@dataclass(frozen=True)
class CapturedPng:
    path: Path
    sha256: str
    byte_size: int
    width: float
    height: float


@dataclass(frozen=True)
class CapturedDocument:
    path: Path
    sha256: str
    byte_size: int


def _normalized_field_hint(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").casefold())


def _is_sensitive_field(
    tag: str,
    attributes: Mapping[str, str | None],
) -> bool:
    field_type = str(attributes.get("type") or "").casefold()
    if tag == "input" and field_type == "password":
        return True

    autocomplete = {
        item.casefold()
        for item in str(attributes.get("autocomplete") or "").split()
    }
    if autocomplete & SENSITIVE_AUTOCOMPLETE_VALUES:
        return True

    hints = " ".join(
        _normalized_field_hint(attributes.get(name))
        for name in ("name", "id", "property", "http-equiv")
    )
    return any(fragment in hints for fragment in SENSITIVE_FIELD_FRAGMENTS)


def _attribute_map(content: str) -> dict[str, str | None]:
    attributes: dict[str, str | None] = {}
    for match in _ATTRIBUTE_PATTERN.finditer(content):
        value = (
            match.group("double")
            if match.group("double") is not None
            else match.group("single")
            if match.group("single") is not None
            else match.group("bare")
        )
        attributes[match.group("name").casefold()] = value
    return attributes


def _redact_tag_values(tag: str) -> str:
    for attribute_name in ("content", "value"):
        pattern = re.compile(
            rf"""(?P<prefix>\s{attribute_name}\s*=\s*)"""
            rf""""[^"]*"|'[^']*'|[^\s>/]+""",
            re.IGNORECASE | re.DOTALL,
        )
        tag = pattern.sub(
            rf'\g<prefix>"{REDACTED_VALUE}"',
            tag,
        )
    return tag


def sanitize_html(content: str) -> str:
    def redact_textarea(match: re.Match) -> str:
        attributes = _attribute_map(match.group("attrs"))
        if not _is_sensitive_field("textarea", attributes):
            return match.group(0)
        return (
            _redact_tag_values(match.group("start"))
            + REDACTED_VALUE
            + match.group("end")
        )

    def redact_tag(match: re.Match) -> str:
        tag = match.group("tag").casefold()
        attributes = _attribute_map(match.group("attrs"))
        if not _is_sensitive_field(tag, attributes):
            return match.group(0)
        return _redact_tag_values(match.group(0))

    content = _TEXTAREA_PATTERN.sub(redact_textarea, content)
    return _SENSITIVE_TAG_PATTERN.sub(redact_tag, content)


def sanitize_mhtml(content: str) -> str:
    sanitized: list[str] = []
    dropping_continuation = False
    for line in content.splitlines(keepends=True):
        if dropping_continuation and line.startswith((" ", "\t")):
            continue
        dropping_continuation = False
        match = _HEADER_PATTERN.match(line)
        if match and match.group(1).casefold() in SENSITIVE_HEADERS:
            dropping_continuation = True
            continue
        sanitized.append(line)
    return "".join(sanitized)


def normalize_html_text(content: str) -> str:
    try:
        document = lxml_html.fromstring(content)
    except (TypeError, ValueError):
        return " ".join(str(content or "").split())

    for element in document.xpath(
        "//script|//style|//noscript|//template|//svg|//canvas"
    ):
        element.drop_tree()
    return " ".join(
        text
        for fragment in document.itertext()
        if (text := " ".join(fragment.split()))
    )


def normalize_selection(selection: Mapping) -> dict[str, float]:
    try:
        x = max(0.0, float(selection.get("x", 0)))
        y = max(0.0, float(selection.get("y", 0)))
        width = float(selection.get("width", 0))
        height = float(selection.get("height", 0))
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid evidence capture coordinates.") from exc

    if width < MIN_CAPTURE_SIZE or height < MIN_CAPTURE_SIZE:
        raise ValueError("The selected evidence area is too small.")
    if width > MAX_CAPTURE_DIMENSION or height > MAX_CAPTURE_DIMENSION:
        raise ValueError("The selected evidence area is too large.")
    if width * height > MAX_CAPTURE_AREA:
        raise ValueError("The selected evidence area contains too many pixels.")

    return {
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "scale": 1.0,
    }


def _write_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_bytes(content)
    os.replace(temporary_path, path)


async def _write_document(
    output_path: Path,
    content: str,
) -> CapturedDocument:
    encoded = content.encode("utf-8")
    output_path = Path(output_path)
    await asyncio.to_thread(_write_atomic, output_path, encoded)
    return CapturedDocument(
        path=output_path,
        sha256=sha256_bytes(encoded),
        byte_size=len(encoded),
    )


async def write_text_document(
    output_path: Path,
    content: str,
) -> CapturedDocument:
    return await _write_document(output_path, content)


async def capture_png(
    tab,
    output_path: Path,
    selection: Mapping,
) -> CapturedPng:
    normalized = normalize_selection(selection)
    encoded = await tab.send(
        cdp.page.capture_screenshot(
            format_="png",
            clip=cdp.page.Viewport(**normalized),
            from_surface=True,
            capture_beyond_viewport=True,
            optimize_for_speed=False,
        )
    )
    content = base64.b64decode(encoded, validate=True)
    output_path = Path(output_path)
    await asyncio.to_thread(_write_atomic, output_path, content)
    return CapturedPng(
        path=output_path,
        sha256=sha256_bytes(content),
        byte_size=len(content),
        width=normalized["width"],
        height=normalized["height"],
    )


async def capture_html(tab, output_path: Path) -> CapturedDocument:
    document = await tab.send(cdp.dom.get_document(depth=0, pierce=False))
    content = await tab.send(
        cdp.dom.get_outer_html(
            node_id=document.node_id,
            include_shadow_dom=False,
        )
    )
    return await _write_document(output_path, sanitize_html(content))


async def capture_mhtml(tab, output_path: Path) -> CapturedDocument:
    content = await tab.send(cdp.page.capture_snapshot(format_="mhtml"))
    return await _write_document(output_path, sanitize_mhtml(content))
