"""Shared presentational render helpers for Synthesix generated pages.

This module is intentionally pure: it performs HTML rendering only, with no path
resolution, settings access, or I/O. Callers compute asset prefixes and hrefs and
pass them in. Visible English text is the i18n source language; ``i18n.js``
translates it at runtime, so emit plain English copy here.

The same primitives back the result report, history page, local archive, and
investigation workspace so every surface shares one button/card/badge/chip
vocabulary (the "cockpit" design system).
"""

from __future__ import annotations

from html import escape
from typing import Iterable, Mapping, Sequence
from urllib.parse import urlsplit

__all__ = [
    "esc",
    "icon",
    "render_page",
    "topbar",
    "context_bar",
    "insight_grid",
    "result_card",
    "chip",
    "score_badge",
    "provenance",
    "empty_state",
    "keyboard_hint",
    "domain_of",
    "score_level",
    "page_behavior_script",
]


# --- low-level -------------------------------------------------------------

def esc(value: object) -> str:
    """HTML-escape a value, quoting attributes safely."""
    return escape(str(value), quote=True)


_ICON_PATHS = {
    "search": '<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.7" y2="16.7"/>',
    "external": (
        '<path d="M11 7H6a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h9a2 2 0 0 0 2-2v-5"/>'
        '<line x1="10" y1="14" x2="20" y2="4"/><polyline points="15 4 20 4 20 9"/>'
    ),
    "bookmark": '<path d="M6 4h12a1 1 0 0 1 1 1v15l-7-4-7 4V5a1 1 0 0 1 1-1z"/>',
    "shield": (
        '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z"/>'
        '<path d="M9 12l2 2 4-4"/>'
    ),
    "globe": (
        '<circle cx="12" cy="12" r="9"/><line x1="3" y1="12" x2="21" y2="12"/>'
        '<path d="M12 3a14 14 0 0 1 0 18 14 14 0 0 1 0-18"/>'
    ),
    "refresh": (
        '<path d="M20 11a8 8 0 1 0-2.3 5.4"/><polyline points="20 4 20 11 13 11"/>'
    ),
    "route": (
        '<circle cx="6" cy="19" r="2"/><circle cx="18" cy="5" r="2"/>'
        '<path d="M8 19h6a4 4 0 0 0 0-8H10a4 4 0 0 1 0-8h6"/>'
    ),
    "clock": '<circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15 14"/>',
    "folder": (
        '<path d="M4 5h5l2 2h9a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1z"/>'
    ),
}


def icon(name: str) -> str:
    """Return an inline, dependency-free SVG icon sized to the current text."""
    path = _ICON_PATHS.get(name, "")
    return (
        '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true">{path}</svg>'
    )


def domain_of(url: str) -> str:
    """Extract a bare hostname for display; empty string when not http(s)."""
    try:
        parts = urlsplit(str(url))
    except ValueError:
        return ""
    if parts.scheme not in ("http", "https"):
        return ""
    host = parts.hostname or ""
    return host[4:] if host.startswith("www.") else host


def score_level(score: float) -> str:
    """Map a numeric relevance score to a semantic accent level."""
    if score >= 8.0:
        return "strong"
    if score >= 5.0:
        return "good"
    if score >= 2.0:
        return "moderate"
    return "weak"


# --- components ------------------------------------------------------------

def chip(label: str, *, tone: str = "neutral", icon_name: str | None = None,
         title: str | None = None) -> str:
    glyph = icon(icon_name) if icon_name else ""
    title_attr = f' title="{esc(title)}"' if title else ""
    return (
        f'<span class="chip chip--{esc(tone)}"{title_attr}>'
        f'{glyph}<span>{esc(label)}</span></span>'
    )


def score_badge(score_text: str, level: str, breakdown_html: str = "",
                note: str = "") -> str:
    """A compact score pill; expandable when a breakdown is provided."""
    if breakdown_html:
        note_html = f'<small class="score-note">{esc(note)}</small>' if note else ""
        return (
            f'<details class="score score--{esc(level)}">'
            f'<summary><span class="score__value">{esc(score_text)}</span></summary>'
            f'<ul class="score__list">{breakdown_html}</ul>{note_html}</details>'
        )
    return (
        f'<span class="score score--{esc(level)}">'
        f'<span class="score__value">{esc(score_text)}</span></span>'
    )


