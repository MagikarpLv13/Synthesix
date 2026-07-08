import asyncio
import argparse
import base64
import binascii
import hashlib
import re
import unicodedata
import importlib.metadata
from datetime import datetime, timedelta, timezone
from pathlib import Path
import logging
import json
import os
import shutil
import time
import sys
from typing import Any, Mapping
from urllib.parse import urlsplit
from uuid import uuid4
from browser import BrowserService, eval_js, get_browser_service
from browser_manager import (
    HeadlessBrowserManager,
    _expected_extension_revision,
    clear_browser_profile_data,
)
from evidence import (
    build_evidence_manifest,
    capture_html,
    capture_mhtml,
    capture_png,
    compare_page_text,
    normalize_html_text,
    write_text_document,
    write_manifest,
)
from evidence.hashing import sha256_file
from exceptions import (
    EvidenceCaptureError,
    InvestigationError,
    InvestigationValidationError,
    RobotChallengeError,
    SearchEngineError,
    SynthesixError,
)
from exports import export_zeroneurone_bundle
from exports.zeroneurone_tagsets import (
    ZERONEURONE_TAGSETS,
    zeroneurone_tagset_suggested_properties,
)
import observability
from investigations import InvestigationRepository, InvestigationService
from investigations.repository import utc_now
from investigations.monitoring_view import generate_page_comparison_report
from investigations.search_view import generate_local_search_page
from investigations.view import generate_investigation_page
from query_operators import SearchFilters, build_display_query
from query_variants import (
    MAX_QUERY_LENGTH,
    normalize_query_variants,
    suggest_query_variants,
)
from search_engine import ACTIVE_ENGINE_TAB_TARGETS
from search_orchestrator import SearchOrchestrator
from settings import AppSettings, get_settings
import zendriver as uc
from utils import (
    clear_synthesix_history,
    is_advanced_query,
    load_search_history,
    smart_parse,
)


RECENT_PAGE_ARCHIVE_REUSE_WINDOW = timedelta(minutes=15)

# How long _open_tabs may keep failing before the main loop gives up on the
# browser connection (crashed or force-killed Chrome).
_BROWSER_UNREACHABLE_QUIT_SECONDS = 10.0

logger = logging.getLogger(__name__)
_MISSING_HISTORY_SIGNATURE = object()
_OVERLAY_BUNDLE_PATH = (
    Path(__file__).resolve().parent / "assets" / "synthesix-overlay.js"
)


class SearchBrowserProvider:
    _BLANK_URLS = {"", "about:blank", "chrome://newtab/"}

    def __init__(
        self,
        settings: AppSettings,
        user_browser_manager: HeadlessBrowserManager,
    ) -> None:
        self.settings = settings
        self.user_browser_manager = user_browser_manager
        self.search_browser_manager: HeadlessBrowserManager | None = None

    @property
    def separate(self) -> bool:
        return self.settings.search_browser_mode == "separate"

    async def get_browser(self):
        if not self.separate:
            return await self.user_browser_manager.get_driver()

        manager = self.search_browser_manager
        if manager is not None and manager.browser is not None:
            if await self._is_browser_alive(manager.browser):
                return manager.browser
            logger.warning("Search browser is not reachable; restarting it.")
            await manager.stop()
            self.search_browser_manager = None

        self.search_browser_manager = await HeadlessBrowserManager.create_search(
            self.settings
        )
        return await self.search_browser_manager.get_driver()

    async def stop(self) -> None:
        if self.search_browser_manager is not None:
            await self.search_browser_manager.stop()
            self.search_browser_manager = None

    async def cleanup_idle_tabs(self) -> None:
        if not self.separate or self.search_browser_manager is None:
            return
        browser = self.search_browser_manager.browser
        if browser is None:
            self.search_browser_manager = None
            return
        # zendriver's ``Tab.closed`` means "no websocket attached" — true for
        # the untouched initial ``about:blank`` tab — so it cannot detect
        # closed tabs. Ask the service for the resynced live tab list instead.
        service = get_browser_service(browser)
        live_tabs = await service.tabs()
        if live_tabs is None or all(
            str(getattr(tab, "url", "") or "").strip().lower() in self._BLANK_URLS
            for tab in live_tabs
        ):
            await self.search_browser_manager.stop()
            self.search_browser_manager = None
            return
        await service.close_blank_tabs()

    async def clear_browser_data(self) -> int:
        if not self.separate:
            return 0
        if self.search_browser_manager is not None:
            await self.search_browser_manager.stop()
            self.search_browser_manager = None
        return clear_browser_profile_data(self.settings.search_profile_dir)

    @staticmethod
    async def _is_browser_alive(browser) -> bool:
        try:
            return await get_browser_service(browser).ping()
        except Exception:
            return False


def _overlay_bundle_script() -> str:
    try:
        return _OVERLAY_BUNDLE_PATH.read_text(encoding="utf-8")
    except OSError:
        logger.debug("Unable to read Synthesix overlay bundle", exc_info=True)
        return ""


def _tool_version() -> str:
    try:
        return importlib.metadata.version("synthesix")
    except importlib.metadata.PackageNotFoundError:
        return "development"


def _stored_path(path: Path, base_dir: Path) -> str:
    path = Path(path).resolve()
    try:
        return path.relative_to(base_dir.resolve()).as_posix()
    except ValueError:
        return str(path)


def _slugify(text: str, *, fallback: str = "export", max_length: int = 60) -> str:
    normalized = unicodedata.normalize("NFKD", str(text or ""))
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_only).strip("-").lower()
    return slug[:max_length].strip("-") or fallback


def _default_capture_name(captured_at: str) -> str:
    compact = (
        str(captured_at or "")
        .replace("T", "_")
        .replace(":", "-")
        .split(".", 1)[0]
        .replace("+00-00", "")
    )
    return f"screenshot_{compact or 'capture'}"


def _default_archive_name(captured_at: str) -> str:
    return _default_capture_name(captured_at).replace(
        "screenshot_",
        "page_archive_",
        1,
    )


def _normalize_tab_url(url: str | None) -> str:
    return (url or "").split("#", 1)[0]


def _prepare_base_query(
    original_query: str,
    *,
    automatic_dorks: bool = True,
) -> str:
    if automatic_dorks and not is_advanced_query(original_query):
        return smart_parse(original_query)
    return original_query


async def _open_tabs(browser: uc.Browser):
    """Live page tabs via the shared :class:`BrowserService`.

    Kept as a module seam: tests patch it to inject fake tab inventories.
    """
    return await get_browser_service(browser).tabs()


def _is_home_tab(tab, index_url: str) -> bool:
    return _normalize_tab_url(getattr(tab, "url", None)) == index_url


async def _consume_home_tab_action(tab):
    """Light per-tick probe: consume one queued action and report the data
    versions currently applied by the page. Payload transfers happen in
    :func:`_push_home_tab_data`, and only when a version differs (T-003)."""
    return await eval_js(
        tab,
        """
        (() => {
            if (
                !window.synthesixHome ||
                typeof window.synthesixHome.consumeAction !== "function"
            ) {
                return { ready: false, action: null };
            }
            if (window.name !== "synthesix-home") {
                window.name = "synthesix-home";
            }
            return {
                ready: true,
                action: window.synthesixHome.consumeAction(),
                historyVersion:
                    window.synthesixHome.historyVersion ?? null,
                investigationsVersion:
                    window.synthesixHome.investigationsVersion ?? null
            };
        })()
        """,
        category="eval_home",
    )


async def _push_home_tab_data(
    tab,
    history_json: str | None = None,
    history_version: str = "",
    investigations_json: str | None = None,
    investigations_version: str = "",
) -> None:
    """Ship history/investigations payloads to a home tab.

    Each part is only embedded when its version diverged, so the steady
    state costs nothing beyond the light probe above."""
    parts = []
    transferred = 0
    if history_json is not None:
        parts.append(
            f"""
                window.synthesixHome.setHistory({history_json});
                window.synthesixHome.historyVersion = {json.dumps(history_version)};
            """
        )
        transferred += len(history_json)
    if investigations_json is not None:
        parts.append(
            f"""
                if (typeof window.synthesixHome.setInvestigations === "function") {{
                    window.synthesixHome.setInvestigations({investigations_json});
                    window.synthesixHome.investigationsVersion = (
                        {json.dumps(investigations_version)}
                    );
                }}
            """
        )
        transferred += len(investigations_json)
    if not parts:
        return

    observability.observe_bytes("eval_home", transferred)
    body = "".join(parts)
    await eval_js(
        tab,
        f"""
        (() => {{
            if (!window.synthesixHome) {{
                return;
            }}
{body}
        }})()
        """,
        category="eval_home",
    )


def _history_signature(settings: AppSettings):
    try:
        stat = settings.history_json_path.stat()
    except OSError:
        return None
    return stat.st_mtime_ns, stat.st_size


def _cached_history_payload(settings: AppSettings, cache: dict) -> tuple[str, str]:
    signature = _history_signature(settings)
    if cache.get("signature", _MISSING_HISTORY_SIGNATURE) != signature:
        cache["signature"] = signature
        cache["json"] = json.dumps(load_search_history(limit=settings.default_history_limit))
        cache["version"] = "" if signature is None else f"{signature[0]}:{signature[1]}"
    return cache["json"], cache["version"]


def _investigation_payload(service: InvestigationService) -> tuple[str, str]:
    payload = json.dumps(
        service.list_payload(include_archived=True),
        ensure_ascii=True,
        sort_keys=True,
    )
    version = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return payload, version


def parse_cli_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Start Synthesix browser-driven multi-engine search.",
    )
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "--quiet",
        action="store_true",
        help="Only show warnings and errors.",
    )
    verbosity.add_argument(
        "--verbose",
        action="store_true",
        help="Show debug logs.",
    )
    parser.add_argument(
        "--debug-html",
        action="store_true",
        help="Keep raw search-engine HTML pages in history/debug_pages/.",
    )
    return parser.parse_args(argv)


def _log_level_from_args(args) -> int:
    if args.verbose:
        return logging.DEBUG
    if args.quiet:
        return logging.WARNING
    return logging.INFO


def configure_logging(args) -> None:
    logging.basicConfig(
        level=_log_level_from_args(args),
        format="%(levelname)s:%(name)s:%(message)s",
    )


def apply_cli_runtime_overrides(args) -> None:
    if args.debug_html:
        os.environ["SYNTHESIX_DEBUG_HTML"] = "1"


def configure_event_loop_policy() -> None:
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def _consume_page_tab_action(tab):
    return await eval_js(
        tab,
        """
        (() => {
            if (
                !window.synthesixPage ||
                typeof window.synthesixPage.consumeAction !== "function"
            ) {
                return null;
            }
            return window.synthesixPage.consumeAction();
        })()
        """,
        category="eval_page",
    )


async def _consume_settings_change(tab):
    return await eval_js(
        tab,
        """
        (() => {
            if (
                !window.synthesixI18n ||
                typeof window.synthesixI18n.consumeSettingsChange !== "function"
            ) {
                return null;
            }
            return window.synthesixI18n.consumeSettingsChange();
        })()
        """,
        category="eval_settings",
    )


async def _apply_settings_to_tabs(tabs, settings: dict, source_tab=None) -> None:
    settings_json = json.dumps(settings, ensure_ascii=True)
    for tab in tabs:
        if tab is source_tab or _is_external_web_tab(tab):
            continue
        await eval_js(
            tab,
            f"""
            (() => {{
                if (
                    window.synthesixI18n &&
                    typeof window.synthesixI18n.applySettings === "function"
                ) {{
                    window.synthesixI18n.applySettings({settings_json});
                }}
            }})()
            """,
            category="eval_settings",
        )


def _is_external_web_tab(tab) -> bool:
    try:
        return urlsplit(str(getattr(tab, "url", "") or "")).scheme in {
            "http",
            "https",
        }
    except ValueError:
        return False


_OVERLAY_MODES = {"auto", "cdp", "extension"}
_EXTENSION_OVERLAY_ACTION = "extension_overlay_action"
_EXTENSION_SPIKE_ACTION = "extension_spike_message"
_EXTENSION_CONTEXT_UPDATE = "synthesix:context-update"
_EXTENSION_BUTTON_STATUS = "synthesix:button-status"


def _overlay_mode(settings: AppSettings | object) -> str:
    mode = str(getattr(settings, "overlay_mode", "auto") or "auto").strip().lower()
    if mode not in _OVERLAY_MODES:
        logger.warning("Invalid SYNTHESIX_OVERLAY_MODE=%r; using auto.", mode)
        return "auto"
    return mode


def _use_extension_overlay(settings: AppSettings | object, available: bool) -> bool:
    mode = _overlay_mode(settings)
    return available and mode in {"auto", "extension"}


def _use_cdp_overlay(settings: AppSettings | object, available: bool) -> bool:
    mode = _overlay_mode(settings)
    return mode == "cdp" or (mode == "auto" and not available)


def _http_url(value: object) -> str:
    raw = str(value or "").strip()
    if len(raw) > 4096:
        return ""
    try:
        parts = urlsplit(raw)
    except ValueError:
        return ""
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return ""
    return raw


def _extension_overlay_message(dispatch: Mapping) -> Mapping | None:
    if dispatch.get("action") != _EXTENSION_OVERLAY_ACTION:
        return None
    payload = dispatch.get("payload")
    if not isinstance(payload, Mapping):
        logger.debug("Discarding extension overlay action without payload")
        return None
    message = payload.get("message")
    if not isinstance(message, Mapping):
        logger.debug("Discarding extension overlay action without message")
        return None
    if message.get("type") != "synthesix:overlay-action":
        logger.debug("Discarding unexpected extension message: %r", message)
        return None
    action = message.get("action")
    if not isinstance(action, Mapping):
        logger.debug("Discarding extension overlay action without action body")
        return None
    if not isinstance(action.get("action"), str) or not action.get("action"):
        logger.debug("Discarding extension overlay action without action name")
        return None
    url = _http_url(message.get("href"))
    if not url:
        sender = payload.get("sender")
        if isinstance(sender, Mapping):
            url = _http_url(sender.get("tabUrl") or sender.get("url"))
    if not url:
        logger.debug("Discarding extension overlay action with invalid URL")
        return None
    return message


def _extension_overlay_tab_id(dispatch: Mapping, message: Mapping) -> int | None:
    candidates = [dispatch.get("tabId")]
    payload = dispatch.get("payload")
    if isinstance(payload, Mapping):
        sender = payload.get("sender")
        if isinstance(sender, Mapping):
            candidates.append(sender.get("tabId"))
    candidates.append(message.get("tabId"))
    for candidate in candidates:
        if isinstance(candidate, bool):
            continue
        if isinstance(candidate, int) and candidate >= 0:
            return candidate
    return None


