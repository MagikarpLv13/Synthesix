from __future__ import annotations

import os
from html import escape
from pathlib import Path
from typing import Mapping
from urllib.parse import urlsplit


STATUS_LABELS = {
    "a_verifier": "To verify",
    "pertinent": "Relevant",
    "ecarte": "Discarded",
    "confirme": "Confirmed",
}


def _html(value) -> str:
    return escape(str(value or ""), quote=True)


def _relative_href(target: Path, from_dir: Path) -> str:
    return os.path.relpath(target.resolve(), from_dir.resolve()).replace(os.sep, "/")


def _safe_external_href(value) -> str:
    url = str(value or "").strip()
    try:
        return url if urlsplit(url).scheme.lower() in {"http", "https"} else "#"
    except ValueError:
        return "#"


def _filter_summary(filters: Mapping) -> str:
    labels = {
        "query": "Query",
        "investigation_title": "Investigation",
        "source": "Engine",
        "analyst_status": "Status",
        "domain": "Domain",
        "observed_after": "After",
        "observed_before": "Before",
    }
    items = []
    for key, label in labels.items():
        value = str(filters.get(key, "") or "").strip()
        if value:
            items.append(
                f'<span class="meta-pill">{_html(label)}: {_html(value)}</span>'
            )
    return "".join(items) or '<span class="meta-pill">All local observations</span>'


def _result_markup(
    result: Mapping,
    *,
    output_dir: Path,
    investigation_pages_dir: Path,
) -> str:
    result_id = str(result.get("result_id", "") or "")
    investigation_id = str(result.get("investigation_id", "") or "")
    investigation_title = str(
        result.get("investigation_title", "") or "Unassigned searches"
    )
    is_saved = bool(result.get("is_saved", False))
    context_markup = _html(investigation_title)
    if investigation_id and is_saved:
        investigation_href = _relative_href(
            investigation_pages_dir / f"{investigation_id}.html",
            output_dir,
        )
        context_markup = (
            f'<a href="{_html(investigation_href)}#result-{_html(result_id)}">'
            f"{_html(investigation_title)}</a>"
        )

    sources = ", ".join(
        str(source)
        for source in result.get("sources", [])
        if str(source).strip()
    ) or "Unknown source"
    tags = ", ".join(
        str(tag)
        for tag in result.get("tags", [])
        if str(tag).strip()
    )
    status_value = str(result.get("analyst_status", "") or "")
    status = STATUS_LABELS.get(status_value, "Not reviewed")
    evidence_count = int(result.get("evidence_count", 0) or 0)
    notes = str(result.get("notes", "") or "")
    notes_markup = (
        f'<p class="result-notes"><strong>Notes:</strong> {_html(notes)}</p>'
        if notes
        else ""
    )
    tags_markup = (
        f'<span>Tags: {_html(tags)}</span>'
        if tags
        else ""
    )

    return f"""
    <article class="investigation-result">
        <div class="result-heading">
            <div class="result-title-block">
                <a
                    class="result-title"
                    href="{_html(_safe_external_href(result.get("url")))}"
                    target="_blank"
                    rel="noopener noreferrer"
                >{_html(result.get("title") or result.get("url"))}</a>
                <div class="result-url">{_html(result.get("url"))}</div>
            </div>
            <span class="meta-pill">Already observed</span>
        </div>
        <p class="result-description">{_html(result.get("description"))}</p>
        {notes_markup}
        <div class="result-metadata">
            <span>Context: {context_markup}</span>
            <span>Engines: {_html(sources)}</span>
            <span>Status: {_html(status)}</span>
            <span>First seen: {_html(result.get("first_observed_at"))}</span>
            <span>Last seen: {_html(result.get("last_observed_at"))}</span>
            <span>{evidence_count} evidence capture(s)</span>
            {tags_markup}
        </div>
    </article>
    """


def generate_local_search_page(
    results: list[Mapping],
    filters: Mapping,
    output_path: Path,
    *,
    base_dir: Path,
    investigation_pages_dir: Path,
) -> str:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_dir = output_path.parent
    home_href = _relative_href(Path(base_dir) / "index.html", output_dir)
    theme_href = _relative_href(Path(base_dir) / "theme.css", output_dir)
    theme_script = _relative_href(Path(base_dir) / "theme.js", output_dir)
    favicon_href = _relative_href(
        Path(base_dir) / "assets" / "favicon.svg",
        output_dir,
    )
    logo_href = _relative_href(
        Path(base_dir) / "assets" / "synthesix-mark.svg",
        output_dir,
    )
    if results:
        results_markup = "".join(
            _result_markup(
                result,
                output_dir=output_dir,
                investigation_pages_dir=investigation_pages_dir,
            )
            for result in results
        )
    else:
        results_markup = (
            '<div class="empty-state">No stored observation matches these filters.</div>'
        )

    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Local archive search</title>
    <link rel="icon" href="{_html(favicon_href)}" type="image/svg+xml">
    <link rel="stylesheet" href="{_html(theme_href)}">
    <script src="{_html(theme_script)}"></script>
</head>
<body>
    <main class="app app--wide">
        <header class="topbar">
            <div class="brand">
                <img class="brand-logo" src="{_html(logo_href)}" alt="">
                <div class="brand-copy">
                    <h1 class="brand-name">Synthesix</h1>
                    <span class="brand-subtitle">Local archive search</span>
                </div>
            </div>
            <div class="top-actions">
                <a href="{_html(home_href)}" class="nav-link">Search</a>
                <button
                    type="button"
                    class="theme-toggle"
                    data-theme-toggle
                    aria-pressed="false"
                >Dark mode</button>
            </div>
        </header>
        <section class="investigation-section">
            <div class="section-header">
                <div>
                    <p class="section-eyebrow">Offline collection</p>
                    <h2>Local archive results</h2>
                </div>
                <span class="meta-pill">{len(results)} result(s)</span>
            </div>
            <div class="page-meta">{_filter_summary(filters)}</div>
            <p class="session-note">
                This report uses only the local SQLite index. No external search
                engine was contacted.
            </p>
            <div class="investigation-results">
                {results_markup}
            </div>
        </section>
    </main>
</body>
</html>
"""
    output_path.write_text(content, encoding="utf-8")
    return str(output_path)