def provenance(label: str, detail: str, *, icon_name: str = "route") -> str:
    return (
        f'<span class="provenance">{icon(icon_name)}'
        f'<span class="provenance__label">{esc(label)}</span>'
        f'<span class="provenance__detail">{esc(detail)}</span></span>'
    )


def result_card(*, title: str, url: str, snippet: str = "", domain: str = "",
                meta_html: str = "", actions_html: str = "",
                accent_level: str = "", triage: bool = True,
                safe_url: str | None = None) -> str:
    """A scannable result row used by reports and the local archive.

    ``url`` is the display/link target; pass ``safe_url`` when the caller has
    validated it (otherwise the link is rendered inert).
    """
    href = safe_url if safe_url is not None else url
    link_open = (
        f'<a class="result-card__title" data-triage-link href="{esc(href)}" '
        'target="_blank" rel="noopener noreferrer">'
        if href and href != "#"
        else '<span class="result-card__title">'
    )
    link_close = "</a>" if href and href != "#" else "</span>"
    domain_html = (
        f'<span class="result-card__domain">{icon("globe")}{esc(domain)}</span>'
        if domain
        else ""
    )
    snippet_html = (
        f'<p class="result-card__snippet">{esc(snippet)}</p>' if snippet else ""
    )
    classes = "result-card"
    if accent_level:
        classes += f" result-card--{esc(accent_level)}"
    triage_attrs = ' data-triage-item tabindex="0"' if triage else ""
    return (
        f'<article class="{classes}"{triage_attrs}>'
        '<div class="result-card__body">'
        f'<div class="result-card__head">{link_open}{esc(title)}{link_close}{domain_html}</div>'
        f"{snippet_html}"
        f'<div class="result-card__meta">{meta_html}</div>'
        "</div>"
        f'<div class="result-card__actions">{actions_html}</div>'
        "</article>"
    )


def insight_grid(cards: Sequence[Mapping[str, str]]) -> str:
    items = []
    for card in cards:
        tone = esc(card.get("tone", "neutral"))
        items.append(
            f'<div class="insight insight--{tone}">'
            f'<span class="insight__value">{esc(card.get("value", ""))}</span>'
            f'<span class="insight__label">{esc(card.get("label", ""))}</span>'
            f'<span class="insight__hint">{esc(card.get("hint", ""))}</span>'
            "</div>"
        )
    return f'<div class="insight-grid">{"".join(items)}</div>'


def context_bar(items: Sequence[Mapping[str, str]], *, label: str = "") -> str:
    """A compact strip of label/value context chips (e.g. search context)."""
    rendered = []
    for item in items:
        icon_name = item.get("icon")
        glyph = icon(icon_name) if icon_name else ""
        rendered.append(
            '<span class="context-item">'
            f'{glyph}<span class="context-item__label">{esc(item.get("label", ""))}</span>'
            f'<span class="context-item__value">{esc(item.get("value", ""))}</span>'
            "</span>"
        )
    aria = f' aria-label="{esc(label)}"' if label else ""
    return f'<div class="context-bar"{aria}>{"".join(rendered)}</div>'


def empty_state(title: str, body: str = "", *, icon_name: str = "search",
                class_name: str = "") -> str:
    extra = f" {esc(class_name)}" if class_name else ""
    body_html = f'<p>{esc(body)}</p>' if body else ""
    return (
        f'<div class="empty-state{extra}">{icon(icon_name)}'
        f"<strong>{esc(title)}</strong>{body_html}</div>"
    )


def keyboard_hint(items: Sequence[tuple[str, str]]) -> str:
    """A discreet legend of keyboard shortcuts: (key, action) pairs."""
    parts = [
        f'<span class="kbd-hint__item"><kbd>{esc(key)}</kbd> {esc(action)}</span>'
        for key, action in items
    ]
    return f'<div class="kbd-hint" aria-hidden="true">{"".join(parts)}</div>'


# --- page shell ------------------------------------------------------------

