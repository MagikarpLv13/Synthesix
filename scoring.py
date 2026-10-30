import math
import re
import unicodedata
from dataclasses import dataclass
from typing import Callable, List, Mapping
from urllib.parse import unquote


ACCENT_TRANSLATION = str.maketrans({
    "é": "e",
    "è": "e",
    "ê": "e",
    "ë": "e",
    "à": "a",
    "â": "a",
    "ä": "a",
    "ï": "i",
    "î": "i",
    "ô": "o",
    "ö": "o",
    "ù": "u",
    "û": "u",
    "ü": "u",
    "ÿ": "y",
    "ç": "c",
})


@dataclass(frozen=True)
class ScoringWeights:
    exact_title: float = 4.5
    exact_description: float = 4.5
    url_match: float = 1.0
    natural_title_term: float = 2.25
    natural_description_term: float = 1.25
    natural_url_term: float = 0.5
    natural_full_coverage: float = 2.0
    natural_sequence: float = 1.5
    natural_sequence_maximum: float = 3.0
    filter_match: float = 1.0
    consensus_per_additional_engine: float = 1.0
    consensus_maximum: float = 2.0


@dataclass(frozen=True)
class ScoreComponent:
    key: str
    label: str
    score: float

    def to_payload(self) -> dict[str, str | float]:
        return {
            "key": self.key,
            "label": self.label,
            "score": self.score,
        }


@dataclass(frozen=True)
class ScoreBreakdown:
    components: tuple[ScoreComponent, ...]

    @property
    def total(self) -> float:
        return sum(component.score for component in self.components)

    def to_payload(self) -> list[dict[str, str | float]]:
        return [component.to_payload() for component in self.components]


DEFAULT_SCORING_WEIGHTS = ScoringWeights()

_ADVANCED_QUERY_OPERATORS = (
    "site:",
    "-site:",
    "inurl:",
    "intitle:",
    "intext:",
    "inbody:",
    "filetype:",
    "ext:",
    "after:",
    "before:",
)
_NATURAL_STOP_WORDS = frozenset({
    "a",
    "an",
    "and",
    "au",
    "aux",
    "de",
    "des",
    "du",
    "el",
    "en",
    "et",
    "for",
    "la",
    "le",
    "les",
    "of",
    "or",
    "the",
    "un",
    "une",
    "y",
})
_EXTRA_LATIN_TRANSLATION = str.maketrans({
    "æ": "ae",
    "đ": "d",
    "ð": "d",
    "ł": "l",
    "œ": "oe",
    "ø": "o",
    "ß": "ss",
    "þ": "th",
})


def extract_scoring_terms(search_term: str) -> List[str]:
    quoted_terms = re.findall(r'"([^"]+)"', search_term)
    if quoted_terms:
        return [term.strip() for term in quoted_terms if term.strip()]

    terms = []
    parts = re.split(r'\s+(AND|OR)\s+', search_term)
    for part in parts:
        if part not in ['AND', 'OR']:
            clean_term = part.strip().strip('"').strip("()")
            if clean_term:
                terms.append(clean_term)
    return terms


def _strip_basic_accents(value: str) -> str:
    return _normalize_text(value)


def _normalize_text(value: object) -> str:
    translated = str(value or "").casefold().translate(ACCENT_TRANSLATION)
    translated = translated.translate(_EXTRA_LATIN_TRANSLATION)
    decomposed = unicodedata.normalize("NFKD", translated)
    without_marks = "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )
    return " ".join(re.findall(r"[^\W_]+", without_marks, flags=re.UNICODE))


def _is_natural_query(search_term: str) -> bool:
    query = str(search_term or "").strip()
    lowered = query.lower()
    if not query:
        return False
    if any(marker in lowered for marker in _ADVANCED_QUERY_OPERATORS):
        return False
    if any(marker in query for marker in ('"', "(", ")")):
        return False
    if re.search(r"\b(?:AND|OR|NOT)\b", query):
        return False
    return re.search(r'(?:^|\s)-(?:"[^"]+"|\S+)', query) is None


def _natural_query_terms(search_term: str) -> tuple[str, ...]:
    terms = []
    seen = set()
    for term in _normalize_text(search_term).split():
        if term in seen:
            continue
        seen.add(term)
        terms.append(term)

    significant_terms = [
        term for term in terms if term not in _NATURAL_STOP_WORDS
    ]
    return tuple(significant_terms or terms)


def _natural_term_weight(term: str) -> float:
    if term.isdigit():
        return 1.35 if len(term) == 4 else 1.15
    if len(term) <= 2:
        return 0.8
    return 1.0


def _minimum_natural_matches(term_count: int) -> int:
    if term_count <= 2:
        return term_count
    return max(2, math.ceil(term_count * 0.6))


def _longest_ordered_run(
    query_terms: tuple[str, ...],
    field_terms: tuple[str, ...],
) -> int:
    if len(query_terms) < 2 or len(field_terms) < 2:
        return 0

    previous = [0] * (len(field_terms) + 1)
    longest = 0
    for query_term in query_terms:
        current = [0]
        for index, field_term in enumerate(field_terms, start=1):
            if query_term == field_term:
                current.append(previous[index - 1] + 1)
                longest = max(longest, current[-1])
            else:
                current.append(0)
        previous = current
    return longest


