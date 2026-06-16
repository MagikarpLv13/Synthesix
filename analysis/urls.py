from __future__ import annotations

import hashlib
import ipaddress
import socket
import time
from dataclasses import dataclass
from email.message import Message
from typing import Callable, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import (
    parse_qsl,
    quote,
    urlencode,
    urljoin,
    urlsplit,
    urlunsplit,
)
from urllib.request import (
    HTTPRedirectHandler,
    OpenerDirector,
    ProxyHandler,
    Request,
    build_opener,
)

from exceptions import UrlAnalysisError


MAX_REDIRECTS = 5
MAX_HASH_BYTES = 5 * 1024 * 1024
DEFAULT_TIMEOUT_SECONDS = 15.0
TRACKING_PARAMETERS = {
    "dclid",
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "msclkid",
}
RETAINED_HEADERS = (
    "content-type",
    "content-length",
    "content-encoding",
    "etag",
    "last-modified",
    "server",
    "cache-control",
    "content-security-policy",
    "strict-transport-security",
    "x-content-type-options",
    "x-frame-options",
    "referrer-policy",
    "permissions-policy",
)


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


@dataclass(frozen=True)
class RedirectObservation:
    url: str
    status_code: int
    location: str

    def to_payload(self) -> dict:
        return {
            "url": self.url,
            "status_code": self.status_code,
            "location": self.location,
        }


@dataclass(frozen=True)
class TechnicalUrlAnalysis:
    requested_url: str
    final_url: str
    final_domain_unicode: str
    final_domain_punycode: str
    status_code: int
    redirects: tuple[RedirectObservation, ...]
    headers: dict[str, str]
    content_type: str
    content_length: int | None
    bytes_read: int
    content_sha256: str
    content_truncated: bool
    elapsed_ms: int
    tracking_parameters: tuple[str, ...]
    cleaned_url: str

    def to_payload(self) -> dict:
        return {
            "requested_url": self.requested_url,
            "final_url": self.final_url,
            "final_domain_unicode": self.final_domain_unicode,
            "final_domain_punycode": self.final_domain_punycode,
            "status_code": self.status_code,
            "redirects": [
                redirect.to_payload() for redirect in self.redirects
            ],
            "headers": dict(self.headers),
            "content_type": self.content_type,
            "content_length": self.content_length,
            "bytes_read": self.bytes_read,
            "content_sha256": self.content_sha256,
            "content_truncated": self.content_truncated,
            "elapsed_ms": self.elapsed_ms,
            "tracking_parameters": list(self.tracking_parameters),
            "cleaned_url": self.cleaned_url,
        }


def _default_opener() -> OpenerDirector:
    return build_opener(ProxyHandler({}), _NoRedirectHandler())


def _resolved_addresses(
    hostname: str,
    port: int,
    resolver: Callable[..., Iterable],
) -> set[str]:
    try:
        records = resolver(hostname, port, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise UrlAnalysisError(
            f"Unable to resolve URL host: {hostname}"
        ) from exc
    addresses = {
        str(record[4][0]).split("%", 1)[0]
        for record in records
        if len(record) >= 5 and record[4]
    }
    if not addresses:
        raise UrlAnalysisError(f"Unable to resolve URL host: {hostname}")
    return addresses


def _validate_public_url(
    value: str,
    resolver: Callable[..., Iterable],
) -> str:
    try:
        parsed = urlsplit(str(value or "").strip())
        port = parsed.port
    except ValueError as exc:
        raise UrlAnalysisError("The URL is malformed.") from exc
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        raise UrlAnalysisError("Only absolute HTTP(S) URLs can be analyzed.")
    if parsed.username or parsed.password:
        raise UrlAnalysisError("URLs containing credentials cannot be analyzed.")

    hostname = parsed.hostname
    resolved_port = port or (443 if parsed.scheme.lower() == "https" else 80)
    for address in _resolved_addresses(hostname, resolved_port, resolver):
        try:
            if not ipaddress.ip_address(address).is_global:
                raise UrlAnalysisError(
                    "Private, local, reserved, and loopback destinations "
                    "cannot be analyzed."
                )
        except ValueError as exc:
            raise UrlAnalysisError("The URL host resolved unexpectedly.") from exc

    try:
        ascii_hostname = hostname.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise UrlAnalysisError("The URL hostname is invalid.") from exc
    netloc = (
        f"[{ascii_hostname}]"
        if ":" in ascii_hostname
        else ascii_hostname
    )
    if port is not None:
        netloc = f"{netloc}:{port}"
    return urlunsplit(
        (
            parsed.scheme.lower(),
            netloc,
            quote(
                parsed.path or "/",
                safe="/%:@!$&'()*+,;=-._~",
            ),
            quote(
                parsed.query,
                safe="=&?/:;+,%@!$'()*[]-._~",
            ),
            "",
        )
    )


def _unicode_hostname(hostname: str) -> str:
    if ":" in hostname:
        return hostname
    return ".".join(
        (
            label.encode("ascii").decode("idna")
            if label.casefold().startswith("xn--")
            else label
        )
        for label in hostname.split(".")
    )


def _tracking_details(value: str) -> tuple[tuple[str, ...], str]:
    parsed = urlsplit(value)
    kept = []
    removed = []
    for key, item_value in parse_qsl(parsed.query, keep_blank_values=True):
        normalized_key = key.casefold()
        if normalized_key.startswith("utm_") or normalized_key in TRACKING_PARAMETERS:
            removed.append(key)
        else:
            kept.append((key, item_value))
    cleaned_url = urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            urlencode(kept, doseq=True),
            "",
        )
    )
    return tuple(dict.fromkeys(removed)), cleaned_url


