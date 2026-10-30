from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping
from urllib.parse import urlsplit

from exceptions import InvestigationValidationError


MONITOR_MODES = ("automatic", "custom")
MONITOR_ARCHIVE_POLICIES = ("never", "on_change")
DEFAULT_MONITOR_PROFILE = "generic_page"
DEFAULT_MONITOR_ARCHIVE_POLICY = "never"
DEFAULT_CHECK_INTERVAL_MINUTES = 24 * 60
MIN_CHECK_INTERVAL_MINUTES = 15
MAX_CHECK_INTERVAL_MINUTES = 30 * 24 * 60
MAX_MONITOR_METRICS = 32
MAX_MONITOR_METRIC_LENGTH = 64
MAX_MONITOR_SELECTOR_LENGTH = 1000

MONITOR_PROFILE_METRICS: dict[str, tuple[str, ...]] = {
    "generic_page": (
        "title",
        "description",
        "visible_text",
        "links",
    ),
    "facebook_page": (
        "display_name",
        "profile_photo",
        "cover_photo",
        "friends_count",
        "followers",
        "bio",
        "profile_details",
        "external_links",
        "latest_post_id",
        "latest_post_date",
        "latest_post_content",
        "latest_post_permalink",
    ),
    "instagram_profile": (
        "profile_name",
        "bio",
        "followers",
        "following",
        "posts",
        "external_links",
    ),
    "tiktok_profile": (
        "profile_name",
        "bio",
        "followers",
        "following",
        "posts",
        "likes",
        "external_links",
    ),
    "x_profile": (
        "profile_name",
        "bio",
        "followers",
        "following",
        "posts",
        "listed",
        "external_links",
    ),
    "youtube_channel": (
        "channel_name",
        "description",
        "subscribers",
        "videos",
        "views",
        "external_links",
    ),
}

_SOCIAL_DOMAINS = {
    "facebook.com",
    "instagram.com",
    "tiktok.com",
    "twitter.com",
    "x.com",
    "youtube.com",
}
_METRIC_KEY_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
_FACEBOOK_NON_PROFILE_PATHS = {
    "events",
    "groups",
    "marketplace",
    "reel",
    "reels",
    "share",
    "stories",
    "watch",
}
_INSTAGRAM_NON_PROFILE_PATHS = {
    "accounts",
    "direct",
    "explore",
    "p",
    "reel",
    "reels",
    "stories",
}
_X_NON_PROFILE_PATHS = {
    "compose",
    "explore",
    "hashtag",
    "home",
    "i",
    "messages",
    "notifications",
    "search",
    "settings",
}


@dataclass(frozen=True)
class MonitorConfiguration:
    mode: str
    profile: str
    metrics: tuple[str, ...]
    selectors: dict[str, str]
    archive_policy: str
    check_interval_minutes: int
    is_enabled: bool

    def storage_payload(self) -> dict[str, Any]:
        return {
            "schema_version": 2,
            "metrics": list(self.metrics),
            "selectors": dict(self.selectors),
            "archive_policy": self.archive_policy,
        }

    def to_payload(self) -> dict[str, Any]:
        return {
            "monitor_mode": self.mode,
            "monitor_profile": self.profile,
            "monitor_config": self.storage_payload(),
            "check_interval_minutes": self.check_interval_minutes,
            "is_enabled": self.is_enabled,
        }


def _parsed_url(value: str):
    text = str(value or "").strip()
    if not text:
        return urlsplit("")
    if "://" not in text:
        text = f"https://{text}"
    try:
        return urlsplit(text)
    except ValueError:
        return urlsplit("")


def _is_domain(hostname: str, domain: str) -> bool:
    return hostname == domain or hostname.endswith(f".{domain}")


def infer_monitor_profile(url: str) -> str:
    parsed = _parsed_url(url)
    hostname = (parsed.hostname or "").lower().removeprefix("www.")
    if not any(_is_domain(hostname, domain) for domain in _SOCIAL_DOMAINS):
        return DEFAULT_MONITOR_PROFILE

    segments = [
        segment.lower()
        for segment in str(parsed.path or "").split("/")
        if segment
    ]
    first = segments[0] if segments else ""

    if _is_domain(hostname, "instagram.com"):
        if first and first not in _INSTAGRAM_NON_PROFILE_PATHS:
            return "instagram_profile"
    elif _is_domain(hostname, "tiktok.com"):
        if first.startswith("@"):
            return "tiktok_profile"
    elif _is_domain(hostname, "twitter.com") or _is_domain(hostname, "x.com"):
        if (
            first
            and first not in _X_NON_PROFILE_PATHS
            and not (len(segments) > 1 and segments[1] == "status")
        ):
            return "x_profile"
    elif _is_domain(hostname, "youtube.com"):
        if first.startswith("@") or first in {"c", "channel", "user"}:
            return "youtube_channel"
    elif _is_domain(hostname, "facebook.com"):
        if (
            first == "profile.php"
            or (first and first not in _FACEBOOK_NON_PROFILE_PATHS)
        ):
            return "facebook_page"
    return DEFAULT_MONITOR_PROFILE


