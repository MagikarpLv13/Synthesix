from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping

import ui

STATUS_LABELS = {
    "a_verifier": "To verify",
    "pertinent": "Relevant",
    "ecarte": "Discarded",
    "confirme": "Confirmed",
}
STATUS_TONES = {
    "confirme": "success",
    "pertinent": "info",
    "ecarte": "muted",
}
STATUS_ACCENTS = {
    "confirme": "strong",
    "pertinent": "good",
    "a_verifier": "moderate",
    "ecarte": "weak",
}


def _relative_href(target: Path, from_dir: Path) -> str:
    return os.path.relpath(target.resolve(), from_dir.resolve()).replace(os.sep, "/")


def _asset_prefix(from_dir: Path, base_dir: Path) -> str:
    relative = os.path.relpath(
        Path(base_dir).resolve(), Path(from_dir).resolve()
    ).replace(os.sep, "/")
    return "" if relative == "." else relative.rstrip("/") + "/"


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
        if not value:
            continue
        if key == "analyst_status":
            value = STATUS_LABELS.get(value, value)
        items.append({"label": label, "value": value})
    if not items:
        items = [{"label": "Scope", "value": "All local observations"}]
    return ui.context_bar(items, label="Search scope")


def _result_card(
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
    url = str(result.get("url") or "")
    safe_url = url if ui.domain_of(url) else "#"
    title = str(result.get("title") or url)
    description = str(result.get("description") or "")
    notes = str(result.get("notes") or "")
    status_value = str(result.get("analyst_status") or "")
    status = STATUS_LABELS.get(status_value, "Not reviewed")
    status_tone = STATUS_TONES.get(status_value, "neutral")
    evidence_count = int(result.get("evidence_count", 0) or 0)
    sources = [str(s).strip() for s in result.get("sources", []) if str(s).strip()]
    tags = [str(t).strip() for t in result.get("tags", []) if str(t).strip()]

    chips = ui.chip("Already observed", tone="info")
    for engine in sources:
        chips += ui.chip(engine, tone="engine")
    chips += ui.chip(status, tone=status_tone)
    chips += ui.chip(f"{evidence_count} evidence capture(s)")

    if investigation_id and is_saved:
        href = _relative_href(
            investigation_pages_dir / f"{investigation_id}.html", output_dir
        ) + f"#result-{result_id}"
        detail = (
            f'<a class="provenance__detail" href="{ui.esc(href)}">'
            f"{ui.esc(investigation_title)}</a>"
        )
    else:
        detail = f'<span class="provenance__detail">{ui.esc(investigation_title)}</span>'
    context = (
        f'<span class="provenance">{ui.icon("folder")}'
        f'<span class="provenance__label">Investigation</span>{detail}</span>'
    )

    seen = ""
    if result.get("first_observed_at"):
        seen += ui.provenance(
            "First seen", str(result.get("first_observed_at")), icon_name="clock"
        )
    if result.get("last_observed_at"):
        seen += ui.provenance(
            "Last seen", str(result.get("last_observed_at")), icon_name="clock"
        )

    extra = ""
    if notes:
        extra += (
            f'<p class="result-card__notes"><strong>Notes</strong> '
            f"{ui.esc(notes)}</p>"
        )
    if tags:
        extra += (
            '<div class="result-card__tags">'
            + "".join(ui.chip(tag, tone="muted") for tag in tags)
            + "</div>"
        )

    return ui.result_card(
        title=title,
        url=url,
        safe_url=safe_url,
        domain=ui.domain_of(url),
        snippet=description,
        extra_html=extra,
        meta_html=chips + context + seen,
        accent_level=STATUS_ACCENTS.get(status_value, ""),
    )


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
    base_dir = Path(base_dir)
    investigation_pages_dir = Path(investigation_pages_dir)
    asset_prefix = _asset_prefix(output_dir, base_dir)
    home_href = _relative_href(base_dir / "index.html", output_dir)

    if results:
        cards = "".join(
            _result_card(
                result,
                output_dir=output_dir,
                investigation_pages_dir=investigation_pages_dir,
            )
            for result in results
        )
        results_html = (
            '<div class="result-list" aria-label="Local archive results">'
            + cards
            + "</div>"
            + ui.keyboard_hint([("j / k", "navigate results"), ("o", "open")])
        )
    else:
        results_html = ui.empty_state(
            "No matching local observation",
            "No stored observation matches these filters.",
            class_name="local-search-empty",
        )

    body = (
        ui.topbar(
            "Local archive search",
            asset_prefix,
            [{"href": home_href, "label": "Search"}],
        )
        + '<section class="page" aria-label="Local archive results">'
        + '<div class="page-head">'
        + '<p class="eyebrow">Offline collection</p>'
        + '<h1 class="page-title">Local archive results</h1>'
        + '<div class="context-bar"><span class="context-item">'
        + f'<span class="context-item__value">{len(results)} result(s)</span>'
        + "</span></div>"
        + _filter_summary(filters)
        + '<p class="session-note">This report uses only the local SQLite '
        + "index. No external search engine was contacted.</p>"
        + "</div>"
        + results_html
        + "</section>"
    )

    full_html = ui.render_page(
        title="Local archive search",
        asset_prefix=asset_prefix,
        body=body,
    )
    output_path.write_text(full_html, encoding="utf-8")
    return str(output_path)
