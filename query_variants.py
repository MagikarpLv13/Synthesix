import re
import unicodedata
from collections.abc import Iterable

from utils import is_advanced_query


MAX_QUERY_LENGTH = 500


def _without_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )


def suggest_query_variants(query: str, limit: int) -> tuple[dict[str, str], ...]:
    query = str(query or "").strip()
    if not query or limit <= 0 or is_advanced_query(query):
        return ()

    words = query.split()
    candidates: list[tuple[str, str]] = []

    accentless = _without_accents(query)
    if accentless != query:
        candidates.append((accentless, "Without accents"))

    spaced = " ".join(re.sub(r"[-_]+", " ", query).split())
    if spaced != query:
        candidates.append((spaced, "Spaces instead of separators"))

    if 2 <= len(words) <= 5:
        candidates.append((" ".join(reversed(words)), "Reversed word order"))
        candidates.append(("-".join(words), "Hyphenated form"))
        candidates.append(("_".join(words), "Underscored form"))
        candidates.append(
            (" ".join([words[0][0], *words[1:]]), "First-name initial")
        )

    lowered = query.lower()
    if lowered != query:
        candidates.append((lowered, "Lowercase form"))

    suggestions = []
    seen = {query}
    for value, label in candidates:
        value = value.strip()
        if not value or len(value) > MAX_QUERY_LENGTH or value in seen:
            continue
        seen.add(value)
        suggestions.append({"query": value, "label": label})
        if len(suggestions) >= limit:
            break
    return tuple(suggestions)


def normalize_query_variants(
    primary_query: str,
    variants: Iterable[object] | object | None,
    limit: int,
) -> tuple[str, ...]:
    primary_query = str(primary_query or "").strip()
    normalized = [primary_query]
    seen = {primary_query}

    if isinstance(variants, (str, bytes)) or not isinstance(variants, Iterable):
        variants = ()

    for variant in variants:
        if not isinstance(variant, str):
            continue
        value = variant.strip()
        if not value or len(value) > MAX_QUERY_LENGTH or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
        if len(normalized) >= max(1, limit):
            break
    return tuple(normalized)
