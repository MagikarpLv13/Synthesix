from __future__ import annotations

import os
import json
from html import escape
from pathlib import Path
from typing import Mapping


STATUS_LABELS = {
    "a_verifier": "To verify",
    "pertinent": "Relevant",
    "ecarte": "Discarded",
    "confirme": "Confirmed",
}
ENTITY_STATUS_LABELS = {
    "proposed": "Proposed",
    "validated": "Validated",
    "rejected": "Rejected",
}
ENTITY_TYPE_LABELS = {
    "email": "Email",
    "phone": "Phone",
    "url": "URL",
    "domain": "Domain",
    "ipv4": "IPv4",
    "ipv6": "IPv6",
    "handle": "Handle",
    "identifier": "Identifier",
    "coordinates": "Coordinates",
}


def _html(value) -> str:
    return escape(str(value or ""), quote=True)


def _relative_href(target: Path, from_dir: Path) -> str:
    return os.path.relpath(target.resolve(), from_dir.resolve()).replace(os.sep, "/")


def _resolve_runtime_path(value: str | None, base_dir: Path) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if not path.is_absolute():
        path = base_dir / path
    return path


def _display_datetime(value: str | None) -> str:
    text = str(value or "").strip()
    if not text:
        return "Unknown"
    return text.replace("T", " ").replace("+00:00", " UTC")


def _local_datetime(value: str | None) -> str:
    text = str(value or "").strip()
    if not text:
        return "Unknown"
    return (
        f'<time datetime="{_html(text)}" data-local-datetime>'
        f"{_html(_display_datetime(text))}</time>"
    )


def _status_options(selected: str) -> str:
    options = []
    for value, label in STATUS_LABELS.items():
        selection = " selected" if value == selected else ""
        options.append(
            f'<option value="{_html(value)}"{selection}>{_html(label)}</option>'
        )
    return "".join(options)


def _entity_status_options(selected: str) -> str:
    return "".join(
        (
            f'<option value="{_html(value)}"'
            f'{" selected" if value == selected else ""}>'
            f"{_html(label)}</option>"
        )
        for value, label in ENTITY_STATUS_LABELS.items()
    )


def _entity_markup(
    entities: list[Mapping],
    *,
    read_only: bool,
) -> str:
    disabled = " disabled" if read_only else ""
    items = []
    for entity in entities:
        entity_type = str(entity.get("entity_type", "") or "")
        status = str(entity.get("status", "proposed") or "proposed")
        confidence = max(
            0.0,
            min(1.0, float(entity.get("confidence", 0) or 0)),
        )
        items.append(
            f"""
            <li
                class="entity-item entity-item--{_html(status)}"
                data-entity-id="{_html(entity.get("id", ""))}"
            >
                <span class="entity-type">
                    {_html(ENTITY_TYPE_LABELS.get(entity_type, entity_type))}
                </span>
                <code class="entity-value">
                    {_html(entity.get("value_original", ""))}
                </code>
                <span class="entity-confidence">
                    {confidence:.0%} deterministic confidence
                </span>
                <label class="entity-status-control">
                    <span class="sr-only">Entity review status</span>
                    <select data-entity-status{disabled}>
                        {_entity_status_options(status)}
                    </select>
                </label>
                <button
                    type="button"
                    class="danger-link delete-entity"
                    {disabled}
                >Delete</button>
                <p class="entity-source">
                    <strong>{_html(entity.get("source_field", ""))}</strong>
                    {_html(entity.get("source_text", ""))}
                </p>
            </li>
            """
        )
    empty = (
        ""
        if items
        else '<p class="session-note">No entity candidate extracted yet.</p>'
    )
    return f"""
        <div class="result-entities">
            <div class="entity-heading">
                <span class="provenance-label">Entities ({len(items)})</span>
                <button
                    type="button"
                    class="secondary-button extract-result-entities"
                    {disabled}
                >Extract entities</button>
            </div>
            {empty}
            <ul class="entity-list">{"".join(items)}</ul>
        </div>
    """


def _score_markup(result: Mapping) -> str:
    score = float(result.get("relevance_score", 0) or 0)
    components = result.get("score_breakdown", [])
    if not isinstance(components, (list, tuple)):
        components = []

    items = []
    for component in components:
        if not isinstance(component, Mapping):
            continue
        component_score = float(component.get("score", 0) or 0)
        label = component.get("label", "Score component")
        items.append(f"<li>+{component_score:.1f} {_html(label)}</li>")

    if not items:
        return f"<span>Score {score:.1f}</span>"
    return (
        '<details class="score-breakdown">'
        f"<summary>Score {score:.1f}</summary>"
        f"<ul>{''.join(items)}</ul>"
        "<p>Multi-engine consensus confirms repeated retrieval, "
        "not factual accuracy.</p>"
        "</details>"
    )