def _build_natural_relevance_explainer(
    search_term: str,
    weights: ScoringWeights,
) -> Callable[[Mapping], ScoreBreakdown]:
    query_terms = _natural_query_terms(search_term)
    query_term_set = set(query_terms)
    term_weights = {
        term: _natural_term_weight(term)
        for term in query_terms
    }
    minimum_matches = _minimum_natural_matches(len(query_terms))

    def explain_row(row: Mapping) -> ScoreBreakdown:
        if not query_terms:
            return ScoreBreakdown(())

        title_terms = tuple(_normalize_text(row.get("title", "")).split())
        description_terms = tuple(
            _normalize_text(row.get("description", "")).split()
        )
        url_terms = tuple(
            _normalize_text(unquote(str(row.get("link", "")))).split()
        )
        title_matches = query_term_set.intersection(title_terms)
        description_matches = query_term_set.intersection(description_terms)
        url_matches = query_term_set.intersection(url_terms)
        covered_terms = title_matches | description_matches | url_matches

        if len(covered_terms) < minimum_matches:
            return ScoreBreakdown(())

        components = []
        if title_matches:
            components.append(ScoreComponent(
                "natural_title_terms",
                "Query terms in title",
                sum(term_weights[term] for term in title_matches)
                * weights.natural_title_term,
            ))
        if description_matches:
            components.append(ScoreComponent(
                "natural_description_terms",
                "Query terms in description",
                sum(term_weights[term] for term in description_matches)
                * weights.natural_description_term,
            ))
        if url_matches:
            components.append(ScoreComponent(
                "natural_url_terms",
                "Query terms in URL",
                sum(term_weights[term] for term in url_matches)
                * weights.natural_url_term,
            ))

        title_run = _longest_ordered_run(
            query_terms,
            tuple(
                term for term in title_terms
                if term not in _NATURAL_STOP_WORDS
            ),
        )
        description_run = _longest_ordered_run(
            query_terms,
            tuple(
                term for term in description_terms
                if term not in _NATURAL_STOP_WORDS
            ),
        )
        ordered_run = max(title_run, description_run)
        if ordered_run >= 2:
            components.append(ScoreComponent(
                "natural_sequence",
                "Query terms appear in sequence",
                min(
                    (ordered_run - 1) * weights.natural_sequence,
                    weights.natural_sequence_maximum,
                ),
            ))

        if covered_terms == query_term_set:
            components.append(ScoreComponent(
                "natural_full_coverage",
                "All significant query terms matched",
                weights.natural_full_coverage,
            ))

        return ScoreBreakdown(tuple(components))

    return explain_row


def _build_structured_relevance_explainer(
    search_term: str,
    weights: ScoringWeights,
) -> Callable[[Mapping], ScoreBreakdown]:
    prepared_terms = tuple(
        normalized_term
        for term in extract_scoring_terms(search_term)
        if (normalized_term := _normalize_text(term.replace('"', "")))
    )

    def explain_row(row: Mapping) -> ScoreBreakdown:
        title = _normalize_text(row.get("title", ""))
        description = _normalize_text(row.get("description", ""))
        link = _normalize_text(unquote(str(row.get("link", ""))))
        compact_link = link.replace(" ", "")
        title_matches = sum(term in title for term in prepared_terms)
        description_matches = sum(term in description for term in prepared_terms)
        url_matches = sum(
            term in link or term.replace(" ", "") in compact_link
            for term in prepared_terms
        )

        components = []
        if title_matches:
            components.append(ScoreComponent(
                "exact_title",
                _match_label("Exact query term in title", title_matches),
                title_matches * weights.exact_title,
            ))
        if description_matches:
            components.append(ScoreComponent(
                "exact_description",
                _match_label("Exact query term in description", description_matches),
                description_matches * weights.exact_description,
            ))
        if url_matches:
            components.append(ScoreComponent(
                "url_match",
                _match_label("Query term variant in URL", url_matches),
                url_matches * weights.url_match,
            ))

        return ScoreBreakdown(tuple(components))

    return explain_row


def build_relevance_explainer(
    search_term: str,
    weights: ScoringWeights = DEFAULT_SCORING_WEIGHTS,
) -> Callable[[Mapping], ScoreBreakdown]:
    if _is_natural_query(search_term):
        return _build_natural_relevance_explainer(search_term, weights)
    return _build_structured_relevance_explainer(search_term, weights)


def _match_label(label: str, count: int) -> str:
    if count == 1:
        return label
    return f"{label} ({count} matches)"


def add_context_to_breakdown(
    breakdown: ScoreBreakdown,
    *,
    engine_count: int,
    filters_matched: bool,
    weights: ScoringWeights = DEFAULT_SCORING_WEIGHTS,
) -> ScoreBreakdown:
    components = list(breakdown.components)
    if engine_count > 1 and (breakdown.total > 0 or filters_matched):
        consensus_score = min(
            (engine_count - 1) * weights.consensus_per_additional_engine,
            weights.consensus_maximum,
        )
        components.append(ScoreComponent(
            "engine_consensus",
            f"Returned by {engine_count} search engines",
            consensus_score,
        ))
    if filters_matched:
        components.append(ScoreComponent(
            "filter_match",
            "Configured filters matched",
            weights.filter_match,
        ))
    return ScoreBreakdown(tuple(components))


def build_relevance_scorer(search_term: str) -> Callable[[dict], float]:
    explainer = build_relevance_explainer(search_term)

    def score_row(row: dict) -> float:
        return explainer(row).total

    return score_row


def calculate_relevance(row: dict, search_term: str) -> float:
    """Calculate a deterministic relevance score.

    Args:
        row: Search result with title, description, and link fields.
        search_term: Natural or structured search query.

    Returns:
        The relevance score. Natural queries use weighted token coverage,
        while structured queries preserve exact phrase/operator semantics.
    """
    return build_relevance_scorer(search_term)(row)
