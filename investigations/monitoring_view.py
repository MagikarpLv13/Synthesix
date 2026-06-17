from __future__ import annotations

from difflib import unified_diff
from html import escape
from pathlib import Path
import re
import os

from evidence.changes import PageTextChange


STATUS_LABELS = {
    "unchanged": "No content change",
    "minor_change": "Minor change",
    "changed": "Significant content change",
    "inconclusive": "Comparison inconclusive",
}


def _relative_href(target: Path, from_dir: Path) -> str:
    return os.path.relpath(target.resolve(), from_dir.resolve()).replace(os.sep, "/")


def _status_badge_class(status: str) -> str:
    return {
        "unchanged": "confirmed",
        "minor_change": "to-verify",
        "changed": "discarded",
        "inconclusive": "unreviewed",
    }.get(status, "unreviewed")


def _fact(label: str, value: str) -> str:
    return (
        '<span class="result-fact">'
        f"<strong>{escape(label)}</strong>"
        f"<span>{escape(value)}</span>"
        "</span>"
    )


def _lines(value: str) -> list[str]:
    text = " ".join(str(value or "").split())
    return [
        part.strip()
        for part in re.split(r"(?<=[.!?])\s+", text)
        if part.strip()
    ]


def generate_page_comparison_report(
    *,
    output_path: Path,
    page_title: str,
    page_url: str,
    previous_captured_at: str,
    current_captured_at: str,
    previous_text: str,
    current_text: str,
    change: PageTextChange,
    base_dir: Path | None = None,
) -> str:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    diff = "\n".join(
        list(
            unified_diff(
                _lines(previous_text),
                _lines(current_text),
                fromfile=previous_captured_at,
                tofile=current_captured_at,
                lineterm="",
            )
        )[:500]
    )
    similarity = (
        f"{change.similarity * 100:.2f}%"
        if change.similarity is not None
        else "Unavailable"
    )
    asset_markup = """
    <style>
        body { max-width: 1100px; margin: 32px auto; padding: 0 20px;
            background: #f8fafc; color: #0f172a; font: 15px/1.5 Arial, sans-serif; }
        main { padding: 24px; border: 1px solid #cbd5e1; border-radius: 8px;
            background: #fff; }
        pre { overflow: auto; padding: 16px; border-radius: 6px;
            background: #0f172a; color: #e2e8f0; white-space: pre-wrap; }
    </style>
    """
    brand_markup = """
    <p class="section-eyebrow">Synthesix page monitoring</p>
    """
    if base_dir is not None:
        base_path = Path(base_dir)
        theme_href = _relative_href(base_path / "theme.css", output_path.parent)
        theme_script = _relative_href(base_path / "theme.js", output_path.parent)
        i18n_script = _relative_href(base_path / "i18n.js", output_path.parent)
        favicon_href = _relative_href(
            base_path / "assets" / "favicon.svg",
            output_path.parent,
        )
        logo_href = _relative_href(
            base_path / "assets" / "synthesix-mark.svg",
            output_path.parent,
        )
        asset_markup = f"""
    <link rel="icon" href="{escape(favicon_href, quote=True)}" type="image/svg+xml">
    <link rel="stylesheet" href="{escape(theme_href, quote=True)}">
    <script src="{escape(theme_script, quote=True)}"></script>
    <script src="{escape(i18n_script, quote=True)}"></script>
        """
        brand_markup = f"""
        <header class="topbar">
            <div class="brand">
                <img class="brand-logo" src="{escape(logo_href, quote=True)}" alt="">
                <div class="brand-copy">
                    <h1 class="brand-name">Synthesix</h1>
                    <span class="brand-subtitle">Page monitoring</span>
                </div>
            </div>
        </header>
        """
    facts = "".join(
        (
            _fact("Previous archive", previous_captured_at),
            _fact("Current archive", current_captured_at),
            _fact("Text similarity", similarity),
            _fact("Previous SHA-256", change.previous_sha256),
            _fact("Current SHA-256", change.current_sha256),
        )
    )
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page comparison - Synthesix</title>
    {asset_markup}
</head>
<body>
<main class="app app--wide">
    {brand_markup}
    <section class="investigation-section comparison-report">
        <div class="section-header">
            <div>
                <p class="section-eyebrow">Temporal comparison</p>
                <h2>{escape(page_title or page_url)}</h2>
            </div>
            <span class="status-badge status-badge--{_status_badge_class(change.status)}">
                {escape(STATUS_LABELS[change.status])}
            </span>
        </div>
        <p class="comparison-url">
            <a href="{escape(page_url, quote=True)}">{escape(page_url)}</a>
        </p>
        <div class="result-metadata result-facts comparison-facts">
            {facts}
        </div>
        <p class="session-note">
            Minor changes above the configured similarity threshold are separated
            from significant changes to reduce alerts caused by dynamic page details.
        </p>
        <h3>Normalized text difference</h3>
        <pre class="comparison-diff">{escape(diff or "No textual difference available.")}</pre>
    </section>
</main>
</body>
</html>
"""
    output_path.write_text(page, encoding="utf-8")
    return str(output_path)
