from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
import json
import math
import re
from typing import Any, Mapping, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import Request, urlopen

from investigations.monitoring import infer_monitor_profile


SOCIAL_ADAPTER_REGISTRY_VERSION = 1
SOCIAL_PARSER_VERSION = 3
DEFAULT_SOCIAL_API_TIMEOUT = 10.0
MAX_SOCIAL_API_RESPONSE_BYTES = 2 * 1024 * 1024

_METRIC_KINDS = {
    "page_name": "text",
    "channel_name": "text",
    "profile_name": "text",
    "description": "text",
    "bio": "text",
    "display_name": "text",
    "friends_count": "number",
    "followers": "number",
    "following": "number",
    "likes": "number",
    "listed": "number",
    "posts": "number",
    "subscribers": "number",
    "videos": "number",
    "views": "number",
    "profile_photo": "text",
    "cover_photo": "text",
    "profile_details": "list",
    "latest_post_id": "text",
    "latest_post_date": "text",
    "latest_post_content": "text",
    "latest_post_permalink": "text",
    "external_links": "list",
}
_PRECISIONS = {"exact", "rounded", "hidden", "unknown"}
_NUMBER_TOKEN = (
    r"(?P<number>\d{1,3}(?:[\s\u00a0\u202f.,]\d{3})+"
    r"|\d+(?:[.,]\d+)?)"
    r"\s*(?P<suffix>k|m|b|bn|md|mio|million|millions|"
    r"billion|billions|milliard|milliards)?"
)
_COUNT_LABELS = {
    "followers": (
        r"followers?",
        r"abonn[ée]s?",
        r"seguidores?",
    ),
    "friends_count": (
        r"friends?",
        r"ami(?:\(e\)|e)?s?",
        r"amigos?",
        r"freunde",
        r"朋友",
    ),
    "following": (
        r"following",
        r"abonnements?",
        r"suivis?",
        r"seguidos?",
    ),
    "posts": (
        r"posts?",
        r"publications?",
        r"tweets?",
    ),
    "likes": (
        r"likes?",
        r"j['’]aime",
        r"mentions?\s+j['’]aime",
    ),
    "listed": (
        r"listed",
        r"listes?",
    ),
    "subscribers": (
        r"subscribers?",
        r"abonn[ée]s?",
    ),
    "videos": (
        r"videos?",
        r"vid[ée]os?",
    ),
    "views": (
        r"views?",
        r"vues?",
    ),
}
_PLATFORM_DOMAINS = {
    "facebook": {"facebook.com", "fb.com"},
    "instagram": {"instagram.com"},
    "tiktok": {"tiktok.com"},
    "x": {"x.com", "twitter.com"},
    "youtube": {"youtube.com", "youtu.be"},
}


@dataclass(frozen=True)
class SocialApiCredentials:
    youtube_api_key: str = field(default="", repr=False)
    x_bearer_token: str = field(default="", repr=False)
    tiktok_research_access_token: str = field(default="", repr=False)

    def for_adapter(self, adapter_name: str) -> str:
        if adapter_name == "youtube":
            return self.youtube_api_key
        if adapter_name == "x":
            return self.x_bearer_token
        if adapter_name == "tiktok":
            return self.tiktok_research_access_token
        return ""


@dataclass(frozen=True)
class SocialExtraction:
    metrics: dict[str, dict[str, Any]]
    errors: list[dict[str, str]]
    attempt: dict[str, Any]


class SocialHttpClient(Protocol):
    async def request_json(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        body: Mapping[str, Any] | None = None,
        timeout: float = DEFAULT_SOCIAL_API_TIMEOUT,
    ) -> Mapping[str, Any]: ...


class SocialApiRequestError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = str(code or "api_request_failed")