def topbar(subtitle: str, asset_prefix: str, nav: Iterable[Mapping[str, str]]) -> str:
    links = []
    for entry in nav:
        attrs = entry.get("attrs", "")
        target = ' target="_blank" rel="noopener noreferrer"' if entry.get("blank") else ""
        links.append(
            f'<a class="nav-link" href="{esc(entry.get("href", "#"))}"{target} {attrs}>'
            f'{esc(entry.get("label", ""))}</a>'
        )
    return (
        '<header class="topbar">'
        '<div class="brand">'
        f'<img class="brand-logo" src="{esc(asset_prefix)}assets/synthesix-mark.svg" alt="">'
        '<div class="brand-copy"><span class="brand-name">Synthesix</span>'
        f'<span class="brand-subtitle">{esc(subtitle)}</span></div></div>'
        f'<nav class="top-actions">{"".join(links)}</nav>'
        "</header>"
    )


def render_page(*, title: str, asset_prefix: str, body: str, lang: str = "en",
                extra_head: str = "", body_class: str = "app app--wide") -> str:
    """Assemble a complete generated HTML document with the shared shell."""
    return f"""<!DOCTYPE html>
<html lang="{esc(lang)}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)}</title>
    <link rel="icon" href="{esc(asset_prefix)}assets/favicon.svg" type="image/svg+xml">
    <link rel="stylesheet" href="{esc(asset_prefix)}theme.css">
    <script src="{esc(asset_prefix)}theme.js"></script>
    <script src="{esc(asset_prefix)}i18n.js"></script>
    {extra_head}
</head>
<body>
    <main class="{esc(body_class)}">
{body}
    </main>
{page_behavior_script()}
</body>
</html>
"""


def page_behavior_script() -> str:
    """Defines window.synthesixPage (consumed by main.py via CDP) and adds
    keyboard-first triage over result cards. The action contract is preserved
    verbatim: focus_home, data-page-action payloads, and a status target."""
    return """    <script>
        (() => {
            const state = { pendingAction: null };
            const status = document.querySelector("[data-page-status]");

            window.synthesixPage = {
                consumeAction() {
                    const action = state.pendingAction;
                    state.pendingAction = null;
                    return action;
                },
                setStatus(message, isError = false) {
                    if (!status) {
                        return;
                    }
                    status.textContent = String(message || "");
                    status.classList.toggle("is-error", Boolean(isError));
                }
            };

            document.querySelectorAll("[data-home-link]").forEach((link) => {
                link.addEventListener("click", (event) => {
                    event.preventDefault();
                    state.pendingAction = { action: "focus_home" };
                });
            });

            document.querySelectorAll("[data-page-action]").forEach((button) => {
                button.addEventListener("click", () => {
                    let payload = {};
                    try {
                        payload = JSON.parse(button.dataset.actionPayload || "{}");
                    } catch (_error) {
                        window.synthesixPage.setStatus(
                            "This report action is invalid.",
                            true
                        );
                        return;
                    }
                    state.pendingAction = {
                        action: button.dataset.pageAction,
                        ...payload
                    };
                    window.synthesixPage.setStatus("Processing...");
                });
            });

            const cards = Array.from(
                document.querySelectorAll("[data-triage-item]")
            );
            if (cards.length) {
                let index = -1;
                const focusCard = (next) => {
                    index = (next + cards.length) % cards.length;
                    cards[index].focus();
                };
                document.addEventListener("keydown", (event) => {
                    const tag = (event.target.tagName || "").toLowerCase();
                    if (["input", "textarea", "select"].includes(tag)) {
                        return;
                    }
                    if (event.key === "j" || event.key === "ArrowDown") {
                        event.preventDefault();
                        focusCard(index + 1);
                    } else if (event.key === "k" || event.key === "ArrowUp") {
                        event.preventDefault();
                        focusCard(index - 1);
                    } else if (event.key === "o" || event.key === "Enter") {
                        const card =
                            cards[index] ||
                            (event.target.closest &&
                                event.target.closest("[data-triage-item]"));
                        const link = card &&
                            card.querySelector("[data-triage-link]");
                        if (link) {
                            event.preventDefault();
                            window.open(link.href, "_blank", "noopener");
                        }
                    }
                });
                cards.forEach((card, position) => {
                    card.addEventListener("focus", () => {
                        index = position;
                    });
                });
            }
        })();
    </script>
"""
