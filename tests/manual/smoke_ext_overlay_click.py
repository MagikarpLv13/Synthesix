"""Manual T-034/T-035 smoke: real extension overlay clicks end to end.

Runs outside unittest. It starts a temporary browser profile with the unpacked
extension, arms the dispatch binding on the MV3 service worker through
``BrowserService`` (the exact production path), then:

0. checks the running worker build revision against ``dist/revision.json``
   while arming (a mismatch would log a stale-worker warning);
1. waits for the extension overlay host on a real https page;
2. clicks "Save page" without an investigation -> expects ``focus_home``;
3. pushes a context update through ``send_extension_backend_message`` and
   waits for the overlay to apply it (storage -> content -> main world);
4. clicks "Save page" again -> expects ``save_page_to_investigation``.

Usage (from the repo root, with Brave):

    set SYNTHESIX_BROWSER=brave
    .venv\\Scripts\\python.exe tests\\manual\\smoke_ext_overlay_click.py
"""

from __future__ import annotations

import asyncio
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import zendriver as uc
from zendriver import cdp

from browser.service import get_browser_service
from browser_manager import (
    _build_zendriver_config,
    _configure_extension_launch,
    _expected_extension_id,
    _expected_extension_revision,
)
from settings import get_settings


PAGE_URL = "https://example.com/?synthesix-overlay-smoke=1"
OVERLAY_HOST_ID = "__synthesix-save-overlay"
SMOKE_INVESTIGATION = {"id": "smoke-inv", "title": "Smoke Investigation"}


async def _eval_value(tab, expression: str) -> Any:
    result, exception = await tab.send(
        cdp.runtime.evaluate(
            expression,
            await_promise=True,
            return_by_value=True,
            allow_unsafe_eval_blocked_by_csp=True,
        )
    )
    if exception is not None:
        raise RuntimeError(f"Runtime.evaluate failed: {exception}")
    return getattr(result, "value", None)


async def _wait_for(tab, expression: str, label: str, timeout: float = 15.0) -> Any:
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        last = await _eval_value(tab, expression)
        if last:
            return last
        await asyncio.sleep(0.25)
    raise TimeoutError(f"Timed out waiting for {label} (last value: {last!r})")


async def _arm_binding(
    service,
    extension_id: str,
    expected_revision: str | None = None,
    timeout: float = 15.0,
) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if await service.arm_extension_dispatch_binding(
            extension_id, expected_revision=expected_revision
        ):
            return
        await asyncio.sleep(0.5)
    raise TimeoutError("Could not arm the extension dispatch binding.")


async def _drain_actions(service, wait_seconds: float = 4.0) -> list[dict]:
    actions: list[dict] = []
    deadline = time.monotonic() + wait_seconds
    while time.monotonic() < deadline:
        remaining = deadline - time.monotonic()
        try:
            action = await asyncio.wait_for(
                service.dispatch_queue.get(), timeout=max(0.1, remaining)
            )
        except asyncio.TimeoutError:
            break
        actions.append(action)
    return actions


def _overlay_action_names(dispatches: list[dict]) -> list[str]:
    names = []
    for dispatch in dispatches:
        if dispatch.get("action") != "extension_overlay_action":
            names.append(f"<{dispatch.get('action')}>")
            continue
        message = (dispatch.get("payload") or {}).get("message") or {}
        action = message.get("action") or {}
        names.append(str(action.get("action")))
    return names


async def run_smoke() -> int:
    settings = get_settings()
    profile_dir = Path(tempfile.mkdtemp(prefix="synthesix-ext-overlay-smoke-"))
    browser = None
    failures: list[str] = []

    try:
        config = _build_zendriver_config(settings)
        config.user_data_dir = str(profile_dir)
        if not _configure_extension_launch(config, settings):
            raise RuntimeError(
                "Extension launch flags rejected; check extension_mode/build."
            )
        extension_id = _expected_extension_id(settings)
        if not extension_id:
            raise RuntimeError("Extension manifest has no stable key/id.")

        expected_revision = _expected_extension_revision(settings)
        print(
            f"Starting browser with extension id {extension_id} "
            f"(build revision {expected_revision})"
        )
        browser = await uc.start(config=config)
        service = get_browser_service(browser)

        tab = await browser.get(PAGE_URL, new_tab=True)
        marker = await _wait_for(
            tab,
            "document.documentElement.dataset.synthesixExt || null",
            "content script marker",
        )
        print(f"[1] content marker: {marker!r}")

        await _arm_binding(service, extension_id, expected_revision)
        stale = sorted(service.stale_extension_worker_targets)
        print(f"[2] dispatch binding armed on service worker (stale targets: {stale})")
        if stale:
            failures.append("service worker runs a stale build revision")

        host_ready = await _wait_for(
            tab,
            f"""(() => {{
                const host = document.getElementById({json.dumps(OVERLAY_HOST_ID)});
                return host && host.hasAttribute("data-synthesix-extension-overlay")
                    ? host.getAttribute("data-synthesix-extension-overlay")
                    : null;
            }})()""",
            "extension overlay host",
        )
        print(f"[3] overlay host present (extension {host_ready!r})")

        token = await _eval_value(
            tab,
            "document.documentElement.dataset.synthesixOverlayToken || null",
        )
        print(f"[4] bridge token visible in main world: {bool(token)}")
        if not token:
            failures.append("bridge token missing (dataset.synthesixOverlayToken)")

        # Click without an investigation: expect focus_home.
        await _eval_value(
            tab,
            f"""(() => {{
                const host = document.getElementById({json.dumps(OVERLAY_HOST_ID)});
                const button = host.querySelector("[data-synthesix-save-page]");
                button.click();
                return true;
            }})()""",
        )
        no_context_actions = _overlay_action_names(await _drain_actions(service))
        print(f"[5] actions after click without investigation: {no_context_actions}")
        if "focus_home" not in no_context_actions:
            failures.append(
                f"expected focus_home after context-less click, got {no_context_actions}"
            )

        sent = await service.send_extension_backend_message(
            extension_id,
            {"type": "synthesix:context-update", "payload": SMOKE_INVESTIGATION},
        )
        print(f"[6] context update accepted by worker: {sent}")
        if not sent:
            failures.append("send_extension_backend_message returned False")

        applied = await _wait_for(
            tab,
            f"""(() => {{
                const host = document.getElementById({json.dumps(OVERLAY_HOST_ID)});
                return host && host.dataset.investigationId === "smoke-inv"
                    ? "smoke-inv"
                    : null;
            }})()""",
            "context applied to overlay",
        )
        print(f"[7] overlay investigation id: {applied!r}")
        # Applying a context queues observe_saved_page; drain it first.
        observe_actions = _overlay_action_names(await _drain_actions(service, 2.0))
        print(f"[8] actions after context update: {observe_actions}")

        await _eval_value(
            tab,
            f"""(() => {{
                const host = document.getElementById({json.dumps(OVERLAY_HOST_ID)});
                const button = host.querySelector("[data-synthesix-save-page]");
                button.click();
                return true;
            }})()""",
        )
        save_actions = _overlay_action_names(await _drain_actions(service))
        print(f"[9] actions after click with investigation: {save_actions}")
        if "save_page_to_investigation" not in save_actions:
            failures.append(
                f"expected save_page_to_investigation, got {save_actions}"
            )

        print("SMOKE_RESULT", "OK" if not failures else "FAILED")
        for failure in failures:
            print(" -", failure)
        return 0 if not failures else 1
    finally:
        if browser is not None:
            await browser.stop()
        shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run_smoke()))
