import re
from dataclasses import dataclass
from typing import Callable, List, Mapping


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
    return value.translate(ACCENT_TRANSLATION)


def build_relevance_explainer(
    search_term: str,
    weights: ScoringWeights = DEFAULT_SCORING_WEIGHTS,
) -> Callable[[Mapping], ScoreBreakdown]:
    prepared_terms = []
    for term in extract_scoring_terms(search_term):
        clean_term = term.replace('"', '')
        lower_term = clean_term.lower()
        lower_term_no_accent = _strip_basic_accents(lower_term)
        prepared_terms.append((
            lower_term,
            lower_term_no_accent,
            " " in lower_term_no_accent or "-" in lower_term_no_accent,
        ))

    def explain_row(row: Mapping) -> ScoreBreakdown:
        title = str(row["title"]).lower()
        description = str(row["description"]).lower()
        link = str(row["link"]).lower()
        title_matches = 0
        description_matches = 0
        url_matches = 0

        for lower_term, lower_term_no_accent, can_have_url_variants in prepared_terms:
            if lower_term in title:
                title_matches += 1
            if lower_term in description:
                description_matches += 1

            if can_have_url_variants:
                hyphenated_term = lower_term_no_accent.replace(" ", "-")
                if hyphenated_term in link:
                    url_matches += 1

                spaced_term = lower_term_no_accent.replace(" ", "")
                if spaced_term in link:
                    url_matches += 1

            if lower_term_no_accent in link:
                url_matches += 1

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
    """Calcul relevance score

    Args:
        row (dict): row of the dataframe
        search_term (str): search term

    Returns:
        int: relevance score
    """
    return build_relevance_scorer(search_term)(row)
