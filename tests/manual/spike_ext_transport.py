"""Manual T-031 spike: extension service worker transport over CDP.

Runs outside unittest. It starts a temporary browser profile with the unpacked
extension, arms Runtime.addBinding on the extension service worker, then sends
messages from two https pages through content script -> service worker -> CDP.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import zendriver as uc
from zendriver import cdp
from zendriver.core.connection import Connection

from browser_manager import _build_zendriver_config, _expected_extension_id
from settings import get_settings


BINDING_NAME = "synthesixDispatch"
PAGE_URLS = (
    "https://example.com/?synthesix-spike=1",
    "https://example.org/?synthesix-spike=2",
)


def _extension_dir() -> Path:
    path = ROOT / "extension"
    required = [
        path / "manifest.json",
        path / "dist" / "content.js",
    ]
    manifest_path = path / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        worker_rel = str(manifest.get("background", {}).get("service_worker", ""))
        if worker_rel:
            # The worker filename is revision-stamped by the frontend build.
            required.append(path / worker_rel)
    missing = [str(item) for item in required if not item.exists()]
    if missing:
        raise RuntimeError(
            "Extension build is incomplete. Run `cd frontend; npm.cmd run build` first. "
            f"Missing: {', '.join(missing)}"
        )
    return path


async def _wait_for_service_worker(
    browser,
    *,
    expected_extension_id: str,
    timeout: float = 10.0,
):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        targets = await browser._get_targets()
        workers = [
            target
            for target in targets
            if target.type_ == "service_worker"
            and str(target.url).startswith(f"chrome-extension://{expected_extension_id}/")
        ]
        if workers:
            target = workers[0]
            websocket_url = _target_websocket_url(browser, str(target.target_id))
            return Connection(
                websocket_url,
                target=target,
                _owner=browser,
            )
        await asyncio.sleep(0.25)
    raise TimeoutError("Extension service_worker target not found.")


def _debugger_targets(browser) -> list[dict[str, Any]]:
    url = f"http://{browser.config.host}:{browser.config.port}/json/list"
    with urllib.request.urlopen(url, timeout=5.0) as response:
        return json.loads(response.read().decode("utf-8"))


def _target_websocket_url(browser, target_id: str) -> str:
    for target in _debugger_targets(browser):
        if target.get("id") == target_id and target.get("webSocketDebuggerUrl"):
            return str(target["webSocketDebuggerUrl"])
    raise RuntimeError(f"WebSocket debugger URL not found for target {target_id}")


def _print_extension_targets(browser) -> None:
    print("Extension-related debugger targets:")
    for target in _debugger_targets(browser):
        target_url = str(target.get("url", ""))
        if target_url.startswith("chrome-extension://"):
            print(
                " -",
                target.get("type"),
                target.get("id"),
                target_url,
            )


async def _wait_for_marker(tab, timeout: float = 10.0) -> Any:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        marker = await _eval_value(
            tab,
            "document.documentElement.dataset.synthesixExt || null",
        )
        if marker:
            return marker
        await asyncio.sleep(0.25)
    return None


async def _eval_value(target, expression: str) -> Any:
    result, exception = await target.send(
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


async def _trigger_spike(tab, label: str) -> Any:
    detail = json.dumps({"label": label})
    expression = f"""
    (() => {{
      window.dispatchEvent(
        new CustomEvent("synthesix:spike-dispatch", {{ detail: {detail} }})
      );
      return document.documentElement.dataset.synthesixExt || null;
    }})()
    """
    return await tab.evaluate(expression)


def _summarize_payload(raw_payload: str) -> dict[str, Any]:
    payload = json.loads(raw_payload)
    message = payload.get("payload", {}).get("message", {})
    sent_at = message.get("sentAtEpochMs")
    latency_ms = None
    if isinstance(sent_at, (int, float)):
        latency_ms = time.time() * 1000 - sent_at
    return {
        "action": payload.get("action"),
        "type": message.get("type"),
        "href": message.get("href"),
        "payload": message.get("payload"),
        "latency_ms": round(latency_ms, 1) if latency_ms is not None else None,
    }


async def run_spike(sleep_seconds: float) -> int:
    extension_dir = _extension_dir()
    profile_dir = Path(tempfile.mkdtemp(prefix="synthesix-ext-spike-"))
    settings = get_settings()
    browser = None

    try:
        config = _build_zendriver_config(settings)
        config.user_data_dir = str(profile_dir)
        extension_arg = str(extension_dir).replace("\\", "/")
        config.add_argument(f"--load-extension={extension_arg}")
        config.add_argument("--disable-features=DisableLoadExtensionCommandLineSwitch")
        expected_extension_id = _expected_extension_id(settings)
        if not expected_extension_id:
            raise RuntimeError("Extension manifest has no stable key/id.")

        print(f"Starting browser with extension: {extension_dir}")
        browser = await uc.start(config=config)
        events: asyncio.Queue[str] = asyncio.Queue()

        first_tab = await browser.get(PAGE_URLS[0], new_tab=True)
        marker = await _wait_for_marker(first_tab)
        print(f"Content marker on first page: {marker!r}")
        if marker is None:
            _print_extension_targets(browser)
            raise RuntimeError(
                "Synthesix content script marker is absent. The unpacked extension "
                "was not loaded into the Zendriver-launched browser."
            )
        await _trigger_spike(first_tab, "warmup-before-binding")

        service_worker = await _wait_for_service_worker(
            browser,
            expected_extension_id=expected_extension_id,
        )
        print(
            "Service worker target:",
            getattr(service_worker, "target_id", None),
            getattr(service_worker, "url", ""),
        )

        async def on_binding_called(event) -> None:
            if getattr(event, "name", None) == BINDING_NAME:
                events.put_nowait(event.payload)

        service_worker.add_handler(cdp.runtime.BindingCalled, on_binding_called)
        await service_worker.send(cdp.runtime.enable())
        await service_worker.send(cdp.runtime.add_binding(name=BINDING_NAME))
        binding_type = await _eval_value(
            service_worker,
            f"typeof globalThis.{BINDING_NAME}",
        )
        print(f"Binding in service worker: {binding_type}")

        delivered: list[dict[str, Any]] = []
        for index, url in enumerate(PAGE_URLS, start=1):
            tab = first_tab if index == 1 else await browser.get(url, new_tab=True)
            await _wait_for_marker(tab)
            marker = await _trigger_spike(tab, f"bound-page-{index}")
            raw_payload = await asyncio.wait_for(events.get(), timeout=1.0)
            summary = _summarize_payload(raw_payload)
            delivered.append(summary)
            print(f"Delivered page {index}: marker={marker!r} {summary}")

        if sleep_seconds > 0:
            print(f"Sleeping {sleep_seconds:.0f}s to observe MV3 worker lifetime...")
            await asyncio.sleep(sleep_seconds)
            marker = await _trigger_spike(first_tab, "after-sleep")
            raw_payload = await asyncio.wait_for(events.get(), timeout=1.0)
            summary = _summarize_payload(raw_payload)
            delivered.append(summary)
            print(f"Delivered after sleep: marker={marker!r} {summary}")

        ok = len(delivered) >= 2 and all(item["action"] for item in delivered)
        print("SPIKE_RESULT", "OK" if ok else "FAILED")
        return 0 if ok else 1
    finally:
        if browser is not None:
            await browser.stop()
        shutil.rmtree(profile_dir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=0.0,
        help="Optional wait before a final post-idle message, e.g. 125.",
    )
    args = parser.parse_args()
    return asyncio.run(run_spike(args.sleep_seconds))


if __name__ == "__main__":
    raise SystemExit(main())