def _evidence_markup(
    captures: list[Mapping],
    *,
    output_dir: Path,
    base_dir: Path,
    read_only: bool,
) -> str:
    if not captures:
        return ""

    items = []
    for capture in captures:
        artifact_hrefs = {}
        for artifact in capture.get("artifacts", []):
            artifact_type = str(artifact.get("artifact_type", "") or "")
            artifact_path = _resolve_runtime_path(
                artifact.get("file_path"),
                base_dir,
            )
            if artifact_type and artifact_path is not None:
                artifact_hrefs[artifact_type] = _relative_href(
                    artifact_path,
                    output_dir,
                )
        png_href = artifact_hrefs.get("png", "")
        manifest_path = _resolve_runtime_path(
            capture.get("manifest_path"),
            base_dir,
        )
        manifest_href = (
            _relative_href(manifest_path, output_dir)
            if manifest_path is not None
            else ""
        )
        artifact_links = "".join(
            f'<a class="secondary-link" href="{_html(href)}" '
            'target="_blank" rel="noopener noreferrer">'
            f"{_html(label)}</a>"
            for artifact_type, label in (
                ("html", "HTML"),
                ("mhtml", "MHTML"),
                ("text", "Text"),
            )
            if (href := artifact_hrefs.get(artifact_type))
        )
        if manifest_href:
            artifact_links += (
                f'<a class="secondary-link" href="{_html(manifest_href)}" '
                'target="_blank" rel="noopener noreferrer">Manifest</a>'
            )
        capture_kind = str(
            capture.get("capture_kind", "screenshot") or "screenshot"
        )
        if capture_kind == "page_archive":
            scope = "Page archive"
        else:
            scope = (
                "Selected area"
                if capture.get("capture_scope") == "region"
                else "Visible area"
            )
        capture_name = str(capture.get("name", "") or "").strip()
        display_name = capture_name or scope
        scope_detail = (
            f'<span class="evidence-scope">{_html(scope)}</span>'
            if capture_name
            else ""
        )
        status_detail = (
            '<span class="evidence-scope">Partial capture</span>'
            if capture.get("status") == "partial"
            else ""
        )
        disabled = " disabled" if read_only else ""
        thumbnail = (
            f'<a class="evidence-thumbnail" href="{_html(png_href)}" '
            'target="_blank" rel="noopener noreferrer" '
            f'aria-label="Open {_html(display_name)}">'
            f'<img src="{_html(png_href)}" alt="" loading="lazy"></a>'
            if png_href
            else (
                '<div class="evidence-thumbnail '
                'evidence-thumbnail--empty evidence-thumbnail--archive" '
                'aria-label="Page archive"></div>'
                if capture_kind == "page_archive"
                else '<div class="evidence-thumbnail evidence-thumbnail--empty"></div>'
            )
        )
        name_markup = (
            f'<a class="evidence-name" href="{_html(png_href)}" '
            'target="_blank" rel="noopener noreferrer">'
            f"{_html(display_name)}</a>"
            if png_href
            else f'<strong class="evidence-name">{_html(display_name)}</strong>'
        )
        verify_title = (
            "Recalculate every artifact hash and compare it with the "
            "recorded SHA-256"
        )
        items.append(
            f"""
            <li
                class="evidence-item"
                data-evidence-id="{_html(capture.get("id", ""))}"
            >
                {thumbnail}
                <div class="evidence-copy">
                    {name_markup}
                    {scope_detail}
                    {status_detail}
                    <span>{_local_datetime(capture.get("captured_at"))}</span>
                </div>
                <div class="evidence-links">
                    {artifact_links}
                    <button
                        type="button"
                        class="secondary-link verify-evidence"
                        title="{verify_title}"
                    >Verify</button>
                    <button
                        type="button"
                        class="danger-link delete-evidence"
                        title="Delete this capture and its local evidence files"
                        {disabled}
                    >Delete</button>
                </div>
                <span
                    class="evidence-verification"
                    data-evidence-verification
                    aria-live="polite"
                ></span>
            </li>
            """
        )
    return (
        '<div class="result-evidence">'
        f'<span class="provenance-label">Evidence ({len(items)})</span>'
        f'<ul class="evidence-list">{"".join(items)}</ul>'
        "</div>"
    )


