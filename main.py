import asyncio
import argparse
import hashlib
import importlib.metadata
from pathlib import Path
import logging
import json
import os
import shutil
import time
import sys
from urllib.parse import urlsplit
from uuid import uuid4
from browser_manager import HeadlessBrowserManager
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
from exceptions import EvidenceCaptureError, InvestigationError, SynthesixError
from investigations import InvestigationRepository, InvestigationService
from investigations.repository import utc_now
from investigations.monitoring_view import generate_page_comparison_report
from investigations.search_view import generate_local_search_page
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
                    const toolbar = document.createElement("div");
                    Object.assign(toolbar.style, {{
                        all: "initial",
                        display: "flex",
                        alignItems: "center",
                        gap: "8px"
                    }});
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
                            page: host.__synthesixPagePayload()
                        }};
                    }});

                    const archiveButton = document.createElement("button");
                    archiveButton.type = "button";
                    archiveButton.setAttribute(
                        "aria-label",
                        "Save page with HTML archive"
                    );
                    Object.assign(archiveButton.style, {{
                        all: "initial",
                        boxSizing: "border-box",
                        display: "inline-flex",
                        alignItems: "center",
                        justifyContent: "center",
                        width: "42px",
                        height: "42px",
                        border: "1px solid #0E7490",
                        borderRadius: "6px",
                        background: "#0891B2",
                        color: "#FFFFFF",
                        boxShadow: "0 10px 28px rgba(15, 23, 42, 0.28)",
                        cursor: "pointer",
                        transition: (
                            "background-color 140ms ease, border-color 140ms ease, "
                            + "box-shadow 140ms ease, transform 140ms ease"
                        )
                    }});
                    const archiveIcon = document.createElementNS(
                        svgNamespace,
                        "svg"
                    );
                    archiveIcon.setAttribute("viewBox", "0 0 24 24");
                    archiveIcon.setAttribute("aria-hidden", "true");
                    Object.assign(archiveIcon.style, {{
                        display: "block",
                        width: "20px",
                        height: "20px"
                    }});
                    const archivePath = document.createElementNS(
                        svgNamespace,
                        "path"
                    );
                    archivePath.setAttribute(
                        "d",
                        "M5 3h11l3 3v15H5zM8 3v6h8V3M8 14h8M8 18h6"
                    );
                    archivePath.setAttribute("fill", "none");
                    archivePath.setAttribute("stroke", "currentColor");
                    archivePath.setAttribute("stroke-width", "2");
                    archivePath.setAttribute("stroke-linejoin", "round");
                    archiveIcon.appendChild(archivePath);
                    archiveButton.appendChild(archiveIcon);

                    const archiveColors = {{
                        idle: ["#0891B2", "#0E7490"],
                        idleHover: ["#0E7490", "#155E75"],
                        archiving: ["#475569", "#334155"],
                        archived: ["#059669", "#047857"],
                        archivedHover: ["#047857", "#065F46"],
                        error: ["#DC2626", "#B91C1C"],
                        errorHover: ["#B91C1C", "#991B1B"]
                    }};
                    host.__synthesixSetArchiveState = (
                        state,
                        tooltip = "Save page with HTML archive",
                        hovered = false
                    ) => {{
                        const key = hovered ? `${{state}}Hover` : state;
                        const colors = archiveColors[key] || archiveColors[state];
                        archiveButton.dataset.state = state;
                        archiveButton.disabled = state === "archiving";
                        archiveButton.title = tooltip;
                        archiveButton.style.background = colors[0];
                        archiveButton.style.borderColor = colors[1];
                        archiveButton.style.cursor = (
                            state === "archiving" ? "wait" : "pointer"
                        );
                    }};
                    archiveButton.addEventListener("click", () => {{
                        if (!host.dataset.investigationId) {{
                            window.__synthesixSavePageAction = {{
                                action: "focus_home"
                            }};
                            return;
                        }}
                        host.__synthesixSetArchiveState(
                            "archiving",
                            "Saving HTML archive..."
                        );
                        window.__synthesixSavePageAction = {{
                            action: "archive_page_to_investigation",
                            investigationId: host.dataset.investigationId,
                            page: host.__synthesixPagePayload()
                        }};
                    }});
                    archiveButton.addEventListener("mouseenter", () => {{
                        if (!archiveButton.disabled) {{
                            host.__synthesixSetArchiveState(
                                archiveButton.dataset.state,
                                archiveButton.title,
                                true
                            );
                            archiveButton.style.transform = "translateY(-1px)";
                        }}
                    }});
                    archiveButton.addEventListener("mouseleave", () => {{
                        host.__synthesixSetArchiveState(
                            archiveButton.dataset.state,
                            archiveButton.title
                        );
                        archiveButton.style.transform = "translateY(0)";
                    }});

                    const captureButton = document.createElement("button");
                    captureButton.type = "button";
                    captureButton.setAttribute(
                        "aria-label",
                        "Capture screenshot"
                    );
                    Object.assign(captureButton.style, {{
                        all: "initial",
                        boxSizing: "border-box",
                        display: "inline-flex",
                        alignItems: "center",
                        justifyContent: "center",
                        width: "42px",
                        height: "42px",
                        border: "1px solid #334155",
                        borderRadius: "6px",
                        background: "#0F172A",
                        color: "#FFFFFF",
                        boxShadow: "0 10px 28px rgba(15, 23, 42, 0.28)",
                        cursor: "pointer",
                        transition: (
                            "background-color 140ms ease, border-color 140ms ease, "
                            + "box-shadow 140ms ease, transform 140ms ease"
                        )
                    }});
                    const camera = document.createElementNS(
                        svgNamespace,
                        "svg"
                    );
                    camera.setAttribute("viewBox", "0 0 24 24");
                    camera.setAttribute("aria-hidden", "true");
                    Object.assign(camera.style, {{
                        display: "block",
                        width: "20px",
                        height: "20px"
                    }});
                    const cameraBody = document.createElementNS(
                        svgNamespace,
                        "path"
                    );
                    cameraBody.setAttribute(
                        "d",
                        "M14.5 4 16 7h3a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h3l1.5-3z"
                    );
                    cameraBody.setAttribute("fill", "none");
                    cameraBody.setAttribute("stroke", "currentColor");
                    cameraBody.setAttribute("stroke-width", "2");
                    cameraBody.setAttribute("stroke-linejoin", "round");
                    const cameraLens = document.createElementNS(
                        svgNamespace,
                        "circle"
                    );
                    cameraLens.setAttribute("cx", "12");
                    cameraLens.setAttribute("cy", "13");
                    cameraLens.setAttribute("r", "3");
                    cameraLens.setAttribute("fill", "none");
                    cameraLens.setAttribute("stroke", "currentColor");
                    cameraLens.setAttribute("stroke-width", "2");
                    camera.append(cameraBody, cameraLens);
                    captureButton.appendChild(camera);

                    const captureMenu = document.createElement("div");
                    Object.assign(captureMenu.style, {{
                        all: "initial",
                        boxSizing: "border-box",
                        display: "none",
                        position: "absolute",
                        right: "0",
                        bottom: "50px",
                        width: "180px",
                        padding: "6px",
                        border: "1px solid #CBD5E1",
                        borderRadius: "6px",
                        background: "#FFFFFF",
                        boxShadow: "0 14px 32px rgba(15, 23, 42, 0.24)",
                        font: "600 13px Arial, sans-serif"
                    }});
                    const captureNameInput = document.createElement("input");
                    captureNameInput.type = "text";
                    captureNameInput.maxLength = 120;
                    captureNameInput.placeholder = "Capture name (optional)";
                    captureNameInput.setAttribute(
                        "aria-label",
                        "Capture name"
                    );
                    Object.assign(captureNameInput.style, {{
                        all: "initial",
                        boxSizing: "border-box",
                        display: "block",
                        width: "100%",
                        marginBottom: "5px",
                        padding: "8px 9px",
                        border: "1px solid #CBD5E1",
                        borderRadius: "4px",
                        background: "#FFFFFF",
                        color: "#0F172A",
                        font: "500 13px Arial, sans-serif"
                    }});
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

                    const createCaptureChoice = (labelText, scope) => {{
                        const choice = document.createElement("button");
                        choice.type = "button";
                        choice.textContent = labelText;
                        Object.assign(choice.style, {{
                            all: "initial",
                            boxSizing: "border-box",
                            display: "block",
                            width: "100%",
                            padding: "9px 10px",
                            borderRadius: "4px",
                            color: "#0F172A",
                            font: "600 13px Arial, sans-serif",
                            cursor: "pointer"
                        }});
                        choice.addEventListener("mouseenter", () => {{
                            choice.style.background = "#EFF6FF";
                            choice.style.color = "#1D4ED8";
                        }});
                        choice.addEventListener("mouseleave", () => {{
                            choice.style.background = "transparent";
                            choice.style.color = "#0F172A";
                        }});
                        choice.addEventListener("click", () => {{
                            captureMenu.style.display = "none";
                            if (!host.dataset.investigationId) {{
                                window.__synthesixSavePageAction = {{
                                    action: "focus_home"
                                }};
                                return;
                            }}
                            if (scope === "viewport") {{
                                host.__synthesixQueueCapture("viewport", {{
                                    x: window.scrollX,
                                    y: window.scrollY,
                                    width: window.innerWidth,
                                    height: window.innerHeight
                                }}, captureNameInput.value);
                            }} else {{
                                host.__synthesixStartRegionSelection(
                                    captureNameInput.value
                                );
                            }}
                        }});
                        return choice;
                    }};
                    captureMenu.append(
                        captureNameInput,
                        createCaptureChoice("Visible area", "viewport"),
                        createCaptureChoice("Select area", "region")
                    );

                    const captureColors = {{
                        idle: ["#0F172A", "#334155"],
                        idleHover: ["#334155", "#475569"],
                        capturing: ["#475569", "#334155"],
                        captured: ["#059669", "#047857"],
                        capturedHover: ["#047857", "#065F46"],
                        error: ["#DC2626", "#B91C1C"],
                        errorHover: ["#B91C1C", "#991B1B"]
                    }};
                    host.__synthesixSetCaptureState = (
                        state,
                        tooltip = "Capture screenshot",
                        hovered = false
                    ) => {{
                        const key = hovered ? `${{state}}Hover` : state;
                        const colors = captureColors[key] || captureColors[state];
                        captureButton.dataset.state = state;
                        captureButton.disabled = state === "capturing";
                        captureButton.title = tooltip;
                        captureButton.style.background = colors[0];
                        captureButton.style.borderColor = colors[1];
                        captureButton.style.cursor = (
                            state === "capturing" ? "wait" : "pointer"
                        );
                    }};
                    host.__synthesixQueueCapture = (
                        scope,
                        selection,
                        captureName
                    ) => {{
                        host.__synthesixSetCaptureState(
                            "capturing",
                            "Capturing evidence..."
                        );
                        host.style.display = "none";
                        window.requestAnimationFrame(() => {{
                            window.requestAnimationFrame(() => {{
                                window.__synthesixSavePageAction = {{
                                    action: "capture_evidence_to_investigation",
                                    investigationId: host.dataset.investigationId,
                                    captureScope: scope,
                                    captureName: String(captureName || "").trim(),
                                    selection,
                                    page: host.__synthesixPagePayload()
                                }};
                                captureNameInput.value = "";
                            }});
                        }});
                    }};
                    host.__synthesixStartRegionSelection = (captureName) => {{
                        host.style.display = "none";
                        const selectionHost = document.createElement("div");
                        selectionHost.id = "__synthesix-evidence-selection";
                        Object.assign(selectionHost.style, {{
                            all: "initial",
                            position: "fixed",
                            inset: "0",
                            zIndex: "2147483647",
                            cursor: "crosshair",
                            background: "rgba(15, 23, 42, 0.16)",
                            userSelect: "none",
                            touchAction: "none"
                        }});
                        const selectionShadow = selectionHost.attachShadow({{
                            mode: "closed"
                        }});
                        const hint = document.createElement("div");
                        hint.textContent = "Drag to select evidence · Esc to cancel";
                        Object.assign(hint.style, {{
                            position: "fixed",
                            top: "16px",
                            left: "50%",
                            transform: "translateX(-50%)",
                            padding: "9px 12px",
                            borderRadius: "6px",
                            background: "#0F172A",
                            color: "#FFFFFF",
                            boxShadow: "0 8px 24px rgba(15, 23, 42, 0.3)",
                            font: "600 13px Arial, sans-serif",
                            pointerEvents: "none"
                        }});
                        const selectionBox = document.createElement("div");
                        Object.assign(selectionBox.style, {{
                            display: "none",
                            position: "fixed",
                            border: "2px solid #06B6D4",
                            background: "rgba(6, 182, 212, 0.12)",
                            boxShadow: "0 0 0 9999px rgba(15, 23, 42, 0.38)",
                            pointerEvents: "none"
                        }});
                        selectionShadow.append(hint, selectionBox);

                        let startX = 0;
                        let startY = 0;
                        let selecting = false;
                        const cleanup = (restoreToolbar) => {{
                            document.removeEventListener(
                                "keydown",
                                onKeyDown,
                                true
                            );
                            selectionHost.remove();
                            if (restoreToolbar) {{
                                host.style.display = "block";
                            }}
                        }};
                        const onKeyDown = (event) => {{
                            if (event.key !== "Escape") {{
                                return;
                            }}
                            event.preventDefault();
                            cleanup(true);
                        }};
                        document.addEventListener("keydown", onKeyDown, true);
                        selectionHost.addEventListener("pointerdown", (event) => {{
                            event.preventDefault();
                            selecting = true;
                            startX = event.clientX;
                            startY = event.clientY;
                            selectionBox.style.display = "block";
                            try {{
                                selectionHost.setPointerCapture(event.pointerId);
                            }} catch (_error) {{
                                // Synthetic events and older browsers may not expose capture.
                            }}
                        }});
                        selectionHost.addEventListener("pointermove", (event) => {{
                            if (!selecting) {{
                                return;
                            }}
                            const left = Math.min(startX, event.clientX);
                            const top = Math.min(startY, event.clientY);
                            selectionBox.style.left = `${{left}}px`;
                            selectionBox.style.top = `${{top}}px`;
                            selectionBox.style.width = (
                                `${{Math.abs(event.clientX - startX)}}px`
                            );
                            selectionBox.style.height = (
                                `${{Math.abs(event.clientY - startY)}}px`
                            );
                        }});
                        selectionHost.addEventListener("pointerup", (event) => {{
                            if (!selecting) {{
                                return;
                            }}
                            selecting = false;
                            const left = Math.min(startX, event.clientX);
                            const top = Math.min(startY, event.clientY);
                            const width = Math.abs(event.clientX - startX);
                            const height = Math.abs(event.clientY - startY);
                            cleanup(false);
                            if (width < 8 || height < 8) {{
                                host.style.display = "block";
                                return;
                            }}
                            host.__synthesixQueueCapture(
                                "region",
                                {{
                                    x: left + window.scrollX,
                                    y: top + window.scrollY,
                                    width,
                                    height
                                }},
                                captureName
                            );
                        }});
                        (document.documentElement || document.body).appendChild(
                            selectionHost
                        );
                    }};

                    captureButton.addEventListener("click", () => {{
                        if (!host.dataset.investigationId) {{
                            window.__synthesixSavePageAction = {{
                                action: "focus_home"
                            }};
                            return;
                        }}
                        captureMenu.style.display = (
                            captureMenu.style.display === "none"
                                ? "block"
                                : "none"
                        );
                        if (
                            captureMenu.style.display === "block"
                            && !captureNameInput.value.trim()
                        ) {{
                            captureNameInput.value = (
                                host.__synthesixDefaultCaptureName()
                            );
                        }}
                    }});
                    captureButton.addEventListener("mouseenter", () => {{
                        if (!captureButton.disabled) {{
                            host.__synthesixSetCaptureState(
                                captureButton.dataset.state,
                                captureButton.title,
                                true
                            );
                            captureButton.style.transform = "translateY(-1px)";
                        }}
                    }});
                    captureButton.addEventListener("mouseleave", () => {{
                        host.__synthesixSetCaptureState(
                            captureButton.dataset.state,
                            captureButton.title
                        );
                        captureButton.style.transform = "translateY(0)";
                    }});
                    toolbar.append(button, archiveButton, captureButton);
                    shadow.append(toolbar, captureMenu);
                    (document.documentElement || document.body).appendChild(host);
                }}

                const pageKey = `${{context.id}}|${{window.location.href}}`;
                const contextChanged = host.dataset.pageKey !== pageKey;
                host.dataset.investigationId = context.id;
                host.dataset.pageKey = pageKey;
                const button = host.shadowRoot.querySelector("button");
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
                    host.__synthesixSetButtonState("idle", "Save page");
                }}
                if (
                    ["captured", "error"].includes(
                        host.shadowRoot.querySelector(
                            'button[aria-label="Capture screenshot"]'
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
                        host.shadowRoot.querySelector(
                            'button[aria-label="Save page with HTML archive"]'
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


async def _set_evidence_overlay_status(
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
        )
    except Exception:
        logger.debug("Unable to update the evidence overlay", exc_info=True)


async def _set_archive_overlay_status(
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
        )
    except Exception:
        logger.debug("Unable to update the page archive overlay", exc_info=True)


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
        captured_png = await capture_png(tab, png_path, selection)
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
    except Exception as exc:
        await asyncio.to_thread(shutil.rmtree, capture_dir, True)
        if isinstance(exc, InvestigationError):
            raise
        raise EvidenceCaptureError(
            f"Evidence capture failed: {exc}"
        ) from exc

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


async def _delete_evidence_capture(
    service: InvestigationService,
    settings: AppSettings,
    investigation_id: str,
    capture_id: str,
) -> None:
    capture = service.get_evidence_capture(investigation_id, capture_id)
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
    service.delete_evidence_capture(investigation_id, capture_id)


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
    try:
        await tab.evaluate(
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
        )
    except Exception:
        logger.debug("Unable to update evidence verification status", exc_info=True)


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
                    report_tab = await browser.get(
                        output_path.resolve().as_uri(),
                        new_tab=True,
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
                        await _set_save_overlay_status(source_tab, "Saved")
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
                    await _set_save_overlay_status(source_tab, "Saved")
                    archive_message = (
                        "Archived and compared"
                        if comparison is not None
                        else "Page archived"
                    )
                    await _set_archive_overlay_status(
                        source_tab,
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
                    await _set_archive_overlay_status(
                        source_tab,
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
                    await _set_save_overlay_status(source_tab, "Saved")
                    await _set_evidence_overlay_status(
                        source_tab,
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
                    await _set_evidence_overlay_status(
                        source_tab,
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

            automatic_dorks = bool(result.get("automaticDorks", True))
            if automatic_dorks and not is_advanced_query(original_query):
                logger.info("Parsing query to a smart query: %s", original_query)
            parsed_base_query = _prepare_base_query(
                original_query,
                automatic_dorks=automatic_dorks,
            )
            if parsed_base_query != original_query:
                logger.info("Smart query: %s", parsed_base_query)

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
