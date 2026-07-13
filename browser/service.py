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
import urllib.request
import weakref
from typing import Any, Callable, Mapping

from zendriver import cdp
from zendriver.core.connection import Connection

import observability

logger = logging.getLogger(__name__)
MAX_DISPATCH_PAYLOAD_BYTES = 256 * 1024


@cdp.util.event_class("Inspector.workerScriptLoaded")
class _InspectorWorkerScriptLoaded:
    """Zendriver 0.15.3 misses this Inspector event on extension workers.

    Chrome can emit it while the Synthesix MV3 service worker is debug-attached.
    Without a registered parser, Zendriver logs a noisy KeyError stack trace
    from its listener loop even though Synthesix does not need the event.
    """

    @classmethod
    def from_json(cls, _json: Mapping[str, Any]) -> "_InspectorWorkerScriptLoaded":
        return cls()


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


async def page_layout(tab) -> dict[str, float]:
    """Return the CSS content dimensions needed for a visual page archive."""
    observability.count("page_layout")
    (
        _layout_viewport,
        _visual_viewport,
        _content_size,
        _css_layout_viewport,
        _css_visual_viewport,
        css_content_size,
    ) = await tab.send(cdp.page.get_layout_metrics())
    return {
        "width": float(css_content_size.width),
        "height": float(css_content_size.height),
    }