def _result_cards(
    results: list[Mapping],
    *,
    evidence_by_result: Mapping[str, list[Mapping]],
    entities_by_result: Mapping[str, list[Mapping]],
    monitors_by_result: Mapping[str, Mapping],
    output_dir: Path,
    base_dir: Path,
    read_only: bool,
) -> str:
    if not results:
        return """
            <div class="investigation-empty">
                No page has been explicitly saved to this investigation yet.
            </div>
        """

    cards = []
    disabled = " disabled" if read_only else ""
    for result in results:
        result_id = str(result.get("id", ""))
        title = str(result.get("title") or result.get("url") or "Untitled result")
        description = str(result.get("description", ""))
        url = str(result.get("url", ""))
        sources = [str(item) for item in result.get("sources", []) if str(item).strip()]
        discovery_sources = [
            str(item)
            for item in result.get("discovery_sources", [])
            if str(item).strip()
        ]
        filter_sources = sorted(
            set([*sources, *discovery_sources]),
            key=str.casefold,
        )
        tags = [str(item) for item in result.get("tags", []) if str(item).strip()]
        notes = str(result.get("notes", ""))
        status = str(result.get("analyst_status", "a_verifier"))
        favorite = bool(result.get("favorite", False))
        latest_observed = str(result.get("latest_observed_at", ""))
        search_text = " ".join(
            [title, description, url, notes, *filter_sources, *tags]
        ).casefold()
        source_filter = "|" + "|".join(
            source.casefold() for source in filter_sources
        ) + "|"
        tag_filter = "|" + "|".join(tag.casefold() for tag in tags) + "|"
        favorite_checked = " checked" if favorite else ""
        tag_markup = "".join(
            f'<span class="result-tag">{_html(tag)}</span>' for tag in tags
        )
        displayed_sources = sources or discovery_sources
        source_markup = (
            ", ".join(_html(source) for source in displayed_sources)
            or "Unknown source"
        )
        discovery_method = str(result.get("discovery_method", "manual_browsing"))
        discovery_query = str(result.get("discovery_query", ""))
        discovery_referrer = str(result.get("discovery_referrer", ""))
        evidence_markup = _evidence_markup(
            evidence_by_result.get(result_id, []),
            output_dir=output_dir,
            base_dir=base_dir,
            read_only=read_only,
        )
        entity_markup = _entity_markup(
            entities_by_result.get(result_id, []),
            read_only=read_only,
        )
        monitor = monitors_by_result.get(result_id)
        if monitor:
            monitor_control = (
                '<span class="meta-pill">Monitoring</span>'
                '<button type="button" class="secondary-button stop-page-monitor" '
                f'data-monitor-id="{_html(monitor.get("id", ""))}"'
                f"{disabled}>Stop</button>"
            )
        else:
            monitor_control = (
                '<button type="button" class="secondary-button start-page-monitor"'
                f"{disabled}>Monitor changes</button>"
            )
        discovery_observed_at = _local_datetime(
            result.get("discovery_observed_at")
        )
        if discovery_method == "search_result" and discovery_query:
            discovery_markup = (
                '<span class="provenance-label">Found through search</span>'
                f'<strong>{_html(discovery_query)}</strong>'
                f'<span>via {_html(", ".join(discovery_sources) or "recorded search")}</span>'
                f"<span>{discovery_observed_at}</span>"
            )
        else:
            referrer_markup = (
                f'<a href="{_html(discovery_referrer)}" target="_blank" '
                'rel="noopener noreferrer">Open referring page</a>'
                if discovery_referrer.startswith(("http://", "https://"))
                else ""
            )
            discovery_markup = (
                '<span class="provenance-label">Saved while browsing</span>'
                f"<span>{discovery_observed_at}</span>"
                f'{referrer_markup}'
            )

        cards.append(
            f"""
            <article
                id="result-{_html(result_id)}"
                class="investigation-result"
                data-result-id="{_html(result_id)}"
                data-search="{_html(search_text)}"
                data-status="{_html(status)}"
                data-sources="{_html(source_filter)}"
                data-tags="{_html(tag_filter)}"
                data-observed="{_html(latest_observed[:10])}"
                data-favorite="{"1" if favorite else "0"}"
            >
                <div class="result-heading">
                    <div class="result-title-block">
                        <a
                            class="result-title"
                            href="{_html(url)}"
                            target="_blank"
                            rel="noopener noreferrer"
                        >{_html(title)}</a>
                        <div class="result-url">{_html(url)}</div>
                    </div>
                    <div class="result-review-controls">
                        {monitor_control}
                        <label
                            class="favorite-toggle"
                            title="Add or remove this page from favorites"
                        >
                            <input
                                class="sr-only"
                                type="checkbox"
                                data-result-favorite
                                aria-label="Favorite"
                                {favorite_checked}{disabled}
                            >
                            <span class="favorite-star" aria-hidden="true"></span>
                        </label>
                        <label class="status-control">
                            <span class="sr-only">Analyst status</span>
                            <select data-result-status{disabled}>
                                {_status_options(status)}
                            </select>
                        </label>
                        <button
                            type="button"
                            class="danger-button remove-saved-page"
                            title="Remove this saved page from the investigation"
                            {disabled}
                        >Remove</button>
                    </div>
                </div>
                <p class="result-description">{_html(description)}</p>
                <div class="result-metadata">
                    <span>{source_markup}</span>
                    {_score_markup(result)}
                    <span>{int(result.get("observation_count", 0) or 0)} observation(s)</span>
                    <span>First seen {_local_datetime(result.get("first_observed_at"))}</span>
                    <span>Last seen {_local_datetime(latest_observed)}</span>
                </div>
                <div class="result-tags" data-result-tags-display>
                    {tag_markup}
                </div>
                <div class="result-provenance">
                    {discovery_markup}
                </div>
                {entity_markup}
                {evidence_markup}
                <details class="analyst-details">
                    <summary>Analyst notes and tags</summary>
                    <div class="analyst-fields">
                        <label>
                            Notes
                            <textarea
                                rows="4"
                                data-result-notes
                                placeholder="Add verification notes, context, or caveats."
                                {disabled}
                            >{_html(notes)}</textarea>
                        </label>
                        <label>
                            Tags
                            <input
                                type="text"
                                data-result-tags
                                value="{_html(", ".join(tags))}"
                                placeholder="identity, registry, follow-up"
                                {disabled}
                            >
                        </label>
                        <button
                            type="button"
                            class="primary-button save-result-metadata"
                            {disabled}
                        >Save notes</button>
                    </div>
                </details>
            </article>
            """
        )
    return "".join(cards)