def _extension_overlay_context_payload(
    investigation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    investigation = investigation or {}
    tagset_properties = {
        tag: [
            str(property_.get("key", "") or "")
            for property_ in zeroneurone_tagset_suggested_properties(tag)
            if str(property_.get("key", "") or "").strip()
        ]
        for tag in ZERONEURONE_TAGSETS
    }
    tagset_property_types = {
        tag: {
            str(property_.get("key", "") or ""): str(
                property_.get("type", "") or ""
            )
            for property_ in zeroneurone_tagset_suggested_properties(tag)
            if str(property_.get("key", "") or "").strip()
        }
        for tag in ZERONEURONE_TAGSETS
    }
    return {
        "id": str(investigation.get("id", "")),
        "title": str(investigation.get("title", "")),
        "baseTagsets": list(ZERONEURONE_TAGSETS),
        "tagsetProperties": tagset_properties,
        "tagsetPropertyTypes": tagset_property_types,
        "existingTags": sorted(
            {
                str(tag).strip()
                for tag in (
                    *investigation.get("tags", []),
                    *(
                        tag
                        for entity in investigation.get("graph_entities", [])
                        for tag in entity.get("tags", [])
                    ),
                )
                if str(tag).strip()
            },
            key=str.casefold,
        ),
        "graphEntities": [
            {
                "id": str(entity.get("id", "")),
                "label": str(entity.get("label", "")),
                "tags": [
                    str(tag)
                    for tag in entity.get("tags", [])
                    if str(tag).strip()
                ],
                "propertyKeys": [
                    str(key)
                    for key in (
                        entity.get("properties", {})
                        if isinstance(entity.get("properties", {}), Mapping)
                        else {}
                    )
                    if str(key).strip()
                ],
            }
            for entity in investigation.get("graph_entities", [])
            if str(entity.get("id", "")).strip()
        ],
    }


def _extension_overlay_context_version(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("utf-8")
    ).hexdigest()


async def _sync_extension_overlay_context(
    service: BrowserService,
    extension_id: str | None,
    payload: Mapping[str, Any],
    cache: dict[str, str],
) -> bool:
    version = _extension_overlay_context_version(payload)
    if cache.get("version") == version:
        return False
    sent = await service.send_extension_backend_message(
        extension_id,
        {
            "type": _EXTENSION_CONTEXT_UPDATE,
            "payload": payload,
        },
    )
    if sent:
        cache["version"] = version
    return sent


async def _set_extension_overlay_button_status(
    service: BrowserService,
    extension_id: str | None,
    tab_id: int | None,
    *,
    kind: str,
    state: str,
    message: str,
) -> bool:
    if not isinstance(tab_id, int) or isinstance(tab_id, bool):
        return False
    return await service.send_extension_backend_message(
        extension_id,
        {
            "type": _EXTENSION_BUTTON_STATUS,
            "tabId": tab_id,
            "kind": kind,
            "state": state,
            "message": message,
        },
    )


async def _set_overlay_save_status(
    service: BrowserService,
    settings: AppSettings,
    extension_id: str | None,
    result: Mapping[str, Any],
    message: str,
    *,
    is_error: bool = False,
) -> None:
    sent = False
    if _use_extension_overlay(settings, True):
        sent = await _set_extension_overlay_button_status(
            service,
            extension_id,
            result.get("_extension_tab_id"),
            kind="save",
            state="error" if is_error else "saved",
            message=message,
        )
    if not sent:
        await _set_save_overlay_status(
            result.get("_source_tab"),
            message,
            is_error=is_error,
        )


async def _set_overlay_capture_status(
    service: BrowserService,
    settings: AppSettings,
    extension_id: str | None,
    result: Mapping[str, Any],
    message: str,
    *,
    is_error: bool = False,
) -> None:
    sent = False
    if _use_extension_overlay(settings, True):
        sent = await _set_extension_overlay_button_status(
            service,
            extension_id,
            result.get("_extension_tab_id"),
            kind="capture",
            state="error" if is_error else "captured",
            message=message,
        )
    if not sent:
        await _set_evidence_overlay_status(
            result.get("_source_tab"),
            message,
            is_error=is_error,
        )


async def _set_overlay_archive_status(
    service: BrowserService,
    settings: AppSettings,
    extension_id: str | None,
    result: Mapping[str, Any],
    message: str,
    *,
    is_error: bool = False,
) -> None:
    sent = False
    if _use_extension_overlay(settings, True):
        sent = await _set_extension_overlay_button_status(
            service,
            extension_id,
            result.get("_extension_tab_id"),
            kind="archive",
            state="error" if is_error else "archived",
            message=message,
        )
    if not sent:
        await _set_archive_overlay_status(
            result.get("_source_tab"),
            message,
            is_error=is_error,
        )


async def _tab_has_extension_token(tab, token: str) -> bool:
    if not token:
        return False
    matched = await eval_js(
        tab,
        f"""
        (() => (
            document.documentElement.dataset.synthesixOverlayToken
            === {json.dumps(token)}
        ))()
        """,
        category="eval_overlay",
    )
    return bool(matched)


async def _resolve_extension_source_tab(
    tabs: list,
    message: Mapping,
) -> object | None:
    token = str(message.get("sourceToken", "") or "")
    if token:
        for tab in tabs:
            if _is_external_web_tab(tab) and await _tab_has_extension_token(tab, token):
                return tab

    url = _http_url(message.get("href"))
    matches = [
        tab
        for tab in tabs
        if _is_external_web_tab(tab)
        and _normalize_tab_url(getattr(tab, "url", None)) == _normalize_tab_url(url)
    ]
    if len(matches) == 1:
        return matches[0]
    if matches:
        logger.warning(
            "Ambiguous extension overlay source for %s (%s tabs); action discarded.",
            url,
            len(matches),
        )
    return None


async def _normalize_dispatch_action(dispatch: dict, tabs: list) -> dict | None:
    if dispatch.get("action") == _EXTENSION_SPIKE_ACTION:
        payload = dispatch.get("payload")
        message = payload.get("message") if isinstance(payload, Mapping) else None
        message_type = message.get("type") if isinstance(message, Mapping) else None
        logger.debug("Ignoring internal extension message type=%r", message_type)
        return None
    if dispatch.get("action") != _EXTENSION_OVERLAY_ACTION:
        return dispatch

    message = _extension_overlay_message(dispatch)
    if message is None:
        return None
    action = dict(message["action"])
    # `focus_home` is a global navigation request used when no investigation is
    # selected. It must not depend on resolving the external page target first.
    if action.get("action") == "focus_home":
        return action
    source_tab = await _resolve_extension_source_tab(tabs, message)
    if source_tab is None:
        logger.warning(
            "Unable to resolve extension overlay source tab for %s",
            message.get("href"),
        )
        return None
    action["_source_tab"] = source_tab
    action["_extension_tab_id"] = _extension_overlay_tab_id(dispatch, message)
    return action


_OVERLAY_BLOCKED_HOST_FRAGMENTS = ("lens.google.", "maps.google.")


def _overlay_focus_guard_script() -> str:
    """JS armed early (before any page script) so it wins the DOM event
    ordering race against third-party SDKs.

    Some hosts (observed on TikTok's video player) run their own keyboard/
    focus-trap code that steals focus back from the overlay's Shadow DOM
    inputs, or preventDefault()s keys meant to be typed there. A script
    injected the normal way (`tab.evaluate()` after the page has loaded)
    always registers its listeners after the host page's own scripts, so it
    loses that race. `Page.addScriptToEvaluateOnNewDocument` runs before any
    script on the frame, guaranteeing this one is registered first — which
    matters because same-node listener order follows registration order.
    """
    return """
    (() => {
        if (window.__synthesixFocusGuardInstalled) {
            return;
        }
        window.__synthesixFocusGuardInstalled = true;

        const isOverlayNode = (node) => {
            while (node) {
                const tag = node.tagName;
                if (typeof tag === "string" && tag.startsWith("SX-OVERLAY-")) {
                    return true;
                }
                node = node.getRootNode
                    ? (node.getRootNode().host || node.parentNode)
                    : node.parentNode;
            }
            return false;
        };

        try {
            const nativeFocus = HTMLElement.prototype.focus;
            HTMLElement.prototype.focus = function synthesixGuardedFocus(...args) {
                if (isOverlayNode(document.activeElement) && !isOverlayNode(this)) {
                    return;
                }
                return nativeFocus.apply(this, args);
            };
        } catch (_error) {}

        const isOverlayFieldEvent = (event) => {
            const path = event.composedPath ? event.composedPath() : [];
            const target = path[0];
            const tag = target && target.tagName;
            if (tag !== "INPUT" && tag !== "TEXTAREA" && tag !== "SELECT") {
                return false;
            }
            return path.some((node) => {
                const nodeTag = node && node.tagName;
                return typeof nodeTag === "string" && nodeTag.startsWith("SX-OVERLAY-");
            });
        };

        for (const type of ["keydown", "keypress", "keyup"]) {
            window.addEventListener(
                type,
                (event) => {
                    if (isOverlayFieldEvent(event)) {
                        // stopImmediatePropagation, not just stopPropagation:
                        // this guard is armed before any page script runs, so
                        // if the host page also binds its own hotkey handler
                        // on `window` (same node), it registers *after* us —
                        // stopPropagation alone would still let that later
                        // same-node listener run and preventDefault() the
                        // keystroke.
                        event.stopImmediatePropagation();
                        event.stopPropagation();
                    }
                },
                true,
            );
        }
    })();
    """


async def _arm_overlay_focus_guard(service: BrowserService, tab) -> None:
    """Register the focus-guard script for future navigations of ``tab``.

    Best-effort and idempotent per tab (registry held by the service), since
    the overlay still works on most hosts without it.
    """
    await service.arm_new_document_script(tab, _overlay_focus_guard_script())


def _overlay_injection_blocked(url: str) -> bool:
    """Skip overlay injection on surfaces where it breaks or crashes Chrome.

    Google Lens and Maps are heavy first-party apps (and Lens powers Chrome's
    built-in image search); injecting the Synthesix overlay there has crashed
    the browser, so we leave those pages untouched.
    """
    try:
        parts = urlsplit(str(url or ""))
    except ValueError:
        return False
    host = parts.netloc.casefold()
    path = parts.path.casefold()
    if any(fragment in host for fragment in _OVERLAY_BLOCKED_HOST_FRAGMENTS):
        return True
    if ".google." in host and (path == "/maps" or path.startswith("/maps/")):
        return True
    return False


async def _install_and_consume_save_overlay(
    service: BrowserService,
    tab,
    investigation: dict | None = None,
):
    if _overlay_injection_blocked(getattr(tab, "url", "")):
        return None
    await _arm_overlay_focus_guard(service, tab)
    investigation = investigation or {}
    tagsets_json = json.dumps(list(ZERONEURONE_TAGSETS), ensure_ascii=True)
    tagset_properties_json = json.dumps(
        {
            tag: [
                str(property_.get("key", "") or "")
                for property_ in zeroneurone_tagset_suggested_properties(tag)
                if str(property_.get("key", "") or "").strip()
            ]
            for tag in ZERONEURONE_TAGSETS
        },
        ensure_ascii=True,
    )
    tagset_property_types_json = json.dumps(
        {
            tag: {
                str(property_.get("key", "") or ""): str(
                    property_.get("type", "") or ""
                )
                for property_ in zeroneurone_tagset_suggested_properties(tag)
                if str(property_.get("key", "") or "").strip()
            }
            for tag in ZERONEURONE_TAGSETS
        },
        ensure_ascii=True,
    )
    context_json = json.dumps(
        {
            "id": str(investigation.get("id", "")),
            "title": str(investigation.get("title", "")),
            "existingTags": sorted(
                {
                    str(tag).strip()
                    for tag in (
                        *investigation.get("tags", []),
                        *(
                            tag
                            for entity in investigation.get(
                                "graph_entities",
                                [],
                            )
                            for tag in entity.get("tags", [])
                        ),
                    )
                    if str(tag).strip()
                },
                key=str.casefold,
            ),
            "graphEntities": [
                {
                    "id": str(entity.get("id", "")),
                    "label": str(entity.get("label", "")),
                    "tags": [
                        str(tag)
                        for tag in entity.get("tags", [])
                        if str(tag).strip()
                    ],
                    "propertyKeys": [
                        str(key)
                        for key in (
                            entity.get("properties", {})
                            if isinstance(entity.get("properties", {}), Mapping)
                            else {}
                        )
                        if str(key).strip()
                    ],
                }
                for entity in investigation.get("graph_entities", [])
                if str(entity.get("id", "")).strip()
            ],
        },
        ensure_ascii=True,
    )
    # The overlay bundle is large; embedding it in the eval on every poll means
    # the host page re-parses ~100 KB on its main thread each cycle. On an
    # already-busy renderer (e.g. Google Lens active in the side panel) this
    # repeated parse freezes the page. Only ship the bundle when the page does
    # not already have it loaded.
    overlay_already_loaded = bool(
        await eval_js(
            tab,
            "!!window.SynthesixOverlay",
            category="eval_overlay",
        )
    )
    overlay_bundle_json = json.dumps(
        "" if overlay_already_loaded else _overlay_bundle_script(),
        ensure_ascii=True,
    )
    observability.observe_bytes(
        "eval_overlay",
        len(overlay_bundle_json) + len(context_json),
    )
    return await eval_js(
        tab,
        f"""
            (() => {{
                const context = {context_json};
                const entityTagsets = {tagsets_json};
                const tagsetProperties = {tagset_properties_json};
                const tagsetPropertyTypes = {tagset_property_types_json};
                const hostId = "__synthesix-save-overlay";
                const queueAction = (queuedAction) => {{
                    (window.__synthesixActions =
                        window.__synthesixActions || []).push(queuedAction);
                }};
                const overlayBundle = {overlay_bundle_json};
                if (!window.SynthesixOverlay && overlayBundle) {{
                    try {{
                        Function(overlayBundle)();
                    }} catch (_error) {{
                        // The legacy inline overlay below remains the fallback.
                    }}
                }}
                let host = document.getElementById(hostId);
                if (!host) {{
                    host = document.createElement("sx-overlay-root");
                    host.id = hostId;
                    host.setAttribute("data-synthesix-overlay-root", "");
                    try {{
                        host.collapsed = (
                            window.localStorage.getItem(
                                "synthesix:external-overlay-collapsed"
                            ) === "1"
                        );
                        host.toggleAttribute("collapsed", host.collapsed);
                    }} catch (_error) {{
                        host.collapsed = false;
                    }}
                    const button = document.createElement("sx-overlay-action");
                    button.setAttribute("data-synthesix-save-page", "");
                    button.setAttribute("slot", "toolbar");
                    button.variant = "primary";
                    button.icon = "mark";
                    button.label = "Save page";
                    button.setAttribute("label", "Save page");
                    button.ariaText = (
                        "Save page to active Synthesix investigation"
                    );
                    button.setAttribute(
                        "aria-text",
                        "Save page to active Synthesix investigation"
                    );
                    button.textContent = "Save page";
                    host.__synthesixSaveButton = button;
                    host.__synthesixPagePayload = () => ({{
                        url: window.location.href,
                        title: document.title || window.location.hostname,
                        description: (
                            document.querySelector(
                                'meta[name="description" i]'
                            )?.content || ""
                        ),
                        referrer: document.referrer || "",
                        browserContext: {{
                            viewportWidth: window.innerWidth,
                            viewportHeight: window.innerHeight,
                            devicePixelRatio: window.devicePixelRatio || 1,
                            language: navigator.language || "",
                            userAgent: navigator.userAgent || ""
                        }}
                    }});

                    host.__synthesixSetButtonState = (state, text) => {{
                        if (typeof host.setSaveButtonState === "function") {{
                            host.setSaveButtonState(state, text);
                        }}
                    }};
                    button.addEventListener("click", () => {{
                        if (!host.dataset.investigationId) {{
                            queueAction({{
                                action: "focus_home"
                            }});
                            return;
                        }}
                        if (button.dataset.state === "saved") {{
                            return;
                        }}
                        host.__synthesixSetButtonState("saving", "Saving...");
                        queueAction({{
                            action: "save_page_to_investigation",
                            investigationId: host.dataset.investigationId,
                            page: host.__synthesixPagePayload()
                        }});
                    }});

                    const archiveButton = document.createElement("sx-overlay-action");
                    archiveButton.setAttribute("data-synthesix-archive", "");
                    archiveButton.setAttribute("slot", "toolbar");
                    archiveButton.variant = "archive";
                    archiveButton.setAttribute("variant", "archive");
                    archiveButton.icon = "archive";
                    archiveButton.setAttribute("icon", "archive");
                    archiveButton.iconOnly = true;
                    archiveButton.setAttribute("icon-only", "");
                    host.__synthesixArchiveButton = archiveButton;
                    host.__synthesixSetArchiveState = (
                        state,
                        tooltip = "Save page with HTML archive"
                    ) => {{
                        if (typeof host.setArchiveState === "function") {{
                            host.setArchiveState(state, tooltip);
                        }}
                    }};
                    archiveButton.addEventListener("click", () => {{
                        if (!host.dataset.investigationId) {{
                            queueAction({{
                                action: "focus_home"
                            }});
                            return;
                        }}
                        host.__synthesixSetArchiveState(
                            "archiving",
                            "Saving HTML archive..."
                        );
                        queueAction({{
                            action: "archive_page_to_investigation",
                            investigationId: host.dataset.investigationId,
                            page: host.__synthesixPagePayload()
                        }});
                    }});

                    const captureButton = document.createElement("sx-overlay-action");
                    captureButton.setAttribute("data-synthesix-capture", "");
                    captureButton.setAttribute("slot", "toolbar");
                    captureButton.variant = "capture";
                    captureButton.setAttribute("variant", "capture");
                    captureButton.icon = "camera";
                    captureButton.setAttribute("icon", "camera");
                    captureButton.iconOnly = true;
                    captureButton.setAttribute("icon-only", "");
                    host.__synthesixCaptureButton = captureButton;

                    const captureMenu = document.createElement(
                        "sx-overlay-capture-menu"
                    );
                    captureMenu.setAttribute("data-synthesix-capture-menu", "");
                    host.__synthesixDefaultCaptureName = () => {{
                        const now = new Date();
                        const pad = (value) => String(value).padStart(2, "0");
                        return (
                            `screenshot_${{now.getFullYear()}}-`
                            + `${{pad(now.getMonth() + 1)}}-`
                            + `${{pad(now.getDate())}}_`
                            + `${{pad(now.getHours())}}-`
                            + `${{pad(now.getMinutes())}}-`
                            + `${{pad(now.getSeconds())}}`
                        );
                    }};
                    captureMenu.addEventListener(
                        "synthesix-capture-choice",
                        (event) => {{
                            const detail = event.detail || {{}};
                            const scope = detail.scope || "";
                            const captureName = detail.captureName || "";
                            const attach = detail.attach || null;
                            if (!host.dataset.investigationId) {{
                                queueAction({{
                                    action: "focus_home"
                                }});
                                return;
                            }}
                            if (scope === "viewport") {{
                                host.__synthesixQueueCapture("viewport", {{
                                    x: window.scrollX,
                                    y: window.scrollY,
                                    width: window.innerWidth,
                                    height: window.innerHeight
                                }}, captureName, attach);
                            }} else if (scope === "region") {{
                                host.__synthesixStartRegionSelection(
                                    captureName,
                                    attach
                                );
                            }}
                        }}
                    );

                    host.__synthesixSetCaptureState = (
                        state,
                        tooltip = "Capture screenshot"
                    ) => {{
                        if (typeof host.setCaptureState === "function") {{
                            host.setCaptureState(state, tooltip);
                        }}
                    }};
                    host.__synthesixQueueCapture = (
                        scope,
                        selection,
                        captureName,
                        attach
                    ) => {{
                        host.__synthesixSetCaptureState(
                            "capturing",
                            "Capturing evidence..."
                        );
                        host.style.display = "none";
                        window.requestAnimationFrame(() => {{
                            window.requestAnimationFrame(() => {{
                                queueAction({{
                                    action: "capture_evidence_to_investigation",
                                    investigationId: host.dataset.investigationId,
                                    captureScope: scope,
                                    captureName: String(captureName || "").trim(),
                                    selection,
                                    attach: attach || null,
                                    page: host.__synthesixPagePayload()
                                }});
                                if (
                                    typeof captureMenu.reset === "function"
                                ) {{
                                    captureMenu.reset();
                                }}
                            }});
                        }});
                    }};
                    host.__synthesixStartRegionSelection = (
                        captureName,
                        attach
                    ) => {{
                        host.style.display = "none";
                        const existing = document.getElementById(
                            "__synthesix-evidence-selection"
                        );
                        if (existing) {{
                            existing.remove();
                        }}
                        const selectionBox = document.createElement(
                            "sx-overlay-selection-box"
                        );
                        selectionBox.id = "__synthesix-evidence-selection";
                        selectionBox.addEventListener(
                            "synthesix-region-selected",
                            (event) => {{
                                selectionBox.remove();
                                const region = event.detail || {{}};
                                host.__synthesixQueueCapture(
                                    "region",
                                    {{
                                        x: region.x,
                                        y: region.y,
                                        width: region.width,
                                        height: region.height
                                    }},
                                    captureName,
                                    attach
                                );
                            }}
                        );
                        selectionBox.addEventListener(
                            "synthesix-region-cancel",
                            () => {{
                                selectionBox.remove();
                                host.style.display = "block";
                            }}
                        );
                        (document.documentElement || document.body).appendChild(
                            selectionBox
                        );
                    }};

                    captureButton.addEventListener("click", () => {{
                        if (!host.dataset.investigationId) {{
                            queueAction({{
                                action: "focus_home"
                            }});
                            return;
                        }}
                        const nextOpen = !captureMenu.hasAttribute("open");
                        captureMenu.open = nextOpen;
                        captureMenu.toggleAttribute("open", nextOpen);
                        if (nextOpen) {{
                            captureMenu.ensureCaptureName?.(
                                host.__synthesixDefaultCaptureName()
                            );
                        }}
                    }});
                    const entityMenu = document.createElement(
                        "sx-overlay-entity-menu"
                    );
                    entityMenu.baseTagsets = entityTagsets;
                    entityMenu.tagsetProperties = tagsetProperties;
                    entityMenu.tagsetPropertyTypes = tagsetPropertyTypes;
                    captureMenu.tagsetProperties = tagsetProperties;
                    host.__synthesixSetEntityTagsets = (tags) => {{
                        entityMenu.existingTags = Array.isArray(tags) ? tags : [];
                    }};
                    host.__synthesixSetGraphEntities = (graphEntities) => {{
                        const entities = (
                            Array.isArray(graphEntities) ? graphEntities : []
                        );
                        entityMenu.graphEntities = entities;
                        captureMenu.graphEntities = entities;
                    }};
                    entityMenu.addEventListener(
                        "synthesix-entity-create",
                        (event) => {{
                            const detail = event.detail || {{}};
                            if (!host.dataset.investigationId) {{
                                queueAction({{
                                    action: "focus_home"
                                }});
                                return;
                            }}
                            queueAction({{
                                action: "create_graph_entity_from_selection",
                                investigationId: host.dataset.investigationId,
                                entity: {{
                                    label: detail.label,
                                    category: detail.category
                                }},
                                page: host.__synthesixPagePayload()
                            }});
                        }}
                    );
                    entityMenu.addEventListener(
                        "synthesix-entity-attach",
                        (event) => {{
                            const detail = event.detail || {{}};
                            if (!host.dataset.investigationId) {{
                                queueAction({{
                                    action: "focus_home"
                                }});
                                return;
                            }}
                            queueAction({{
                                action: "attach_selection_to_graph_entity",
                                investigationId: host.dataset.investigationId,
                                entityId: detail.entityId,
                                property: {{
                                    key: detail.propertyKey,
                                    value: detail.label,
                                    property_type: detail.propertyType || ""
                                }},
                                page: host.__synthesixPagePayload()
                            }});
                        }}
                    );
                    host.addEventListener(
                        "synthesix-overlay-toggle",
                        (event) => {{
                            const collapsed = Boolean(
                                event.detail && event.detail.collapsed
                            );
                            try {{
                                window.localStorage.setItem(
                                    "synthesix:external-overlay-collapsed",
                                    collapsed ? "1" : "0"
                                );
                            }} catch (_error) {{}}
                            if (collapsed) {{
                                if (typeof captureMenu.reset === "function") {{
                                    captureMenu.reset();
                                }}
                                captureMenu.open = false;
                                captureMenu.removeAttribute("open");
                            }}
                        }}
                    );
                    host.append(
                        button,
                        archiveButton,
                        captureButton,
                        captureMenu,
                        entityMenu
                    );
                    (document.documentElement || document.body).appendChild(host);
                }}

                const pageKey = `${{context.id}}|${{window.location.href}}`;
                const contextChanged = host.dataset.pageKey !== pageKey;
                host.dataset.investigationId = context.id;
                host.dataset.pageKey = pageKey;
                if (host.__synthesixSetGraphEntities) {{
                    host.__synthesixSetGraphEntities(
                        context.graphEntities || []
                    );
                }}
                if (host.__synthesixSetEntityTagsets) {{
                    host.__synthesixSetEntityTagsets(
                        context.existingTags || []
                    );
                }}
                const button = (
                    host.__synthesixSaveButton
                    || host.querySelector(
                        "[data-synthesix-save-page]"
                    )
                );
                if (!button) {{
                    return null;
                }}
                const statusUntil = Number(host.dataset.statusUntil || 0);
                const captureStatusUntil = Number(
                    host.dataset.captureStatusUntil || 0
                );
                const archiveStatusUntil = Number(
                    host.dataset.archiveStatusUntil || 0
                );
                if (contextChanged) {{
                    host.dataset.saved = "0";
                    host.dataset.statusUntil = "0";
                    if (context.id) {{
                        button.title = (
                            `Save this page to "${{context.title}}"`
                        );
                        button.titleText = button.title;
                        button.setAttribute("title-text", button.title);
                        host.__synthesixSetButtonState("idle", "Save page");
                    }} else {{
                        button.title = (
                            "Open Synthesix to select an investigation before saving this page"
                        );
                        button.titleText = button.title;
                        button.setAttribute("title-text", button.title);
                        host.__synthesixSetButtonState(
                            "idle",
                            "Select investigation"
                        );
                    }}
                    host.__synthesixSetCaptureState(
                        "idle",
                        "Capture screenshot"
                    );
                    host.__synthesixSetArchiveState(
                        "idle",
                        "Save page with HTML archive"
                    );
                }} else if (
                    button.dataset.state === "error"
                    && Date.now() >= statusUntil
                ) {{
                    button.title = context.id
                        ? `Save this page to "${{context.title}}"`
                        : "Open Synthesix to select an investigation before saving this page";
                    button.titleText = button.title;
                    button.setAttribute("title-text", button.title);
                    host.__synthesixSetButtonState("idle", "Save page");
                }}
                if (
                    ["captured", "error"].includes(
                        (
                            host.__synthesixCaptureButton
                            || host.querySelector(
                                "[data-synthesix-capture]"
                            )
                        )?.dataset.state
                    )
                    && Date.now() >= captureStatusUntil
                ) {{
                    host.__synthesixSetCaptureState(
                        "idle",
                        "Capture screenshot"
                    );
                }}
                if (
                    ["archived", "error"].includes(
                        (
                            host.__synthesixArchiveButton
                            || host.querySelector(
                                "[data-synthesix-archive]"
                            )
                        )?.dataset.state
                    )
                    && Date.now() >= archiveStatusUntil
                ) {{
                    host.__synthesixSetArchiveState(
                        "idle",
                        "Save page with HTML archive"
                    );
                }}

                if (
                    context.id
                    && host.dataset.observationKey !== pageKey
                ) {{
                    host.dataset.observationKey = pageKey;
                    queueAction({{
                        action: "observe_saved_page",
                        investigationId: context.id,
                        page: {{
                            url: window.location.href
                        }}
                    }});
                }}

                const queued = window.__synthesixActions;
                return queued && queued.length ? queued.shift() : null;
            }})()
            """,
        category="eval_overlay",
    )


async def _set_save_overlay_status(
    tab,
    message: str,
    *,
    is_error: bool = False,
) -> None:
    if tab is None:
        return
    await eval_js(
        tab,
        f"""
        (() => {{
            const host = document.getElementById("__synthesix-save-overlay");
            const button = (
                host?.__synthesixSaveButton
                || host?.querySelector(
                    "[data-synthesix-save-page]"
                )
            );
            if (!button || !host.__synthesixSetButtonState) {{
                return;
            }}
            const isError = {json.dumps(is_error)};
            host.dataset.saved = isError ? "0" : "1";
            button.title = {json.dumps(message)};
            button.titleText = button.title;
            button.setAttribute("title-text", button.title);
            host.__synthesixSetButtonState(
                isError ? "error" : "saved",
                {json.dumps(message)}
            );
            host.dataset.statusUntil = isError
                ? String(Date.now() + 1800)
                : "0";
        }})()
        """,
        category="eval_overlay",
    )


async def _set_evidence_overlay_status(
    tab,
    message: str,
    *,
    is_error: bool = False,
) -> None:
    if tab is None:
        return
    await eval_js(
        tab,
        f"""
        (() => {{
            const host = document.getElementById("__synthesix-save-overlay");
            if (!host || !host.__synthesixSetCaptureState) {{
                return;
            }}
            host.style.display = "block";
            host.__synthesixSetCaptureState(
                {json.dumps("error" if is_error else "captured")},
                {json.dumps(message)}
            );
            host.dataset.captureStatusUntil = String(Date.now() + 2200);
        }})()
        """,
        category="eval_overlay",
    )


async def _set_archive_overlay_status(
    tab,
    message: str,
    *,
    is_error: bool = False,
) -> None:
    if tab is None:
        return
    await eval_js(
        tab,
        f"""
        (() => {{
            const host = document.getElementById("__synthesix-save-overlay");
            if (!host || !host.__synthesixSetArchiveState) {{
                return;
            }}
            host.__synthesixSetArchiveState(
                {json.dumps("error" if is_error else "archived")},
                {json.dumps(message)}
            );
            host.dataset.archiveStatusUntil = String(Date.now() + 2200);
        }})()
        """,
        category="eval_overlay",
    )


async def _capture_evidence(
    service: InvestigationService,
    settings: AppSettings,
    tab,
    investigation_id: str,
    payload: dict,
):
    investigation = service.get(investigation_id)
    if investigation.status != "active":
        raise EvidenceCaptureError("Archived investigations are read-only.")

    page = payload.get("page", {})
    saved = service.save_page(investigation_id, page)
    capture_scope = str(payload.get("captureScope", "") or "").strip()
    if capture_scope not in {"viewport", "region"}:
        raise EvidenceCaptureError("Unsupported evidence capture scope.")

    selection = payload.get("selection", {})
    capture_id = str(uuid4())
    captured_at = utc_now()
    capture_name = (
        str(payload.get("captureName", "") or "").strip()
        or _default_capture_name(captured_at)
    )[:120]
    capture_dir = settings.evidence_dir / investigation_id / capture_id
    png_path = capture_dir / "capture.png"
    manifest_path = capture_dir / "manifest.json"
    tool_version = _tool_version()

    try:
        captured_png = await capture_png(
            tab,
            png_path,
            selection,
            capture_beyond_viewport=capture_scope != "viewport",
        )
        stored_png_path = _stored_path(png_path, settings.base_dir)
        artifacts = [
            {
                "id": str(uuid4()),
                "artifact_type": "png",
                "file_path": stored_png_path,
                "mime_type": "image/png",
                "sha256": captured_png.sha256,
                "byte_size": captured_png.byte_size,
                "created_at": captured_at,
            }
        ]
        manifest_artifacts = [
            {
                "type": "png",
                "path": stored_png_path,
                "mime_type": "image/png",
                "sha256": captured_png.sha256,
                "byte_size": captured_png.byte_size,
            }
        ]
        browser_context = page.get("browserContext", {})
        if not isinstance(browser_context, dict):
            browser_context = {}
        manifest = build_evidence_manifest(
            capture_id=capture_id,
            investigation_id=investigation_id,
            result_id=saved.id,
            name=capture_name,
            captured_at=captured_at,
            source_url=saved.url,
            page_title=saved.title,
            capture_kind="screenshot",
            capture_scope=capture_scope,
            selection={
                "x": float(selection.get("x", 0)),
                "y": float(selection.get("y", 0)),
                "width": captured_png.width,
                "height": captured_png.height,
            },
            browser_context={
                "viewport_width": browser_context.get("viewportWidth"),
                "viewport_height": browser_context.get("viewportHeight"),
                "device_pixel_ratio": browser_context.get("devicePixelRatio"),
                "language": browser_context.get("language"),
                "user_agent": browser_context.get("userAgent"),
            },
            tool_version=tool_version,
            artifacts=manifest_artifacts,
        )
        await asyncio.to_thread(write_manifest, manifest_path, manifest)
        capture = service.record_evidence_capture(
            capture_id=capture_id,
            investigation_id=investigation_id,
            result_id=saved.id,
            name=capture_name,
            source_url=saved.url,
            page_title=saved.title,
            capture_scope=capture_scope,
            selection=manifest["capture"]["selection_css_pixels"],
            manifest_path=_stored_path(manifest_path, settings.base_dir),
            captured_at=captured_at,
            tool_version=tool_version,
            artifacts=artifacts,
            capture_kind="screenshot",
        )
        attach_payload = payload.get("attach")
        if isinstance(attach_payload, Mapping):
            attach_entity_id = str(
                attach_payload.get("entityId", "") or ""
            ).strip()
            if attach_entity_id:
                try:
                    service.attach_evidence_capture_to_entity(
                        investigation_id,
                        capture.id,
                        {
                            "graph_entity_id": attach_entity_id,
                            "property_key": str(
                                attach_payload.get("propertyKey", "") or ""
                            ),
                            "property_type": str(
                                attach_payload.get("propertyType", "") or ""
                            ),
                        },
                    )
                except InvestigationError:
                    # Best-effort: the capture itself succeeded, so keep it
                    # even if the immediate attach failed (e.g. stale entity
                    # id). The analyst can still attach it from the
                    # investigation page.
                    logger.warning(
                        "Unable to attach capture to entity at capture time.",
                        exc_info=True,
                    )
    except Exception as exc:
        await asyncio.to_thread(shutil.rmtree, capture_dir, True)
        if isinstance(exc, InvestigationError):
            raise
        raise EvidenceCaptureError(
            f"Evidence capture failed: {exc}"
        ) from exc

    return investigation, saved, capture


_MAX_IMPORT_BYTES = 50 * 1024 * 1024


def _safe_import_filename(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", str(name or "").strip())
    cleaned = cleaned.strip("._") or "fichier"
    return cleaned[:120]


def _import_evidence_file(
    service: InvestigationService,
    settings: AppSettings,
    investigation_id: str,
    payload: dict,
):
    investigation = service.get(investigation_id)
    if investigation.status != "active":
        raise EvidenceCaptureError("Archived investigations are read-only.")
    filename = str(payload.get("fileName", "") or "").strip()[:200] or "fichier"
    try:
        raw = base64.b64decode(str(payload.get("data", "") or ""), validate=False)
    except (ValueError, binascii.Error):
        raise EvidenceCaptureError("Invalid file data.")
    if not raw:
        raise EvidenceCaptureError("Empty file.")
    if len(raw) > _MAX_IMPORT_BYTES:
        raise EvidenceCaptureError("File too large (max 50 MB).")
    mime = str(payload.get("mimeType", "") or "application/octet-stream")
    source_url = str(payload.get("sourceUrl", "") or "").strip()
    capture_id = str(uuid4())
    captured_at = utc_now()
    if source_url:
        page = {"url": source_url, "title": filename}
        evidence_source_url = source_url
    else:
        page = {
            "url": f"https://files.synthesix.local/{capture_id}",
            "title": filename,
        }
        evidence_source_url = ""
    saved = service.save_page(investigation_id, page)

    capture_dir = settings.evidence_dir / investigation_id / capture_id
    safe_name = _safe_import_filename(filename)
    file_path = capture_dir / safe_name
    manifest_path = capture_dir / "manifest.json"
    tool_version = _tool_version()
    try:
        capture_dir.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(raw)
        sha = hashlib.sha256(raw).hexdigest()
        stored = _stored_path(file_path, settings.base_dir)
        artifact_type = (Path(safe_name).suffix.lower().lstrip(".") or "file")[:20]
        artifacts = [
            {
                "id": str(uuid4()),
                "artifact_type": artifact_type,
                "file_path": stored,
                "mime_type": mime,
                "sha256": sha,
                "byte_size": len(raw),
                "created_at": captured_at,
            }
        ]
        manifest = build_evidence_manifest(
            capture_id=capture_id,
            investigation_id=investigation_id,
            result_id=saved.id,
            name=filename,
            captured_at=captured_at,
            source_url=evidence_source_url or saved.url,
            page_title=filename,
            capture_kind="imported",
            capture_scope="viewport",
            selection={},
            browser_context={},
            tool_version=tool_version,
            artifacts=[
                {
                    "type": artifact_type,
                    "path": stored,
                    "mime_type": mime,
                    "sha256": sha,
                    "byte_size": len(raw),
                }
            ],
        )
        write_manifest(manifest_path, manifest)
        capture = service.record_evidence_capture(
            capture_id=capture_id,
            investigation_id=investigation_id,
            result_id=saved.id,
            name=filename,
            source_url=evidence_source_url,
            page_title=filename,
            capture_scope="viewport",
            selection={},
            manifest_path=_stored_path(manifest_path, settings.base_dir),
            captured_at=captured_at,
            tool_version=tool_version,
            artifacts=artifacts,
            capture_kind="imported",
        )
    except Exception as exc:
        shutil.rmtree(capture_dir, ignore_errors=True)
        if isinstance(exc, InvestigationError):
            raise
        raise EvidenceCaptureError(f"Import failed: {exc}") from exc
    return investigation, saved, capture


def _artifact_file_path(
    capture,
    artifact_type: str,
    settings: AppSettings,
) -> Path | None:
    for artifact in capture.artifacts:
        if artifact.artifact_type != artifact_type:
            continue
        path = Path(artifact.file_path)
        return path if path.is_absolute() else settings.base_dir / path
    return None


async def _compare_page_archive(
    service: InvestigationService,
    settings: AppSettings,
    investigation_id: str,
    capture,
    current_text: str,
):
    monitor = service.get_page_monitor_for_result(
        investigation_id,
        capture.result_id,
    )
    if monitor is None:
        return None
    if not monitor.last_capture_id:
        service.advance_page_monitor(
            investigation_id,
            monitor.id,
            capture.id,
        )
        return None

    previous_capture = service.get_evidence_capture(
        investigation_id,
        monitor.last_capture_id,
    )
    previous_text_path = _artifact_file_path(
        previous_capture,
        "text",
        settings,
    )
    try:
        previous_text = (
            await asyncio.to_thread(
                previous_text_path.read_text,
                encoding="utf-8",
            )
            if previous_text_path is not None
            else ""
        )
    except OSError:
        previous_text = ""

    change = compare_page_text(previous_text, current_text)
    report_path = (
        settings.evidence_dir
        / investigation_id
        / capture.id
        / "comparison.html"
    )
    await asyncio.to_thread(
        generate_page_comparison_report,
        output_path=report_path,
        page_title=capture.page_title,
        page_url=capture.source_url,
        previous_captured_at=previous_capture.captured_at,
        current_captured_at=capture.captured_at,
        previous_text=previous_text,
        current_text=current_text,
        change=change,
        base_dir=settings.base_dir,
    )
    return service.record_page_comparison(
        investigation_id=investigation_id,
        monitor_id=monitor.id,
        previous_capture_id=previous_capture.id,
        current_capture_id=capture.id,
        status=change.status,
        similarity=change.similarity,
        previous_sha256=change.previous_sha256,
        current_sha256=change.current_sha256,
        report_path=_stored_path(report_path, settings.base_dir),
        generated_at=capture.captured_at,
    )


async def _archive_page(
    service: InvestigationService,
    settings: AppSettings,
    tab,
    investigation_id: str,
    payload: dict,
):
    investigation = service.get(investigation_id)
    if investigation.status != "active":
        raise EvidenceCaptureError("Archived investigations are read-only.")

    page = payload.get("page", {})
    saved = service.save_page(investigation_id, page)
    capture_id = str(uuid4())
    captured_at = utc_now()
    archive_name = (
        str(payload.get("archiveName", "") or "").strip()
        or _default_archive_name(captured_at)
    )[:120]
    capture_dir = settings.evidence_dir / investigation_id / capture_id
    html_path = capture_dir / "page.html"
    mhtml_path = capture_dir / "page.mhtml"
    text_path = capture_dir / "page.txt"
    manifest_path = capture_dir / "manifest.json"
    tool_version = _tool_version()
    artifacts = []
    manifest_artifacts = []
    capture_errors = []
    normalized_text = ""

    try:
        try:
            captured_html = await capture_html(tab, html_path)
            normalized_text = normalize_html_text(
                await asyncio.to_thread(
                    html_path.read_text,
                    encoding="utf-8",
                )
            )
            captured_text = await write_text_document(
                text_path,
                normalized_text,
            )
            for artifact_type, path, mime_type, document in (
                (
                    "html",
                    html_path,
                    "text/html; charset=utf-8",
                    captured_html,
                ),
                (
                    "text",
                    text_path,
                    "text/plain; charset=utf-8",
                    captured_text,
                ),
            ):
                stored_path = _stored_path(path, settings.base_dir)
                artifact = {
                    "id": str(uuid4()),
                    "artifact_type": artifact_type,
                    "file_path": stored_path,
                    "mime_type": mime_type,
                    "sha256": document.sha256,
                    "byte_size": document.byte_size,
                    "created_at": captured_at,
                }
                artifacts.append(artifact)
                manifest_artifacts.append(
                    {
                        "type": artifact_type,
                        "path": stored_path,
                        "mime_type": mime_type,
                        "sha256": document.sha256,
                        "byte_size": document.byte_size,
                    }
                )
        except Exception as exc:
            capture_errors.append(
                f"HTML archive unavailable ({type(exc).__name__})."
            )
            logger.debug("HTML page archive unavailable", exc_info=True)

        try:
            captured_mhtml = await capture_mhtml(tab, mhtml_path)
            stored_mhtml_path = _stored_path(
                mhtml_path,
                settings.base_dir,
            )
            artifacts.append(
                {
                    "id": str(uuid4()),
                    "artifact_type": "mhtml",
                    "file_path": stored_mhtml_path,
                    "mime_type": "multipart/related",
                    "sha256": captured_mhtml.sha256,
                    "byte_size": captured_mhtml.byte_size,
                    "created_at": captured_at,
                }
            )
            manifest_artifacts.append(
                {
                    "type": "mhtml",
                    "path": stored_mhtml_path,
                    "mime_type": "multipart/related",
                    "sha256": captured_mhtml.sha256,
                    "byte_size": captured_mhtml.byte_size,
                }
            )
        except Exception as exc:
            capture_errors.append(
                f"MHTML archive unavailable ({type(exc).__name__})."
            )
            logger.debug("MHTML page archive unavailable", exc_info=True)

        if not artifacts:
            raise EvidenceCaptureError(
                "Page archive failed: HTML and MHTML are unavailable."
            )
        browser_context = page.get("browserContext", {})
        if not isinstance(browser_context, dict):
            browser_context = {}
        capture_status = "partial" if capture_errors else "completed"
        manifest = build_evidence_manifest(
            capture_id=capture_id,
            investigation_id=investigation_id,
            result_id=saved.id,
            name=archive_name,
            captured_at=captured_at,
            source_url=saved.url,
            page_title=saved.title,
            capture_kind="page_archive",
            capture_scope="viewport",
            selection={},
            browser_context={
                "viewport_width": browser_context.get("viewportWidth"),
                "viewport_height": browser_context.get("viewportHeight"),
                "device_pixel_ratio": browser_context.get("devicePixelRatio"),
                "language": browser_context.get("language"),
                "user_agent": browser_context.get("userAgent"),
            },
            tool_version=tool_version,
            artifacts=manifest_artifacts,
            status=capture_status,
            errors=capture_errors,
        )
        await asyncio.to_thread(write_manifest, manifest_path, manifest)
        capture = service.record_evidence_capture(
            capture_id=capture_id,
            investigation_id=investigation_id,
            result_id=saved.id,
            name=archive_name,
            source_url=saved.url,
            page_title=saved.title,
            capture_scope="viewport",
            selection={},
            manifest_path=_stored_path(manifest_path, settings.base_dir),
            captured_at=captured_at,
            tool_version=tool_version,
            artifacts=artifacts,
            capture_kind="page_archive",
            status=capture_status,
            error=" ".join(capture_errors),
        )
    except Exception as exc:
        await asyncio.to_thread(shutil.rmtree, capture_dir, True)
        if isinstance(exc, InvestigationError):
            raise
        raise EvidenceCaptureError(f"Page archive failed: {exc}") from exc

    try:
        comparison = await _compare_page_archive(
            service,
            settings,
            investigation_id,
            capture,
            normalized_text,
        )
    except Exception:
        comparison = None
        logger.error(
            "Page archive was saved but its monitoring comparison failed.",
            exc_info=True,
        )

    return investigation, saved, capture, comparison


def _parse_capture_time(value: object) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value or "").replace("Z", "+00:00"))
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _has_page_archive_artifact(capture) -> bool:
    for artifact in getattr(capture, "artifacts", ()) or ():
        artifact_type = str(getattr(artifact, "artifact_type", "") or "").casefold()
        mime_type = str(getattr(artifact, "mime_type", "") or "").casefold()
        if artifact_type in {"html", "mhtml", "text", "txt"}:
            return True
        if "html" in mime_type or mime_type.startswith("text/"):
            return True
    return False