def _normalize_metrics(
    value: object,
    *,
    default: Iterable[str],
) -> tuple[str, ...]:
    if value is None:
        candidates = default
    elif isinstance(value, str):
        candidates = value.split(",")
    elif isinstance(value, Iterable):
        candidates = value
    else:
        raise InvestigationValidationError(
            "Monitor metrics must be a list of metric identifiers."
        )

    metrics = []
    seen = set()
    for candidate in candidates:
        metric = str(candidate or "").strip().lower()
        if not metric:
            continue
        if (
            len(metric) > MAX_MONITOR_METRIC_LENGTH
            or _METRIC_KEY_PATTERN.fullmatch(metric) is None
        ):
            raise InvestigationValidationError(
                f"Unsupported monitor metric identifier: {metric}"
            )
        if metric in seen:
            continue
        metrics.append(metric)
        seen.add(metric)
        if len(metrics) > MAX_MONITOR_METRICS:
            raise InvestigationValidationError(
                f"A page monitor supports at most {MAX_MONITOR_METRICS} metrics."
            )
    if not metrics:
        raise InvestigationValidationError(
            "A page monitor must observe at least one metric."
        )
    return tuple(metrics)


def _normalize_selectors(
    value: object,
    *,
    metrics: tuple[str, ...],
) -> dict[str, str]:
    if value in (None, {}):
        return {}
    if not isinstance(value, Mapping):
        raise InvestigationValidationError(
            "Monitor selectors must map metric identifiers to CSS selectors."
        )

    selectors = {}
    metric_set = set(metrics)
    for raw_metric, raw_selector in value.items():
        metric = str(raw_metric or "").strip().lower()
        selector = str(raw_selector or "").strip()
        if metric not in metric_set:
            raise InvestigationValidationError(
                f"Monitor selector references an unselected metric: {metric}"
            )
        if not selector:
            continue
        if len(selector) > MAX_MONITOR_SELECTOR_LENGTH:
            raise InvestigationValidationError(
                f"Monitor selector is too long for metric: {metric}"
            )
        selectors[metric] = selector
    return selectors


def resolve_monitor_configuration(
    url: str,
    payload: Mapping[str, object] | None = None,
) -> MonitorConfiguration:
    values = dict(payload or {})
    mode = str(values.get("mode", "automatic") or "automatic").strip().lower()
    if mode not in MONITOR_MODES:
        raise InvestigationValidationError(
            f"Unsupported page monitor mode: {mode}"
        )

    if mode == "automatic":
        profile = infer_monitor_profile(url)
    else:
        profile = (
            str(
                values.get("profile", DEFAULT_MONITOR_PROFILE)
                or DEFAULT_MONITOR_PROFILE
            )
            .strip()
            .lower()
        )
    if profile not in MONITOR_PROFILE_METRICS:
        raise InvestigationValidationError(
            f"Unsupported page monitor profile: {profile}"
        )

    metrics = _normalize_metrics(
        values.get("metrics"),
        default=MONITOR_PROFILE_METRICS[profile],
    )
    selectors = _normalize_selectors(
        values.get("selectors"),
        metrics=metrics,
    )
    archive_policy = str(
        values.get(
            "archive_policy",
            DEFAULT_MONITOR_ARCHIVE_POLICY,
        )
        or DEFAULT_MONITOR_ARCHIVE_POLICY
    ).strip().lower()
    if archive_policy not in MONITOR_ARCHIVE_POLICIES:
        raise InvestigationValidationError(
            f"Unsupported page monitor archive policy: {archive_policy}"
        )

    raw_interval = values.get(
        "check_interval_minutes",
        DEFAULT_CHECK_INTERVAL_MINUTES,
    )
    if isinstance(raw_interval, bool):
        raise InvestigationValidationError(
            "Page monitor interval must be a number of minutes."
        )
    try:
        check_interval_minutes = int(raw_interval)
    except (TypeError, ValueError) as exc:
        raise InvestigationValidationError(
            "Page monitor interval must be a number of minutes."
        ) from exc
    if not (
        MIN_CHECK_INTERVAL_MINUTES
        <= check_interval_minutes
        <= MAX_CHECK_INTERVAL_MINUTES
    ):
        raise InvestigationValidationError(
            "Page monitor interval must be between "
            f"{MIN_CHECK_INTERVAL_MINUTES} and "
            f"{MAX_CHECK_INTERVAL_MINUTES} minutes."
        )

    is_enabled = values.get("is_enabled", True)
    if not isinstance(is_enabled, bool):
        raise InvestigationValidationError(
            "Page monitor enabled state must be a boolean."
        )

    return MonitorConfiguration(
        mode=mode,
        profile=profile,
        metrics=metrics,
        selectors=selectors,
        archive_policy=archive_policy,
        check_interval_minutes=check_interval_minutes,
        is_enabled=is_enabled,
    )