def _retained_headers(headers: Message) -> dict[str, str]:
    retained = {}
    for name in RETAINED_HEADERS:
        value = str(headers.get(name, "") or "").strip()
        if value:
            retained[name] = value[:2000]
    return retained


def _content_length(headers: Message) -> int | None:
    try:
        value = int(str(headers.get("content-length", "") or ""))
    except ValueError:
        return None
    return value if value >= 0 else None


def _read_for_hash(response, declared_length: int | None) -> tuple[int, str, bool]:
    if declared_length is not None and declared_length > MAX_HASH_BYTES:
        return 0, "", True

    digest = hashlib.sha256()
    bytes_read = 0
    while bytes_read <= MAX_HASH_BYTES:
        chunk = response.read(min(64 * 1024, MAX_HASH_BYTES + 1 - bytes_read))
        if not chunk:
            return bytes_read, digest.hexdigest(), False
        bytes_read += len(chunk)
        if bytes_read > MAX_HASH_BYTES:
            return bytes_read, "", True
        digest.update(chunk)
    return bytes_read, "", True


def analyze_url(
    url: str,
    *,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    opener: OpenerDirector | None = None,
    resolver: Callable[..., Iterable] = socket.getaddrinfo,
) -> TechnicalUrlAnalysis:
    requested_url = str(url or "").strip()
    current_url = _validate_public_url(requested_url, resolver)
    redirects = []
    client = opener or _default_opener()
    started = time.monotonic()

    for _ in range(MAX_REDIRECTS + 1):
        request = Request(
            current_url,
            headers={
                "User-Agent": "Synthesix URL Analysis/1.0",
                "Accept": "*/*",
                "Accept-Encoding": "identity",
            },
            method="GET",
        )
        try:
            response = client.open(request, timeout=max(1.0, float(timeout)))
        except HTTPError as exc:
            response = exc
        except (OSError, URLError) as exc:
            raise UrlAnalysisError(f"URL analysis request failed: {exc}") from exc

        try:
            status_code = int(getattr(response, "status", response.getcode()))
            headers = response.headers
            location = str(headers.get("location", "") or "").strip()
            if status_code in {301, 302, 303, 307, 308} and location:
                if len(redirects) >= MAX_REDIRECTS:
                    raise UrlAnalysisError(
                        f"URL exceeded the {MAX_REDIRECTS}-redirect limit."
                    )
                next_url = urljoin(current_url, location)
                next_url = _validate_public_url(next_url, resolver)
                redirects.append(
                    RedirectObservation(
                        url=current_url,
                        status_code=status_code,
                        location=next_url,
                    )
                )
                current_url = next_url
                continue

            retained_headers = _retained_headers(headers)
            declared_length = _content_length(headers)
            bytes_read, content_sha256, truncated = _read_for_hash(
                response,
                declared_length,
            )
            final_url = str(response.geturl() or current_url)
            final_url = _validate_public_url(final_url, resolver)
            final_host = urlsplit(final_url).hostname or ""
            tracking_parameters, cleaned_url = _tracking_details(final_url)
            return TechnicalUrlAnalysis(
                requested_url=requested_url,
                final_url=final_url,
                final_domain_unicode=_unicode_hostname(final_host),
                final_domain_punycode=final_host,
                status_code=status_code,
                redirects=tuple(redirects),
                headers=retained_headers,
                content_type=retained_headers.get("content-type", ""),
                content_length=declared_length,
                bytes_read=bytes_read,
                content_sha256=content_sha256,
                content_truncated=truncated,
                elapsed_ms=max(0, round((time.monotonic() - started) * 1000)),
                tracking_parameters=tracking_parameters,
                cleaned_url=cleaned_url,
            )
        finally:
            response.close()

    raise UrlAnalysisError(f"URL exceeded the {MAX_REDIRECTS}-redirect limit.")
