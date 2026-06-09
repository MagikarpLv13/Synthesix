import asyncio
import argparse
import hashlib
from pathlib import Path
import logging
import json
import os
import time
import sys
from urllib.parse import urlsplit
from browser_manager import HeadlessBrowserManager
from exceptions import InvestigationError, SynthesixError
from investigations import InvestigationRepository, InvestigationService
from investigations.repository import utc_now
from investigations.view import generate_investigation_page
from query_operators import SearchFilters, build_display_query
from search_orchestrator import SearchOrchestrator
from settings import AppSettings, get_settings
import zendriver as uc
from utils import (
    clear_synthesix_history,
    is_advanced_query,
    load_search_history,
    smart_parse,
)

logger = logging.getLogger(__name__)
_MISSING_HISTORY_SIGNATURE = object()


def _normalize_tab_url(url: str | None) -> str:
    return (url or "").split("#", 1)[0]


async def _open_tabs(browser: uc.Browser):
    try:
        await browser.update_targets()
        targets = await browser._get_targets()
        live_page_ids = {
            target.target_id
            for target in targets
            if target.type_ == "page"
        }
    except Exception:
        logger.debug("Unable to update browser targets", exc_info=True)
        return None

    return [
        tab
        for tab in browser.tabs
        if getattr(tab, "target_id", None) in live_page_ids
    ]


def _is_home_tab(tab, index_url: str) -> bool:
    return _normalize_tab_url(getattr(tab, "url", None)) == index_url


async def _consume_home_tab_action(
    tab,
    history_json: str,
    history_version: str,
    investigations_json: str = "[]",
    investigations_version: str = "",
):
    history_version_json = json.dumps(history_version)
    investigations_version_json = json.dumps(investigations_version)
    try:
        return await tab.evaluate(
            f"""
            (() => {{
                if (
                    !window.synthesixHome ||
                    typeof window.synthesixHome.consumeAction !== "function"
                ) {{
                    return {{ ready: false, action: null }};
                }}
                window.name = "synthesix-home";
                const nextHistoryVersion = {history_version_json};
                if (window.synthesixHome.historyVersion !== nextHistoryVersion) {{
                    window.synthesixHome.setHistory({history_json});
                    window.synthesixHome.historyVersion = nextHistoryVersion;
                }}
                const nextInvestigationsVersion = {investigations_version_json};
                if (
                    typeof window.synthesixHome.setInvestigations === "function" &&
                    window.synthesixHome.investigationsVersion !== nextInvestigationsVersion
                ) {{
                    window.synthesixHome.setInvestigations({investigations_json});
                    window.synthesixHome.investigationsVersion = nextInvestigationsVersion;
                }}
                return {{
                    ready: true,
                    action: window.synthesixHome.consumeAction()
                }};
            }})()
            """,
        )
    except Exception:
        logger.debug("Unable to read home tab action", exc_info=True)
        return None


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
    try:
        return await tab.evaluate(
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
        )
    except Exception:
        logger.debug("Unable to read page tab action", exc_info=True)
        return None


def _is_external_web_tab(tab) -> bool:
    try:
        return urlsplit(str(getattr(tab, "url", "") or "")).scheme in {
            "http",
            "https",
        }
    except ValueError:
        return False


