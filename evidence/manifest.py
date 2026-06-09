from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Mapping


EVIDENCE_MANIFEST_SCHEMA_VERSION = 1


def build_evidence_manifest(
    *,
    capture_id: str,
    investigation_id: str,
    result_id: str,
    name: str,
    captured_at: str,
    source_url: str,
    page_title: str,
    capture_scope: str,
    selection: Mapping,
    browser_context: Mapping,
    tool_version: str,
    artifacts: list[Mapping],
) -> dict:
    return {
        "schema_version": EVIDENCE_MANIFEST_SCHEMA_VERSION,
        "capture_id": capture_id,
        "investigation_id": investigation_id,
        "result_id": result_id,
        "name": name,
        "captured_at_utc": captured_at,
        "source": {
            "url": source_url,
            "title": page_title,
        },
        "capture": {
            "scope": capture_scope,
            "selection_css_pixels": dict(selection),
            "browser_context": dict(browser_context),
        },
        "tool": {
            "name": "Synthesix",
            "version": tool_version,
        },
        "artifacts": [dict(artifact) for artifact in artifacts],
    }


def write_manifest(path: Path, manifest: Mapping) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(
            dict(manifest),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    os.replace(temporary_path, path)
