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
    i18n_script = ""
    if base_dir is not None:
        relative_script = os.path.relpath(
            (Path(base_dir) / "i18n.js").resolve(),
            output_path.parent.resolve(),
        ).replace(os.sep, "/")
        i18n_script = f'<script src="{escape(relative_script, quote=True)}"></script>'
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page comparison - Synthesix</title>
    <style>
        body {{ max-width: 1100px; margin: 32px auto; padding: 0 20px;
            background: #f8fafc; color: #0f172a; font: 15px/1.5 Arial, sans-serif; }}
        main {{ padding: 24px; border: 1px solid #cbd5e1; border-radius: 8px;
            background: #fff; }}
        h1 {{ margin: 0 0 8px; }}
        a {{ color: #1d4ed8; overflow-wrap: anywhere; }}
        dl {{ display: grid; grid-template-columns: max-content 1fr; gap: 6px 16px; }}
        dt {{ font-weight: 700; }}
        dd {{ margin: 0; overflow-wrap: anywhere; }}
        pre {{ overflow: auto; padding: 16px; border-radius: 6px;
            background: #0f172a; color: #e2e8f0; white-space: pre-wrap; }}
    </style>
    {i18n_script}
</head>
<body>
<main>
    <p>Synthesix page monitoring</p>
    <h1>{escape(STATUS_LABELS[change.status])}</h1>
    <h2>{escape(page_title or page_url)}</h2>
    <p><a href="{escape(page_url, quote=True)}">{escape(page_url)}</a></p>
    <dl>
        <dt>Previous archive</dt><dd>{escape(previous_captured_at)}</dd>
        <dt>Current archive</dt><dd>{escape(current_captured_at)}</dd>
        <dt>Text similarity</dt><dd>{similarity}</dd>
        <dt>Previous SHA-256</dt><dd>{escape(change.previous_sha256)}</dd>
        <dt>Current SHA-256</dt><dd>{escape(change.current_sha256)}</dd>
    </dl>
    <p>
        Minor changes above the configured similarity threshold are separated
        from significant changes to reduce alerts caused by dynamic page details.
    </p>
    <h2>Normalized text difference</h2>
    <pre>{escape(diff or "No textual difference available.")}</pre>
</main>
</body>
</html>
"""
    output_path.write_text(page, encoding="utf-8")
    return str(output_path)