async def _install_and_consume_save_overlay(
    tab,
    investigation: dict | None = None,
):
    investigation = investigation or {}
    context_json = json.dumps(
        {
            "id": str(investigation.get("id", "")),
            "title": str(investigation.get("title", "")),
        },
        ensure_ascii=True,
    )
    try:
        return await tab.evaluate(
            f"""
            (() => {{
                const context = {context_json};
                const hostId = "__synthesix-save-overlay";
                let host = document.getElementById(hostId);
                if (!host) {{
                    host = document.createElement("div");
                    host.id = hostId;
                    Object.assign(host.style, {{
                        all: "initial",
                        position: "fixed",
                        right: "18px",
                        bottom: "18px",
                        zIndex: "2147483647",
                        pointerEvents: "auto"
                    }});
                    const shadow = host.attachShadow({{ mode: "open" }});
                    const button = document.createElement("button");
                    button.type = "button";
                    Object.assign(button.style, {{
                        all: "initial",
                        boxSizing: "border-box",
                        display: "inline-flex",
                        alignItems: "center",
                        justifyContent: "center",
                        gap: "8px",
                        height: "42px",
                        padding: "0 14px 0 11px",
                        border: "1px solid #1D4ED8",
                        borderRadius: "6px",
                        background: "#2563EB",
                        color: "#FFFFFF",
                        boxShadow: "0 10px 28px rgba(15, 23, 42, 0.28)",
                        font: "700 14px Arial, sans-serif",
                        lineHeight: "1",
                        cursor: "pointer",
                        whiteSpace: "nowrap",
                        transition: (
                            "background-color 140ms ease, border-color 140ms ease, "
                            + "box-shadow 140ms ease, transform 140ms ease"
                        )
                    }});

                    const svgNamespace = "http://www.w3.org/2000/svg";
                    const mark = document.createElementNS(svgNamespace, "svg");
                    mark.setAttribute("viewBox", "0 0 128 128");
                    mark.setAttribute("aria-hidden", "true");
                    Object.assign(mark.style, {{
                        display: "block",
                        width: "20px",
                        height: "20px",
                        flex: "0 0 20px"
                    }});
                    for (let index = 0; index < 10; index += 1) {{
                        const blade = document.createElementNS(
                            svgNamespace,
                            "path"
                        );
                        blade.setAttribute(
                            "d",
                            "M58 12 69 6l9 38-12 9-9-7z"
                        );
                        blade.setAttribute(
                            "transform",
                            `rotate(${{index * 36}} 64 64)`
                        );
                        blade.setAttribute(
                            "fill",
                            index % 2 === 0 ? "#FFFFFF" : "#67E8F9"
                        );
                        mark.appendChild(blade);
                    }}
                    const markCenter = document.createElementNS(
                        svgNamespace,
                        "circle"
                    );
                    markCenter.setAttribute("cx", "64");
                    markCenter.setAttribute("cy", "64");
                    markCenter.setAttribute("r", "14");
                    markCenter.setAttribute("fill", "#FFFFFF");
                    mark.appendChild(markCenter);

                    const label = document.createElement("span");
                    label.textContent = "Save page";
                    label.style.display = "block";
                    button.append(mark, label);

                    const stateColors = {{
                        idle: ["#2563EB", "#1D4ED8"],
                        idleHover: ["#1D4ED8", "#1E40AF"],
                        saving: ["#475569", "#334155"],
                        saved: ["#059669", "#047857"],
                        savedHover: ["#047857", "#065F46"],
                        error: ["#DC2626", "#B91C1C"],
                        errorHover: ["#B91C1C", "#991B1B"]
                    }};
                    host.__synthesixSetButtonState = (
                        state,
                        text,
                        hovered = false
                    ) => {{
                        const colorKey = hovered
                            ? `${{state}}Hover`
                            : state;
                        const colors = stateColors[colorKey] || stateColors[state];
                        button.dataset.state = state;
                        button.disabled = state === "saving";
                        label.textContent = text;
                        button.style.background = colors[0];
                        button.style.borderColor = colors[1];
                        button.style.cursor = (
                            state === "saving" ? "wait" : "pointer"
                        );
                    }};
                    button.addEventListener("mouseenter", () => {{
                        if (!button.disabled) {{
                            host.__synthesixSetButtonState(
                                button.dataset.state,
                                label.textContent,
                                true
                            );
                            button.style.transform = "translateY(-1px)";
                            button.style.boxShadow = (
                                "0 12px 30px rgba(15, 23, 42, 0.34)"
                            );
                        }}
                    }});
                    button.addEventListener("mouseleave", () => {{
                        host.__synthesixSetButtonState(
                            button.dataset.state,
                            label.textContent
                        );
                        button.style.transform = "translateY(0)";
                        button.style.boxShadow = (
                            "0 10px 28px rgba(15, 23, 42, 0.28)"
                        );
                    }});
                    button.addEventListener("focus", () => {{
                        button.style.outline = "3px solid rgba(6, 182, 212, 0.55)";
                        button.style.outlineOffset = "2px";
                    }});
                    button.addEventListener("blur", () => {{
                        button.style.outline = "none";
                    }});
                    button.addEventListener("click", () => {{
                        if (!host.dataset.investigationId) {{
                            window.__synthesixSavePageAction = {{
                                action: "focus_home"
                            }};
                            return;
                        }}
                        if (button.dataset.state === "saved") {{
                            return;
                        }}
                        host.__synthesixSetButtonState("saving", "Saving...");
                        window.__synthesixSavePageAction = {{
                            action: "save_page_to_investigation",
                            investigationId: host.dataset.investigationId,
                            page: {{
                                url: window.location.href,
                                title: document.title || window.location.hostname,
                                description: (
                                    document.querySelector(
                                        'meta[name="description" i]'
                                    )?.content || ""
                                ),
                                referrer: document.referrer || ""
                            }}
                        }};
                    }});
                    shadow.appendChild(button);
                    (document.documentElement || document.body).appendChild(host);
                }}

                const pageKey = `${{context.id}}|${{window.location.href}}`;
                const contextChanged = host.dataset.pageKey !== pageKey;
                host.dataset.investigationId = context.id;
                host.dataset.pageKey = pageKey;
                const button = host.shadowRoot.querySelector("button");
                const statusUntil = Number(host.dataset.statusUntil || 0);
                if (contextChanged) {{
                    host.dataset.saved = "0";
                    host.dataset.statusUntil = "0";
                    if (context.id) {{
                        host.__synthesixSetButtonState("idle", "Save page");
                        button.title = (
                            `Save this page to "${{context.title}}"`
                        );
                    }} else {{
                        host.__synthesixSetButtonState(
                            "idle",
                            "Select investigation"
                        );
                        button.title = (
                            "Open Synthesix to select an investigation before saving this page"
                        );
                    }}
                }} else if (
                    button.dataset.state === "error"
                    && Date.now() >= statusUntil
                ) {{
                    host.__synthesixSetButtonState("idle", "Save page");
                }}

                if (
                    context.id
                    && host.dataset.observationKey !== pageKey
                    && !window.__synthesixSavePageAction
                ) {{
                    host.dataset.observationKey = pageKey;
                    window.__synthesixSavePageAction = {{
                        action: "observe_saved_page",
                        investigationId: context.id,
                        page: {{
                            url: window.location.href
                        }}
                    }};
                }}

                const action = window.__synthesixSavePageAction || null;
                window.__synthesixSavePageAction = null;
                return action;
            }})()
            """,
        )
    except Exception:
        logger.debug("Unable to install or read the save-page overlay", exc_info=True)
        return None


