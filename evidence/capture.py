from __future__ import annotations

import asyncio
import base64
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from zendriver import cdp

from evidence.hashing import sha256_bytes


MIN_CAPTURE_SIZE = 8.0
MAX_CAPTURE_DIMENSION = 32768.0
MAX_CAPTURE_AREA = 100_000_000.0


@dataclass(frozen=True)
class CapturedPng:
    path: Path
    sha256: str
    byte_size: int
    width: float
    height: float


def normalize_selection(selection: Mapping) -> dict[str, float]:
    try:
        x = max(0.0, float(selection.get("x", 0)))
        y = max(0.0, float(selection.get("y", 0)))
        width = float(selection.get("width", 0))
        height = float(selection.get("height", 0))
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid evidence capture coordinates.") from exc

    if width < MIN_CAPTURE_SIZE or height < MIN_CAPTURE_SIZE:
        raise ValueError("The selected evidence area is too small.")
    if width > MAX_CAPTURE_DIMENSION or height > MAX_CAPTURE_DIMENSION:
        raise ValueError("The selected evidence area is too large.")
    if width * height > MAX_CAPTURE_AREA:
        raise ValueError("The selected evidence area contains too many pixels.")

    return {
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "scale": 1.0,
    }


def _write_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_bytes(content)
    os.replace(temporary_path, path)


async def capture_png(
    tab,
    output_path: Path,
    selection: Mapping,
) -> CapturedPng:
    normalized = normalize_selection(selection)
    encoded = await tab.send(
        cdp.page.capture_screenshot(
            format_="png",
            clip=cdp.page.Viewport(**normalized),
            from_surface=True,
            capture_beyond_viewport=True,
            optimize_for_speed=False,
        )
    )
    content = base64.b64decode(encoded, validate=True)
    output_path = Path(output_path)
    await asyncio.to_thread(_write_atomic, output_path, content)
    return CapturedPng(
        path=output_path,
        sha256=sha256_bytes(content),
        byte_size=len(content),
        width=normalized["width"],
        height=normalized["height"],
    )
