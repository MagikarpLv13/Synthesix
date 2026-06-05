import re
from typing import Callable, List


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


def build_relevance_scorer(search_term: str) -> Callable[[dict], float]:
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

    def score_row(row: dict) -> float:
        title = str(row["title"]).lower()
        description = str(row["description"]).lower()
        link = str(row["link"]).lower()
        score = 0.0

        for lower_term, lower_term_no_accent, can_have_url_variants in prepared_terms:
            if lower_term in title:
                score += 4.5
            if lower_term in description:
                score += 4.5

            if can_have_url_variants:
                hyphenated_term = lower_term_no_accent.replace(" ", "-")
                if hyphenated_term in link:
                    score += 1

                spaced_term = lower_term_no_accent.replace(" ", "")
                if spaced_term in link:
                    score += 1

            if lower_term_no_accent in link:
                score += 1

        return score

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
