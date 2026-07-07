"""Thin single layer over Zendriver/CDP (T-020).

Every CDP exchange initiated by the application code goes through this
module so that transport evolutions (push bindings T-021, event-driven
target discovery T-022, second browser T-040) touch one place only:

- module-level, stateless wrappers for tab-scoped calls (:func:`eval_js`,
  :func:`screenshot`, :func:`mhtml`, :func:`outer_html`) usable from code
  that only holds a tab handle (``evidence/capture.py``);
- :class:`BrowserService` for browser-scoped state: tab inventory, tab
  opening, and the registry of new-document scripts armed per target.

Design constraints (docs/tasks/T-020-browserservice.md):

- thin typed wrappers, no framework, no speculative abstraction;
- pure displacement: same CDP requests and same exception semantics as the
  call sites this replaces — :func:`eval_js` is best-effort (UI pushes
  historically swallow failures and fall back to ``None``), while the
  capture wrappers propagate (evidence integrity must fail loudly);
- every wrapper instrumented with the T-006 observability categories.

Tabs returned by :meth:`BrowserService.tabs` are live zendriver ``Tab``
handles, not snapshots: callers keep using their public API directly
(``bring_to_front``, ``reload``, ``select``, …). Only raw CDP traffic
(``tab.send``, ``tab.evaluate``, private browser APIs) is confined here.
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import time
import weakref
from typing import Any, Callable, Mapping

from zendriver import cdp

import observability

logger = logging.getLogger(__name__)


async def eval_js(tab, script: str, *, category: str) -> Any:
    """Evaluate ``script`` on ``tab``, best-effort.

    Counts one instrumented call under ``category`` (T-006). Failures are
    normalized: they are logged at DEBUG level and surface as ``None``,
    matching the historical behavior of every UI push/consume call site.
    """
    observability.count(category)
    try:
        return await tab.evaluate(script)
    except Exception:
        logger.debug("Browser eval failed (%s)", category, exc_info=True)
        return None


async def screenshot(
    tab,
    clip: Mapping[str, float],
    *,
    beyond_viewport: bool = True,
) -> bytes:
    """Capture a PNG of the ``clip`` viewport region, returned as bytes.

    Exceptions propagate: evidence captures must fail loudly.
    """
    observability.count("screenshot")
    encoded = await tab.send(
        cdp.page.capture_screenshot(
            format_="png",
            clip=cdp.page.Viewport(**clip),
            from_surface=True,
            capture_beyond_viewport=beyond_viewport,
            optimize_for_speed=False,
        )
    )
    return base64.b64decode(encoded, validate=True)


async def mhtml(tab) -> str:
    """Return the full MHTML snapshot of the page. Exceptions propagate."""
    observability.count("capture_mhtml")
    return await tab.send(cdp.page.capture_snapshot(format_="mhtml"))


async def outer_html(tab) -> str:
    """Return the document outer HTML (no shadow DOM). Exceptions propagate."""
    observability.count("capture_html")
    document = await tab.send(cdp.dom.get_document(depth=0, pierce=False))
    return await tab.send(
        cdp.dom.get_outer_html(
            node_id=document.node_id,
            include_shadow_dom=False,
        )
    )


async def click_at(tab, x: float, y: float) -> bool:
    """Dispatch a trusted left-click at viewport coordinates ``(x, y)``.

    Unlike a JS ``element.click()`` (``isTrusted == false``, which reCAPTCHA
    flags), a CDP ``Input.dispatchMouseEvent`` produces a trusted event.
    Best-effort like :func:`eval_js`: failures are logged and surface as
    ``False`` so callers can fall back.
    """
    observability.count("input_click")
    try:
        await tab.send(cdp.input_.dispatch_mouse_event("mouseMoved", x=x, y=y))
        await tab.send(
            cdp.input_.dispatch_mouse_event(
                "mousePressed",
                x=x,
                y=y,
                button=cdp.input_.MouseButton.LEFT,
                click_count=1,
            )
        )
        await tab.send(
            cdp.input_.dispatch_mouse_event(
                "mouseReleased",
                x=x,
                y=y,
                button=cdp.input_.MouseButton.LEFT,
                click_count=1,
            )
        )
        return True
    except Exception:
        logger.debug("Browser click failed", exc_info=True)
        return False


class BrowserService:
    """Browser-scoped CDP operations and per-target state.

    One instance per live browser; obtain it through
    :func:`get_browser_service` so the armed-script registry survives across
    call sites that only hold the raw browser handle.
    """

    def __init__(self, browser) -> None:
        self.browser = browser
        # CDP target ids for which a new-document script has already been
        # armed. Re-arming on every poll tick would stack duplicate scripts
        # on the same target; pruned against live targets by :meth:`tabs`.
        self.armed_script_targets: set[str] = set()
        # T-021: target ids with a confirmed `synthesixDispatch` binding, and
        # the push queue it feeds. One queue per browser (shared across
        # repeated `wait_for_home_action` calls via `get_browser_service`).
        self.armed_binding_targets: set[str] = set()
        self.dispatch_queue: asyncio.Queue = asyncio.Queue()
        # Per-target last time the local-page consume/sync evaluate actually
        # ran, so callers can throttle it once push delivery is confirmed.
        self.last_local_sync_at: dict[str, float] = {}
        # T-022: zendriver keeps `browser.tabs` up to date from Target.*
        # events, so the per-tick `getTargets` inventory is replaced by a
        # slow authoritative resync. Overridable from settings by the caller.
        self.target_resync_interval: float = 10.0
        self._last_target_resync: float = 0.0

    def _live_page_ids(self) -> set[str]:
        """Page-target ids from zendriver's event-maintained registry."""
        return {
            target_id
            for tab in self.browser.tabs
            if (target_id := getattr(tab, "target_id", None))
        }

    def _browser_unhealthy(self) -> bool:
        """Cheap per-tick liveness signal (no CDP round-trip).

        The event-maintained registry can go stale when Chrome dies: no
        ``TargetDestroyed`` is delivered, so ``browser.tabs`` keeps listing
        gone tabs. zendriver's browser-connection ``Listener`` loop breaks on
        that dropped websocket, so a stopped listener (or a stopped process)
        means the registry can no longer be trusted and an authoritative
        resync must run now instead of waiting out the interval — otherwise
        the "all tabs closed => quit" path never fires (T-022 regression).
        """
        if getattr(self.browser, "stopped", False):
            return True
        connection = getattr(self.browser, "connection", None)
        listener = getattr(connection, "listener", None)
        # Only trust an explicit "not running": a missing listener (never
        # opened, or a test double) must not be read as unhealthy.
        return listener is not None and not getattr(listener, "running", True)

    async def _resync_targets(self) -> set[str] | None:
        """Authoritative `getTargets` round-trip: refresh the registry and
        report the live page-target ids. Returns ``None`` when the browser
        is unreachable — the only remaining per-loop CDP liveness probe.

        zendriver 0.15.3's ``update_targets()`` only adds/refreshes (never
        removes closed targets), so the fresh ``_get_targets()`` list stays
        the authority on which tabs are still alive.
        """
        observability.count("targets_poll")
        try:
            await self.browser.update_targets()
            targets = await self.browser._get_targets()
        except Exception:
            logger.debug("Unable to update browser targets", exc_info=True)
            return None
        return {
            target.target_id
            for target in targets
            if target.type_ == "page"
        }

    async def tabs(self) -> list | None:
        """Live page tabs, or ``None`` when the browser is unreachable.

        Reads zendriver's event-maintained registry on every call; an
        authoritative ``getTargets`` resync only runs every
        :attr:`target_resync_interval` seconds (or when the registry looks
        empty, so a transient event gap cannot be mistaken for "all tabs
        closed"). The ``None`` return drives the unreachable-browser quit
        guard in the main loop, so failures must not surface as an empty
        list.
        """
        registry_ids = self._live_page_ids()
        now = time.monotonic()
        first_resync = self._last_target_resync == 0.0
        # Resync on the slow interval, but also immediately whenever the
        # registry can't be trusted: empty (a transient event gap must not
        # read as "no tabs => quit") or the browser looks gone (so the
        # quit/unreachable path fires without waiting out the interval).
        resync_due = (
            now - self._last_target_resync >= self.target_resync_interval
            or not registry_ids
            or self._browser_unhealthy()
        )
        if resync_due:
            live_page_ids = await self._resync_targets()
            if live_page_ids is None:
                return None
            self._last_target_resync = now
            if not first_resync and live_page_ids != registry_ids:
                logger.debug(
                    "Target registry drift: events=%s wire=%s",
                    sorted(registry_ids),
                    sorted(live_page_ids),
                )
        else:
            live_page_ids = registry_ids

        self.armed_script_targets.intersection_update(live_page_ids)
        self.armed_binding_targets.intersection_update(live_page_ids)
        self.last_local_sync_at = {
            target_id: at
            for target_id, at in self.last_local_sync_at.items()
            if target_id in live_page_ids
        }
        return [
            tab
            for tab in self.browser.tabs
            if getattr(tab, "target_id", None) in live_page_ids
        ]

    async def open_tab(self, url: str, *, new_tab: bool = True):
        """Open ``url`` (new tab by default) and return the tab handle."""
        observability.count("open_tab")
        return await self.browser.get(url, new_tab=new_tab)

    async def arm_new_document_script(self, tab, script: str) -> None:
        """Arm ``script`` to run before any page script on future
        navigations of ``tab``.

        Best-effort and idempotent per target: on failure (or if already
        armed) this silently no-ops — callers historically tolerate hosts
        where arming fails.
        """
        target_id = getattr(tab, "target_id", None)
        if not target_id or target_id in self.armed_script_targets:
            return
        observability.count("arm_script")
        try:
            # Page.addScriptToEvaluateOnNewDocument silently no-ops unless
            # the Page domain has been enabled on this CDP session first.
            await tab.send(cdp.page.enable())
            await tab.send(
                cdp.page.add_script_to_evaluate_on_new_document(script)
            )
            self.armed_script_targets.add(target_id)
        except Exception:
            logger.debug("Unable to arm new-document script", exc_info=True)

    async def arm_dispatch_binding(self, tab, name: str = "synthesixDispatch") -> bool:
        """Expose ``window.<name>(payload)`` on ``tab`` and route each call
        into :attr:`dispatch_queue` (T-021 push transport for local pages).

        Best-effort and idempotent per target, like
        :meth:`arm_new_document_script`: on failure this silently returns
        ``False`` and the caller keeps polling that tab.
        """
        target_id = getattr(tab, "target_id", None)
        if not target_id:
            return False
        if target_id in self.armed_binding_targets:
            return True
        observability.count("arm_binding")
        try:
            await tab.send(cdp.runtime.enable())
            await tab.send(cdp.runtime.add_binding(name=name))
            tab.add_handler(
                cdp.runtime.BindingCalled,
                self._make_binding_handler(tab, name),
            )
            self.armed_binding_targets.add(target_id)
            return True
        except Exception:
            logger.debug("Unable to arm dispatch binding", exc_info=True)
            return False

    def _make_binding_handler(self, tab, name: str) -> Callable:
        # Must stay a coroutine function: zendriver dispatches plain
        # callbacks via `asyncio.to_thread` (a worker thread), where touching
        # `asyncio.Queue` is not safe. Coroutine handlers instead run as a
        # plain task on the event loop itself (`asyncio.create_task`).
        async def _on_binding_called(event) -> None:
            if getattr(event, "name", None) != name:
                return
            try:
                parsed = json.loads(event.payload)
            except (TypeError, ValueError):
                logger.debug("Discarding non-JSON dispatch payload", exc_info=True)
                return
            if not isinstance(parsed, dict) or not parsed.get("action"):
                logger.debug("Discarding malformed dispatch payload: %r", parsed)
                return
            parsed["_source_tab"] = tab
            observability.count("push_action")
            self.dispatch_queue.put_nowait(parsed)

        return _on_binding_called

    def on_event(self, tab, event_type, handler: Callable) -> None:
        """Register ``handler`` for a CDP event on ``tab`` (zendriver
        ``add_handler``). Seam for the T-021 push transport."""
        tab.add_handler(event_type, handler)


_services: "weakref.WeakKeyDictionary[Any, BrowserService]" = (
    weakref.WeakKeyDictionary()
)


def get_browser_service(browser) -> BrowserService:
    """Shared :class:`BrowserService` for ``browser`` (one per instance).

    Browsers that cannot be weak-referenced (e.g. ``SimpleNamespace`` test
    doubles) get a fresh, uncached service: fine for single-shot tests, and
    real ``zendriver.Browser`` instances are always cacheable.
    """
    try:
        service = _services.get(browser)
    except TypeError:
        return BrowserService(browser)
    if service is None:
        service = BrowserService(browser)
        _services[browser] = service
    return service