def _recent_page_archive(
    service: InvestigationService,
    investigation_id: str,
    result_id: str,
):
    now = datetime.now(timezone.utc)
    candidates = [
        capture
        for capture in service.list_evidence_captures(investigation_id)
        if capture.result_id == result_id
        and capture.capture_kind == "page_archive"
        and _has_page_archive_artifact(capture)
    ]
    for capture in sorted(
        candidates,
        key=lambda item: _parse_capture_time(item.captured_at),
        reverse=True,
    ):
        captured_at = _parse_capture_time(capture.captured_at)
        if now - captured_at <= RECENT_PAGE_ARCHIVE_REUSE_WINDOW:
            return capture
    return None


async def _archive_page_for_selection_source(
    service: InvestigationService,
    settings: AppSettings,
    tab,
    investigation_id: str,
    payload: Mapping,
    saved,
):
    reusable = _recent_page_archive(service, investigation_id, saved.id)
    if reusable is not None:
        return saved, reusable
    _, archived_saved, capture, _comparison = await _archive_page(
        service,
        settings,
        tab,
        investigation_id,
        payload,
    )
    return archived_saved, capture


def _create_graph_entity_from_selection(
    service: InvestigationService,
    investigation_id: str,
    payload: Mapping,
) -> tuple[object, object, dict]:
    entity_payload = payload.get("entity", {})
    if not isinstance(entity_payload, Mapping):
        entity_payload = {}
    page_payload = payload.get("page", {})
    if not isinstance(page_payload, Mapping):
        page_payload = {}

    label = str(
        entity_payload.get("label")
        or payload.get("text")
        or ""
    ).strip()
    category = str(
        entity_payload.get("category")
        or entity_payload.get("tags")
        or "Entité"
    ).strip()
    if not label:
        raise InvestigationValidationError("Selected text is required.")
    if not category:
        raise InvestigationValidationError("Entity category is required.")

    investigation = service.get(investigation_id)
    saved = service.save_page(investigation_id, page_payload)
    entity = service.create_graph_entity_from_result(
        investigation_id,
        saved.id,
        {
            "label": label,
            "category": category,
            "notes": (
                f"Created from selected text on {saved.url}"
                if saved.url
                else "Created from selected text."
            ),
        },
    )
    return investigation, saved, entity