class UrlLibSocialHttpClient:
    async def request_json(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        body: Mapping[str, Any] | None = None,
        timeout: float = DEFAULT_SOCIAL_API_TIMEOUT,
    ) -> Mapping[str, Any]:
        return await asyncio.to_thread(
            self._request_json,
            method,
            url,
            headers=dict(headers or {}),
            body=dict(body) if body is not None else None,
            timeout=float(timeout),
        )

    @staticmethod
    def _request_json(
        method: str,
        url: str,
        *,
        headers: Mapping[str, str],
        body: Mapping[str, Any] | None,
        timeout: float,
    ) -> Mapping[str, Any]:
        payload = None
        request_headers = {
            "Accept": "application/json",
            "User-Agent": "Synthesix/monitoring",
            **dict(headers),
        }
        if body is not None:
            payload = json.dumps(
                body,
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
            request_headers["Content-Type"] = "application/json"
        request = Request(
            url,
            data=payload,
            headers=request_headers,
            method=str(method or "GET").upper(),
        )
        try:
            with urlopen(request, timeout=timeout) as response:
                raw = response.read(MAX_SOCIAL_API_RESPONSE_BYTES + 1)
        except HTTPError as exc:
            raise SocialApiRequestError(
                "api_http_error",
                f"Social API returned HTTP {exc.code}.",
            ) from None
        except (URLError, TimeoutError, OSError):
            raise SocialApiRequestError(
                "api_unreachable",
                "Social API request failed.",
            ) from None
        if len(raw) > MAX_SOCIAL_API_RESPONSE_BYTES:
            raise SocialApiRequestError(
                "api_response_too_large",
                "Social API response exceeded the configured limit.",
            )
        try:
            parsed = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise SocialApiRequestError(
                "api_invalid_json",
                "Social API returned an invalid JSON response.",
            ) from None
        if not isinstance(parsed, Mapping):
            raise SocialApiRequestError(
                "api_invalid_payload",
                "Social API returned an unexpected payload.",
            )
        return parsed


class SocialProfileAdapter(Protocol):
    name: str
    profile: str
    parser_version: int

    async def extract_api(
        self,
        url: str,
        metrics: tuple[str, ...],
    ) -> SocialExtraction: ...

    def extract_dom(
        self,
        raw: Mapping[str, Any],
        metrics: tuple[str, ...],
    ) -> SocialExtraction: ...

    def absent_metric(self, metric: str) -> dict[str, Any]: ...


def _collapsed_text(value: object, *, max_length: int = 200_000) -> str:
    return " ".join(str(value or "").split())[:max_length]


def _provenance(
    source: str,
    *,
    adapter: str,
    parser: str,
    parser_version: int,
    field: str = "",
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "source": source,
        "adapter": adapter,
        "parser": parser,
        "parser_version": int(parser_version),
    }
    if field:
        result["field"] = _collapsed_text(field, max_length=200)
    return result


def _metric(
    *,
    status: str,
    kind: str,
    value: Any,
    precision: str,
    source: str,
    adapter: str,
    parser: str,
    parser_version: int,
    field: str = "",
    truncated: bool = False,
    comparison_key: str = "",
) -> dict[str, Any]:
    result = {
        "status": status,
        "kind": kind,
        "value": value if status == "ok" else None,
        "precision": (
            precision if precision in _PRECISIONS else "unknown"
        ),
        "provenance": _provenance(
            source,
            adapter=adapter,
            parser=parser,
            parser_version=parser_version,
            field=field,
        ),
    }
    if truncated:
        result["truncated"] = True
    if comparison_key:
        result["comparison_key"] = _collapsed_text(
            comparison_key,
            max_length=4_000,
        )
    return result


def _safe_number(value: object) -> int | float | None:
    if isinstance(value, bool):
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(numeric):
        return None
    return int(numeric) if numeric.is_integer() else numeric


def _number_from_text(value: object) -> tuple[int | float | None, str]:
    text = _collapsed_text(value, max_length=200).lower()
    match = re.fullmatch(_NUMBER_TOKEN, text, flags=re.IGNORECASE)
    if match is None:
        return None, "unknown"
    raw_number = match.group("number")
    suffix = (match.group("suffix") or "").lower()
    compact = re.sub(r"[\s\u00a0\u202f]", "", raw_number)
    if suffix:
        compact = compact.replace(",", ".")
        if compact.count(".") > 1:
            parts = compact.split(".")
            compact = "".join(parts[:-1]) + "." + parts[-1]
        try:
            numeric = float(compact)
        except ValueError:
            return None, "unknown"
        multiplier = {
            "k": 1_000,
            "m": 1_000_000,
            "mio": 1_000_000,
            "million": 1_000_000,
            "millions": 1_000_000,
            "b": 1_000_000_000,
            "bn": 1_000_000_000,
            "md": 1_000_000_000,
            "billion": 1_000_000_000,
            "billions": 1_000_000_000,
            "milliard": 1_000_000_000,
            "milliards": 1_000_000_000,
        }[suffix]
        result = numeric * multiplier
        return (
            int(round(result)) if result.is_integer() else result,
            "rounded",
        )
    if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", compact):
        return int(re.sub(r"[.,]", "", compact)), "exact"
    if re.fullmatch(r"\d+", compact):
        return int(compact), "exact"
    try:
        numeric = float(compact.replace(",", "."))
    except ValueError:
        return None, "unknown"
    return numeric, "unknown"


def _find_labeled_number(
    values: list[str],
    labels: tuple[str, ...],
) -> tuple[int | float | None, str, str]:
    label_pattern = "(?:" + "|".join(labels) + ")"
    before = re.compile(
        rf"{_NUMBER_TOKEN}\s*{label_pattern}",
        flags=re.IGNORECASE,
    )
    after = re.compile(
        rf"{label_pattern}\s*[:\-]?\s*{_NUMBER_TOKEN}",
        flags=re.IGNORECASE,
    )
    for text in values:
        for pattern in (before, after):
            match = pattern.search(text)
            if match is None:
                continue
            token = f"{match.group('number')}{match.group('suffix') or ''}"
            number, precision = _number_from_text(token)
            if number is not None:
                return number, precision, text[:200]
    return None, "unknown", ""


def _iter_json_objects(value: object):
    if isinstance(value, Mapping):
        yield value
        for child in value.values():
            yield from _iter_json_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_json_objects(child)


def _json_ld_objects(signals: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    objects: list[Mapping[str, Any]] = []
    raw_items = signals.get("json_ld")
    if not isinstance(raw_items, list):
        return objects
    for raw in raw_items[:20]:
        if not isinstance(raw, str):
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            continue
        objects.extend(_iter_json_objects(value))
    return objects


def _structured_text(
    objects: list[Mapping[str, Any]],
    key: str,
) -> str:
    for item in objects:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return _collapsed_text(value, max_length=20_000)
    return ""


def _structured_counts(
    objects: list[Mapping[str, Any]],
) -> dict[str, int | float]:
    counts: dict[str, int | float] = {}
    action_metrics = {
        "followaction": "followers",
        "subscribeaction": "subscribers",
        "likeaction": "likes",
        "watchaction": "views",
        "viewaction": "views",
    }
    for item in objects:
        statistics = item.get("interactionStatistic")
        if isinstance(statistics, Mapping):
            candidates = [statistics]
        elif isinstance(statistics, list):
            candidates = [
                candidate
                for candidate in statistics
                if isinstance(candidate, Mapping)
            ]
        else:
            continue
        for statistic in candidates:
            interaction = statistic.get("interactionType")
            if isinstance(interaction, Mapping):
                interaction = interaction.get("@type")
            key = str(interaction or "").split("/")[-1].lower()
            metric = action_metrics.get(key)
            value = _safe_number(statistic.get("userInteractionCount"))
            if metric and value is not None:
                counts[metric] = value
    return counts


def _metric_error(
    metric: str,
    code: str,
    message: str,
) -> dict[str, str]:
    return {
        "metric": _collapsed_text(metric, max_length=64),
        "code": _collapsed_text(code, max_length=100),
        "message": _collapsed_text(message, max_length=500),
    }


class _BaseSocialAdapter:
    name = ""
    profile = ""
    parser_version = SOCIAL_PARSER_VERSION
    name_metric = "profile_name"
    bio_metric = "bio"
    api_metrics: frozenset[str] = frozenset()

    def __init__(
        self,
        credentials: SocialApiCredentials,
        http_client: SocialHttpClient,
        *,
        api_timeout: float,
    ) -> None:
        self.credentials = credentials
        self.http_client = http_client
        self.api_timeout = float(api_timeout)

    def metric_kind(self, metric: str) -> str:
        return _METRIC_KINDS.get(metric, "text")

    def absent_metric(self, metric: str) -> dict[str, Any]:
        return _metric(
            status="unavailable",
            kind=self.metric_kind(metric),
            value=None,
            precision="unknown",
            source="absent",
            adapter=self.name,
            parser=f"{self.name}_adapter",
            parser_version=self.parser_version,
        )

    def _dom_platform_metric(
        self,
        metric: str,
        signals: Mapping[str, Any],
        objects: list[Mapping[str, Any]],
    ) -> dict[str, Any] | None:
        return None

    def _attempt(
        self,
        source: str,
        status: str,
        parser: str,
        *,
        reason: str = "",
    ) -> dict[str, Any]:
        result = {
            "source": source,
            "status": status,
            "parser": parser,
            "parser_version": self.parser_version,
        }
        if reason:
            result["reason"] = reason
        return result

    async def extract_api(
        self,
        url: str,
        metrics: tuple[str, ...],
    ) -> SocialExtraction:
        requested = tuple(
            metric for metric in metrics if metric in self.api_metrics
        )
        parser = f"{self.name}_api"
        if not requested:
            return SocialExtraction(
                metrics={},
                errors=[],
                attempt=self._attempt(
                    "api",
                    "skipped",
                    parser,
                    reason="no_supported_metric",
                ),
            )
        credential = self.credentials.for_adapter(self.name)
        if not credential:
            return SocialExtraction(
                metrics={},
                errors=[],
                attempt=self._attempt(
                    "api",
                    "skipped",
                    parser,
                    reason="credential_not_configured",
                ),
            )
        try:
            return await self._extract_api(url, requested, credential)
        except asyncio.CancelledError:
            raise
        except SocialApiRequestError as exc:
            return SocialExtraction(
                metrics={},
                errors=[
                    _metric_error("", exc.code, str(exc))
                ],
                attempt=self._attempt(
                    "api",
                    "error",
                    parser,
                    reason=exc.code,
                ),
            )
        except Exception:
            return SocialExtraction(
                metrics={},
                errors=[
                    _metric_error(
                        "",
                        "api_adapter_failed",
                        "The social API adapter failed.",
                    )
                ],
                attempt=self._attempt(
                    "api",
                    "error",
                    parser,
                    reason="api_adapter_failed",
                ),
            )

    async def _extract_api(
        self,
        url: str,
        metrics: tuple[str, ...],
        credential: str,
    ) -> SocialExtraction:
        raise SocialApiRequestError(
            "api_not_supported",
            "No official API adapter is configured for this platform.",
        )

    def extract_dom(
        self,
        raw: Mapping[str, Any],
        metrics: tuple[str, ...],
    ) -> SocialExtraction:
        parser = f"{self.name}_dom"
        raw_signals = raw.get("signals")
        signals = raw_signals if isinstance(raw_signals, Mapping) else {}
        raw_custom = raw.get("custom_metrics")
        custom_metrics = (
            raw_custom if isinstance(raw_custom, Mapping) else {}
        )
        objects = _json_ld_objects(signals)
        structured_counts = _structured_counts(objects)
        values = [
            _collapsed_text(signals.get("og_description")),
            _collapsed_text(signals.get("meta_description")),
        ]
        labeled_texts = signals.get("labeled_texts")
        if isinstance(labeled_texts, list):
            values.extend(
                _collapsed_text(item, max_length=2_000)
                for item in labeled_texts[:300]
            )
        values.append(
            _collapsed_text(signals.get("body_text"), max_length=50_000)
        )

        blocking_reason = ""
        raw_metadata = raw.get("metadata")
        if isinstance(raw_metadata, Mapping):
            blocking_reason = _collapsed_text(
                raw_metadata.get("blocking_reason"),
                max_length=100,
            )

        extracted: dict[str, dict[str, Any]] = {}
        errors: list[dict[str, str]] = []
        for metric in metrics:
            custom = custom_metrics.get(metric)
            if isinstance(custom, Mapping):
                extracted[metric] = self._dom_custom_metric(
                    metric,
                    custom,
                )
                continue
            platform_metric = self._dom_platform_metric(
                metric,
                signals,
                objects,
            )
            if platform_metric is not None:
                extracted[metric] = platform_metric
            elif metric == self.name_metric:
                value, field = self._dom_name(signals, objects)
                extracted[metric] = _metric(
                    status="ok" if value else "missing",
                    kind="text",
                    value=value or None,
                    precision="exact" if value else "unknown",
                    source="dom",
                    adapter=self.name,
                    parser=parser,
                    parser_version=self.parser_version,
                    field=field,
                )
            elif metric == self.bio_metric:
                value, field = self._dom_bio(signals, objects)
                extracted[metric] = _metric(
                    status="ok" if value else "missing",
                    kind="text",
                    value=value or None,
                    precision="exact" if value else "unknown",
                    source="dom",
                    adapter=self.name,
                    parser=parser,
                    parser_version=self.parser_version,
                    field=field,
                )
            elif metric == "external_links":
                links = self._external_links(signals)
                extracted[metric] = _metric(
                    status="ok" if links else "missing",
                    kind="list",
                    value=links or None,
                    precision="unknown",
                    source="dom",
                    adapter=self.name,
                    parser=parser,
                    parser_version=self.parser_version,
                    field="signals.links",
                )
            elif metric in _COUNT_LABELS:
                if metric in structured_counts:
                    extracted[metric] = _metric(
                        status="ok",
                        kind="number",
                        value=structured_counts[metric],
                        precision="exact",
                        source="dom",
                        adapter=self.name,
                        parser=parser,
                        parser_version=self.parser_version,
                        field="json_ld.interactionStatistic",
                    )
                else:
                    value, precision, field = _find_labeled_number(
                        values,
                        _COUNT_LABELS[metric],
                    )
                    extracted[metric] = _metric(
                        status="ok" if value is not None else "missing",
                        kind="number",
                        value=value,
                        precision=precision,
                        source="dom",
                        adapter=self.name,
                        parser=parser,
                        parser_version=self.parser_version,
                        field="dom.text" if field else "",
                    )
            else:
                extracted[metric] = self.absent_metric(metric)

            if (
                extracted[metric]["status"] != "ok"
                and not blocking_reason
            ):
                errors.append(
                    _metric_error(
                        metric,
                        "selector_miss",
                        "The social DOM parser found no supported signal "
                        "for this metric.",
                    )
                )

        statuses = {
            item.get("status")
            for item in extracted.values()
        }
        attempt_status = (
            "ok"
            if statuses and statuses <= {"ok"}
            else "partial"
            if "ok" in statuses
            else "error"
            if errors
            else "missing"
        )
        return SocialExtraction(
            metrics=extracted,
            errors=errors,
            attempt=self._attempt("dom", attempt_status, parser),
        )

    def _dom_custom_metric(
        self,
        metric: str,
        raw: Mapping[str, Any],
    ) -> dict[str, Any]:
        status = str(raw.get("status", "error") or "error").lower()
        kind = str(
            raw.get("kind", self.metric_kind(metric))
            or self.metric_kind(metric)
        ).lower()
        value = raw.get("value")
        precision = str(raw.get("precision", "unknown") or "unknown")
        return _metric(
            status=status,
            kind=kind,
            value=value,
            precision=precision,
            source="dom",
            adapter=self.name,
            parser=f"{self.name}_dom_selector",
            parser_version=self.parser_version,
            field=f"selector:{metric}",
            truncated=bool(raw.get("truncated", False)),
        )

    def _dom_name(
        self,
        signals: Mapping[str, Any],
        objects: list[Mapping[str, Any]],
    ) -> tuple[str, str]:
        structured = _structured_text(objects, "name")
        if structured:
            return structured, "json_ld.name"
        for key in ("og_title", "title"):
            raw = _collapsed_text(signals.get(key), max_length=2_000)
            if raw:
                return self._clean_name(raw), f"signals.{key}"
        return "", ""

    def _dom_bio(
        self,
        signals: Mapping[str, Any],
        objects: list[Mapping[str, Any]],
    ) -> tuple[str, str]:
        structured = _structured_text(objects, "description")
        if structured:
            return structured, "json_ld.description"
        for key in ("og_description", "meta_description"):
            raw = _collapsed_text(signals.get(key), max_length=20_000)
            if not raw:
                continue
            prefix, separator, suffix = raw.partition(" - ")
            if separator and any(
                re.search(label, prefix, flags=re.IGNORECASE)
                for labels in _COUNT_LABELS.values()
                for label in labels
            ):
                raw = suffix
            return raw, f"signals.{key}"
        return "", ""

    def _clean_name(self, value: str) -> str:
        text = value
        for separator in (" • ", " | ", " - "):
            if separator in text:
                text = text.split(separator, 1)[0]
        return _collapsed_text(text, max_length=2_000)

    def _external_links(
        self,
        signals: Mapping[str, Any],
    ) -> list[str]:
        raw_links = signals.get("links")
        if not isinstance(raw_links, list):
            return []
        domains = _PLATFORM_DOMAINS.get(self.name, set())
        links: list[str] = []
        seen = set()
        for raw in raw_links[:200]:
            if isinstance(raw, Mapping):
                href = _collapsed_text(raw.get("href"), max_length=4_000)
            else:
                href = _collapsed_text(raw, max_length=4_000)
            parsed = urlsplit(href)
            hostname = (parsed.hostname or "").lower().removeprefix("www.")
            if (
                parsed.scheme not in {"http", "https"}
                or not hostname
                or any(
                    hostname == domain
                    or hostname.endswith(f".{domain}")
                    for domain in domains
                )
                or href in seen
            ):
                continue
            seen.add(href)
            links.append(href)
        return links


class FacebookPageAdapter(_BaseSocialAdapter):
    name = "facebook"
    profile = "facebook_page"
    name_metric = "page_name"
    bio_metric = "bio"

    @staticmethod
    def _profile_signals(
        signals: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        raw = signals.get("facebook_profile")
        return raw if isinstance(raw, Mapping) else {}

    def _dom_name(
        self,
        signals: Mapping[str, Any],
        objects: list[Mapping[str, Any]],
    ) -> tuple[str, str]:
        display_name = _collapsed_text(
            self._profile_signals(signals).get("display_name"),
            max_length=2_000,
        )
        if display_name:
            return display_name, "signals.facebook_profile.display_name"
        return super()._dom_name(signals, objects)

    def _dom_platform_metric(
        self,
        metric: str,
        signals: Mapping[str, Any],
        objects: list[Mapping[str, Any]],
    ) -> dict[str, Any] | None:
        profile = self._profile_signals(signals)
        parser = f"{self.name}_dom"
        if metric == "display_name":
            value, field = self._dom_name(signals, objects)
            return _metric(
                status="ok" if value else "missing",
                kind="text",
                value=value or None,
                precision="exact" if value else "unknown",
                source="dom",
                adapter=self.name,
                parser=parser,
                parser_version=self.parser_version,
                field=field,
            )
        if metric == "friends_count":
            value, precision = _number_from_text(
                profile.get("friends_count_text")
            )
            field = "signals.facebook_profile.friends_count_text"
            if value is None:
                value, precision, matched = _find_labeled_number(
                    [
                        _collapsed_text(
                            profile.get("friends_text"),
                            max_length=500,
                        )
                    ],
                    _COUNT_LABELS[metric],
                )
                field = (
                    "signals.facebook_profile.friends_text"
                    if matched
                    else ""
                )
            return _metric(
                status="ok" if value is not None else "missing",
                kind="number",
                value=value,
                precision=precision,
                source="dom",
                adapter=self.name,
                parser=parser,
                parser_version=self.parser_version,
                field=field,
            )
        if metric == "followers":
            value, precision = _number_from_text(
                profile.get("followers_count_text")
            )
            return _metric(
                status="ok" if value is not None else "missing",
                kind="number",
                value=value,
                precision=precision,
                source="dom",
                adapter=self.name,
                parser=parser,
                parser_version=self.parser_version,
                field=(
                    "signals.facebook_profile.followers_count_text"
                    if value is not None else ""
                ),
            )
        if metric in {"bio", "description"}:
            value = _collapsed_text(
                profile.get("bio"),
                max_length=20_000,
            )
            if not value:
                if metric == "bio":
                    value, field = self._dom_bio(signals, objects)
                else:
                    value, field = super()._dom_bio(signals, objects)
            else:
                field = "signals.facebook_profile.bio"
            return _metric(
                status="ok" if value else "missing",
                kind="text",
                value=value or None,
                precision="exact" if value else "unknown",
                source="dom",
                adapter=self.name,
                parser=parser,
                parser_version=self.parser_version,
                field=field,
            )
        if metric == "profile_details":
            raw_details = profile.get("details")
            details = []
            if isinstance(raw_details, list):
                details = [
                    _collapsed_text(item, max_length=2_000)
                    for item in raw_details[:50]
                    if _collapsed_text(item, max_length=2_000)
                ]
            return _metric(
                status="ok" if details else "missing",
                kind="list",
                value=details or None,
                precision="exact" if details else "unknown",
                source="dom",
                adapter=self.name,
                parser=parser,
                parser_version=self.parser_version,
                field="signals.facebook_profile.details" if details else "",
            )
        if metric == "external_links":
            raw_links = profile.get("external_links")
            links = []
            if isinstance(raw_links, list):
                links = [
                    _collapsed_text(item, max_length=4_000)
                    for item in raw_links[:200]
                    if _collapsed_text(item, max_length=4_000)
                ]
            return _metric(
                status="ok" if links else "missing",
                kind="list",
                value=links or None,
                precision="unknown",
                source="dom",
                adapter=self.name,
                parser=parser,
                parser_version=self.parser_version,
                field=(
                    "signals.facebook_profile.external_links"
                    if links else ""
                ),
            )
        if metric == "profile_photo":
            value = _collapsed_text(
                profile.get("profile_photo_url"),
                max_length=4_000,
            )
            identity = _collapsed_text(
                profile.get("profile_photo_identity"),
                max_length=1_000,
            )
            return _metric(
                status="ok" if value else "missing",
                kind="text",
                value=value or None,
                precision="exact" if value else "unknown",
                source="dom",
                adapter=self.name,
                parser=parser,
                parser_version=self.parser_version,
                field="signals.facebook_profile.profile_photo_url" if value else "",
                comparison_key=identity,
            )
        if metric == "cover_photo":
            value = _collapsed_text(
                profile.get("cover_photo_url"),
                max_length=4_000,
            )
            identity = _collapsed_text(
                profile.get("cover_photo_identity"),
                max_length=1_000,
            )
            return _metric(
                status="ok" if value else "missing",
                kind="text",
                value=value or None,
                precision="exact" if value else "unknown",
                source="dom",
                adapter=self.name,
                parser=parser,
                parser_version=self.parser_version,
                field="signals.facebook_profile.cover_photo_url" if value else "",
                comparison_key=identity,
            )

        raw_post = profile.get("latest_post")
        post = raw_post if isinstance(raw_post, Mapping) else {}
        post_fields = {
            "latest_post_id": ("id", 500),
            "latest_post_date": ("date", 500),
            "latest_post_content": ("content", 200_000),
            "latest_post_permalink": ("permalink", 4_000),
        }
        if metric not in post_fields:
            return None
        key, max_length = post_fields[metric]
        value = _collapsed_text(post.get(key), max_length=max_length)
        post_identity = _collapsed_text(
            post.get("id") or post.get("permalink"),
            max_length=4_000,
        )
        return _metric(
            status="ok" if value else "missing",
            kind="text",
            value=value or None,
            precision=(
                "unknown" if metric == "latest_post_date"
                else "exact" if value else "unknown"
            ),
            source="dom",
            adapter=self.name,
            parser=parser,
            parser_version=self.parser_version,
            field=f"signals.facebook_profile.latest_post.{key}" if value else "",
            truncated=(
                bool(post.get("content_truncated", False))
                if metric == "latest_post_content"
                else False
            ),
            comparison_key=(
                post_identity if metric == "latest_post_date" else ""
            ),
        )


class InstagramProfileAdapter(_BaseSocialAdapter):
    name = "instagram"
    profile = "instagram_profile"


class TikTokProfileAdapter(_BaseSocialAdapter):
    name = "tiktok"
    profile = "tiktok_profile"
    api_metrics = frozenset(
        {
            "profile_name",
            "bio",
            "followers",
            "following",
            "posts",
            "likes",
            "external_links",
        }
    )

    async def _extract_api(
        self,
        url: str,
        metrics: tuple[str, ...],
        credential: str,
    ) -> SocialExtraction:
        username = _profile_path_identifier(url, require_at=True)
        if not username:
            raise SocialApiRequestError(
                "api_identifier_unavailable",
                "TikTok username could not be derived from the profile URL.",
            )
        fields = (
            "display_name,bio_description,follower_count,following_count,"
            "likes_count,video_count,bio_url"
        )
        response = await self.http_client.request_json(
            "POST",
            "https://open.tiktokapis.com/v2/research/user/info/?"
            + urlencode({"fields": fields}),
            headers={"Authorization": f"Bearer {credential}"},
            body={"username": username},
            timeout=self.api_timeout,
        )
        raw_data = response.get("data")
        if not isinstance(raw_data, Mapping):
            raise SocialApiRequestError(
                "api_profile_not_found",
                "TikTok Research API returned no user profile.",
            )
        mapping = {
            "profile_name": ("text", "display_name"),
            "bio": ("text", "bio_description"),
            "followers": ("number", "follower_count"),
            "following": ("number", "following_count"),
            "posts": ("number", "video_count"),
            "likes": ("number", "likes_count"),
            "external_links": ("list", "bio_url"),
        }
        extracted = self._mapped_api_metrics(
            raw_data,
            metrics,
            mapping,
            parser="tiktok_research_api",
        )
        return SocialExtraction(
            metrics=extracted,
            errors=[],
            attempt=self._attempt(
                "api",
                _attempt_status(extracted),
                "tiktok_research_api",
            ),
        )

    def _mapped_api_metrics(
        self,
        raw_data: Mapping[str, Any],
        metrics: tuple[str, ...],
        mapping: Mapping[str, tuple[str, str]],
        *,
        parser: str,
    ) -> dict[str, dict[str, Any]]:
        extracted: dict[str, dict[str, Any]] = {}
        for metric in metrics:
            kind, field = mapping[metric]
            raw_value = raw_data.get(field)
            if kind == "number":
                value = _safe_number(raw_value)
            elif kind == "list":
                text = _collapsed_text(raw_value, max_length=4_000)
                value = [text] if text else None
            else:
                value = _collapsed_text(raw_value, max_length=20_000)
            extracted[metric] = _metric(
                status="ok" if value not in (None, "") else "missing",
                kind=kind,
                value=value,
                precision="exact" if value not in (None, "") else "unknown",
                source="api",
                adapter=self.name,
                parser=parser,
                parser_version=self.parser_version,
                field=field,
            )
        return extracted


class XProfileAdapter(_BaseSocialAdapter):
    name = "x"
    profile = "x_profile"
    api_metrics = frozenset(
        {
            "profile_name",
            "bio",
            "followers",
            "following",
            "posts",
            "listed",
            "external_links",
        }
    )

    async def _extract_api(
        self,
        url: str,
        metrics: tuple[str, ...],
        credential: str,
    ) -> SocialExtraction:
        username = _profile_path_identifier(url)
        if not username or re.fullmatch(r"[A-Za-z0-9_]{1,15}", username) is None:
            raise SocialApiRequestError(
                "api_identifier_unavailable",
                "X username could not be derived from the profile URL.",
            )
        endpoint = (
            "https://api.x.com/2/users/by/username/"
            f"{quote(username)}?"
            + urlencode(
                {
                    "user.fields": (
                        "name,description,entities,public_metrics,url"
                    )
                }
            )
        )
        response = await self.http_client.request_json(
            "GET",
            endpoint,
            headers={"Authorization": f"Bearer {credential}"},
            timeout=self.api_timeout,
        )
        raw_data = response.get("data")
        if not isinstance(raw_data, Mapping):
            raise SocialApiRequestError(
                "api_profile_not_found",
                "X API returned no user profile.",
            )
        public_metrics = raw_data.get("public_metrics")
        counts = (
            public_metrics
            if isinstance(public_metrics, Mapping)
            else {}
        )
        links = _x_external_links(raw_data)
        values: dict[str, tuple[str, Any, str]] = {
            "profile_name": ("text", raw_data.get("name"), "name"),
            "bio": ("text", raw_data.get("description"), "description"),
            "followers": (
                "number",
                counts.get("followers_count"),
                "public_metrics.followers_count",
            ),
            "following": (
                "number",
                counts.get("following_count"),
                "public_metrics.following_count",
            ),
            "posts": (
                "number",
                counts.get("tweet_count"),
                "public_metrics.tweet_count",
            ),
            "listed": (
                "number",
                counts.get("listed_count"),
                "public_metrics.listed_count",
            ),
            "external_links": ("list", links, "entities"),
        }
        extracted = _api_metric_mapping(
            self,
            metrics,
            values,
            parser="x_api_v2",
        )
        return SocialExtraction(
            metrics=extracted,
            errors=[],
            attempt=self._attempt(
                "api",
                _attempt_status(extracted),
                "x_api_v2",
            ),
        )


class YouTubeChannelAdapter(_BaseSocialAdapter):
    name = "youtube"
    profile = "youtube_channel"
    name_metric = "channel_name"
    bio_metric = "description"
    api_metrics = frozenset(
        {
            "channel_name",
            "description",
            "subscribers",
            "videos",
            "views",
        }
    )

    async def _extract_api(
        self,
        url: str,
        metrics: tuple[str, ...],
        credential: str,
    ) -> SocialExtraction:
        identifier = _youtube_identifier(url)
        if identifier is None:
            raise SocialApiRequestError(
                "api_identifier_unavailable",
                "YouTube channel identifier could not be derived from the URL.",
            )
        identifier_kind, identifier_value = identifier
        query = {
            "part": "snippet,statistics",
            identifier_kind: identifier_value,
            "key": credential,
        }
        response = await self.http_client.request_json(
            "GET",
            "https://www.googleapis.com/youtube/v3/channels?"
            + urlencode(query),
            timeout=self.api_timeout,
        )
        items = response.get("items")
        if not isinstance(items, list) or not items:
            raise SocialApiRequestError(
                "api_profile_not_found",
                "YouTube Data API returned no channel.",
            )
        raw_item = items[0]
        if not isinstance(raw_item, Mapping):
            raise SocialApiRequestError(
                "api_invalid_payload",
                "YouTube Data API returned an invalid channel.",
            )
        snippet = raw_item.get("snippet")
        statistics = raw_item.get("statistics")
        snippet = snippet if isinstance(snippet, Mapping) else {}
        statistics = (
            statistics if isinstance(statistics, Mapping) else {}
        )
        hidden_subscribers = bool(
            statistics.get("hiddenSubscriberCount", False)
        )
        extracted: dict[str, dict[str, Any]] = {}
        for metric in metrics:
            if metric == "channel_name":
                value = _collapsed_text(snippet.get("title"), max_length=2_000)
                kind = "text"
                precision = "exact"
                field = "snippet.title"
            elif metric == "description":
                value = _collapsed_text(
                    snippet.get("description"),
                    max_length=20_000,
                )
                kind = "text"
                precision = "exact"
                field = "snippet.description"
            elif metric == "subscribers" and hidden_subscribers:
                extracted[metric] = _metric(
                    status="missing",
                    kind="number",
                    value=None,
                    precision="hidden",
                    source="api",
                    adapter=self.name,
                    parser="youtube_api_v3",
                    parser_version=self.parser_version,
                    field="statistics.hiddenSubscriberCount",
                )
                continue
            else:
                field_name = {
                    "subscribers": "subscriberCount",
                    "videos": "videoCount",
                    "views": "viewCount",
                }[metric]
                value = _safe_number(statistics.get(field_name))
                kind = "number"
                precision = (
                    "rounded" if metric == "subscribers" else "exact"
                )
                field = f"statistics.{field_name}"
            extracted[metric] = _metric(
                status="ok" if value not in (None, "") else "missing",
                kind=kind,
                value=value,
                precision=precision if value not in (None, "") else "unknown",
                source="api",
                adapter=self.name,
                parser="youtube_api_v3",
                parser_version=self.parser_version,
                field=field,
            )
        return SocialExtraction(
            metrics=extracted,
            errors=[],
            attempt=self._attempt(
                "api",
                _attempt_status(extracted),
                "youtube_api_v3",
            ),
        )


def _api_metric_mapping(
    adapter: _BaseSocialAdapter,
    metrics: tuple[str, ...],
    values: Mapping[str, tuple[str, Any, str]],
    *,
    parser: str,
) -> dict[str, dict[str, Any]]:
    extracted: dict[str, dict[str, Any]] = {}
    for metric in metrics:
        kind, raw_value, field = values[metric]
        if kind == "number":
            value = _safe_number(raw_value)
        elif kind == "list":
            value = raw_value if isinstance(raw_value, list) else []
            value = value or None
        else:
            value = _collapsed_text(raw_value, max_length=20_000)
        extracted[metric] = _metric(
            status="ok" if value not in (None, "", []) else "missing",
            kind=kind,
            value=value,
            precision="exact" if value not in (None, "", []) else "unknown",
            source="api",
            adapter=adapter.name,
            parser=parser,
            parser_version=adapter.parser_version,
            field=field,
        )
    return extracted


def _attempt_status(metrics: Mapping[str, Mapping[str, Any]]) -> str:
    statuses = {
        str(metric.get("status", "error"))
        for metric in metrics.values()
    }
    if statuses and statuses <= {"ok"}:
        return "ok"
    if "ok" in statuses:
        return "partial"
    if statuses:
        return "missing"
    return "skipped"


def _profile_path_identifier(
    url: str,
    *,
    require_at: bool = False,
) -> str:
    parsed = urlsplit(str(url or ""))
    segments = [
        segment
        for segment in parsed.path.split("/")
        if segment
    ]
    if not segments:
        return ""
    first = segments[0]
    if require_at and not first.startswith("@"):
        return ""
    return first.removeprefix("@")


def _youtube_identifier(url: str) -> tuple[str, str] | None:
    parsed = urlsplit(str(url or ""))
    segments = [
        segment
        for segment in parsed.path.split("/")
        if segment
    ]
    if not segments:
        return None
    first = segments[0]
    if first.startswith("@"):
        return "forHandle", first
    if len(segments) > 1 and first == "channel":
        return "id", segments[1]
    if len(segments) > 1 and first == "user":
        return "forUsername", segments[1]
    return None


def _x_external_links(raw_data: Mapping[str, Any]) -> list[str]:
    candidates = [raw_data.get("url")]
    entities = raw_data.get("entities")
    if isinstance(entities, Mapping):
        for section in ("url", "description"):
            value = entities.get(section)
            if not isinstance(value, Mapping):
                continue
            urls = value.get("urls")
            if not isinstance(urls, list):
                continue
            for item in urls:
                if not isinstance(item, Mapping):
                    continue
                candidates.append(
                    item.get("expanded_url") or item.get("url")
                )
    links: list[str] = []
    seen = set()
    for candidate in candidates:
        text = _collapsed_text(candidate, max_length=4_000)
        if (
            not text
            or urlsplit(text).scheme not in {"http", "https"}
            or text in seen
        ):
            continue
        seen.add(text)
        links.append(text)
    return links


class SocialAdapterRegistry:
    def __init__(
        self,
        *,
        credentials: SocialApiCredentials | None = None,
        http_client: SocialHttpClient | None = None,
        api_timeout: float = DEFAULT_SOCIAL_API_TIMEOUT,
    ) -> None:
        resolved_credentials = credentials or SocialApiCredentials()
        resolved_client = http_client or UrlLibSocialHttpClient()
        self._adapters: dict[str, SocialProfileAdapter] = {}
        for adapter_type in (
            FacebookPageAdapter,
            InstagramProfileAdapter,
            TikTokProfileAdapter,
            XProfileAdapter,
            YouTubeChannelAdapter,
        ):
            adapter = adapter_type(
                resolved_credentials,
                resolved_client,
                api_timeout=api_timeout,
            )
            self._adapters[adapter.profile] = adapter

    def get(self, profile: str) -> SocialProfileAdapter | None:
        return self._adapters.get(str(profile or "").strip().lower())

    def for_url(self, url: str) -> SocialProfileAdapter | None:
        return self.get(infer_monitor_profile(url))

    @property
    def profiles(self) -> tuple[str, ...]:
        return tuple(sorted(self._adapters))
