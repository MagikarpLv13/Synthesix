from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
import html
import json
import math
import time
from typing import Any, Mapping

from browser import (
    BrowserService,
    monitor_probe_page_state,
    monitor_probe_snapshot,
    social_profile_snapshot,
)
from evidence import compare_page_text, normalize_html_text
from evidence.hashing import sha256_bytes
from exceptions import InvestigationValidationError
from investigations.models import PageMonitor, PageMonitorObservation
from investigations.service import InvestigationService
from investigations.social_adapters import (
    SocialAdapterRegistry,
    SocialApiCredentials,
)
from settings import get_settings


MONITOR_OBSERVATION_SCHEMA_VERSION = 2
DEFAULT_PROBE_OPEN_TIMEOUT = 30.0
DEFAULT_PROBE_NAVIGATION_TIMEOUT = 15.0
DEFAULT_PROBE_NAVIGATION_INTERVAL = 0.1
DEFAULT_PROBE_EXTRACTION_TIMEOUT = 10.0
MINOR_NUMBER_RELATIVE_CHANGE = 0.01
MINOR_LIST_SIMILARITY = 0.90
_METRIC_STATUSES = {"ok", "missing", "unavailable", "error"}
_METRIC_KINDS = {"text", "number", "list", "state"}
_METRIC_PRECISIONS = {"exact", "rounded", "hidden", "unknown"}
_METRIC_PROVENANCE_SOURCES = {"api", "dom", "absent"}


@dataclass(frozen=True)
class ProbeResult:
    observation: PageMonitorObservation

    @property
    def archive_recommended(self) -> bool:
        return self.observation.archive_recommended


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _collapsed_text(value: object, *, max_length: int = 200_000) -> str:
    text = str(value or "")
    if not text.strip():
        return ""
    escaped = html.escape(text)
    return normalize_html_text(escaped)[:max_length]


def _normalized_list(value: object) -> list[Any]:
    if not isinstance(value, list):
        return []
    normalized: list[Any] = []
    for item in value[:200]:
        if isinstance(item, bool):
            normalized.append(item)
        elif isinstance(item, (int, float)) and math.isfinite(float(item)):
            normalized.append(item)
        else:
            text = _collapsed_text(item, max_length=2_000)
            if text:
                normalized.append(text)
    return normalized


def _normalize_metric(raw: object) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        return {"status": "error", "kind": "text", "value": None}
    status = str(raw.get("status", "error") or "error").strip().lower()
    kind = str(raw.get("kind", "text") or "text").strip().lower()
    if status not in _METRIC_STATUSES:
        status = "error"
    if kind not in _METRIC_KINDS:
        kind = "text"
    value = raw.get("value")
    if status != "ok":
        value = None
    elif kind == "number":
        if isinstance(value, bool):
            status = "error"
            value = None
        else:
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                status = "error"
                value = None
            else:
                if not math.isfinite(numeric):
                    status = "error"
                    value = None
                else:
                    value = int(numeric) if numeric.is_integer() else numeric
    elif kind == "list":
        value = _normalized_list(value)
        if not value:
            status = "missing"
            value = None
    elif kind == "state":
        if isinstance(value, bool):
            pass
        else:
            value = _collapsed_text(value, max_length=2_000)
            if not value:
                status = "missing"
                value = None
    else:
        value = _collapsed_text(value)
        if not value:
            status = "missing"
            value = None

    result = {"status": status, "kind": kind, "value": value}
    if bool(raw.get("truncated", False)):
        result["truncated"] = True
    comparison_key = _collapsed_text(
        raw.get("comparison_key"),
        max_length=4_000,
    )
    if comparison_key:
        result["comparison_key"] = comparison_key
    precision = str(raw.get("precision", "") or "").strip().lower()
    if precision in _METRIC_PRECISIONS:
        result["precision"] = precision
    raw_provenance = raw.get("provenance")
    if isinstance(raw_provenance, Mapping):
        source = str(
            raw_provenance.get("source", "absent") or "absent"
        ).strip().lower()
        if source not in _METRIC_PROVENANCE_SOURCES:
            source = "absent"
        provenance: dict[str, Any] = {"source": source}
        for key, max_length in (
            ("adapter", 100),
            ("parser", 100),
            ("field", 200),
        ):
            text = _collapsed_text(
                raw_provenance.get(key),
                max_length=max_length,
            )
            if text:
                provenance[key] = text
        raw_version = raw_provenance.get("parser_version")
        if isinstance(raw_version, int) and not isinstance(raw_version, bool):
            provenance["parser_version"] = max(1, raw_version)
        result["provenance"] = provenance
    return result