def _append_property_text(current: object, value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return str(current or "").strip()
    values = [
        item.strip()
        for item in str(current or "").split(";")
        if item.strip()
    ]
    if text not in values:
        values.append(text)
    return "; ".join(values)


def _attach_selection_to_graph_entity(
    service: InvestigationService,
    investigation_id: str,
    entity_id: str,
    payload: Mapping,
) -> tuple[object, object, dict, dict | None]:
    property_payload = payload.get("property", {})
    if not isinstance(property_payload, Mapping):
        property_payload = {}
    page_payload = payload.get("page", {})
    if not isinstance(page_payload, Mapping):
        page_payload = {}

    key = str(property_payload.get("key", "") or "").strip()
    value = str(
        property_payload.get("value")
        or payload.get("text")
        or ""
    ).strip()
    if not entity_id:
        raise InvestigationValidationError("Select an investigation entity.")
    if not key:
        raise InvestigationValidationError("Property type is required.")
    if not value:
        raise InvestigationValidationError("Selected text is required.")

    entity_type = str(property_payload.get("entity_type", "") or "").strip()
    property_type = str(property_payload.get("property_type", "") or "").strip()

    investigation = service.get(investigation_id)
    workspace = service.workspace_payload(investigation_id)
    graph_entity = next(
        (
            entity
            for entity in workspace.get("graph_entities", [])
            if str(entity.get("id", "")) == entity_id
        ),
        None,
    )
    if graph_entity is None:
        raise InvestigationValidationError(
            f"Investigation entity not found: {entity_id}"
        )

    saved = service.save_page(investigation_id, page_payload)
    service.link_result_to_graph_entity(
        investigation_id,
        entity_id,
        saved.id,
    )
    # Record the selection as a sourced extracted entity on the page, then
    # attach it as a property. This makes it appear under the page's entities
    # and lets the property link back to its source.
    extracted = service.record_selection_entity(
        investigation_id,
        saved.id,
        value=value,
        property_key=key,
        property_type=property_type,
        entity_type=entity_type or "other",
    )
    attached = None
    if extracted is not None:
        attached = service.attach_extracted_property(
            investigation_id,
            extracted.id,
            {
                "graph_entity_id": entity_id,
                "property_key": key,
                "property_type": property_type,
            },
        )
    return investigation, saved, graph_entity, attached


async def _delete_evidence_files(
    settings: AppSettings,
    capture,
) -> None:
    manifest_path = Path(capture.manifest_path)
    if not manifest_path.is_absolute():
        manifest_path = settings.base_dir / manifest_path
    capture_dir = manifest_path.resolve().parent
    evidence_root = settings.evidence_dir.resolve()
    try:
        capture_dir.relative_to(evidence_root)
    except ValueError as exc:
        raise EvidenceCaptureError(
            "Refusing to delete evidence outside the configured evidence directory."
        ) from exc

    if capture_dir.exists():
        try:
            await asyncio.to_thread(shutil.rmtree, capture_dir)
        except OSError as exc:
            raise EvidenceCaptureError(
                f"Unable to delete evidence files: {exc}"
            ) from exc


async def _delete_evidence_capture(
    service: InvestigationService,
    settings: AppSettings,
    investigation_id: str,
    capture_id: str,
) -> None:
    capture = service.get_evidence_capture(investigation_id, capture_id)
    service.ensure_evidence_capture_deletable(investigation_id, capture_id)
    await _delete_evidence_files(settings, capture)
    service.delete_evidence_capture(investigation_id, capture_id)


async def _delete_investigation_export(
    service: InvestigationService,
    settings: AppSettings,
    investigation_id: str,
    export_id: str,
) -> None:
    export = service.get_export(investigation_id, export_id)
    stored_paths = (
        export.archive_path,
        export.dossier_path,
        export.graphml_path,
        export.csv_path,
        export.nodes_csv_path,
        export.edges_csv_path,
        export.manifest_path,
    )
    artifact_dirs = set()
    for stored_path in stored_paths:
        if not stored_path:
            continue
        path = Path(stored_path)
        if not path.is_absolute():
            path = settings.base_dir / path
        artifact_dirs.add(path.resolve().parent)

    if len(artifact_dirs) != 1:
        raise InvestigationValidationError(
            "Refusing to delete an export whose files span multiple directories."
        )
    export_dir = artifact_dirs.pop()
    investigation_exports_root = (
        settings.exports_dir / investigation_id
    ).resolve()
    try:
        relative_export_dir = export_dir.relative_to(
            investigation_exports_root
        )
    except ValueError as exc:
        raise InvestigationValidationError(
            "Refusing to delete files outside this investigation's export directory."
        ) from exc
    if not relative_export_dir.parts:
        raise InvestigationValidationError(
            "Refusing to delete the investigation export directory."
        )

    if export_dir.exists():
        try:
            await asyncio.to_thread(shutil.rmtree, export_dir)
        except OSError as exc:
            raise InvestigationValidationError(
                f"Unable to delete export files: {exc}"
            ) from exc
    service.delete_export(investigation_id, export_id)


async def _verify_evidence_capture(
    service: InvestigationService,
    settings: AppSettings,
    investigation_id: str,
    capture_id: str,
) -> bool:
    capture = service.get_evidence_capture(investigation_id, capture_id)
    if not capture.artifacts:
        raise EvidenceCaptureError("This capture has no artifact.")

    evidence_root = settings.evidence_dir.resolve()
    for artifact in capture.artifacts:
        artifact_path = Path(artifact.file_path)
        if not artifact_path.is_absolute():
            artifact_path = settings.base_dir / artifact_path
        artifact_path = artifact_path.resolve()
        try:
            artifact_path.relative_to(evidence_root)
        except ValueError as exc:
            raise EvidenceCaptureError(
                "Refusing to verify evidence outside the configured directory."
            ) from exc
        if not artifact_path.is_file():
            raise EvidenceCaptureError(
                f"Evidence {artifact.artifact_type.upper()} is missing."
            )

        actual_hash = await asyncio.to_thread(sha256_file, artifact_path)
        if actual_hash != artifact.sha256:
            return False
    return True


async def _set_evidence_verification_status(
    tab,
    capture_id: str,
    message: str,
    *,
    is_error: bool = False,
) -> None:
    if tab is None:
        return
    await eval_js(
        tab,
        f"""
        (() => {{
            const item = document.querySelector(
                `[data-evidence-id="${{CSS.escape({json.dumps(capture_id)})}}"]`
            );
            const status = item?.querySelector("[data-evidence-verification]");
            if (!status) {{
                return;
            }}
            status.textContent = {json.dumps(message)};
            status.classList.toggle("is-error", {json.dumps(is_error)});
            status.classList.toggle("is-verified", {json.dumps(not is_error)});
        }})()
        """,
        category="eval_page",
    )


def _generate_investigation_page(
    service: InvestigationService,
    settings: AppSettings,
    investigation_id: str,
) -> Path:
    output_path = settings.investigation_page_path(investigation_id)
    generate_investigation_page(
        service.workspace_payload(investigation_id),
        output_path,
        base_dir=settings.base_dir,
        history_report_path=settings.history_report_path,
    )
    return output_path


async def _set_page_status(tab, message: str, *, is_error: bool = False) -> None:
    if tab is None:
        return
    await eval_js(
        tab,
        f"""
        (() => {{
            if (
                window.synthesixPage &&
                typeof window.synthesixPage.setStatus === "function"
            ) {{
                window.synthesixPage.setStatus(
                    {json.dumps(message)},
                    {json.dumps(is_error)}
                );
            }}
        }})()
        """,
        category="eval_page",
    )


def _refresh_investigation_page_file(
    service: InvestigationService,
    settings: AppSettings,
    investigation_id: str,
) -> None:
    """Regenerate the on-disk investigation page after a no-reload save.

    The open tab is intentionally not reloaded; only the generated file is
    rewritten so a manual refresh reflects the change instead of the stale
    snapshot that otherwise survives until the next restart.
    """
    if not investigation_id:
        return
    try:
        _generate_investigation_page(service, settings, investigation_id)
    except Exception:
        logger.debug(
            "Unable to refresh the investigation page file after a save",
            exc_info=True,
        )


async def _save_in_place(
    service: InvestigationService,
    settings: AppSettings,
    source_tab,
    investigation_id: str,
) -> None:
    """Persist a no-reload action to the page file and confirm with "Saved."."""
    _refresh_investigation_page_file(service, settings, investigation_id)
    await _set_page_status(source_tab, "Saved.")


async def _open_or_refresh_investigation_page(
    browser: uc.Browser,
    page_path: Path,
    *,
    bring_to_front: bool,
    open_if_missing: bool = True,
) -> None:
    page_url = page_path.resolve().as_uri()
    tabs = await _open_tabs(browser) or []
    matching_tabs = [
        tab
        for tab in tabs
        if _normalize_tab_url(getattr(tab, "url", None)) == page_url
    ]

    if not matching_tabs and open_if_missing:
        tab = await get_browser_service(browser).open_tab(page_url)
        if bring_to_front:
            await tab.bring_to_front()
        return
    if not matching_tabs:
        return

    for tab in matching_tabs:
        try:
            await tab.reload()
        except Exception:
            logger.debug("Unable to reload investigation page", exc_info=True)
    if bring_to_front:
        await matching_tabs[0].bring_to_front()


async def _set_home_status(
    browser: uc.Browser,
    index_url: str,
    message: str,
    is_error: bool = False,
) -> None:
    tabs = await _open_tabs(browser) or []
    message_json = json.dumps(message)
    error_json = json.dumps(is_error)
    for tab in tabs:
        if not _is_home_tab(tab, index_url):
            continue
        await eval_js(
            tab,
            f"""
            (() => {{
                if (
                    window.synthesixHome &&
                    typeof window.synthesixHome.setStatus === "function"
                ) {{
                    window.synthesixHome.setStatus({message_json}, {error_json});
                }}
            }})()
            """,
            category="eval_home",
        )


async def _set_home_search_running(
    browser: uc.Browser,
    index_url: str,
    running: bool,
) -> None:
    """Toggle the home 'search running' UI state (cancel button)."""
    tabs = await _open_tabs(browser) or []
    running_json = json.dumps(bool(running))
    for tab in tabs:
        if not _is_home_tab(tab, index_url):
            continue
        await eval_js(
            tab,
            f"""
            (() => {{
                if (
                    window.synthesixHome &&
                    typeof window.synthesixHome.setSearchRunning === "function"
                ) {{
                    window.synthesixHome.setSearchRunning({running_json});
                }}
            }})()
            """,
            category="eval_home",
        )


async def _set_query_variant_suggestions(
    tab,
    query: str,
    suggestions: tuple[dict[str, str], ...],
) -> None:
    query_json = json.dumps(query, ensure_ascii=True)
    suggestions_json = json.dumps(suggestions, ensure_ascii=True)
    await eval_js(
        tab,
        f"""
        (() => {{
            if (
                window.synthesixHome &&
                typeof window.synthesixHome.setQueryVariants === "function"
            ) {{
                window.synthesixHome.setQueryVariants(
                    {query_json},
                    {suggestions_json}
                );
            }}
        }})()
        """,
        category="eval_home",
    )


async def _set_home_investigation_selection(
    browser: uc.Browser,
    index_url: str,
    investigation_id: str | None,
) -> None:
    tabs = await _open_tabs(browser) or []
    investigation_id_json = json.dumps(investigation_id or "")
    for tab in tabs:
        if not _is_home_tab(tab, index_url):
            continue
        await eval_js(
            tab,
            f"""
            (() => {{
                if (
                    window.synthesixHome &&
                    typeof window.synthesixHome.setSelectedInvestigation === "function"
                ) {{
                    window.synthesixHome.setSelectedInvestigation(
                        {investigation_id_json}
                    );
                }}
            }})()
            """,
            category="eval_home",
        )


async def _focus_or_open_home_tab(
    browser: uc.Browser,
    index_url: str,
    home_tabs=None,
    reuse_current_tab: bool = False,
):
    if home_tabs is None:
        tabs = await _open_tabs(browser) or []
        home_tabs = [tab for tab in tabs if _is_home_tab(tab, index_url)]

    for home_tab in home_tabs:
        try:
            await home_tab.bring_to_front()
            return home_tab
        except Exception:
            logger.debug("Unable to focus existing home tab", exc_info=True)

    home_tab = await get_browser_service(browser).open_tab(
        index_url,
        new_tab=not reuse_current_tab,
    )
    await home_tab.bring_to_front()
    return home_tab


def _should_sync_local_tab(
    service: BrowserService, tab, transport_mode: str, fallback_interval: float
) -> bool:
    """Whether the per-tick consume/sync evaluate should run for a local
    page ``tab`` (T-021). Always ``True`` in poll mode, or while a tab's
    push binding isn't confirmed armed yet (safety net); once confirmed, the
    evaluate is only replayed every ``fallback_interval`` seconds, since
    inbound actions arrive through :attr:`BrowserService.dispatch_queue`."""
    if transport_mode != "push":
        return True
    target_id = getattr(tab, "target_id", None)
    if not target_id or target_id not in service.armed_binding_targets:
        return True
    last_sync = service.last_local_sync_at.get(target_id)
    if last_sync is None:
        return True
    return time.monotonic() - last_sync >= fallback_interval


def _mark_local_tab_synced(service: BrowserService, tab) -> None:
    target_id = getattr(tab, "target_id", None)
    if target_id:
        service.last_local_sync_at[target_id] = time.monotonic()


async def wait_for_home_action(
    browser: uc.Browser,
    index_url: str,
    settings: AppSettings | None = None,
    investigations_json: str = "[]",
    investigations_version: str = "",
    overlay_investigation: dict | None = None,
    extension_available: bool = False,
    extension_id: str | None = None,
    extension_revision: str | None = None,
):
    settings = settings or get_settings()
    service = get_browser_service(browser)
    # T-021: "poll" (or older test doubles missing the attribute) keeps the
    # pre-T-021 behavior byte for byte; only "push" arms bindings/throttles.
    transport_mode = getattr(settings, "transport_mode", "poll")
    push_fallback_interval = getattr(
        settings, "home_push_fallback_interval", settings.home_poll_interval
    )
    # T-022: event-driven tab discovery; the authoritative getTargets resync
    # cadence lives on the shared service (default kept for older doubles).
    service.target_resync_interval = getattr(
        settings, "target_resync_interval", service.target_resync_interval
    )
    use_extension_overlay = _use_extension_overlay(settings, extension_available)
    use_cdp_overlay = _use_cdp_overlay(settings, extension_available)
    empty_since = None
    unreachable_since = None
    history_cache = {}

    while True:
        if getattr(browser, "stopped", False):
            return {"action": "quit"}

        observability.maybe_log_snapshot()
        tabs = await _open_tabs(browser)
        if tabs is None:
            # A crashed/killed Chrome never sets browser.stopped; without
            # this guard the loop would poll a dead connection forever.
            if unreachable_since is None:
                unreachable_since = time.monotonic()
            elif (
                time.monotonic() - unreachable_since
                >= _BROWSER_UNREACHABLE_QUIT_SECONDS
            ):
                logger.error(
                    "Browser unreachable for %.0f seconds; shutting down.",
                    _BROWSER_UNREACHABLE_QUIT_SECONDS,
                )
                return {"action": "quit"}
            await asyncio.sleep(settings.home_poll_interval)
            continue

        unreachable_since = None

        if not tabs:
            if empty_since is None:
                empty_since = time.monotonic()
            elif time.monotonic() - empty_since >= settings.empty_tabs_grace_seconds:
                return {"action": "quit"}
            await asyncio.sleep(settings.home_poll_interval)
            continue

        empty_since = None

        if use_extension_overlay:
            await service.arm_extension_dispatch_binding(
                extension_id, expected_revision=extension_revision
            )

        for tab in tabs:
            if _is_external_web_tab(tab):
                continue
            settings_change = await _consume_settings_change(tab)
            if settings_change:
                await _apply_settings_to_tabs(
                    tabs,
                    settings_change,
                    source_tab=tab,
                )
                break

        home_tabs = [tab for tab in tabs if _is_home_tab(tab, index_url)]
        if home_tabs:
            history_json, history_version = _cached_history_payload(settings, history_cache)
            for tab in home_tabs:
                if transport_mode == "push":
                    await service.arm_dispatch_binding(tab)
                if not _should_sync_local_tab(
                    service, tab, transport_mode, push_fallback_interval
                ):
                    continue
                state = await _consume_home_tab_action(tab)
                _mark_local_tab_synced(service, tab)
                if state and state.get("ready"):
                    history_stale = state.get("historyVersion") != history_version
                    investigations_stale = (
                        state.get("investigationsVersion") != investigations_version
                    )
                    if history_stale or investigations_stale:
                        await _push_home_tab_data(
                            tab,
                            history_json=history_json if history_stale else None,
                            history_version=history_version,
                            investigations_json=(
                                investigations_json if investigations_stale else None
                            ),
                            investigations_version=investigations_version,
                        )
                if state and state.get("action"):
                    action = state["action"]
                    action["_source_tab"] = tab
                    return action

        for tab in tabs:
            if tab in home_tabs:
                continue
            # T-011: searches run concurrently with this loop; leave the
            # tabs owned by a running engine alone (no overlay injection,
            # no focus-guard arming mid-scrape).
            if str(getattr(tab, "target_id", "")) in ACTIVE_ENGINE_TAB_TARGETS:
                continue
            if _is_external_web_tab(tab) and use_cdp_overlay:
                action = await _install_and_consume_save_overlay(
                    service,
                    tab,
                    overlay_investigation,
                )
            elif _is_external_web_tab(tab):
                continue
            else:
                if transport_mode == "push":
                    await service.arm_dispatch_binding(tab)
                if not _should_sync_local_tab(
                    service, tab, transport_mode, push_fallback_interval
                ):
                    continue
                action = await _consume_page_tab_action(tab)
                _mark_local_tab_synced(service, tab)
            if not action:
                continue
            if action.get("action") == "focus_home":
                await _focus_or_open_home_tab(browser, index_url, home_tabs)
                break
            action["_source_tab"] = tab
            return action

        try:
            # T-021: races the fixed poll interval against the push queue —
            # same wait duration as before when nothing is pushed (poll mode
            # or an empty queue always times out here), but wakes up
            # immediately once a bound page dispatches an action.
            action = await asyncio.wait_for(
                service.dispatch_queue.get(), timeout=settings.home_poll_interval
            )
            action = await _normalize_dispatch_action(action, tabs)
            if not action:
                continue
            if action.get("action") == "home_ready":
                # A local page just (re)loaded behind an armed push binding:
                # drop its sync throttle so the next tick pushes fresh data
                # instead of waiting out the push fallback interval.
                target_id = getattr(action.get("_source_tab"), "target_id", None)
                if target_id:
                    service.last_local_sync_at.pop(target_id, None)
                continue
            if action.get("action") == "focus_home":
                await _focus_or_open_home_tab(browser, index_url, home_tabs)
                continue
            return action
        except asyncio.TimeoutError:
            pass


async def _retry_search_combination(
    result: dict,
    browser: uc.Browser,
    settings: AppSettings,
    investigation_service: InvestigationService,
    report_browser: uc.Browser | None = None,
) -> tuple[str, bool]:
    query = str(result.get("query", "") or "").strip()
    engine = str(result.get("engine", "") or "").strip().lower()
    if not query or len(query) > MAX_QUERY_LENGTH:
        return "The query variant cannot be retried.", True
    if engine not in settings.default_engines:
        return "The selected search engine cannot be retried.", True

    try:
        num_results = int(result.get("numResults", settings.default_max_results))
    except (TypeError, ValueError):
        num_results = settings.default_max_results
    num_results = min(100, max(1, num_results))
    filters = SearchFilters.from_payload(result.get("filters"))
    investigation_id = str(result.get("investigationId", "") or "").strip() or None
    original_query = (
        str(result.get("originalQuery", "") or "").strip()
        or query
    )
    retry_error = await perform_search(
        original_query,
        build_display_query(query, filters),
        browser,
        {
            engine_name: engine_name == engine
            for engine_name in settings.default_engines
        },
        num_results,
        filters,
        query,
        investigation_service=investigation_service,
        investigation_id=investigation_id,
        query_variants=(query,),
        report_browser=report_browser,
    )
    if retry_error:
        return retry_error, True
    return f"Retry completed for {engine.title()}.", False


def _search_task_running(task: asyncio.Task | None) -> bool:
    return task is not None and not task.done()


def _log_search_task_outcome(task: asyncio.Task) -> None:
    if task.cancelled():
        return
    exc = task.exception()
    if exc is not None:
        logger.error(
            "Search task terminated with an unhandled exception.",
            exc_info=(type(exc), exc, exc.__traceback__),
        )


def _start_search_task(coro) -> asyncio.Task:
    """Run a search concurrently with the action loop (T-011).

    The done callback guarantees no exception ever dies silently, even if
    the wrapper coroutine itself is buggy.
    """
    task = asyncio.create_task(coro)
    task.add_done_callback(_log_search_task_outcome)
    return task


def _robot_challenge_errors(error: Exception) -> list[RobotChallengeError]:
    if isinstance(error, RobotChallengeError):
        return [error]
    if isinstance(error, SearchEngineError):
        return [
            engine_error
            for engine_error in error.engine_errors.values()
            if isinstance(engine_error, RobotChallengeError)
        ]
    return []


def _preferred_robot_challenge_artifact(
    error: Exception,
    *,
    base_dir: Path,
) -> Path | None:
    for challenge_error in _robot_challenge_errors(error):
        artifacts = getattr(challenge_error, "captured_artifacts", {}) or {}
        for key in ("html", "screenshot", "text"):
            raw_path = artifacts.get(key)
            if not raw_path:
                continue
            path = Path(raw_path)
            if not path.is_absolute():
                path = base_dir / path
            if path.exists():
                return path
    return None


async def _open_robot_challenge_artifact(
    browser,
    error: Exception,
    settings: AppSettings,
) -> Path | None:
    artifact_path = _preferred_robot_challenge_artifact(
        error,
        base_dir=settings.base_dir,
    )
    if artifact_path is None:
        return None
    try:
        tab = await get_browser_service(browser).open_tab(
            artifact_path.resolve().as_uri()
        )
        await tab.bring_to_front()
    except Exception:
        logger.debug("Unable to open robot challenge artifact.", exc_info=True)
        return artifact_path
    return artifact_path


async def _run_search_action(
    browser: uc.Browser,
    index_url: str,
    search_kwargs: dict,
    search_browser_provider: SearchBrowserProvider | None = None,
) -> None:
    """Background home search; owns the final home statuses."""
    try:
        effective_kwargs = dict(search_kwargs)
        if search_browser_provider is not None:
            effective_kwargs["browser"] = await search_browser_provider.get_browser()
            effective_kwargs.setdefault("report_browser", browser)
        else:
            effective_kwargs.setdefault("browser", browser)
        persistence_error = await perform_search(**effective_kwargs)
        if persistence_error:
            await _set_home_status(
                browser,
                index_url,
                persistence_error,
                is_error=True,
            )
    except asyncio.CancelledError:
        raise
    except Exception:
        logger.exception("Search failed unexpectedly.")
        await _set_home_status(
            browser,
            index_url,
            "Search failed. Check the logs for details.",
            is_error=True,
        )
    finally:
        await _set_home_search_running(browser, index_url, False)
        if search_browser_provider is not None:
            await search_browser_provider.cleanup_idle_tabs()


async def _run_retry_search_action(
    result: dict,
    browser: uc.Browser,
    index_url: str,
    settings: AppSettings,
    investigation_service: InvestigationService,
    search_browser_provider: SearchBrowserProvider | None = None,
) -> None:
    """Background retry of one query/engine cell; reports to its page tab."""
    source_tab = result.get("_source_tab")
    try:
        search_browser = (
            await search_browser_provider.get_browser()
            if search_browser_provider is not None
            else browser
        )
        message, is_error = await _retry_search_combination(
            result,
            search_browser,
            settings,
            investigation_service,
            report_browser=browser,
        )
    except asyncio.CancelledError:
        await _set_page_status(source_tab, "Search cancelled.", is_error=True)
        raise
    except Exception:
        logger.exception("Retry search failed unexpectedly.")
        await _set_page_status(
            source_tab,
            "Search failed. Check the logs for details.",
            is_error=True,
        )
    else:
        await _set_page_status(source_tab, message, is_error=is_error)
    finally:
        if search_browser_provider is not None:
            await search_browser_provider.cleanup_idle_tabs()
        await _set_home_search_running(browser, index_url, False)


async def main():
    settings = get_settings()
    investigation_service = InvestigationService(
        InvestigationRepository(settings.database_path),
        base_dir=settings.base_dir,
    )
    imported_history = investigation_service.initialize(settings.history_json_path)
    if imported_history:
        logger.info(
            "Imported %s legacy history entries into the investigation database.",
            imported_history,
        )

    # Use a file:// URL so navigation works across platforms
    index_url = (settings.base_dir / "index.html").resolve().as_uri()
    browser_manager = await HeadlessBrowserManager.create(home_url=index_url, settings=settings)
    browser = await browser_manager.get_driver()
    search_browser_provider = SearchBrowserProvider(settings, browser_manager)
    browser_service = get_browser_service(browser)
    home_tab = await _focus_or_open_home_tab(browser, index_url, reuse_current_tab=True)
    await home_tab.bring_to_front()
    if (
        getattr(settings, "extension_mode", "auto") != "off"
        and not getattr(browser_manager, "extension_available", False)
    ):
        await _set_home_status(
            browser,
            index_url,
            "Extension Chrome inactive. Install the unpacked extension from extension/README.md; CDP overlay remains active.",
        )
    active_investigation = None
    # T-011: searches run as a background task so the action loop keeps
    # consuming actions; one search at a time, backend is the source of
    # truth for the "search running" state.
    active_search_task: asyncio.Task | None = None
    extension_context_cache: dict[str, str] = {}
    extension_revision = _expected_extension_revision(settings)

    try:
        while True:
            investigations_json, investigations_version = _investigation_payload(
                investigation_service
            )
            overlay_investigation = None
            if active_investigation is not None:
                workspace = investigation_service.workspace_payload(
                    active_investigation.id
                )
                overlay_investigation = {
                    "id": active_investigation.id,
                    "title": active_investigation.title,
                    "tags": list(active_investigation.tags),
                    "graph_entities": [
                        {
                            "id": str(entity.get("id", "") or ""),
                            "label": str(entity.get("label", "") or ""),
                            "tags": [
                                str(tag)
                                for tag in entity.get("tags", [])
                                if str(tag).strip()
                            ],
                            "properties": (
                                dict(entity.get("properties", {}))
                                if isinstance(
                                    entity.get("properties", {}),
                                    Mapping,
                                )
                                else {}
                            ),
                        }
                        for entity in workspace.get("graph_entities", [])
                    ],
                }
            extension_available = getattr(browser_manager, "extension_available", False)
            extension_id = getattr(browser_manager, "extension_id", None)
            if _use_extension_overlay(settings, extension_available):
                await browser_service.arm_extension_dispatch_binding(
                    extension_id, expected_revision=extension_revision
                )
                await _sync_extension_overlay_context(
                    browser_service,
                    extension_id,
                    _extension_overlay_context_payload(overlay_investigation),
                    extension_context_cache,
                )
            result = await wait_for_home_action(
                browser,
                index_url,
                settings=settings,
                investigations_json=investigations_json,
                investigations_version=investigations_version,
                overlay_investigation=overlay_investigation,
                extension_available=extension_available,
                extension_id=extension_id,
                extension_revision=extension_revision,
            )

            # Quit the browser if the user wants to
            if result["action"] == "quit":
                return
            if result["action"] == "select_investigation":
                investigation_id = str(result.get("investigationId", "") or "").strip()
                if not investigation_id:
                    active_investigation = None
                    continue
                try:
                    investigation = investigation_service.get(investigation_id)
                    active_investigation = (
                        investigation if investigation.status == "active" else None
                    )
                except InvestigationError:
                    active_investigation = None
                continue
            if result["action"] == "suggest_query_variants":
                query = str(result.get("value", "") or "").strip()
                source_tab = result.get("_source_tab")
                suggestions = suggest_query_variants(
                    query,
                    limit=max(0, settings.max_query_variants - 1),
                )
                if source_tab is not None:
                    await _set_query_variant_suggestions(
                        source_tab,
                        query,
                        suggestions,
                    )
                continue
            if result["action"] == "retry_search_combination":
                source_tab = result.get("_source_tab")
                if _search_task_running(active_search_task):
                    await _set_page_status(
                        source_tab,
                        "A search is already running. "
                        "Cancel it or wait for it to finish.",
                        is_error=True,
                    )
                    continue
                await _set_page_status(source_tab, "Retrying...")
                await _set_home_search_running(browser, index_url, True)
                active_search_task = _start_search_task(
                    _run_retry_search_action(
                        result,
                        browser,
                        index_url,
                        settings,
                        investigation_service,
                        search_browser_provider,
                    )
                )
                continue
            if result["action"] == "cancel_search":
                if not _search_task_running(active_search_task):
                    await _set_home_status(
                        browser,
                        index_url,
                        "No search is currently running.",
                    )
                    continue
                active_search_task.cancel()
                await asyncio.gather(active_search_task, return_exceptions=True)
                await _set_home_search_running(browser, index_url, False)
                await _set_home_status(browser, index_url, "Search cancelled.")
                continue
            if result["action"] == "local_archive_search":
                filters = dict(result.get("filters", {}) or {})
                try:
                    local_results = investigation_service.search_local_archive(
                        filters
                    )
                    investigation_id = str(
                        filters.get("investigation_id", "") or ""
                    )
                    if investigation_id == "__unassigned__":
                        filters["investigation_title"] = "Unassigned searches"
                    elif investigation_id:
                        filters["investigation_title"] = (
                            investigation_service.get(investigation_id).title
                        )
                    output_path = settings.history_dir / "local_search.html"
                    generate_local_search_page(
                        local_results,
                        filters,
                        output_path,
                        base_dir=settings.base_dir,
                        investigation_pages_dir=settings.investigation_pages_dir,
                    )
                    report_tab = await get_browser_service(browser).open_tab(
                        output_path.resolve().as_uri(),
                    )
                    await report_tab.bring_to_front()
                    await _set_home_status(
                        browser,
                        index_url,
                        f"Local archive search: {len(local_results)} result(s).",
                    )
                except InvestigationError as exc:
                    await _set_home_status(
                        browser,
                        index_url,
                        str(exc),
                        is_error=True,
                    )
                except Exception:
                    logger.exception("Local archive search failed.")
                    await _set_home_status(
                        browser,
                        index_url,
                        "Local archive search failed. Check the logs for details.",
                        is_error=True,
                    )
                continue
            if result["action"] == "rebuild_local_search_index":
                try:
                    indexed_count = (
                        investigation_service.rebuild_local_search_index()
                    )
                    await _set_home_status(
                        browser,
                        index_url,
                        f"Local archive index rebuilt: {indexed_count} document(s).",
                    )
                except Exception:
                    logger.exception("Local archive index rebuild failed.")
                    await _set_home_status(
                        browser,
                        index_url,
                        "Local archive index rebuild failed. Check the logs.",
                        is_error=True,
                    )
                continue
            if result["action"] == "create_investigation":
                try:
                    investigation = investigation_service.create(
                        result.get("investigation", {})
                    )
                    active_investigation = investigation
                    await _set_home_investigation_selection(
                        browser,
                        index_url,
                        investigation.id,
                    )
                    await _set_home_status(
                        browser,
                        index_url,
                        f'Investigation "{investigation.title}" created.',
                    )
                except InvestigationError as exc:
                    await _set_home_status(
                        browser,
                        index_url,
                        str(exc),
                        is_error=True,
                    )
                continue
            if result["action"] == "update_investigation":
                investigation_id = str(result.get("investigationId", "") or "").strip()
                try:
                    investigation = investigation_service.update(
                        investigation_id,
                        result.get("investigation", {}),
                    )
                    if (
                        active_investigation is not None
                        and active_investigation.id == investigation.id
                    ):
                        active_investigation = investigation
                    page_path = _generate_investigation_page(
                        investigation_service,
                        settings,
                        investigation.id,
                    )
                    await _open_or_refresh_investigation_page(
                        browser,
                        page_path,
                        bring_to_front=False,
                        open_if_missing=False,
                    )
                    await _set_home_status(
                        browser,
                        index_url,
                        f'Investigation "{investigation.title}" updated.',
                    )
                except InvestigationError as exc:
                    await _set_home_status(
                        browser,
                        index_url,
                        str(exc),
                        is_error=True,
                    )
                continue
            if result["action"] == "archive_investigation":
                investigation_id = str(result.get("investigationId", "") or "").strip()
                try:
                    investigation = investigation_service.archive(investigation_id)
                    if (
                        active_investigation is not None
                        and active_investigation.id == investigation.id
                    ):
                        active_investigation = None
                    page_path = _generate_investigation_page(
                        investigation_service,
                        settings,
                        investigation.id,
                    )
                    await _open_or_refresh_investigation_page(
                        browser,
                        page_path,
                        bring_to_front=False,
                        open_if_missing=False,
                    )
                    await _set_home_investigation_selection(browser, index_url, None)
                    await _set_home_status(
                        browser,
                        index_url,
                        f'Investigation "{investigation.title}" archived.',
                    )
                except InvestigationError as exc:
                    await _set_home_status(
                        browser,
                        index_url,
                        str(exc),
                        is_error=True,
                    )
                continue
            if result["action"] == "delete_investigation":
                investigation_id = str(result.get("investigationId", "") or "").strip()
                try:
                    investigation = investigation_service.get(investigation_id)
                    investigation_service.delete(investigation_id)
                    if (
                        active_investigation is not None
                        and active_investigation.id == investigation.id
                    ):
                        active_investigation = None
                    await _set_home_investigation_selection(browser, index_url, None)
                    await _set_home_status(
                        browser,
                        index_url,
                        f'Investigation "{investigation.title}" deleted.',
                    )
                except InvestigationError as exc:
                    await _set_home_status(
                        browser,
                        index_url,
                        str(exc),
                        is_error=True,
                    )
                continue
            if result["action"] == "observe_saved_page":
                investigation_id = str(result.get("investigationId", "") or "").strip()
                source_tab = result.get("_source_tab")
                try:
                    was_saved = investigation_service.observe_saved_page(
                        investigation_id,
                        result.get("page", {}),
                    )
                    if was_saved:
                        page_path = _generate_investigation_page(
                            investigation_service,
                            settings,
                            investigation_id,
                        )
                        await _open_or_refresh_investigation_page(
                            browser,
                            page_path,
                            bring_to_front=False,
                            open_if_missing=False,
                        )
                        await _set_overlay_save_status(
                            browser_service,
                            settings,
                            extension_id,
                            result,
                            "Saved",
                        )
                except InvestigationError:
                    logger.debug(
                        "Unable to record a saved-page revisit",
                        exc_info=True,
                    )
                continue
            if result["action"] == "archive_page_to_investigation":
                investigation_id = str(
                    result.get("investigationId", "") or ""
                ).strip()
                source_tab = result.get("_source_tab")
                try:
                    (
                        investigation,
                        saved,
                        capture,
                        comparison,
                    ) = await _archive_page(
                        investigation_service,
                        settings,
                        source_tab,
                        investigation_id,
                        result,
                    )
                    active_investigation = investigation
                    page_path = _generate_investigation_page(
                        investigation_service,
                        settings,
                        investigation_id,
                    )
                    await _open_or_refresh_investigation_page(
                        browser,
                        page_path,
                        bring_to_front=False,
                        open_if_missing=False,
                    )
                    await _set_overlay_save_status(
                        browser_service,
                        settings,
                        extension_id,
                        result,
                        "Saved",
                    )
                    archive_message = (
                        "Archived and compared"
                        if comparison is not None
                        else "Page archived"
                    )
                    await _set_overlay_archive_status(
                        browser_service,
                        settings,
                        extension_id,
                        result,
                        archive_message,
                    )
                    comparison_detail = (
                        f", comparison: {comparison.status.replace('_', ' ')}"
                        if comparison is not None
                        else ""
                    )
                    await _set_home_status(
                        browser,
                        index_url,
                        (
                            f"Page archived for {saved.title or saved.url}"
                            f"{comparison_detail}."
                        ),
                    )
                except InvestigationError as exc:
                    await _set_overlay_archive_status(
                        browser_service,
                        settings,
                        extension_id,
                        result,
                        "Archive failed",
                        is_error=True,
                    )
                    await _set_home_status(
                        browser,
                        index_url,
                        str(exc),
                        is_error=True,
                    )
                continue
            if result["action"] == "import_evidence_file":
                investigation_id = str(
                    result.get("investigationId", "") or ""
                ).strip()
                source_tab = result.get("_source_tab")
                try:
                    investigation, saved, capture = _import_evidence_file(
                        investigation_service,
                        settings,
                        investigation_id,
                        result,
                    )
                    active_investigation = investigation
                    page_path = _generate_investigation_page(
                        investigation_service,
                        settings,
                        investigation_id,
                    )
                    await _open_or_refresh_investigation_page(
                        browser,
                        page_path,
                        bring_to_front=False,
                        open_if_missing=False,
                    )
                    await _set_page_status(
                        source_tab,
                        f'Fichier importé : {capture.name or saved.title}.',
                    )
                except InvestigationError as exc:
                    await _set_page_status(source_tab, str(exc), is_error=True)
                continue
            if result["action"] == "capture_evidence_to_investigation":
                investigation_id = str(
                    result.get("investigationId", "") or ""
                ).strip()
                source_tab = result.get("_source_tab")
                try:
                    investigation, saved, capture = await _capture_evidence(
                        investigation_service,
                        settings,
                        source_tab,
                        investigation_id,
                        result,
                    )
                    active_investigation = investigation
                    page_path = _generate_investigation_page(
                        investigation_service,
                        settings,
                        investigation_id,
                    )
                    await _open_or_refresh_investigation_page(
                        browser,
                        page_path,
                        bring_to_front=False,
                        open_if_missing=False,
                    )
                    await _set_overlay_save_status(
                        browser_service,
                        settings,
                        extension_id,
                        result,
                        "Saved",
                    )
                    await _set_overlay_capture_status(
                        browser_service,
                        settings,
                        extension_id,
                        result,
                        "Screenshot captured",
                    )
                    await _set_home_status(
                        browser,
                        index_url,
                        (
                            f"Evidence captured for "
                            f"{saved.title or saved.url} "
                            f"({capture.capture_scope})."
                        ),
                    )
                except InvestigationError as exc:
                    await _set_overlay_capture_status(
                        browser_service,
                        settings,
                        extension_id,
                        result,
                        "Capture failed",
                        is_error=True,
                    )
                    await _set_home_status(
                        browser,
                        index_url,
                        str(exc),
                        is_error=True,
                    )
                continue
            if result["action"] == "create_graph_entity_from_selection":
                investigation_id = str(
                    result.get("investigationId", "") or ""
                ).strip()
                source_tab = result.get("_source_tab")
                try:
                    investigation, saved, entity = (
                        _create_graph_entity_from_selection(
                            investigation_service,
                            investigation_id,
                            result,
                        )
                    )
                    saved, archive = await _archive_page_for_selection_source(
                        investigation_service,
                        settings,
                        source_tab,
                        investigation_id,
                        result,
                        saved,
                    )
                    active_investigation = investigation
                    page_path = _generate_investigation_page(
                        investigation_service,
                        settings,
                        investigation_id,
                    )
                    await _open_or_refresh_investigation_page(
                        browser,
                        page_path,
                        bring_to_front=False,
                        open_if_missing=False,
                    )
                    await _set_overlay_save_status(
                        browser_service,
                        settings,
                        extension_id,
                        result,
                        "Entity created",
                    )
                    await _set_home_status(
                        browser,
                        index_url,
                        (
                            f'Entity "{entity["label"]}" created from '
                            f"{saved.title or saved.url}."
                        ),
                    )
                except InvestigationError as exc:
                    await _set_overlay_save_status(
                        browser_service,
                        settings,
                        extension_id,
                        result,
                        "Entity failed",
                        is_error=True,
                    )
                    await _set_home_status(
                        browser,
                        index_url,
                        str(exc),
                        is_error=True,
                    )
                continue
            if result["action"] == "attach_selection_to_graph_entity":
                investigation_id = str(
                    result.get("investigationId", "") or ""
                ).strip()
                source_tab = result.get("_source_tab")
                try:
                    investigation, saved, entity, extracted = (
                        _attach_selection_to_graph_entity(
                            investigation_service,
                            investigation_id,
                            str(result.get("entityId", "") or "").strip(),
                            result,
                        )
                    )
                    saved, archive = await _archive_page_for_selection_source(
                        investigation_service,
                        settings,
                        source_tab,
                        investigation_id,
                        result,
                        saved,
                    )
                    if extracted:
                        investigation_service.set_extracted_entity_source_capture(
                            investigation_id,
                            str(extracted.get("id", "") or ""),
                            archive.id,
                        )
                    active_investigation = investigation
                    page_path = _generate_investigation_page(
                        investigation_service,
                        settings,
                        investigation_id,
                    )
                    await _open_or_refresh_investigation_page(
                        browser,
                        page_path,
                        bring_to_front=False,
                        open_if_missing=False,
                    )
                    await _set_overlay_save_status(
                        browser_service,
                        settings,
                        extension_id,
                        result,
                        "Text attached",
                    )
                    await _set_home_status(
                        browser,
                        index_url,
                        (
                            f'Text attached to "{entity["label"]}" from '
                            f"{saved.title or saved.url}."
                        ),
                    )
                except InvestigationError as exc:
                    await _set_overlay_save_status(
                        browser_service,
                        settings,
                        extension_id,
                        result,
                        "Attach failed",
                        is_error=True,
                    )
                    await _set_home_status(
                        browser,
                        index_url,
                        str(exc),
                        is_error=True,
                    )
                continue
            if result["action"] == "save_page_to_investigation":
                investigation_id = str(result.get("investigationId", "") or "").strip()
                source_tab = result.get("_source_tab")
                try:
                    investigation = investigation_service.get(investigation_id)
                    saved = investigation_service.save_page(
                        investigation_id,
                        result.get("page", {}),
                    )
                    active_investigation = investigation
                    page_path = _generate_investigation_page(
                        investigation_service,
                        settings,
                        investigation_id,
                    )
                    await _open_or_refresh_investigation_page(
                        browser,
                        page_path,
                        bring_to_front=False,
                        open_if_missing=False,
                    )
                    await _set_overlay_save_status(
                        browser_service,
                        settings,
                        extension_id,
                        result,
                        "Saved",
                    )
                    await _set_home_status(
                        browser,
                        index_url,
                        f'Page saved: {saved.title or saved.url}',
                    )
                except InvestigationError as exc:
                    await _set_overlay_save_status(
                        browser_service,
                        settings,
                        extension_id,
                        result,
                        "Save failed",
                        is_error=True,
                    )
                    await _set_home_status(
                        browser,
                        index_url,
                        str(exc),
                        is_error=True,
                    )
                continue
            if result["action"] == "open_investigation":
                investigation_id = str(result.get("investigationId", "") or "").strip()
                try:
                    investigation = investigation_service.get(investigation_id)
                    if investigation.status == "active":
                        active_investigation = investigation
                    page_path = _generate_investigation_page(
                        investigation_service,
                        settings,
                        investigation_id,
                    )
                    await _open_or_refresh_investigation_page(
                        browser,
                        page_path,
                        bring_to_front=True,
                    )
                    await _set_home_status(browser, index_url, "")
                except InvestigationError as exc:
                    await _set_home_status(
                        browser,
                        index_url,
                        str(exc),
                        is_error=True,
                    )
                continue
            if result["action"] == "refresh_investigation":
                investigation_id = str(result.get("investigationId", "") or "").strip()
                source_tab = result.get("_source_tab")
                try:
                    page_path = _generate_investigation_page(
                        investigation_service,
                        settings,
                        investigation_id,
                    )
                    await _open_or_refresh_investigation_page(
                        browser,
                        page_path,
                        bring_to_front=False,
                        open_if_missing=False,
                    )
                except InvestigationError as exc:
                    await _set_page_status(source_tab, str(exc), is_error=True)
                continue
            if result["action"] == "update_investigation_result":
                investigation_id = str(result.get("investigationId", "") or "").strip()
                result_id = str(result.get("resultId", "") or "").strip()
                source_tab = result.get("_source_tab")
                try:
                    investigation_service.update_result(
                        investigation_id,
                        result_id,
                        result.get("result", {}),
                    )
                    # In-place: the card already reflects favorite/status/tags,
                    # so keep the analyst's place instead of reloading.
                    await _save_in_place(
                        investigation_service, settings, source_tab, investigation_id
                    )
                except InvestigationError as exc:
                    await _set_page_status(source_tab, str(exc), is_error=True)
                continue
            if result["action"] == "update_graph_entity":
                investigation_id = str(
                    result.get("investigationId", "") or ""
                ).strip()
                entity_id = str(result.get("entityId", "") or "").strip()
                source_tab = result.get("_source_tab")
                try:
                    investigation_service.update_graph_entity(
                        investigation_id,
                        entity_id,
                        result.get("entity", {}),
                    )
                    # In-place save: the rail keeps the edited values, so skip
                    # the page reload for a smoother editing flow.
                    await _save_in_place(
                        investigation_service, settings, source_tab, investigation_id
                    )
                except InvestigationError as exc:
                    await _set_page_status(source_tab, str(exc), is_error=True)
                continue
            if result["action"] == "delete_graph_entity_property":
                investigation_id = str(
                    result.get("investigationId", "") or ""
                ).strip()
                entity_id = str(result.get("entityId", "") or "").strip()
                source_tab = result.get("_source_tab")
                try:
                    investigation_service.delete_graph_entity_property(
                        investigation_id,
                        entity_id,
                        str(result.get("key", "") or ""),
                    )
                    # In-place delete: the row is removed client-side, so skip
                    # the page reload.
                    await _save_in_place(
                        investigation_service, settings, source_tab, investigation_id
                    )
                except InvestigationError as exc:
                    await _set_page_status(source_tab, str(exc), is_error=True)
                continue
            if result["action"] in {
                "create_graph_entity",
                "create_graph_entity_from_result",
                "create_graph_entity_from_extracted",
                "delete_graph_entity",
                "set_graph_entity_property",
                "link_result_to_graph_entity",
                "unlink_result_from_graph_entity",
                "attach_extracted_property",
                "detach_extracted_property",
                "set_entity_property_scope",
                "delete_entities",
                "attach_extracted_properties",
                "add_graph_entity_relation",
                "update_graph_entity_relation",
                "delete_graph_entity_relation",
                "rename_evidence_capture",
                "attach_evidence_capture_to_entity",
                "set_url_grouping_rule",
            }:
                investigation_id = str(
                    result.get("investigationId", "") or ""
                ).strip()
                source_tab = result.get("_source_tab")
                try:
                    action = result["action"]
                    entity_id = str(
                        result.get("entityId", "") or ""
                    ).strip()
                    if action == "create_graph_entity":
                        investigation_service.create_graph_entity(
                            investigation_id,
                            result.get("entity", {}),
                        )
                    elif action == "create_graph_entity_from_result":
                        investigation_service.create_graph_entity_from_result(
                            investigation_id,
                            str(result.get("resultId", "") or "").strip(),
                            result.get("entity", {}),
                        )
                    elif action == "create_graph_entity_from_extracted":
                        investigation_service.create_graph_entity_from_extracted(
                            investigation_id,
                            str(
                                result.get("extractedEntityId", "") or ""
                            ).strip(),
                            result.get("entity", {}),
                        )
                    elif action == "delete_graph_entity":
                        investigation_service.delete_graph_entity(
                            investigation_id,
                            entity_id,
                        )
                    elif action == "set_graph_entity_property":
                        investigation_service.set_graph_entity_property(
                            investigation_id,
                            entity_id,
                            result.get("property", {}),
                        )
                    elif action == "add_graph_entity_relation":
                        investigation_service.add_graph_entity_relation(
                            investigation_id,
                            entity_id,
                            str(result.get("targetEntityId", "") or "").strip(),
                            str(result.get("label", "") or ""),
                            relation_id=str(
                                result.get("relationId", "") or ""
                            ).strip(),
                        )
                    elif action == "update_graph_entity_relation":
                        investigation_service.update_graph_entity_relation(
                            investigation_id,
                            str(result.get("relationId", "") or "").strip(),
                            str(result.get("label", "") or ""),
                        )
                    elif action == "delete_graph_entity_relation":
                        investigation_service.delete_graph_entity_relation(
                            investigation_id,
                            str(result.get("relationId", "") or "").strip(),
                        )
                    elif action == "link_result_to_graph_entity":
                        investigation_service.link_result_to_graph_entity(
                            investigation_id,
                            entity_id,
                            str(result.get("resultId", "") or "").strip(),
                        )
                    elif action == "unlink_result_from_graph_entity":
                        investigation_service.unlink_result_from_graph_entity(
                            investigation_id,
                            entity_id,
                            str(result.get("resultId", "") or "").strip(),
                        )
                    elif action == "attach_extracted_property":
                        investigation_service.attach_extracted_property(
                            investigation_id,
                            str(
                                result.get("extractedEntityId", "") or ""
                            ).strip(),
                            result.get("property", {}),
                        )
                    elif action == "set_entity_property_scope":
                        investigation_service.set_entity_property_scope(
                            investigation_id,
                            str(
                                result.get("extractedEntityId", "") or ""
                            ).strip(),
                            str(result.get("scope", "") or "").strip(),
                        )
                    elif action == "delete_entities":
                        for raw_id in result.get("entityIds", []) or []:
                            candidate = str(raw_id or "").strip()
                            if not candidate:
                                continue
                            try:
                                investigation_service.delete_entity(
                                    investigation_id,
                                    candidate,
                                )
                            except InvestigationError:
                                logger.debug(
                                    "Batch delete skipped one entity",
                                    exc_info=True,
                                )
                    elif action == "attach_extracted_properties":
                        graph_entity_id = str(
                            result.get("graphEntityId", "") or ""
                        ).strip()
                        for item in result.get("items", []) or []:
                            if not isinstance(item, Mapping):
                                continue
                            extracted_id = str(
                                item.get("extractedEntityId", "") or ""
                            ).strip()
                            if not extracted_id:
                                continue
                            try:
                                investigation_service.attach_extracted_property(
                                    investigation_id,
                                    extracted_id,
                                    {
                                        "graph_entity_id": graph_entity_id,
                                        "property_key": str(
                                            item.get("propertyKey", "") or ""
                                        ).strip(),
                                        "property_type": str(
                                            item.get("propertyType", "") or ""
                                        ).strip(),
                                        "duplicate_strategy": str(
                                            item.get("duplicateStrategy", "")
                                            or "append"
                                        ).strip(),
                                    },
                                )
                            except InvestigationError:
                                logger.debug(
                                    "Batch attach skipped one entity",
                                    exc_info=True,
                                )
                    elif action == "rename_evidence_capture":
                        investigation_service.rename_evidence_capture(
                            investigation_id,
                            str(result.get("captureId", "") or "").strip(),
                            str(result.get("name", "") or ""),
                        )
                    elif action == "attach_evidence_capture_to_entity":
                        investigation_service.attach_evidence_capture_to_entity(
                            investigation_id,
                            str(result.get("captureId", "") or "").strip(),
                            result.get("property", {}),
                        )
                    elif action == "set_url_grouping_rule":
                        investigation_service.set_url_grouping_rule(
                            str(result.get("domain", "") or "").strip(),
                            int(result.get("pathSegments", 1) or 1),
                            bool(result.get("enabled", True)),
                        )
                    else:
                        investigation_service.detach_extracted_property(
                            investigation_id,
                            str(
                                result.get("extractedEntityId", "") or ""
                            ).strip(),
                        )
                    # Attaching/detaching an extracted property (incl. batch)
                    # is reflected in place by the JS, so keep the analyst's
                    # scroll position instead of reloading the whole page.
                    if action in {
                        "set_graph_entity_property",
                        "add_graph_entity_relation",
                        "update_graph_entity_relation",
                        "delete_graph_entity_relation",
                        "attach_extracted_property",
                        "detach_extracted_property",
                        "set_entity_property_scope",
                        "delete_entities",
                        "attach_extracted_properties",
                    }:
                        await _save_in_place(
                            investigation_service,
                            settings,
                            source_tab,
                            investigation_id,
                        )
                    else:
                        page_path = _generate_investigation_page(
                            investigation_service,
                            settings,
                            investigation_id,
                        )
                        await _open_or_refresh_investigation_page(
                            browser,
                            page_path,
                            bring_to_front=False,
                            open_if_missing=False,
                        )
                except InvestigationError as exc:
                    await _set_page_status(source_tab, str(exc), is_error=True)
                continue
            if result["action"] == "extract_result_entities":
                investigation_id = str(
                    result.get("investigationId", "") or ""
                ).strip()
                result_id = str(result.get("resultId", "") or "").strip()
                source_tab = result.get("_source_tab")
                try:
                    entities = investigation_service.extract_entities(
                        investigation_id,
                        result_id,
                    )
                    page_path = _generate_investigation_page(
                        investigation_service,
                        settings,
                        investigation_id,
                    )
                    await _open_or_refresh_investigation_page(
                        browser,
                        page_path,
                        bring_to_front=False,
                        open_if_missing=False,
                    )
                    await _set_page_status(
                        source_tab,
                        f"{len(entities)} entity candidate(s) available.",
                    )
                except InvestigationError as exc:
                    await _set_page_status(source_tab, str(exc), is_error=True)
                continue
            if result["action"] == "analyze_result_url":
                investigation_id = str(
                    result.get("investigationId", "") or ""
                ).strip()
                result_id = str(result.get("resultId", "") or "").strip()
                source_tab = result.get("_source_tab")
                try:
                    analysis = await asyncio.to_thread(
                        investigation_service.analyze_result_url,
                        investigation_id,
                        result_id,
                    )
                    page_path = _generate_investigation_page(
                        investigation_service,
                        settings,
                        investigation_id,
                    )
                    await _open_or_refresh_investigation_page(
                        browser,
                        page_path,
                        bring_to_front=False,
                        open_if_missing=False,
                    )
                    await _set_page_status(
                        source_tab,
                        (
                            f"URL analysis completed: HTTP "
                            f"{analysis['status_code']}, "
                            f"{len(analysis['redirects'])} redirect(s)."
                        ),
                    )
                except InvestigationError as exc:
                    await _set_page_status(source_tab, str(exc), is_error=True)
                continue
            if result["action"] == "update_entity_status":
                investigation_id = str(
                    result.get("investigationId", "") or ""
                ).strip()
                entity_id = str(result.get("entityId", "") or "").strip()
                source_tab = result.get("_source_tab")
                try:
                    investigation_service.update_entity_status(
                        investigation_id,
                        entity_id,
                        result.get("status", ""),
                    )
                    # Persist in place; the panel already shows the new value,
                    # so a full page reload would only disrupt the analyst.
                    await _save_in_place(
                        investigation_service, settings, source_tab, investigation_id
                    )
                except InvestigationError as exc:
                    await _set_page_status(source_tab, str(exc), is_error=True)
                continue
            if result["action"] == "update_entity_metadata":
                investigation_id = str(
                    result.get("investigationId", "") or ""
                ).strip()
                entity_id = str(result.get("entityId", "") or "").strip()
                source_tab = result.get("_source_tab")
                try:
                    investigation_service.update_entity_metadata(
                        investigation_id,
                        entity_id,
                        result.get("entity", {}),
                    )
                    # In-place save: no reload so the analyst keeps their place.
                    await _save_in_place(
                        investigation_service, settings, source_tab, investigation_id
                    )
                except InvestigationError as exc:
                    await _set_page_status(source_tab, str(exc), is_error=True)
                continue
            if result["action"] == "delete_entity":
                investigation_id = str(
                    result.get("investigationId", "") or ""
                ).strip()
                entity_id = str(result.get("entityId", "") or "").strip()
                source_tab = result.get("_source_tab")
                try:
                    investigation_service.delete_entity(
                        investigation_id,
                        entity_id,
                    )
                    # In-place: the JS already hid the row, so a reload would
                    # only disrupt the analyst mid-triage.
                    await _save_in_place(
                        investigation_service, settings, source_tab, investigation_id
                    )
                except InvestigationError as exc:
                    await _set_page_status(source_tab, str(exc), is_error=True)
                continue
            if result["action"] == "export_zeroneurone":
                investigation_id = str(
                    result.get("investigationId", "") or ""
                ).strip()
                source_tab = result.get("_source_tab")
                include_evidence = bool(result.get("includeEvidence", False))
                include_unreviewed = bool(
                    result.get("includeUnreviewed", False)
                )
                include_page_archives = bool(
                    result.get("includePageArchives", False)
                )
                try:
                    workspace = investigation_service.workspace_payload(
                        investigation_id
                    )
                    timestamp = (
                        utc_now()
                        .replace("+00:00", "")
                        .replace("-", "")
                        .replace(":", "")
                        .replace("T", "_")
                        .replace(".", "_")
                    )
                    report_slug = _slugify(
                        workspace.get("investigation", {}).get("title", "")
                    )
                    output_dir = (
                        settings.exports_dir
                        / investigation_id
                        / f"{report_slug}_{timestamp}"
                    )
                    exported = await asyncio.to_thread(
                        export_zeroneurone_bundle,
                        workspace,
                        output_dir,
                        include_evidence=include_evidence,
                        include_unreviewed=include_unreviewed,
                        include_page_archives=include_page_archives,
                        tool_version=_tool_version(),
                        base_dir=settings.base_dir,
                        asset_root=settings.evidence_dir,
                    )
                    investigation_service.record_export(
                        investigation_id,
                        archive_path=_stored_path(
                            exported.archive_path,
                            settings.base_dir,
                        ),
                        dossier_path=_stored_path(
                            exported.dossier_path,
                            settings.base_dir,
                        ),
                        graphml_path=_stored_path(
                            exported.graphml_path,
                            settings.base_dir,
                        ),
                        csv_path=_stored_path(
                            exported.csv_path,
                            settings.base_dir,
                        ),
                        nodes_csv_path=_stored_path(
                            exported.nodes_csv_path,
                            settings.base_dir,
                        ),
                        edges_csv_path=_stored_path(
                            exported.edges_csv_path,
                            settings.base_dir,
                        ),
                        manifest_path=_stored_path(
                            exported.manifest_path,
                            settings.base_dir,
                        ),
                        include_evidence=include_evidence,
                        include_unreviewed=include_unreviewed,
                        include_page_archives=include_page_archives,
                        node_count=exported.node_count,
                        edge_count=exported.edge_count,
                        asset_count=exported.asset_count,
                        generated_at=exported.generated_at,
                    )
                    page_path = _generate_investigation_page(
                        investigation_service,
                        settings,
                        investigation_id,
                    )
                    await _open_or_refresh_investigation_page(
                        browser,
                        page_path,
                        bring_to_front=False,
                        open_if_missing=False,
                    )
                    await _set_page_status(
                        source_tab,
                        (
                            f"Export generated: {exported.node_count} nodes, "
                            f"{exported.edge_count} links."
                        ),
                    )
                except Exception as exc:
                    logger.error(
                        "Unable to generate ZeroNeurone export.",
                        exc_info=True,
                    )
                    await _set_page_status(
                        source_tab,
                        "Export failed. Check the logs for details.",
                        is_error=True,
                    )
                continue
            if result["action"] == "delete_zeroneurone_export":
                investigation_id = str(
                    result.get("investigationId", "") or ""
                ).strip()
                export_id = str(result.get("exportId", "") or "").strip()
                source_tab = result.get("_source_tab")
                try:
                    await _delete_investigation_export(
                        investigation_service,
                        settings,
                        investigation_id,
                        export_id,
                    )
                    await _save_in_place(
                        investigation_service, settings, source_tab, investigation_id
                    )
                except InvestigationError as exc:
                    await _set_page_status(source_tab, str(exc), is_error=True)
                continue
            if result["action"] == "remove_saved_page":
                investigation_id = str(result.get("investigationId", "") or "").strip()
                result_id = str(result.get("resultId", "") or "").strip()
                source_tab = result.get("_source_tab")
                try:
                    captures = [
                        capture
                        for capture in investigation_service.list_evidence_captures(
                            investigation_id
                        )
                        if capture.result_id == result_id
                    ]
                    for capture in captures:
                        await _delete_evidence_files(settings, capture)
                    investigation_service.remove_saved_page(
                        investigation_id,
                        result_id,
                    )
                    # In-place: the JS removes the card and closes its rail
                    # panel, so keep the analyst's place instead of reloading.
                    await _save_in_place(
                        investigation_service, settings, source_tab, investigation_id
                    )
                except InvestigationError as exc:
                    await _set_page_status(source_tab, str(exc), is_error=True)
                continue
            if result["action"] == "delete_evidence_capture":
                investigation_id = str(
                    result.get("investigationId", "") or ""
                ).strip()
                capture_id = str(result.get("captureId", "") or "").strip()
                source_tab = result.get("_source_tab")
                try:
                    await _delete_evidence_capture(
                        investigation_service,
                        settings,
                        investigation_id,
                        capture_id,
                    )
                    # The evidence row is removed client-side. Keep the rail
                    # context instead of refreshing the whole investigation.
                    await _save_in_place(
                        investigation_service, settings, source_tab, investigation_id
                    )
                except InvestigationError as exc:
                    await _set_page_status(source_tab, str(exc), is_error=True)
                continue
            if result["action"] == "verify_evidence_capture":
                investigation_id = str(
                    result.get("investigationId", "") or ""
                ).strip()
                capture_id = str(result.get("captureId", "") or "").strip()
                source_tab = result.get("_source_tab")
                try:
                    verified = await _verify_evidence_capture(
                        investigation_service,
                        settings,
                        investigation_id,
                        capture_id,
                    )
                    await _set_evidence_verification_status(
                        source_tab,
                        capture_id,
                        "Verified" if verified else "Hash mismatch",
                        is_error=not verified,
                    )
                except InvestigationError as exc:
                    await _set_evidence_verification_status(
                        source_tab,
                        capture_id,
                        str(exc),
                        is_error=True,
                    )
                continue
            if result["action"] == "create_page_monitor":
                investigation_id = str(
                    result.get("investigationId", "") or ""
                ).strip()
                result_id = str(result.get("resultId", "") or "").strip()
                source_tab = result.get("_source_tab")
                try:
                    investigation_service.create_page_monitor(
                        investigation_id,
                        result_id,
                    )
                    page_path = _generate_investigation_page(
                        investigation_service,
                        settings,
                        investigation_id,
                    )
                    await _open_or_refresh_investigation_page(
                        browser,
                        page_path,
                        bring_to_front=False,
                        open_if_missing=False,
                    )
                except InvestigationError as exc:
                    await _set_page_status(source_tab, str(exc), is_error=True)
                continue
            if result["action"] == "delete_page_monitor":
                investigation_id = str(
                    result.get("investigationId", "") or ""
                ).strip()
                monitor_id = str(
                    result.get("monitorId", "") or ""
                ).strip()
                source_tab = result.get("_source_tab")
                try:
                    investigation_service.delete_page_monitor(
                        investigation_id,
                        monitor_id,
                    )
                    await _save_in_place(
                        investigation_service, settings, source_tab, investigation_id
                    )
                except InvestigationError as exc:
                    await _set_page_status(source_tab, str(exc), is_error=True)
                continue
            if result["action"] == "attach_investigation_search":
                investigation_id = str(result.get("investigationId", "") or "").strip()
                search_run_id = str(result.get("searchRunId", "") or "").strip()
                source_tab = result.get("_source_tab")
                try:
                    investigation_service.attach_search(
                        investigation_id,
                        search_run_id,
                    )
                    page_path = _generate_investigation_page(
                        investigation_service,
                        settings,
                        investigation_id,
                    )
                    await _open_or_refresh_investigation_page(
                        browser,
                        page_path,
                        bring_to_front=False,
                        open_if_missing=False,
                    )
                except InvestigationError as exc:
                    await _set_page_status(source_tab, str(exc), is_error=True)
                continue
            if result["action"] == "clear_synthesix_history":
                database_removed = investigation_service.clear_search_history()
                removed = clear_synthesix_history()
                for investigation in investigation_service.list_investigations(
                    include_archived=True
                ):
                    page_path = _generate_investigation_page(
                        investigation_service,
                        settings,
                        investigation.id,
                    )
                    await _open_or_refresh_investigation_page(
                        browser,
                        page_path,
                        bring_to_front=False,
                        open_if_missing=False,
                    )
                await _set_home_status(
                    browser,
                    index_url,
                    "Synthesix history cleared "
                    f"({database_removed} searches and {removed} files removed).",
                )
                continue
            if result["action"] == "clear_browser_data":
                if _search_task_running(active_search_task):
                    await _set_home_status(
                        browser,
                        index_url,
                        "A search is running. Cancel it before clearing browser data.",
                        is_error=True,
                    )
                    continue
                try:
                    await search_browser_provider.clear_browser_data()
                    browser = await browser_manager.clear_browser_data()
                    browser_service = get_browser_service(browser)
                    home_tab = await _focus_or_open_home_tab(
                        browser,
                        index_url,
                        reuse_current_tab=True,
                    )
                    await home_tab.bring_to_front()
                    await _set_home_status(
                        browser,
                        index_url,
                        "Browser history, cookies, cache, and site data cleared.",
                    )
                except Exception:
                    logger.error("Unable to clear browser data.", exc_info=True)
                    await _set_home_status(
                        browser,
                        index_url,
                        "Browser data could not be cleared. Check the logs.",
                        is_error=True,
                    )
                continue
            original_query = str(result.get("value", "") or "").strip()
            filters = SearchFilters.from_payload(result.get("filters"))
            if not original_query and not filters.has_filters():
                return

            investigation_id = str(result.get("investigationId", "") or "").strip() or None
            if investigation_id:
                try:
                    investigation = investigation_service.get(investigation_id)
                    if investigation.status != "active":
                        raise InvestigationError(
                            "The selected investigation is no longer active."
                        )
                    active_investigation = investigation
                except InvestigationError as exc:
                    await _set_home_status(
                        browser,
                        index_url,
                        str(exc),
                        is_error=True,
                    )
                    continue

            automatic_dorks = bool(result.get("automaticDorks", True))
            if automatic_dorks and not is_advanced_query(original_query):
                logger.info("Parsing query to a smart query: %s", original_query)
            raw_query_variants = normalize_query_variants(
                original_query,
                result.get("queryVariants"),
                settings.max_query_variants,
            )
            parsed_query_variants = tuple(
                _prepare_base_query(
                    query,
                    automatic_dorks=automatic_dorks,
                )
                for query in raw_query_variants
            )
            parsed_base_query = parsed_query_variants[0]
            if parsed_base_query != original_query:
                logger.info("Smart query: %s", parsed_base_query)

            parsed_query = build_display_query(parsed_base_query, filters)
            engines = result.get("engines", settings.default_engines)
            num_results = result.get("numResults", settings.default_max_results)
            if _search_task_running(active_search_task):
                await _set_home_status(
                    browser,
                    index_url,
                    "A search is already running. "
                    "Cancel it or wait for it to finish.",
                    is_error=True,
                )
                continue
            await _set_home_search_running(browser, index_url, True)
            await _set_home_status(browser, index_url, "Search in progress...")
            active_search_task = _start_search_task(
                _run_search_action(
                    browser,
                    index_url,
                    {
                        "original_query": original_query,
                        "parsed_query": parsed_query,
                        "engines": engines,
                        "num_results": num_results,
                        "filters": filters,
                        "base_query": parsed_base_query,
                        "investigation_service": investigation_service,
                        "investigation_id": investigation_id,
                        "query_variants": parsed_query_variants,
                    },
                    search_browser_provider,
                )
            )

    finally:
        if _search_task_running(active_search_task):
            active_search_task.cancel()
            await asyncio.gather(active_search_task, return_exceptions=True)
        await search_browser_provider.stop()
        await browser_manager.stop()
        logger.info("Goodbye!")


async def perform_search(
    original_query: str,
    parsed_query: str,
    browser: uc.Browser,
    engines: dict,
    num_results: int,
    filters: SearchFilters | None = None,
    base_query: str | None = None,
    investigation_service: InvestigationService | None = None,
    investigation_id: str | None = None,
    query_variants: tuple[str, ...] | None = None,
    report_browser: uc.Browser | None = None,
):
    started_at = utc_now()
    try:
        search_result = await SearchOrchestrator().search(
            original_query,
            parsed_query,
            browser,
            engines,
            num_results,
            filters=filters,
            base_query=base_query,
            investigation_id=investigation_id,
            query_variants=query_variants,
        )
    except SynthesixError as exc:
        logger.error("Search failed.", exc_info=True)
        settings = get_settings()
        if settings.search_window_mode == "headless":
            artifact_path = await _open_robot_challenge_artifact(
                report_browser or browser,
                exc,
                settings,
            )
            if artifact_path is not None:
                return (
                    "Search stopped by an anti-robot challenge. "
                    f"Captured challenge opened: {artifact_path.name}."
                )
        return "Search failed. Check the logs for details."

    if investigation_service is not None:
        try:
            investigation_service.record_search(
                investigation_id=investigation_id,
                original_query=original_query,
                parsed_query=parsed_query,
                filters=(filters or SearchFilters()).to_payload(),
                engines=engines,
                requested_results=num_results,
                report_path=search_result.output_path,
                total_time=search_result.total_time,
                engine_errors=search_result.engine_errors,
                results=search_result.results,
                started_at=started_at,
            )
        except Exception:
            logger.error(
                "Search completed but could not be saved to the investigation database.",
                exc_info=True,
            )
            persistence_error = (
                "Search completed, but its investigation data could not be saved."
            )
        else:
            persistence_error = None
    else:
        persistence_error = None

    if (
        investigation_service is not None
        and investigation_id
        and persistence_error is None
    ):
        try:
            settings = get_settings()
            page_path = _generate_investigation_page(
                investigation_service,
                settings,
                investigation_id,
            )
            await _open_or_refresh_investigation_page(
                report_browser or browser,
                page_path,
                bring_to_front=False,
                open_if_missing=False,
            )
        except Exception:
            logger.debug(
                "Unable to refresh the open investigation page.",
                exc_info=True,
            )

    if search_result.output_path:
        result_tab = await get_browser_service(report_browser or browser).open_tab(
            Path(search_result.output_path).resolve().as_uri()
        )
        await result_tab.bring_to_front()
    return persistence_error

if __name__ == "__main__":
    cli_args = parse_cli_args()
    apply_cli_runtime_overrides(cli_args)
    configure_logging(cli_args)
    configure_event_loop_policy()
    asyncio.run(main())
