from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
import logging
import random
from typing import Awaitable, Callable
from uuid import uuid4

from investigations.models import PageMonitor
from investigations.probe import PageMonitorProbe, ProbeResult
from investigations.service import InvestigationService


logger = logging.getLogger(__name__)

INTERVENTION_ERROR_CODES = {
    "authentication_required",
    "challenge_required",
    "consent_required",
}


@dataclass(frozen=True)
class MonitorSchedulerOptions:
    poll_interval: float = 60.0
    batch_size: int = 4
    concurrency: int = 2
    lease_seconds: float = 300.0
    attempt_timeout: float = 75.0
    retry_attempts: int = 1
    retry_delay: float = 1.0
    retry_backoff: float = 2.0
    jitter_seconds: float = 2.0
    failure_backoff_seconds: float = 300.0
    max_failures: int = 3

    def __post_init__(self) -> None:
        if self.poll_interval <= 0:
            raise ValueError("Monitor poll interval must be positive.")
        if not 1 <= self.batch_size <= 100:
            raise ValueError("Monitor batch size must be between 1 and 100.")
        if not 1 <= self.concurrency <= self.batch_size:
            raise ValueError(
                "Monitor concurrency must be between 1 and the batch size."
            )
        if not 5.0 <= self.lease_seconds <= 3600.0:
            raise ValueError(
                "Monitor lease must be between 5 and 3600 seconds."
            )
        if self.attempt_timeout <= 0:
            raise ValueError("Monitor attempt timeout must be positive.")
        if not 0 <= self.retry_attempts <= 10:
            raise ValueError(
                "Monitor retry attempts must be between 0 and 10."
            )
        if self.retry_delay < 0 or self.failure_backoff_seconds < 0:
            raise ValueError("Monitor backoff delays cannot be negative.")
        if self.retry_backoff < 1:
            raise ValueError("Monitor retry backoff must be at least 1.")
        if self.jitter_seconds < 0:
            raise ValueError("Monitor jitter cannot be negative.")
        if not 1 <= self.max_failures <= 100:
            raise ValueError(
                "Monitor maximum failures must be between 1 and 100."
            )


@dataclass(frozen=True)
class MonitorRunSummary:
    claimed: int = 0
    succeeded: int = 0
    partial: int = 0
    failed: int = 0
    archived: int = 0
    archive_failed: int = 0
    paused: int = 0

    @property
    def exit_code(self) -> int:
        return 1 if self.failed or self.archive_failed else 0

    def to_line(self) -> str:
        return (
            "Monitoring: "
            f"claimed={self.claimed} "
            f"succeeded={self.succeeded} "
            f"partial={self.partial} "
            f"failed={self.failed} "
            f"archived={self.archived} "
            f"archive_failed={self.archive_failed} "
            f"paused={self.paused}"
        )


@dataclass(frozen=True)
class _MonitorOutcome:
    status: str
    archived: bool = False
    archive_failed: bool = False
    paused: bool = False


ArchiveHandler = Callable[[PageMonitor, ProbeResult], Awaitable[None]]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _requires_intervention(result: ProbeResult) -> bool:
    return any(
        str(error.get("code", "") or "") in INTERVENTION_ERROR_CODES
        for error in result.observation.errors
    )


def _archive_policy(monitor: PageMonitor) -> str:
    return str(
        (monitor.monitor_config or {}).get("archive_policy", "never")
        or "never"
    ).strip().lower()