async def _set_save_overlay_status(
    tab,
    message: str,
    *,
    is_error: bool = False,
) -> None:
    if tab is None:
        return
    try:
        await tab.evaluate(
            f"""
            (() => {{
                const host = document.getElementById("__synthesix-save-overlay");
                const button = host?.shadowRoot?.querySelector("button");
                if (!button || !host.__synthesixSetButtonState) {{
                    return;
                }}
                const isError = {json.dumps(is_error)};
                host.dataset.saved = isError ? "0" : "1";
                host.__synthesixSetButtonState(
                    isError ? "error" : "saved",
                    {json.dumps(message)}
                );
                host.dataset.statusUntil = isError
                    ? String(Date.now() + 1800)
                    : "0";
            }})()
            """,
        )
    except Exception:
        logger.debug("Unable to update the save-page overlay", exc_info=True)


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
    try:
        await tab.evaluate(
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
        )
    except Exception:
        logger.debug("Unable to update page status", exc_info=True)


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
        tab = await browser.get(page_url, new_tab=True)
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
        try:
            await tab.evaluate(
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
            )
        except Exception:
            logger.debug("Unable to update the home status", exc_info=True)


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
        try:
            await tab.evaluate(
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
            )
        except Exception:
            logger.debug(
                "Unable to update the selected investigation",
                exc_info=True,
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

    home_tab = await browser.get(index_url, new_tab=not reuse_current_tab)
    await home_tab.bring_to_front()
    return home_tab


async def wait_for_home_action(
    browser: uc.Browser,
    index_url: str,
    settings: AppSettings | None = None,
    investigations_json: str = "[]",
    investigations_version: str = "",
    overlay_investigation: dict | None = None,
):
    settings = settings or get_settings()
    empty_since = None
    history_cache = {}

    while True:
        if getattr(browser, "stopped", False):
            return {"action": "quit"}

        tabs = await _open_tabs(browser)
        if tabs is None:
            await asyncio.sleep(settings.home_poll_interval)
            continue

        if not tabs:
            if empty_since is None:
                empty_since = time.monotonic()
            elif time.monotonic() - empty_since >= settings.empty_tabs_grace_seconds:
                return {"action": "quit"}
            await asyncio.sleep(settings.home_poll_interval)
            continue

        empty_since = None

        home_tabs = [tab for tab in tabs if _is_home_tab(tab, index_url)]
        if home_tabs:
            history_json, history_version = _cached_history_payload(settings, history_cache)
            for tab in home_tabs:
                state = await _consume_home_tab_action(
                    tab,
                    history_json,
                    history_version,
                    investigations_json,
                    investigations_version,
                )
                if state and state.get("action"):
                    return state["action"]

        for tab in tabs:
            if tab in home_tabs:
                continue
            if _is_external_web_tab(tab):
                action = await _install_and_consume_save_overlay(
                    tab,
                    overlay_investigation,
                )
            else:
                action = await _consume_page_tab_action(tab)
            if not action:
                continue
            if action.get("action") == "focus_home":
                await _focus_or_open_home_tab(browser, index_url, home_tabs)
                break
            action["_source_tab"] = tab
            return action

        await asyncio.sleep(settings.home_poll_interval)


async def main():
    settings = get_settings()
    investigation_service = InvestigationService(
        InvestigationRepository(settings.database_path)
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
    home_tab = await _focus_or_open_home_tab(browser, index_url, reuse_current_tab=True)
    await home_tab.bring_to_front()
    active_investigation = None

    try:
        while True:
            investigations_json, investigations_version = _investigation_payload(
                investigation_service
            )
            result = await wait_for_home_action(
                browser,
                index_url,
                settings=settings,
                investigations_json=investigations_json,
                investigations_version=investigations_version,
                overlay_investigation=(
                    {
                        "id": active_investigation.id,
                        "title": active_investigation.title,
                    }
                    if active_investigation is not None
                    else None
                ),
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
                        await _set_save_overlay_status(source_tab, "Saved")
                except InvestigationError:
                    logger.debug(
                        "Unable to record a saved-page revisit",
                        exc_info=True,
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
                    await _set_save_overlay_status(
                        source_tab,
                        "Saved",
                    )
                    await _set_home_status(
                        browser,
                        index_url,
                        f'Page saved: {saved.title or saved.url}',
                    )
                except InvestigationError as exc:
                    await _set_save_overlay_status(
                        source_tab,
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
            if result["action"] == "remove_saved_page":
                investigation_id = str(result.get("investigationId", "") or "").strip()
                result_id = str(result.get("resultId", "") or "").strip()
                source_tab = result.get("_source_tab")
                try:
                    investigation_service.remove_saved_page(
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
                try:
                    browser = await browser_manager.clear_browser_data()
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

            if not is_advanced_query(original_query):
                logger.info("Parsing query to a smart query: %s", original_query)
                parsed_base_query = smart_parse(original_query)
                logger.info("Smart query: %s", parsed_base_query)
            else:
                parsed_base_query = original_query

            parsed_query = build_display_query(parsed_base_query, filters)
            engines = result.get("engines", settings.default_engines)
            num_results = result.get("numResults", settings.default_max_results)
            persistence_error = await perform_search(
                original_query,
                parsed_query,
                browser,
                engines,
                num_results,
                filters,
                parsed_base_query,
                investigation_service=investigation_service,
                investigation_id=investigation_id,
            )
            if persistence_error:
                await _set_home_status(
                    browser,
                    index_url,
                    persistence_error,
                    is_error=True,
                )

    finally:
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
        )
    except SynthesixError:
        logger.error("Search failed.", exc_info=True)
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
                browser,
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
        result_tab = await browser.get(Path(search_result.output_path).resolve().as_uri(), new_tab=True)
        await result_tab.bring_to_front()
    return persistence_error

if __name__ == "__main__":
    cli_args = parse_cli_args()
    apply_cli_runtime_overrides(cli_args)
    configure_logging(cli_args)
    configure_event_loop_policy()
    asyncio.run(main())