def _normalize_probe_context(
    monitor: PageMonitor,
    raw: Mapping[str, Any],
) -> tuple[str, dict[str, Any], list[dict[str, str]]]:
    raw_metadata = raw.get("metadata")
    if not isinstance(raw_metadata, Mapping):
        raw_metadata = {}
    raw_diagnostics = raw.get("diagnostics")
    if not isinstance(raw_diagnostics, Mapping):
        raw_diagnostics = {}
    metadata = {
        "profile": monitor.monitor_profile,
        "ready_state": _collapsed_text(
            raw_metadata.get("ready_state"),
            max_length=100,
        ),
        "language": _collapsed_text(
            raw_metadata.get("language"),
            max_length=100,
        ),
        "canonical_url": _collapsed_text(
            raw_metadata.get("canonical_url"),
            max_length=4_000,
        ),
        "content_type": _collapsed_text(
            raw_metadata.get("content_type"),
            max_length=200,
        ),
        "blocking_reason": _collapsed_text(
            raw_metadata.get("blocking_reason"),
            max_length=100,
        ),
        "diagnostics": {
            key: int(value)
            for key, value in raw_diagnostics.items()
            if isinstance(value, int) and not isinstance(value, bool)
        },
    }

    errors: list[dict[str, str]] = []
    raw_errors = raw.get("errors")
    if isinstance(raw_errors, list):
        for raw_error in raw_errors[:32]:
            if not isinstance(raw_error, Mapping):
                continue
            errors.append(
                {
                    "metric": _collapsed_text(
                        raw_error.get("metric"),
                        max_length=64,
                    ),
                    "code": _collapsed_text(
                        raw_error.get("code"),
                        max_length=100,
                    ),
                    "message": _collapsed_text(
                        raw_error.get("message"),
                        max_length=500,
                    ),
                }
            )

    final_url = _collapsed_text(raw.get("final_url"), max_length=4_000)
    return final_url, metadata, errors


def normalize_probe_snapshot(
    monitor: PageMonitor,
    raw: Mapping[str, Any],
) -> tuple[str, dict[str, Any], dict[str, Any], list[dict[str, str]]]:
    config = monitor.monitor_config or {}
    selected_metrics = [
        str(metric)
        for metric in config.get("metrics", [])
        if str(metric or "").strip()
    ]
    raw_metrics = raw.get("metrics")
    if not isinstance(raw_metrics, Mapping):
        raw_metrics = {}
    metrics = {
        metric: _normalize_metric(raw_metrics.get(metric))
        for metric in selected_metrics
    }
    final_url, metadata, errors = _normalize_probe_context(monitor, raw)
    return final_url, metadata, metrics, errors


def _canonical_list(values: object) -> set[str]:
    if not isinstance(values, list):
        return set()
    return {
        json.dumps(value, ensure_ascii=False, sort_keys=True)
        for value in values
    }


def compare_metric_values(
    previous: Mapping[str, Any],
    current: Mapping[str, Any],
) -> dict[str, Any]:
    previous_status = str(previous.get("status", "error"))
    current_status = str(current.get("status", "error"))
    kind = str(current.get("kind") or previous.get("kind") or "text")
    change: dict[str, Any] = {
        "status": "unchanged",
        "kind": kind,
        "previous_status": previous_status,
        "current_status": current_status,
    }
    if previous_status != "ok" or current_status != "ok":
        if previous_status == current_status == "missing":
            return change
        if "error" in {previous_status, current_status} or "unavailable" in {
            previous_status,
            current_status,
        }:
            change["status"] = "inconclusive"
            return change
        change["status"] = "changed"
        return change

    previous_value = previous.get("comparison_key", previous.get("value"))
    current_value = current.get("comparison_key", current.get("value"))
    if kind != str(previous.get("kind") or kind):
        change["status"] = "changed"
        return change

    if kind == "number":
        try:
            previous_number = float(previous_value)
            current_number = float(current_value)
        except (TypeError, ValueError):
            change["status"] = "inconclusive"
            return change
        if not (
            math.isfinite(previous_number)
            and math.isfinite(current_number)
        ):
            change["status"] = "inconclusive"
            return change
        absolute_change = abs(current_number - previous_number)
        relative_change = absolute_change / max(
            abs(previous_number),
            abs(current_number),
            1.0,
        )
        change.update(
            {
                "absolute_change": absolute_change,
                "relative_change": relative_change,
            }
        )
        if absolute_change == 0:
            return change
        change["status"] = (
            "minor_change"
            if (
                absolute_change <= 1
                or relative_change <= MINOR_NUMBER_RELATIVE_CHANGE
            )
            else "changed"
        )
        return change

    if kind == "list":
        previous_items = _canonical_list(previous_value)
        current_items = _canonical_list(current_value)
        if previous_items == current_items:
            change["similarity"] = 1.0
            return change
        union = previous_items | current_items
        similarity = (
            len(previous_items & current_items) / len(union)
            if union
            else 1.0
        )
        change["similarity"] = similarity
        change["status"] = (
            "minor_change"
            if similarity >= MINOR_LIST_SIMILARITY
            else "changed"
        )
        return change

    if kind == "state":
        if previous_value != current_value:
            change["status"] = "changed"
        return change

    text_change = compare_page_text(
        str(previous_value or ""),
        str(current_value or ""),
    )
    change["status"] = text_change.status
    change["similarity"] = text_change.similarity
    return change