def _page_monitor_cards(
    monitors: list[Mapping],
    *,
    output_dir: Path,
    base_dir: Path,
    read_only: bool,
) -> str:
    if not monitors:
        return """
            <div class="investigation-empty">
                No page is monitored. Enable monitoring from a saved page,
                then use the HTML archive button while browsing it.
            </div>
        """

    labels = {
        "unchanged": "No content change",
        "minor_change": "Minor change",
        "changed": "Significant change",
        "inconclusive": "Inconclusive",
    }
    cards = []
    disabled = " disabled" if read_only else ""
    for monitor in monitors:
        report_path = _resolve_runtime_path(
            monitor.get("comparison_report_path"),
            base_dir,
        )
        report_link = (
            f'<a class="secondary-link" '
            f'href="{_html(_relative_href(report_path, output_dir))}" '
            'target="_blank" rel="noopener noreferrer">Open comparison</a>'
            if report_path is not None
            else '<span>Archive the page twice to generate a comparison.</span>'
        )
        status = str(monitor.get("comparison_status", "") or "")
        similarity = monitor.get("comparison_similarity")
        similarity_text = (
            f"{float(similarity) * 100:.2f}% text similarity"
            if similarity is not None
            else ""
        )
        cards.append(
            f"""
            <article
                class="page-monitor-card"
                data-page-monitor-id="{_html(monitor.get("id", ""))}"
            >
                <div>
                    <a
                        class="result-title"
                        href="{_html(monitor.get("result_url", ""))}"
                        target="_blank"
                        rel="noopener noreferrer"
                    >{_html(monitor.get("result_title") or monitor.get("result_url"))}</a>
                    <div class="result-url">{_html(monitor.get("result_url", ""))}</div>
                </div>
                <div class="page-monitor-summary">
                    <span class="meta-pill">
                        {int(monitor.get("archive_count", 0) or 0)} archive(s)
                    </span>
                    <strong>{_html(labels.get(status, "Waiting for baseline"))}</strong>
                    <span>{_html(similarity_text)}</span>
                    {report_link}
                </div>
                <button
                    type="button"
                    class="danger-button stop-page-monitor"
                    data-monitor-id="{_html(monitor.get("id", ""))}"
                    {disabled}
                >Stop monitoring</button>
            </article>
            """
        )
    return "".join(cards)


def _search_rows(
    searches: list[Mapping],
    *,
    output_dir: Path,
    base_dir: Path,
) -> str:
    if not searches:
        return """
            <tr>
                <td colspan="5" class="empty-row">No search attached.</td>
            </tr>
        """

    rows = []
    for search in searches:
        report_path = _resolve_runtime_path(search.get("report_path"), base_dir)
        report_link = (
            f'<a href="{_html(_relative_href(report_path, output_dir))}" '
            'target="_blank" rel="noopener noreferrer">Open report</a>'
            if report_path is not None
            else "No report"
        )
        enabled_engines = [
            str(name).title()
            for name, enabled in search.get("engines", {}).items()
            if enabled
        ]
        query = search.get("original_query") or search.get("parsed_query") or "Filter-only search"
        rows.append(
            f"""
            <tr>
                <td>{_local_datetime(search.get("started_at"))}</td>
                <td>{_html(query)}</td>
                <td>{_html(", ".join(enabled_engines) or "Legacy")}</td>
                <td>{int(search.get("result_count", 0) or 0)}</td>
                <td>{report_link}</td>
            </tr>
            """
        )
    return "".join(rows)


def _export_cards(
    exports: list[Mapping],
    *,
    output_dir: Path,
    base_dir: Path,
    read_only: bool,
) -> str:
    if not exports:
        return """
            <div class="investigation-empty">
                No ZeroNeurone export has been generated yet.
            </div>
        """

    cards = []
    disabled = " disabled" if read_only else ""
    for export in exports:
        links = []
        for key, label in (
            ("archive_path", "ZeroNeurone ZIP"),
            ("dossier_path", "Dossier JSON"),
            ("graphml_path", "GraphML"),
            ("csv_path", "ZeroNeurone CSV"),
            ("nodes_csv_path", "Nodes CSV"),
            ("edges_csv_path", "Edges CSV"),
            ("manifest_path", "Manifest"),
        ):
            path = _resolve_runtime_path(export.get(key), base_dir)
            if path is None:
                continue
            links.append(
                f'<a class="secondary-link" '
                f'href="{_html(_relative_href(path, output_dir))}" '
                'target="_blank" rel="noopener noreferrer">'
                f"{_html(label)}</a>"
            )
        options = ["validated entities"]
        if export.get("include_unreviewed"):
            options.append("all entity review states")
        if export.get("include_evidence"):
            options.append("evidence assets")
        cards.append(
            f"""
            <article
                class="investigation-export-card"
                data-export-id="{_html(export.get("id", ""))}"
            >
                <div>
                    <strong>ZeroNeurone export</strong>
                    <span>{_local_datetime(export.get("generated_at"))}</span>
                </div>
                <div class="export-summary">
                    <span>{int(export.get("node_count", 0) or 0)} nodes</span>
                    <span>{int(export.get("edge_count", 0) or 0)} links</span>
                    <span>{int(export.get("asset_count", 0) or 0)} assets</span>
                    <span>{_html(", ".join(options))}</span>
                </div>
                <div class="export-links">
                    {"".join(links)}
                    <button
                        type="button"
                        class="danger-link delete-export"
                        {disabled}
                    >Delete export</button>
                </div>
            </article>
            """
        )
    return "".join(cards)


