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

import base64
import logging
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

    async def tabs(self) -> list | None:
        """Live page tabs, or ``None`` when the browser is unreachable.

        The ``None`` return drives the unreachable-browser quit guard in the
        main loop, so failures must not surface as an empty list.
        """
        observability.count("targets_poll")
        try:
            await self.browser.update_targets()
            # Second fetch on purpose: zendriver 0.15.3's update_targets()
            # adds and refreshes targets but never removes closed ones, so
            # the fresh list is the only way to know which tabs are still
            # alive (checked — Connection.closed is also True for live tabs
            # that never attached a websocket). Both requests go away with
            # T-022 (Target events).
            targets = await self.browser._get_targets()
            live_page_ids = {
                target.target_id
                for target in targets
                if target.type_ == "page"
            }
        except Exception:
            logger.debug("Unable to update browser targets", exc_info=True)
            return None

        self.armed_script_targets.intersection_update(live_page_ids)
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