def compare_observation_metrics(
    previous: PageMonitorObservation | None,
    current_metrics: Mapping[str, Mapping[str, Any]],
    *,
    observation_status: str,
) -> tuple[dict[str, Any], str, bool]:
    if observation_status == "error":
        return {}, "error", False
    if previous is None:
        return {}, "baseline", False

    changes = {
        metric: compare_metric_values(
            previous.metrics.get(
                metric,
                {"status": "unavailable", "kind": "text", "value": None},
            ),
            current,
        )
        for metric, current in current_metrics.items()
    }
    statuses = {
        str(change.get("status", "inconclusive"))
        for change in changes.values()
    }
    if "changed" in statuses:
        return changes, "changed", True
    if "minor_change" in statuses:
        return changes, "minor_change", False
    if statuses and statuses <= {"unchanged"}:
        return changes, "unchanged", False
    return changes, "inconclusive", False


def observation_content_sha256(metrics: Mapping[str, Mapping[str, Any]]) -> str:
    canonical: dict[str, Any] = {}
    for metric, item in sorted(metrics.items()):
        value = item.get("comparison_key", item.get("value"))
        if str(item.get("kind")) == "list" and isinstance(value, list):
            value = sorted(
                value,
                key=lambda candidate: json.dumps(
                    candidate,
                    ensure_ascii=False,
                    sort_keys=True,
                ),
            )
        canonical[metric] = {
            "status": item.get("status"),
            "kind": item.get("kind"),
            "value": value,
        }
    encoded = json.dumps(
        canonical,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256_bytes(encoded)


async def wait_for_monitor_navigation(
    tab,
    *,
    timeout: float = DEFAULT_PROBE_NAVIGATION_TIMEOUT,
    interval: float = DEFAULT_PROBE_NAVIGATION_INTERVAL,
) -> None:
    deadline = time.monotonic() + float(timeout)
    last_error: Exception | None = None
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            message = "Monitoring page navigation timed out."
            if last_error is not None:
                message = f"{message} Last error: {last_error}"
            raise asyncio.TimeoutError(message)
        try:
            state = await asyncio.wait_for(
                monitor_probe_page_state(tab),
                timeout=min(2.0, remaining),
            )
            final_url = str(state.get("final_url", "") or "").strip()
            ready_state = str(
                state.get("ready_state", "") or ""
            ).strip().lower()
            if (
                final_url.lower()
                not in {"", "about:blank", "chrome://newtab/"}
                and ready_state in {"interactive", "complete"}
                and bool(state.get("has_body"))
            ):
                return
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            last_error = exc
        await asyncio.sleep(min(float(interval), remaining))


def _metric_observation_status(
    metrics: Mapping[str, Mapping[str, Any]],
    *,
    blocking_reason: str = "",
) -> str:
    if blocking_reason:
        return "error"
    metric_statuses = {
        str(item.get("status", "error"))
        for item in metrics.values()
    }
    if metric_statuses and metric_statuses <= {"ok"}:
        return "ok"
    if metric_statuses and "ok" in metric_statuses:
        return "partial"
    if metric_statuses and metric_statuses <= {
        "missing",
        "unavailable",
    }:
        return "partial"
    return "error"


def _normalized_adapter_errors(
    raw_errors: list[dict[str, str]],
) -> list[dict[str, str]]:
    return [
        {
            "metric": _collapsed_text(
                error.get("metric"),
                max_length=64,
            ),
            "code": _collapsed_text(
                error.get("code"),
                max_length=100,
            ),
            "message": _collapsed_text(
                error.get("message"),
                max_length=500,
            ),
        }
        for error in raw_errors[:32]
    ]


class PageMonitorProbe:
    def __init__(
        self,
        browser_service: BrowserService,
        investigation_service: InvestigationService,
        *,
        open_timeout: float = DEFAULT_PROBE_OPEN_TIMEOUT,
        navigation_timeout: float = DEFAULT_PROBE_NAVIGATION_TIMEOUT,
        navigation_interval: float = DEFAULT_PROBE_NAVIGATION_INTERVAL,
        extraction_timeout: float = DEFAULT_PROBE_EXTRACTION_TIMEOUT,
        social_registry: SocialAdapterRegistry | None = None,
    ) -> None:
        self.browser_service = browser_service
        self.investigation_service = investigation_service
        self.open_timeout = float(open_timeout)
        self.navigation_timeout = float(navigation_timeout)
        self.navigation_interval = float(navigation_interval)
        self.extraction_timeout = float(extraction_timeout)
        if social_registry is None:
            settings = get_settings()
            social_registry = SocialAdapterRegistry(
                credentials=SocialApiCredentials(
                    youtube_api_key=settings.youtube_api_key,
                    x_bearer_token=settings.x_bearer_token,
                    tiktok_research_access_token=(
                        settings.tiktok_research_access_token
                    ),
                ),
                api_timeout=settings.social_api_timeout,
            )
        self.social_registry = social_registry

    async def _wait_for_navigation(self, tab) -> None:
        await wait_for_monitor_navigation(
            tab,
            timeout=self.navigation_timeout,
            interval=self.navigation_interval,
        )

    async def run(
        self,
        investigation_id: str,
        monitor_id: str,
    ) -> ProbeResult:
        monitor = await asyncio.to_thread(
            self.investigation_service.get_page_monitor,
            investigation_id,
            monitor_id,
        )
        if not monitor.is_enabled:
            raise InvestigationValidationError(
                "Paused page monitors cannot be probed."
            )
        previous = await asyncio.to_thread(
            self.investigation_service.get_latest_page_monitor_observation,
            investigation_id,
            monitor_id,
        )
        config = monitor.monitor_config or {}
        metrics = tuple(str(metric) for metric in config.get("metrics", []))
        selectors = {
            str(metric): str(selector)
            for metric, selector in dict(config.get("selectors", {})).items()
        }
        started = time.monotonic()
        tab = None
        final_url = monitor.result_url
        metadata: dict[str, Any] = {"profile": monitor.monitor_profile}
        normalized_metrics: dict[str, Any] = {}
        errors: list[dict[str, str]] = []
        status = "error"
        adapter = self.social_registry.get(monitor.monitor_profile)
        adapter_attempts: list[dict[str, Any]] = []
        if adapter is not None:
            api_extraction = await adapter.extract_api(
                monitor.result_url,
                metrics,
            )
            adapter_attempts.append(dict(api_extraction.attempt))
            errors.extend(
                _normalized_adapter_errors(api_extraction.errors)
            )
            for metric, raw_metric in api_extraction.metrics.items():
                if metric in metrics and metric not in selectors:
                    normalized_metrics[metric] = _normalize_metric(
                        raw_metric
                    )

        browser_metrics = tuple(
            metric
            for metric in metrics
            if (
                metric in selectors
                or normalized_metrics.get(metric, {}).get("status") != "ok"
            )
        )
        if browser_metrics:
            try:
                tab = await asyncio.wait_for(
                    self.browser_service.open_tab(
                        monitor.result_url,
                        new_tab=True,
                    ),
                    timeout=self.open_timeout,
                )
                await self._wait_for_navigation(tab)
                if adapter is None:
                    raw = await asyncio.wait_for(
                        monitor_probe_snapshot(tab, metrics, selectors),
                        timeout=self.extraction_timeout,
                    )
                    (
                        extracted_url,
                        metadata,
                        normalized_metrics,
                        errors,
                    ) = normalize_probe_snapshot(monitor, raw)
                else:
                    raw = await asyncio.wait_for(
                        social_profile_snapshot(
                            tab,
                            monitor.monitor_profile,
                            browser_metrics,
                            {
                                metric: selector
                                for metric, selector in selectors.items()
                                if metric in browser_metrics
                            },
                        ),
                        timeout=self.extraction_timeout,
                    )
                    (
                        extracted_url,
                        browser_metadata,
                        browser_errors,
                    ) = _normalize_probe_context(monitor, raw)
                    metadata.update(browser_metadata)
                    errors.extend(browser_errors)
                    dom_extraction = adapter.extract_dom(
                        raw,
                        browser_metrics,
                    )
                    adapter_attempts.append(
                        dict(dom_extraction.attempt)
                    )
                    errors.extend(
                        _normalized_adapter_errors(
                            dom_extraction.errors
                        )
                    )
                    for metric in browser_metrics:
                        raw_metric = dom_extraction.metrics.get(
                            metric,
                            adapter.absent_metric(metric),
                        )
                        candidate = _normalize_metric(raw_metric)
                        existing = normalized_metrics.get(metric)
                        if (
                            metric in selectors
                            or candidate.get("status") == "ok"
                            or existing is None
                            or existing.get("precision") != "hidden"
                        ):
                            normalized_metrics[metric] = candidate
                final_url = extracted_url or str(
                    getattr(tab, "url", "") or monitor.result_url
                )
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                code = (
                    "probe_timeout"
                    if isinstance(exc, asyncio.TimeoutError)
                    else "probe_failed"
                )
                errors.append(
                    {
                        "metric": "",
                        "code": code,
                        "message": _collapsed_text(exc, max_length=500)
                        or type(exc).__name__,
                    }
                )
                if adapter is not None:
                    adapter_attempts.append(
                        {
                            "source": "dom",
                            "status": "error",
                            "parser": f"{adapter.name}_dom",
                            "parser_version": adapter.parser_version,
                            "reason": code,
                        }
                    )
                for metric in browser_metrics:
                    existing = normalized_metrics.get(metric)
                    if (
                        metric not in selectors
                        and existing is not None
                        and existing.get("precision") == "hidden"
                    ):
                        continue
                    if adapter is None:
                        normalized_metrics[metric] = {
                            "status": "error",
                            "kind": "text",
                            "value": None,
                        }
                        continue
                    failed = adapter.absent_metric(metric)
                    failed["status"] = "error"
                    failed["provenance"] = {
                        "source": "dom",
                        "adapter": adapter.name,
                        "parser": f"{adapter.name}_dom",
                        "parser_version": adapter.parser_version,
                    }
                    normalized_metrics[metric] = _normalize_metric(failed)
                if tab is not None:
                    final_url = str(
                        getattr(tab, "url", "") or monitor.result_url
                    )
            finally:
                if tab is not None:
                    await self.browser_service.close_tab(tab)

        if adapter is not None:
            for metric in metrics:
                normalized_metrics.setdefault(
                    metric,
                    _normalize_metric(adapter.absent_metric(metric)),
                )
            metadata["social_adapter"] = {
                "registry_version": 1,
                "profile": monitor.monitor_profile,
                "adapter": adapter.name,
                "parser_version": adapter.parser_version,
                "attempts": adapter_attempts,
            }

        blocking_reason = str(
            metadata.get("blocking_reason", "") or ""
        )
        if blocking_reason:
            errors.append(
                {
                    "metric": "",
                    "code": blocking_reason,
                    "message": (
                        "The monitored page requires browser "
                        "interaction before extraction."
                    ),
                }
            )
        status = _metric_observation_status(
            normalized_metrics,
            blocking_reason=blocking_reason,
        )

        duration_ms = max(0, round((time.monotonic() - started) * 1000))
        changes, change_status, archive_recommended = (
            compare_observation_metrics(
                previous,
                normalized_metrics,
                observation_status=status,
            )
        )
        observation = await asyncio.to_thread(
            self.investigation_service.record_page_monitor_observation,
            investigation_id,
            monitor_id,
            previous_observation_id=(previous.id if previous else None),
            schema_version=MONITOR_OBSERVATION_SCHEMA_VERSION,
            observed_at=_utc_now(),
            final_url=final_url,
            duration_ms=duration_ms,
            status=status,
            content_sha256=observation_content_sha256(
                normalized_metrics
            ),
            metadata=metadata,
            metrics=normalized_metrics,
            errors=errors,
            changes=changes,
            change_status=change_status,
            archive_recommended=archive_recommended,
        )
        return ProbeResult(observation=observation)