def _unassigned_options(searches: list[Mapping]) -> str:
    options = ['<option value="">Select a search</option>']
    for search in searches:
        query = search.get("original_query") or search.get("parsed_query") or "Filter-only search"
        label = (
            f"{_display_datetime(search.get('started_at'))} - "
            f"{query} ({int(search.get('result_count', 0) or 0)} results)"
        )
        options.append(
            f'<option value="{_html(search.get("id", ""))}">{_html(label)}</option>'
        )
    return "".join(options)


def generate_investigation_page(
    workspace: Mapping,
    output_path: Path,
    *,
    base_dir: Path,
    history_report_path: Path,
) -> str:
    investigation = workspace["investigation"]
    results = list(workspace.get("results", []))
    evidence = list(workspace.get("evidence", []))
    entities = list(workspace.get("entities", []))
    exports = list(workspace.get("exports", []))
    searches = list(workspace.get("searches", []))
    page_monitors = list(workspace.get("page_monitors", []))
    unassigned_searches = list(workspace.get("unassigned_searches", []))
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_dir = output_path.parent

    asset_prefix = _relative_href(base_dir, output_dir).rstrip("/") + "/"
    home_href = _relative_href(base_dir / "index.html", output_dir)
    history_href = _relative_href(history_report_path, output_dir)
    read_only = investigation.get("status") != "active"
    all_sources = sorted(
        {
            str(source)
            for result in results
            for source in (
                *result.get("sources", []),
                *result.get("discovery_sources", []),
            )
            if str(source).strip()
        },
        key=str.casefold,
    )
    all_tags = sorted(
        {
            str(tag)
            for result in results
            for tag in result.get("tags", [])
            if str(tag).strip()
        },
        key=str.casefold,
    )
    source_options = "".join(
        f'<option value="{_html(source.casefold())}">{_html(source)}</option>'
        for source in all_sources
    )
    tag_options = "".join(
        f'<option value="{_html(tag.casefold())}">{_html(tag)}</option>'
        for tag in all_tags
    )
    investigation_tags = "".join(
        f'<span class="result-tag">{_html(tag)}</span>'
        for tag in investigation.get("tags", [])
    )
    archive_notice = (
        '<p class="archive-notice">This investigation is archived and read-only.</p>'
        if read_only
        else ""
    )
    attach_disabled = " disabled" if read_only or not unassigned_searches else ""
    evidence_by_result: dict[str, list[Mapping]] = {}
    for capture in evidence:
        evidence_by_result.setdefault(
            str(capture.get("result_id", "")),
            [],
        ).append(capture)
    entities_by_result: dict[str, list[Mapping]] = {}
    for entity in entities:
        entities_by_result.setdefault(
            str(entity.get("result_id", "")),
            [],
        ).append(entity)
    monitors_by_result = {
        str(monitor.get("result_id", "")): monitor
        for monitor in page_monitors
    }

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{_html(investigation.get("title"))} - Synthesix</title>
    <link rel="icon" href="{asset_prefix}assets/favicon.svg" type="image/svg+xml">
    <link rel="stylesheet" href="{asset_prefix}theme.css">
    <script src="{asset_prefix}theme.js"></script>
    <script src="{asset_prefix}i18n.js"></script>
