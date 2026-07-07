"""Process-wide counters for CDP traffic (T-006).

Categories used across the codebase:

- ``targets_poll``     : tab inventory requests (main poll loop)
- ``eval_home``        : home-tab consume/push/status evaluates
- ``eval_overlay``     : external-tab overlay install/consume/status evaluates
- ``eval_settings``    : settings-bridge evaluates on local tabs
- ``eval_page``        : investigation/report page consume/status evaluates
- ``eval_engine_wait`` : per-iteration probes in engine wait loops
- ``engine_tab_open``  : engine tabs created by the search tab pool
- ``engine_tab_reuse`` : pooled engine tab reused for another variant
- ``get_content``      : full-page HTML retrievals
- ``screenshot``       : evidence screenshot captures
- ``capture_html``     : evidence outer-HTML captures (BrowserService)
- ``capture_mhtml``    : evidence MHTML snapshots (BrowserService)
- ``open_tab``         : tabs opened by the app (home, reports, pages)
- ``arm_script``       : new-document scripts armed on a target (once/tab)

Counters are cheap (dict increments under a lock) and always on; the
periodic dump only formats output when DEBUG logging is enabled
(``python main.py --verbose``).
"""

from __future__ import annotations

import logging
import threading
import time
from collections import Counter

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_calls: Counter = Counter()
_bytes: Counter = Counter()
_started_at = time.monotonic()
_last_dump = 0.0


def count(category: str, n: int = 1) -> None:
    with _lock:
        _calls[category] += n


def observe_bytes(category: str, n: int) -> None:
    with _lock:
        _bytes[category] += int(n)


def snapshot() -> dict:
    with _lock:
        return {
            "elapsed_seconds": time.monotonic() - _started_at,
            "calls": dict(_calls),
            "bytes": dict(_bytes),
        }


def reset() -> None:
    global _started_at, _last_dump
    with _lock:
        _calls.clear()
        _bytes.clear()
        _started_at = time.monotonic()
        _last_dump = 0.0


def maybe_log_snapshot(interval: float = 10.0) -> None:
    """Log a rate summary at DEBUG level, at most once per ``interval``."""
    global _last_dump
    if not logger.isEnabledFor(logging.DEBUG):
        return
    now = time.monotonic()
    with _lock:
        if now - _last_dump < interval:
            return
        _last_dump = now
        elapsed = max(now - _started_at, 1e-6)
        calls = dict(_calls)
        sizes = dict(_bytes)
    rates = ", ".join(
        f"{category}={total} ({total / elapsed:.1f}/s)"
        for category, total in sorted(calls.items())
    )
    kib = ", ".join(
        f"{category}={total / 1024:.0f}KiB"
        for category, total in sorted(sizes.items())
    )
    logger.debug("CDP calls: %s | payloads: %s", rates or "none", kib or "none")
