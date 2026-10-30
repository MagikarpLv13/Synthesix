"""Pure exact-phrase and explicit-dork query syntax."""

import re


def smart_parse(query: str)-> str:
    """Quote plain terms; comma-separated terms are combined with AND."""

    terms = [t.strip() for t in query.split(",") if t.strip()]
    if len(terms) == 0:
        return ""
    if len(terms) == 1:
        return f'"{terms[0]}"'

    all_and = " AND ".join(f'"{t}"' for t in terms)
    return f"({all_and})"


def is_advanced_query(query: str) -> bool:
    lowered = query.lower()
    advanced_markers = (
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
        "\"",
        "(",
    )
    if any(op in lowered for op in advanced_markers):
        return True
    if re.search(r'(?:^|\s)-(?:"[^"]+"|\S+)', query):
        return True
    return re.search(r"\b(AND|OR|NOT)\b", query) is not None
