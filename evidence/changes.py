from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher

from evidence.hashing import sha256_bytes


SIGNIFICANT_CHANGE_THRESHOLD = 0.98
MAX_COMPARISON_TOKENS = 20_000


@dataclass(frozen=True)
class PageTextChange:
    status: str
    similarity: float | None
    previous_sha256: str
    current_sha256: str


def compare_page_text(
    previous_text: str,
    current_text: str,
) -> PageTextChange:
    previous = " ".join(str(previous_text or "").split())
    current = " ".join(str(current_text or "").split())
    previous_sha256 = sha256_bytes(previous.encode("utf-8")) if previous else ""
    current_sha256 = sha256_bytes(current.encode("utf-8")) if current else ""

    if not previous or not current:
        return PageTextChange(
            status="inconclusive",
            similarity=None,
            previous_sha256=previous_sha256,
            current_sha256=current_sha256,
        )
    if previous_sha256 == current_sha256:
        return PageTextChange(
            status="unchanged",
            similarity=1.0,
            previous_sha256=previous_sha256,
            current_sha256=current_sha256,
        )

    similarity = SequenceMatcher(
        None,
        previous.split()[:MAX_COMPARISON_TOKENS],
        current.split()[:MAX_COMPARISON_TOKENS],
        autojunk=True,
    ).ratio()
    return PageTextChange(
        status=(
            "minor_change"
            if similarity >= SIGNIFICANT_CHANGE_THRESHOLD
            else "changed"
        ),
        similarity=similarity,
        previous_sha256=previous_sha256,
        current_sha256=current_sha256,
    )