</head>
<body>
    <main class="app app--wide">
        <header class="topbar investigation-topbar">
            <div class="brand">
                <img class="brand-logo" src="{asset_prefix}assets/synthesix-mark.svg" alt="">
                <div class="brand-copy">
                    <h1 class="brand-name">Synthesix</h1>
                    <span class="brand-subtitle">Investigation workspace</span>
                </div>
            </div>
            <div class="top-actions">
                <button type="button" class="nav-link" data-refresh-investigation>Refresh</button>
                <a href="{_html(home_href)}" data-home-link class="nav-link">Search</a>
                <a href="{_html(history_href)}" class="nav-link">History</a>
            </div>
        </header>
        <p id="investigation-action-status" class="action-status"></p>

        <nav class="investigation-nav" aria-label="Investigation sections">
            <a href="#overview">Overview</a>
            <a href="#saved-pages">Saved pages</a>
            <a href="#page-monitoring">Monitoring</a>
            <a href="#exports">Exports</a>
            <a href="#attach-search">Attach search</a>
            <a href="#search-runs">Search runs</a>
        </nav>

        <section id="overview" class="investigation-overview">
            <div>
                <p class="section-eyebrow">Investigation</p>
                <h2 class="page-title">{_html(investigation.get("title"))}</h2>
                <p class="investigation-reference">{_html(investigation.get("reference"))}</p>
                <p class="investigation-description">{_html(investigation.get("description"))}</p>
                <div class="result-tags">{investigation_tags}</div>
                {archive_notice}
            </div>
            <div class="investigation-metrics" aria-label="Investigation metrics">
                <div><strong>{len(searches)}</strong><span>Searches</span></div>
                <div><strong>{len(results)}</strong><span>Saved pages</span></div>
                <div><strong>{sum(1 for item in results if item.get("favorite"))}</strong><span>Favorites</span></div>
                <div><strong>{sum(1 for item in results if item.get("analyst_status") == "confirme")}</strong><span>Confirmed</span></div>
            </div>
        </section>

        <section
            id="saved-pages"
            class="investigation-section"
            aria-label="Saved investigation pages"
        >
            <div class="section-header">
                <div>
                    <p class="section-eyebrow">Analyst selection</p>
                    <h3>Saved pages</h3>
                </div>
                <span id="visible-result-count" class="meta-pill">{len(results)} visible</span>
            </div>
            <div class="investigation-filters">
                <label class="filter-wide">
                    Search
                    <input id="result-filter-query" type="search" placeholder="Title, URL, notes, tags...">
                </label>
                <label>
                    Status
                    <select id="result-filter-status">
                        <option value="">All statuses</option>
                        <option value="a_verifier">To verify</option>
                        <option value="pertinent">Relevant</option>
                        <option value="confirme">Confirmed</option>
                        <option value="ecarte">Discarded</option>
                    </select>
                </label>
                <label>
                    Source
                    <select id="result-filter-source">
                        <option value="">All sources</option>
                        {source_options}
                    </select>
                </label>
                <label>
                    Tag
                    <select id="result-filter-tag">
                        <option value="">All tags</option>
                        {tag_options}
                    </select>
                </label>
                <label>
                    Observed after
                    <input id="result-filter-after" type="date">
                </label>
                <label>
                    Observed before
                    <input id="result-filter-before" type="date">
                </label>
                <label class="favorite-filter">
                    <input id="result-filter-favorite" type="checkbox">
                    Favorites only
                </label>
                <button id="clear-result-filters" type="button" class="secondary-button">Clear filters</button>
            </div>
            <div id="investigation-results" class="investigation-results">
                {_result_cards(
                    results,
                    evidence_by_result=evidence_by_result,
                    entities_by_result=entities_by_result,
                    monitors_by_result=monitors_by_result,
                    output_dir=output_dir,
                    base_dir=base_dir,
                    read_only=read_only,
                )}
            </div>
        </section>

        <section
            id="page-monitoring"
            class="investigation-section"
            aria-label="Page monitoring"
        >
            <div class="section-header">
                <div>
                    <p class="section-eyebrow">Temporal comparison</p>
                    <h3>Page monitoring</h3>
                </div>
                <span class="meta-pill">{len(page_monitors)} monitored</span>
            </div>
            <p class="session-note">
                Monitoring compares normalized text from explicit HTML archives.
                Screenshots are not compared automatically to avoid noisy alerts
                from animations, maps, ads, or cursor changes. Open a monitored
                page and use the HTML archive button to create the next snapshot.
            </p>
            <div class="page-monitor-list">
                {_page_monitor_cards(
                    page_monitors,
                    output_dir=output_dir,
                    base_dir=base_dir,
                    read_only=read_only,
                )}
            </div>
        </section>

        <section
            id="exports"
            class="investigation-section"
            aria-label="ZeroNeurone exports"
        >
            <div class="section-header">
                <div>
                    <p class="section-eyebrow">Interoperability</p>
                    <h3>ZeroNeurone export</h3>
                </div>
                <span class="meta-pill">{len(exports)} export(s)</span>
            </div>
            <form id="zeroneurone-export-form" class="export-form">
                <label>
                    <input id="export-include-evidence" type="checkbox">
                    Include evidence files as assets
                </label>
                <label>
                    <input id="export-include-unreviewed" type="checkbox">
                    Include proposed and rejected entity candidates
                </label>
                <button type="submit" class="primary-button">
                    Export GraphML and CSV
                </button>
            </form>
            <p class="session-note">
                The default export includes saved pages and validated entities.
                Evidence assets and unvalidated candidates require explicit options.
            </p>
            <div class="investigation-export-list">
                {_export_cards(
                    exports,
                    output_dir=output_dir,
                    base_dir=base_dir,
                    read_only=read_only,
                )}
            </div>
        </section>

        <section
            id="attach-search"
            class="investigation-section"
            aria-label="Attach existing search"
        >
            <div class="section-header">
                <div>
                    <p class="section-eyebrow">Existing collection</p>
                    <h3>Attach a previous search</h3>
                </div>
            </div>
            <form id="attach-search-form" class="attach-search-form">
                <label>
                    Unassigned search
                    <select id="unassigned-search"{attach_disabled}>
                        {_unassigned_options(unassigned_searches)}
                    </select>
                </label>
                <button type="submit" class="primary-button"{attach_disabled}>Attach</button>
            </form>
            <p class="session-note">
                Attaching a search preserves its original query, report, and observations.
                Its results are not added to the saved pages automatically.
            </p>
        </section>

        <section
            id="search-runs"
            class="investigation-section"
            aria-label="Investigation searches"
        >
            <div class="section-header">
                <div>
                    <p class="section-eyebrow">Provenance</p>
                    <h3>Search runs</h3>
                </div>
            </div>
            <div class="table-shell investigation-table-shell">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Query</th>
                            <th>Engines</th>
                            <th>Results</th>
                            <th>Report</th>
                        </tr>
                    </thead>
                    <tbody>
                        {_search_rows(searches, output_dir=output_dir, base_dir=base_dir)}
                    </tbody>
                </table>
            </div>
        </section>
    </main>
    <script>
        (() => {{
            const investigationId = {json.dumps(str(investigation.get("id", "")))};
            const actionQueue = [];
            const resultCards = Array.from(
                document.querySelectorAll(".investigation-result")
            );
            const filterIds = [
                "result-filter-query",
                "result-filter-status",
                "result-filter-source",
                "result-filter-tag",
                "result-filter-after",
                "result-filter-before",
                "result-filter-favorite"
            ];

            const queueAction = (action, payload = {{}}) => {{
                actionQueue.push({{ action, investigationId, ...payload }});
            }};

            const formatLocalDatetimes = () => {{
                const formatter = new Intl.DateTimeFormat(undefined, {{
                    dateStyle: "medium",
                    timeStyle: "medium"
                }});
                document.querySelectorAll("time[data-local-datetime]").forEach(
                    (element) => {{
                        const rawValue = element.getAttribute("datetime") || "";
                        const normalizedValue = rawValue.replace(
                            /(\\.\\d{{3}})\\d+(?=(?:Z|[+-]\\d{{2}}:\\d{{2}})$)/,
                            "$1"
                        );
                        const parsed = new Date(normalizedValue);
                        if (Number.isNaN(parsed.getTime())) {{
                            return;
                        }}
                        element.textContent = formatter.format(parsed);
                        element.title = rawValue;
                    }}
                );
            }};

            window.synthesixPage = {{
                consumeAction() {{
                    return actionQueue.shift() || null;
                }},
                setStatus(message, isError = false) {{
                    const status = document.getElementById(
                        "investigation-action-status"
                    );
                    status.textContent = String(message || "");
                    status.classList.toggle("is-error", Boolean(isError));
                }}
            }};
            formatLocalDatetimes();

            document.querySelectorAll("[data-home-link]").forEach((link) => {{
                link.addEventListener("click", (event) => {{
                    event.preventDefault();
                    queueAction("focus_home");
                }});
            }});

            document.querySelectorAll("[data-refresh-investigation]").forEach((button) => {{
                button.addEventListener("click", () => {{
                    queueAction("refresh_investigation");
                }});
            }});

            const resultPayload = (card) => ({{
                analyst_status: card.querySelector("[data-result-status]").value,
                favorite: card.querySelector("[data-result-favorite]").checked,
                notes: card.querySelector("[data-result-notes]").value.trim(),
                tags: card.querySelector("[data-result-tags]").value.trim()
            }});

            const saveResult = (card) => {{
                queueAction("update_investigation_result", {{
                    resultId: card.dataset.resultId,
                    result: resultPayload(card)
                }});
            }};

            resultCards.forEach((card) => {{
                card.querySelector("[data-result-status]")?.addEventListener(
                    "change",
                    () => saveResult(card)
                );
                card.querySelector("[data-result-favorite]")?.addEventListener(
                    "change",
                    () => {{
                        card.dataset.favorite = card.querySelector(
                            "[data-result-favorite]"
                        ).checked ? "1" : "0";
                        saveResult(card);
                    }}
                );
                card.querySelector(".save-result-metadata")?.addEventListener(
                    "click",
                    () => saveResult(card)
                );
                card.querySelector(".start-page-monitor")?.addEventListener(
                    "click",
                    () => queueAction("create_page_monitor", {{
                        resultId: card.dataset.resultId
                    }})
                );
                card.querySelector(".extract-result-entities")?.addEventListener(
                    "click",
                    () => queueAction("extract_result_entities", {{
                        resultId: card.dataset.resultId
                    }})
                );
                card.querySelectorAll("[data-entity-status]").forEach(
                    (select) => {{
                        select.addEventListener("change", () => {{
                            const item = select.closest("[data-entity-id]");
                            if (item) {{
                                queueAction("update_entity_status", {{
                                    entityId: item.dataset.entityId,
                                    status: select.value
                                }});
                            }}
                        }});
                    }}
                );
                card.querySelectorAll(".delete-entity").forEach((button) => {{
                    button.addEventListener("click", () => {{
                        const item = button.closest("[data-entity-id]");
                        if (item && confirm("Delete this extracted entity?")) {{
                            queueAction("delete_entity", {{
                                entityId: item.dataset.entityId
                            }});
                        }}
                    }});
                }});
                card.querySelector(".remove-saved-page")?.addEventListener(
                    "click",
                    () => {{
                        if (
                            confirm(
                                "Remove this page from the investigation? "
                                + "The underlying search observation is preserved."
                            )
                        ) {{
                            queueAction("remove_saved_page", {{
                                resultId: card.dataset.resultId
                            }});
                        }}
                    }}
                );
                card.querySelectorAll(".delete-evidence").forEach((button) => {{
                    button.addEventListener("click", () => {{
                        const item = button.closest("[data-evidence-id]");
                        if (
                            item
                            && confirm("Delete this evidence capture and its files?")
                        ) {{
                            queueAction("delete_evidence_capture", {{
                                captureId: item.dataset.evidenceId
                            }});
                        }}
                    }});
                }});
                card.querySelectorAll(".verify-evidence").forEach((button) => {{
                    button.addEventListener("click", () => {{
                        const item = button.closest("[data-evidence-id]");
                        if (!item) {{
                            return;
                        }}
                        const status = item.querySelector(
                            "[data-evidence-verification]"
                        );
                        status.textContent = "Checking...";
                        status.className = "evidence-verification";
                        queueAction("verify_evidence_capture", {{
                            captureId: item.dataset.evidenceId
                        }});
                    }});
                }});
            }});

            document.querySelectorAll(".stop-page-monitor").forEach((button) => {{
                button.addEventListener("click", () => {{
                    if (confirm("Stop monitoring this page?")) {{
                        queueAction("delete_page_monitor", {{
                            monitorId: button.dataset.monitorId
                        }});
                    }}
                }});
            }});

            const normalize = (value) => String(value || "").toLowerCase().trim();
            const applyFilters = () => {{
                const query = normalize(document.getElementById("result-filter-query").value);
                const status = document.getElementById("result-filter-status").value;
                const source = normalize(document.getElementById("result-filter-source").value);
                const tag = normalize(document.getElementById("result-filter-tag").value);
                const after = document.getElementById("result-filter-after").value;
                const before = document.getElementById("result-filter-before").value;
                const favoritesOnly = document.getElementById(
                    "result-filter-favorite"
                ).checked;
                let visible = 0;

                resultCards.forEach((card) => {{
                    const observed = card.dataset.observed || "";
                    const matches = (
                        (!query || card.dataset.search.includes(query))
                        && (!status || card.dataset.status === status)
                        && (!source || card.dataset.sources.includes(`|${{source}}|`))
                        && (!tag || card.dataset.tags.includes(`|${{tag}}|`))
                        && (!after || observed >= after)
                        && (!before || observed <= before)
                        && (!favoritesOnly || card.dataset.favorite === "1")
                    );
                    card.hidden = !matches;
                    if (matches) {{
                        visible += 1;
                    }}
                }});
                document.getElementById(
                    "visible-result-count"
                ).textContent = `${{visible}} visible`;
            }};

            filterIds.forEach((id) => {{
                document.getElementById(id)?.addEventListener("input", applyFilters);
                document.getElementById(id)?.addEventListener("change", applyFilters);
            }});
            document.getElementById("clear-result-filters")?.addEventListener(
                "click",
                () => {{
                    filterIds.forEach((id) => {{
                        const field = document.getElementById(id);
                        if (field.type === "checkbox") {{
                            field.checked = false;
                        }} else {{
                            field.value = "";
                        }}
                    }});
                    applyFilters();
                }}
            );

            document.getElementById("attach-search-form")?.addEventListener(
                "submit",
                (event) => {{
                    event.preventDefault();
                    const searchRunId = document.getElementById(
                        "unassigned-search"
                    ).value;
                    if (searchRunId) {{
                        queueAction("attach_investigation_search", {{ searchRunId }});
                    }}
                }}
            );

            document.getElementById(
                "zeroneurone-export-form"
            )?.addEventListener("submit", (event) => {{
                event.preventDefault();
                queueAction("export_zeroneurone", {{
                    includeEvidence: document.getElementById(
                        "export-include-evidence"
                    ).checked,
                    includeUnreviewed: document.getElementById(
                        "export-include-unreviewed"
                    ).checked
                }});
                window.synthesixPage.setStatus("Generating export...");
            }});
            document.querySelectorAll(".delete-export").forEach((button) => {{
                button.addEventListener("click", () => {{
                    const card = button.closest("[data-export-id]");
                    if (
                        card
                        && confirm("Delete this ZeroNeurone export and its files?")
                    ) {{
                        queueAction("delete_zeroneurone_export", {{
                            exportId: card.dataset.exportId
                        }});
                    }}
                }});
            }});
        }})();
    </script>
</body>
</html>
"""
    output_path.write_text(page, encoding="utf-8")
    return str(output_path)