class PageMonitorScheduler:
    def __init__(
        self,
        investigation_service: InvestigationService,
        probe: PageMonitorProbe,
        *,
        options: MonitorSchedulerOptions | None = None,
        archive_handler: ArchiveHandler | None = None,
        worker_id: str | None = None,
        random_value: Callable[[], float] = random.random,
    ) -> None:
        self.investigation_service = investigation_service
        self.probe = probe
        self.options = options or MonitorSchedulerOptions()
        self.archive_handler = archive_handler
        self.worker_id = str(worker_id or uuid4())
        self.random_value = random_value

    async def run_once(self) -> MonitorRunSummary:
        claimed = await asyncio.to_thread(
            self.investigation_service.claim_due_page_monitors,
            self.worker_id,
            due_at=_utc_now(),
            limit=self.options.batch_size,
            lease_seconds=self.options.lease_seconds,
        )
        if not claimed:
            return MonitorRunSummary()

        semaphore = asyncio.Semaphore(self.options.concurrency)

        async def run_claim(monitor: PageMonitor) -> _MonitorOutcome:
            async with semaphore:
                return await self._run_claimed_monitor(monitor)

        results = await asyncio.gather(
            *(run_claim(monitor) for monitor in claimed),
            return_exceptions=True,
        )
        outcomes: list[_MonitorOutcome] = []
        for monitor, result in zip(claimed, results):
            if isinstance(result, asyncio.CancelledError):
                raise result
            if isinstance(result, BaseException):
                logger.error(
                    "Page monitor %s failed outside its isolation boundary.",
                    monitor.id,
                    exc_info=(
                        type(result),
                        result,
                        result.__traceback__,
                    ),
                )
                outcomes.append(_MonitorOutcome(status="error"))
            else:
                outcomes.append(result)

        return MonitorRunSummary(
            claimed=len(claimed),
            succeeded=sum(
                outcome.status == "ok" for outcome in outcomes
            ),
            partial=sum(
                outcome.status == "partial" for outcome in outcomes
            ),
            failed=sum(
                outcome.status == "error" for outcome in outcomes
            ),
            archived=sum(outcome.archived for outcome in outcomes),
            archive_failed=sum(
                outcome.archive_failed for outcome in outcomes
            ),
            paused=sum(outcome.paused for outcome in outcomes),
        )

    async def run_monitor_now(
        self,
        investigation_id: str,
        monitor_id: str,
    ) -> MonitorRunSummary:
        monitor = await asyncio.to_thread(
            self.investigation_service.claim_page_monitor_now,
            investigation_id,
            monitor_id,
            self.worker_id,
            lease_seconds=self.options.lease_seconds,
        )
        try:
            outcome = await self._run_claimed_monitor(monitor)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error(
                "Page monitor %s failed outside its isolation boundary.",
                monitor.id,
                exc_info=(type(exc), exc, exc.__traceback__),
            )
            outcome = _MonitorOutcome(status="error")
        return MonitorRunSummary(
            claimed=1,
            succeeded=int(outcome.status == "ok"),
            partial=int(outcome.status == "partial"),
            failed=int(outcome.status == "error"),
            archived=int(outcome.archived),
            archive_failed=int(outcome.archive_failed),
            paused=int(outcome.paused),
        )

    async def run_forever(self) -> None:
        while True:
            try:
                summary = await self.run_once()
                if summary.claimed:
                    logger.info(summary.to_line())
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Monitoring scheduler cycle failed.")
            await asyncio.sleep(self.options.poll_interval)

    async def _run_claimed_monitor(
        self,
        monitor: PageMonitor,
    ) -> _MonitorOutcome:
        if self.options.jitter_seconds:
            await asyncio.sleep(
                self.random_value() * self.options.jitter_seconds
            )

        result: ProbeResult | None = None
        last_exception: Exception | None = None
        intervention_required = False
        try:
            for attempt in range(self.options.retry_attempts + 1):
                try:
                    result = await asyncio.wait_for(
                        self.probe.run(
                            monitor.investigation_id,
                            monitor.id,
                        ),
                        timeout=self.options.attempt_timeout,
                    )
                    last_exception = None
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    last_exception = exc
                    result = None

                if result is not None:
                    intervention_required = _requires_intervention(result)
                    if (
                        result.observation.status != "error"
                        or intervention_required
                    ):
                        break
                if attempt >= self.options.retry_attempts:
                    break
                delay = (
                    self.options.retry_delay
                    * (self.options.retry_backoff ** attempt)
                    + self.random_value() * self.options.jitter_seconds
                )
                if delay:
                    await asyncio.sleep(delay)

            if result is None:
                return await self._finish_exception(
                    monitor,
                    last_exception or RuntimeError(
                        "Page monitor probe failed without a result."
                    ),
                )
            if result.observation.status == "error":
                return await self._finish_error_result(
                    monitor,
                    result,
                    intervention_required=intervention_required,
                )
            return await self._finish_success(monitor, result)
        except asyncio.CancelledError:
            await self._release_cancelled_claim(monitor)
            raise

    async def _finish_success(
        self,
        monitor: PageMonitor,
        result: ProbeResult,
    ) -> _MonitorOutcome:
        archived = False
        archive_failed = False
        if (
            result.archive_recommended
            and _archive_policy(monitor) == "on_change"
        ):
            if self.archive_handler is None:
                archive_failed = True
                logger.error(
                    "Page monitor %s requested an archive but no archive "
                    "handler is configured.",
                    monitor.id,
                )
            else:
                try:
                    await self.archive_handler(monitor, result)
                    archived = True
                except asyncio.CancelledError:
                    raise
                except Exception:
                    archive_failed = True
                    logger.exception(
                        "Automatic archive failed for page monitor %s.",
                        monitor.id,
                    )

        await asyncio.to_thread(
            self.investigation_service.finish_page_monitor_claim,
            monitor.investigation_id,
            monitor.id,
            self.worker_id,
            checked_at=result.observation.observed_at,
        )
        self.investigation_service.mark_changed()
        return _MonitorOutcome(
            status=result.observation.status,
            archived=archived,
            archive_failed=archive_failed,
        )

    async def _finish_error_result(
        self,
        monitor: PageMonitor,
        result: ProbeResult,
        *,
        intervention_required: bool,
    ) -> _MonitorOutcome:
        refreshed = await asyncio.to_thread(
            self.investigation_service.get_page_monitor,
            monitor.investigation_id,
            monitor.id,
        )
        pause = (
            intervention_required
            or refreshed.consecutive_failures >= self.options.max_failures
        )
        backoff = None
        if not pause:
            backoff = min(
                refreshed.check_interval_minutes * 60.0,
                self.options.failure_backoff_seconds
                * (
                    self.options.retry_backoff
                    ** max(0, refreshed.consecutive_failures - 1)
                ),
            )
        await asyncio.to_thread(
            self.investigation_service.finish_page_monitor_claim,
            monitor.investigation_id,
            monitor.id,
            self.worker_id,
            checked_at=result.observation.observed_at,
            pause=pause,
            failure_backoff_seconds=backoff,
        )
        self.investigation_service.mark_changed()
        return _MonitorOutcome(status="error", paused=pause)

    async def _finish_exception(
        self,
        monitor: PageMonitor,
        error: Exception,
    ) -> _MonitorOutcome:
        logger.warning(
            "Page monitor %s failed before recording an observation: %s",
            monitor.id,
            error,
        )
        refreshed = await asyncio.to_thread(
            self.investigation_service.get_page_monitor,
            monitor.investigation_id,
            monitor.id,
        )
        pause = (
            refreshed.consecutive_failures + 1
            >= self.options.max_failures
        )
        backoff = None
        if not pause:
            backoff = min(
                refreshed.check_interval_minutes * 60.0,
                self.options.failure_backoff_seconds
                * (
                    self.options.retry_backoff
                    ** refreshed.consecutive_failures
                ),
            )
        await asyncio.to_thread(
            self.investigation_service.finish_page_monitor_claim,
            monitor.investigation_id,
            monitor.id,
            self.worker_id,
            pause=pause,
            increment_failure=True,
            failure_backoff_seconds=backoff,
        )
        self.investigation_service.mark_changed()
        return _MonitorOutcome(status="error", paused=pause)

    async def _release_cancelled_claim(
        self,
        monitor: PageMonitor,
    ) -> None:
        try:
            await asyncio.to_thread(
                self.investigation_service.finish_page_monitor_claim,
                monitor.investigation_id,
                monitor.id,
                self.worker_id,
            )
        except Exception:
            logger.warning(
                "Unable to release cancelled page monitor lease %s.",
                monitor.id,
                exc_info=True,
            )