async def visual_viewport(tab) -> dict[str, float]:
    """Return the current scroll position and viewport size for evidence."""
    observability.count("visual_viewport")
    result = await tab.evaluate(
        """
        (() => ({
          x: window.scrollX || 0,
          y: window.scrollY || 0,
          width: window.innerWidth || document.documentElement.clientWidth || 0,
          height: window.innerHeight || document.documentElement.clientHeight || 0,
        }))()
        """
    )
    if not isinstance(result, Mapping):
        raise RuntimeError("Unable to read the browser viewport.")
    try:
        return {
            "x": float(result["x"]),
            "y": float(result["y"]),
            "width": float(result["width"]),
            "height": float(result["height"]),
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError("Invalid browser viewport response.") from exc


async def scroll_for_visual_capture(tab, x: float, y: float) -> None:
    """Scroll a page while warming lazy content for a visual archive."""
    observability.count("visual_scroll")
    coordinates = json.dumps([float(x), float(y)])
    await tab.evaluate(
        f"""
        (() => {{
          const overlay = document.getElementById('__synthesix-save-overlay')
            || document.querySelector('[data-synthesix-overlay-root]');
          if (overlay && !Object.hasOwn(overlay.dataset, 'synthesixVisualCaptureStyle')) {{
            overlay.dataset.synthesixVisualCaptureStyle = overlay.style.cssText;
          }}
          if (overlay) overlay.style.setProperty('display', 'none', 'important');
          window.scrollTo(...{coordinates});
        }})()
        """
    )


async def finish_visual_capture(tab, x: float, y: float) -> None:
    """Restore the analyst's scroll position and the Synthesix overlay."""
    observability.count("visual_restore")
    coordinates = json.dumps([float(x), float(y)])
    await tab.evaluate(
        f"""
        (() => {{
          window.scrollTo(...{coordinates});
          const overlay = document.getElementById('__synthesix-save-overlay')
            || document.querySelector('[data-synthesix-overlay-root]');
          if (overlay && Object.hasOwn(overlay.dataset, 'synthesixVisualCaptureStyle')) {{
            overlay.style.cssText = overlay.dataset.synthesixVisualCaptureStyle;
            delete overlay.dataset.synthesixVisualCaptureStyle;
          }}
        }})()
        """
    )


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
        self.armed_extension_binding_targets: set[str] = set()
        self.extension_worker_connections: dict[str, Any] = {}
        # Worker target ids already reported as running a build revision that
        # differs from the one on disk (warn once per target, not per tick).
        self.stale_extension_worker_targets: set[str] = set()
        self.dispatch_queue: asyncio.Queue = asyncio.Queue()
        # Per-target last time the local-page consume/sync evaluate actually
        # ran, so callers can throttle it once push delivery is confirmed.
        self.last_local_sync_at: dict[str, float] = {}
        # T-022: zendriver keeps `browser.tabs` up to date from Target.*
        # events, so the per-tick `getTargets` inventory is replaced by a
        # slow authoritative resync. Overridable from settings by the caller.
        self.target_resync_interval: float = 10.0
        self._last_target_resync: float = 0.0
        # A dead Chrome makes zendriver's `send` await a response that never
        # arrives (the CDP transaction has no timeout of its own), which would
        # hang the whole action loop. Bound the resync so `tabs()` reports the
        # browser as unreachable instead of freezing.
        self.target_resync_timeout: float = 5.0

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
            targets = await asyncio.wait_for(
                self._fetch_targets(), timeout=self.target_resync_timeout
            )
        except Exception:
            # Includes asyncio.TimeoutError: a dead browser whose CDP response
            # never comes must read as unreachable, not hang the loop.
            logger.debug("Unable to update browser targets", exc_info=True)
            return None
        return {
            target.target_id
            for target in targets
            if target.type_ == "page"
        }

    async def _fetch_targets(self):
        await self.browser.update_targets()
        return await self.browser._get_targets()

    async def ping(self) -> bool:
        return await self._resync_targets() is not None

    async def close_blank_tabs(self) -> int:
        # Do not filter on ``Tab.closed``: zendriver defines it as "no
        # websocket attached", which is also true for the untouched initial
        # ``about:blank`` tab — the very one this method must close.
        closed = 0
        for tab in list(getattr(self.browser, "tabs", ())):
            if str(getattr(tab, "url", "") or "").strip().lower() not in {
                "",
                "about:blank",
                "chrome://newtab/",
            }:
                continue
            try:
                await asyncio.wait_for(tab.close(), timeout=5.0)
            except Exception:
                logger.debug("Unable to close blank browser tab", exc_info=True)
            else:
                closed += 1
        return closed

    async def show_tab_window_for_manual_interaction(
        self,
        tab,
        *,
        left: int = 80,
        top: int = 80,
        width: int = 1280,
        height: int = 900,
    ) -> None:
        async def focus_tab() -> None:
            if hasattr(tab, "bring_to_front"):
                await tab.bring_to_front()
            elif hasattr(tab, "activate"):
                await tab.activate()

        target_id = getattr(tab, "target_id", None)
        if not target_id:
            await focus_tab()
            return
        connection = getattr(tab, "connection", None) or getattr(
            self.browser,
            "connection",
            None,
        )
        if connection is None:
            await focus_tab()
            return
        try:
            window_id, _bounds = await connection.send(
                cdp.browser.get_window_for_target(cdp.target.TargetID(target_id))
            )
            await connection.send(
                cdp.browser.set_window_bounds(
                    window_id,
                    cdp.browser.Bounds(
                        left=left,
                        top=top,
                        width=width,
                        height=height,
                        window_state=cdp.browser.WindowState.NORMAL,
                    ),
                )
            )
        except Exception:
            logger.debug("Unable to move browser window on screen", exc_info=True)
        await focus_tab()

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
        self.armed_binding_targets.intersection_update(
            live_page_ids | self.armed_extension_binding_targets
        )
        self.armed_extension_binding_targets.intersection_update(
            self.armed_binding_targets
        )
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

    async def arm_extension_dispatch_binding(
        self,
        extension_id: str | None,
        name: str = "synthesixDispatch",
        expected_revision: str | None = None,
    ) -> bool:
        """Expose the dispatch binding on Synthesix' MV3 service worker.

        The worker is not a page tab, so zendriver does not list it in
        ``browser.tabs``. We attach directly to its debugger websocket and
        then reuse :meth:`arm_dispatch_binding`.

        When ``expected_revision`` is given, the running worker is compared to
        the on-disk build (``dist/revision.json``) and a mismatch is logged
        once per worker target. Arming still proceeds: an out-of-date worker
        beats a dead one, and the browser picks up the rebuilt bundles at the
        next launch (the build stamps the worker filename, which defeats the
        Chromium service-worker script cache).
        """
        if not extension_id:
            return False
        target = await self._find_extension_service_worker_target(extension_id)
        if target is None:
            return False
        target_id = str(getattr(target, "target_id", "") or "")
        if not target_id:
            return False
        if target_id in self.armed_extension_binding_targets:
            return True
        try:
            connection = self._extension_connection(target, target_id)
        except Exception:
            logger.debug("Unable to attach to extension service worker", exc_info=True)
            return False
        # zendriver's Connection exposes target metadata, but make the id
        # explicit for fakes and future versions.
        try:
            setattr(connection, "target_id", target_id)
        except Exception:
            pass
        if expected_revision:
            running = await self._extension_worker_revision(connection)
            if (
                running != expected_revision
                and target_id not in self.stale_extension_worker_targets
            ):
                self.stale_extension_worker_targets.add(target_id)
                logger.warning(
                    "Extension service worker runs build revision %r but the "
                    "build on disk is %r; restart the browser (or reload the "
                    "extension) to pick up the new bundles. Arming anyway.",
                    running,
                    expected_revision,
                )
        armed = await self.arm_dispatch_binding(connection, name=name)
        if armed:
            self.armed_extension_binding_targets.add(target_id)
            self.extension_worker_connections[target_id] = connection
        return armed

    async def _extension_worker_revision(self, connection) -> str:
        try:
            remote, exception = await connection.send(
                cdp.runtime.evaluate(
                    expression='String(globalThis.synthesixBackgroundRevision || "")',
                    return_by_value=True,
                )
            )
        except Exception:
            logger.debug("Unable to read extension worker revision", exc_info=True)
            return ""
        if exception is not None:
            logger.debug("Extension worker revision read rejected: %r", exception)
            return ""
        return str(getattr(remote, "value", "") or "")

    async def send_extension_backend_message(
        self,
        extension_id: str | None,
        message: Mapping[str, Any],
    ) -> bool:
        """Deliver a backend-originated message to Synthesix' service worker.

        T-035 uses the same worker CDP attachment as the extension action
        binding, but in the opposite direction: Python evaluates a small
        promise in the MV3 worker, which then updates extension storage or
        relays a targeted tab message.
        """
        if not extension_id:
            return False
        target = await self._find_extension_service_worker_target(extension_id)
        if target is None:
            return False
        target_id = str(getattr(target, "target_id", "") or "")
        if not target_id:
            return False
        connection = self.extension_worker_connections.get(target_id)
        if connection is None:
            try:
                connection = self._extension_connection(target, target_id)
            except Exception:
                logger.debug(
                    "Unable to attach to extension service worker",
                    exc_info=True,
                )
                return False
            try:
                setattr(connection, "target_id", target_id)
            except Exception:
                pass
            self.extension_worker_connections[target_id] = connection
        payload_json = json.dumps(message, ensure_ascii=True)
        observability.count("extension_backend_message")
        observability.observe_bytes("extension_backend_message", len(payload_json))
        try:
            remote, exception = await connection.send(
                cdp.runtime.evaluate(
                    expression=(
                        "globalThis.synthesixReceiveBackendMessage"
                        "? globalThis.synthesixReceiveBackendMessage"
                        f"({payload_json}) : false"
                    ),
                    await_promise=True,
                    return_by_value=True,
                )
            )
        except Exception:
            logger.debug("Unable to send extension backend message", exc_info=True)
            return False
        if exception is not None:
            logger.debug("Extension backend message rejected: %r", exception)
            return False
        return bool(getattr(remote, "value", False))

    async def _find_extension_service_worker_target(self, extension_id: str):
        expected_prefix = f"chrome-extension://{extension_id}/"
        try:
            targets = await self.browser._get_targets()
        except Exception:
            logger.debug("Unable to inspect extension service worker", exc_info=True)
            return None
        return next(
            (
                target
                for target in targets
                if getattr(target, "type_", None) == "service_worker"
                and str(getattr(target, "url", "")).startswith(expected_prefix)
            ),
            None,
        )

    def _extension_connection(self, target, target_id: str):
        websocket_url = self._target_websocket_url(target_id)
        # Do not pass the browser as owner here. Zendriver uses `_owner` to run
        # page-specific preparation commands before every send; those commands
        # are invalid/noisy on MV3 service workers and can destabilize the
        # browser-level session during overlay clicks.
        return Connection(websocket_url, target=target)

    def _target_websocket_url(self, target_id: str) -> str:
        config = getattr(self.browser, "config", None)
        host = getattr(config, "host", None)
        port = getattr(config, "port", None)
        if not host or not port:
            raise RuntimeError("Browser debugger endpoint is unavailable.")
        url = f"http://{host}:{port}/json/list"
        with urllib.request.urlopen(url, timeout=5.0) as response:
            targets = json.loads(response.read().decode("utf-8"))
        for target in targets:
            if target.get("id") == target_id and target.get("webSocketDebuggerUrl"):
                return str(target["webSocketDebuggerUrl"])
        raise RuntimeError(f"WebSocket debugger URL not found for {target_id}")

    def _make_binding_handler(self, tab, name: str) -> Callable:
        # Must stay a coroutine function: zendriver dispatches plain
        # callbacks via `asyncio.to_thread` (a worker thread), where touching
        # `asyncio.Queue` is not safe. Coroutine handlers instead run as a
        # plain task on the event loop itself (`asyncio.create_task`).
        async def _on_binding_called(event) -> None:
            if getattr(event, "name", None) != name:
                return
            if len(str(getattr(event, "payload", "") or "").encode("utf-8")) > (
                MAX_DISPATCH_PAYLOAD_BYTES
            ):
                logger.warning("Discarding oversized dispatch payload")
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
