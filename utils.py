import re
import json
import os
import logging
from html import escape, unescape
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from settings import get_settings


logger = logging.getLogger(__name__)
HISTORY_DATE_FORMATS = ("%d/%m/%Y %H:%M",)


def _html_escape(value) -> str:
    return escape(str(value), quote=True)


def _theme_assets(asset_prefix: str = "") -> str:
    return f"""
    <link rel="icon" href="{asset_prefix}assets/favicon.svg" type="image/svg+xml">
    <link rel="stylesheet" href="{asset_prefix}theme.css">
    <script src="{asset_prefix}theme.js"></script>
    <script src="{asset_prefix}i18n.js"></script>
"""


def _brand_markup(subtitle: str, asset_prefix: str = "") -> str:
    return f"""
            <div class="brand">
                <img class="brand-logo" src="{asset_prefix}assets/synthesix-mark.svg" alt="">
                <div class="brand-copy">
                    <h1 class="brand-name">Synthesix</h1>
                    <span class="brand-subtitle">{_html_escape(subtitle)}</span>
                </div>
            </div>
"""


def _relative_href(target: Path, from_dir: Path) -> str:
    return os.path.relpath(target.resolve(), from_dir.resolve()).replace(os.sep, "/")


def _asset_prefix(from_dir: Path, base_dir: Path) -> str:
    relative_base = _relative_href(base_dir, from_dir)
    if relative_base == ".":
        return ""
    return relative_base.rstrip("/") + "/"


def _home_navigation_script() -> str:
    return """
    <script>
        (() => {
            const state = { pendingAction: null };
            const status = document.querySelector("[data-page-status]");

            window.synthesixPage = {
                consumeAction() {
                    const action = state.pendingAction;
                    state.pendingAction = null;
                    return action;
                },
                setStatus(message, isError = false) {
                    if (!status) {
                        return;
                    }
                    status.textContent = String(message || "");
                    status.classList.toggle("is-error", Boolean(isError));
                }
            };

            document.querySelectorAll("[data-home-link]").forEach((link) => {
                link.addEventListener("click", (event) => {
                    event.preventDefault();
                    state.pendingAction = { action: "focus_home" };
                });
            });

            document.querySelectorAll("[data-page-action]").forEach((button) => {
                button.addEventListener("click", () => {
                    let payload = {};
                    try {
                        payload = JSON.parse(button.dataset.actionPayload || "{}");
                    } catch (_error) {
                        window.synthesixPage.setStatus(
                            "This report action is invalid.",
                            true
                        );
                        return;
                    }
                    state.pendingAction = {
                        action: button.dataset.pageAction,
                        ...payload
                    };
                    window.synthesixPage.setStatus("Processing...");
                });
            });
        })();
    </script>
"""


def _read_history_entries(path: Path) -> list[dict]:
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as f:
            history = json.load(f)
    except (OSError, json.JSONDecodeError):
        logger.debug("Unable to read search history file: %s", path, exc_info=True)
        return []

    if not isinstance(history, list):
        return []
    return [entry for entry in history if isinstance(entry, dict)]


def _parse_history_datetime(entry: dict) -> datetime | None:
    timestamp = str(entry.get("timestamp", "")).strip()
    if timestamp:
        try:
            return datetime.fromisoformat(timestamp)
        except ValueError:
            logger.debug("Invalid history timestamp ignored: %s", timestamp)

    date = str(entry.get("date", "")).strip()
    for date_format in HISTORY_DATE_FORMATS:
        try:
            return datetime.strptime(date, date_format)
        except ValueError:
            continue
    return None


def _history_sort_key(entry: dict) -> float:
    parsed = _parse_history_datetime(entry)
    if parsed is None:
        return 0.0
    return parsed.timestamp()


def _sorted_history_entries(history: list[dict]) -> list[dict]:
    indexed_history = list(enumerate(history))
    indexed_history.sort(
        key=lambda item: (_history_sort_key(item[1]), item[0]),
        reverse=True,
    )
    return [entry for _, entry in indexed_history]


def load_search_history(limit: int | None = None) -> List[dict]:
    settings = get_settings()
    limit = settings.default_history_limit if limit is None else limit
    history = _read_history_entries(settings.history_json_path)

    searches = []
    seen_searches = set()
    for entry in _sorted_history_entries(history):
        query = str(entry.get("query", "")).strip()
        display_query = query or str(entry.get("smart_query", "")).strip()
        filters = entry.get("filters", {}) if isinstance(entry.get("filters", {}), dict) else {}
        dedupe_key = (query, json.dumps(filters, sort_keys=True))
        if not display_query or dedupe_key in seen_searches:
            continue
        seen_searches.add(dedupe_key)
        searches.append(
            {
                "query": query,
                "display_query": display_query,
                "smart_query": str(entry.get("smart_query", "")).strip(),
                "date": str(entry.get("date", "")).strip(),
                "nb_results": entry.get("nb_results", ""),
                "filters": filters,
                "investigation_id": str(entry.get("investigation_id", "") or ""),
            }
        )
        if len(searches) >= limit:
            break

    return searches


def add_to_history(
    query: str,
    smart_query: str,
    nb_results: int,
    link: str,
    filters: dict | None = None,
    investigation_id: str | None = None,
):
    """Add a search to the history
    
    Args:
        query (str): The query
        nb_results (int): The number of results
        link (str): The link to the search results
    """
    
    settings = get_settings()
    path = settings.history_json_path
    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y %H:%M")
    data = {
        "date": date_str,
        "timestamp": now.isoformat(timespec="microseconds"),
        "query": query,
        "smart_query": smart_query,
        "nb_results": nb_results,
        "link": link
    }
    if filters:
        data["filters"] = filters
    if investigation_id:
        data["investigation_id"] = investigation_id

    path.parent.mkdir(parents=True, exist_ok=True)
    history = _read_history_entries(path)
    
    history.append(data)
    with path.open("w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)


def clear_synthesix_history() -> int:
    settings = get_settings()
    paths = {
        settings.history_json_path,
        settings.history_report_path,
        *settings.history_dir.glob("search_results_*.html"),
    }
    removed = 0
    for path in paths:
        try:
            if path.is_file():
                path.unlink()
                removed += 1
        except OSError:
            logger.warning("Unable to remove Synthesix history file: %s", path, exc_info=True)

    generate_history_html()
    return removed


def generate_history_html():
    """Generate an HTML report of the history
    
    Returns:
        str: The path to the generated HTML report
    """
    settings = get_settings()
    path = settings.history_json_path
    output_path = settings.history_report_path
    
    history = _read_history_entries(path)

    # Début du HTML
    search_href = _relative_href(settings.base_dir / "index.html", output_path.parent)
    asset_prefix = _asset_prefix(output_path.parent, settings.base_dir)

    html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Synthesix History</title>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    {_theme_assets(asset_prefix)}
</head>
<body>
    <main class="app app--wide">
        <header class="topbar">
            {_brand_markup("Search history", asset_prefix)}
            <div class="top-actions">
                <a href="{search_href}" data-home-link class="nav-link">Search</a>
            </div>
        </header>

        <section aria-label="Search history">
            <div class="page-header">
                <h2 class="page-title">Search history</h2>
                <div class="page-meta">
                    <span class="meta-pill">{len(history)} saved searches</span>
                </div>
            </div>
            <div class="table-shell">
                <table id="historyTable" class="data-table display">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Original Query</th>
                            <th>Smart Query</th>
                            <th>Number of results</th>
                            <th>Link to results</th>
                        </tr>
                    </thead>
                    <tbody>
'''
    rows = []
    for entry in _sorted_history_entries(history):
        date = _html_escape(entry.get('date', ''))
        sort_key = _html_escape(f"{_history_sort_key(entry):.6f}")
        query = _html_escape(entry.get('query') or entry.get('smart_query', ''))
        smart_query = _html_escape(entry.get('smart_query', ''))
        nb_results = _html_escape(entry.get('nb_results', ''))
        link = _html_escape(entry.get('link', '#'))
        rows.append(f"""
            <tr>
                <td data-order="{sort_key}">{date}</td>
                <td>{query}</td>
                <td>{smart_query}</td>
                <td>{nb_results}</td>
                <td><a href="{link}" target="_blank" rel="noopener noreferrer">View results</a></td>
            </tr>
        """)
    html += "".join(rows)
    html += '''
                    </tbody>
                </table>
            </div>
        </section>
    </main>
    <script>
        $(document).ready(function() {
            $('#historyTable').DataTable({
                order: [[0, 'desc']],
                pageLength: 50,
                lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]]
            });
        });
    </script>
''' + _home_navigation_script() + '''
</body>
</html>
'''
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.write(html)
    return str(output_path)

def js_like_to_json(js_text):
    """Convert a JS like text to a JSON object

    Args:
        js_text (str): The JS like text to convert

    Returns:
        dict: The JSON object
    """

    # Replace void 0 by null
    js_text = js_text.replace("void 0", "null")

    js_text = re.sub(r"(^|\{|\[|,)\s*([a-zA-Z0-9_]+)\s*:", r'\1"\2":', js_text)

    # Remove the u003c strings
    js_text = js_text.replace("\\u003C", "<")
    js_text = js_text.replace("&quot;", "")
    js_text = unescape(js_text)

    # Remove the html tags
    js_text = re.sub(r"<[^>]+>", "", js_text)

    # Add [{ at the beginning and }] at the end
    js_text = "[{" + js_text + "}]"

    # Parse to JSON
    try:
        data = json.loads(js_text)
        return data
    except json.JSONDecodeError:
        logger.debug("Unable to parse JavaScript-like JSON payload.", exc_info=True)
        return None


def smart_parse(query: str)-> str:
    """Parse a query to a smart query

    Args:
        query (str): The query to parse

    Returns:
        str: The smart query
    
    Example:
        "apple, banana, orange" -> "("apple" AND "banana" AND "orange") OR ("apple" OR "banana" OR "orange")"
        "apple, banana" -> "("apple" AND "banana") OR ("apple" OR "banana")"
        "apple" -> "apple"
        "" -> ""
    """

    terms = [t.strip() for t in query.split(",") if t.strip()]
    if len(terms) == 0:
        return ""
    if len(terms) == 1:
        return f'"{terms[0]}"'

    all_and = " AND ".join(f'"{t}"' for t in terms)
    #all_or = " OR ".join(f'"{t}"' for t in terms) # Searches are more relevant without OR
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


def generate_html_report(df: pd.DataFrame, search_term: str, total_time: float, nb_results: int) -> Optional[str]:
    """Generate an HTML report of the search results
    
    Args:
        df (pd.DataFrame): The DataFrame containing the search results
        search_term (str): The search term
        total_time (float): The total time taken to perform the search
        nb_results (int): The number of results

    Returns:
        str: The path to the generated HTML report
    """

    coverage = tuple(df.attrs.get("query_coverage", ()))
    search_context = df.attrs.get("search_context", {})
    if not isinstance(search_context, dict):
        search_context = {}
    if "relevance_score" in df.columns:
        df = (
            df.sort_values("relevance_score", ascending=False, kind="stable")
            .reset_index(drop=True)
        )
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    settings = get_settings()
    output_path = settings.search_results_path(date_str)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    asset_prefix = _asset_prefix(output_path.parent, settings.base_dir)
    search_href = _relative_href(settings.base_dir / "index.html", output_path.parent)
    history_href = _relative_href(settings.history_report_path, output_path.parent)
    safe_search_term = _html_escape(search_term)
    safe_output_path = _html_escape(output_path)
    coverage_engines = sorted({
        str(engine)
        for item in coverage
        if isinstance(item, dict)
        for engine in item.get("engines", {})
    })
    coverage_html = ""
    if len(coverage) > 1 and len(coverage_engines) > 1:
        coverage_headers = "".join(
            f"<th>{_html_escape(engine.title())}</th>"
            for engine in coverage_engines
        )
        coverage_rows = []
        for item in coverage:
            if not isinstance(item, dict):
                continue
            engine_states = item.get("engines", {})
            cells = []
            for engine in coverage_engines:
                state = engine_states.get(engine, {})
                status = str(state.get("status", "not run"))
                if status == "ok":
                    cell_markup = _html_escape(
                        str(int(state.get("count", 0) or 0))
                    )
                else:
                    retry_payload = {
                        "query": str(item.get("query", "") or ""),
                        "engine": engine,
                        "originalQuery": str(
                            search_context.get("original_query", "") or ""
                        ),
                        "filters": search_context.get("filters", {}),
                        "numResults": search_context.get("num_results", 20),
                        "investigationId": str(
                            search_context.get("investigation_id", "") or ""
                        ),
                    }
                    payload_json = _html_escape(
                        json.dumps(
                            retry_payload,
                            ensure_ascii=True,
                            separators=(",", ":"),
                        )
                    )
                    cell_markup = (
                        f'<span class="coverage-state">{_html_escape(status)}</span>'
                        f'<button type="button" class="secondary-button coverage-retry" '
                        f'data-page-action="retry_search_combination" '
                        f'data-action-payload="{payload_json}">Retry</button>'
                    )
                cells.append(f"<td>{cell_markup}</td>")
            coverage_rows.append(
                "<tr>"
                f"<td><code>{_html_escape(item.get('query', ''))}</code></td>"
                f"{''.join(cells)}"
                "</tr>"
            )
        coverage_html = f"""
            <details class="coverage-summary">
                <summary>Query coverage ({len(coverage)} variants)</summary>
                <p>Counts distinguish successful zero-result searches from timeouts,
                challenges, and other errors.</p>
                <p class="action-status" data-page-status aria-live="polite"></p>
                <div class="table-shell">
                    <table class="data-table coverage-table">
                        <thead>
                            <tr><th>Exact query</th>{coverage_headers}</tr>
                        </thead>
                        <tbody>{''.join(coverage_rows)}</tbody>
                    </table>
                </div>
            </details>
        """

    html_head = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Results for: {safe_search_term}</title>
    {_theme_assets(asset_prefix)}
</head>
<body>
    <main class="app app--wide">
        <header class="topbar">
            {_brand_markup("Search results", asset_prefix)}
            <div class="top-actions">
                <a href="{search_href}" data-home-link class="nav-link">Search</a>
                <a href="{history_href}" class="nav-link">History</a>
            </div>
        </header>

        <section aria-label="Search results">
            <div class="page-header">
                <h2 class="page-title">Search Results for: {safe_search_term}</h2>
                <div class="page-meta">
                    <span class="meta-pill">Total time: {total_time:.3f} seconds</span>
                    <span class="meta-pill">Created: {date_str}</span>
                    <span class="meta-pill">Relevant results: {nb_results}</span>
                    <span class="meta-pill">Report: {safe_output_path}</span>
                </div>
            </div>
            {coverage_html}
            <div id="results" class="report-results" role="list">
"""

    if nb_results == 0:
        rows_html = """
                <div class="report-empty" role="status">
                No relevant results found
                </div>
        """
        html_footer = """
            </div>
        </section>
    </main>
""" + _home_navigation_script() + """
</body>
</html>
"""
        full_html = html_head + rows_html + html_footer
        
        with output_path.open("w", encoding="utf-8") as f:
            f.write(full_html)
            
        return str(output_path.resolve())
        
        
    rows = []
    for _, row in df.iterrows():
        title = _html_escape(row["title"])
        desc = _html_escape(row["description"])
        link = _html_escape(row["link"])
        source = _html_escape(row["source"])
        numeric_score = float(row["relevance_score"])
        score = f"{numeric_score:.2f}"
        query_variants = row.get("query_variants", [])
        if not isinstance(query_variants, (list, tuple)):
            query_variants = []
        variants_markup = "".join(
            f"<code>{_html_escape(query)}</code>"
            for query in query_variants
        )
        if not variants_markup:
            variants_markup = "<span>No query variant recorded</span>"
        score_breakdown = row.get("score_breakdown", [])
        breakdown_items = []
        if isinstance(score_breakdown, list):
            for component in score_breakdown:
                if not isinstance(component, dict):
                    continue
                component_score = float(component.get("score", 0) or 0)
                component_label = _html_escape(component.get("label", "Score component"))
                breakdown_items.append(
                    f"<li>+{component_score:.1f} {component_label}</li>"
                )
        if breakdown_items:
            score_markup = (
                f'<details class="score-breakdown"><summary>{score}</summary>'
                f"<ul>{''.join(breakdown_items)}</ul>"
                "<small>Multi-engine consensus confirms repeated retrieval, "
                "not factual accuracy.</small></details>"
            )
        else:
            score_markup = f'<span class="score-value">{score}</span>'
        rows.append(f"""
                <article class="report-result-card" role="listitem" data-score="{numeric_score:.6f}">
                    <div class="result-heading">
                        <div class="result-title-block">
                            <a class="result-title" href="{link}" target="_blank" rel="noopener noreferrer">{title}</a>
                            <a class="result-url" href="{link}" target="_blank" rel="noopener noreferrer">{link}</a>
                        </div>
                        <div class="report-result-score" aria-label="Relevance score {score}">
                            <span class="score-label">Score</span>
                            {score_markup}
                        </div>
                    </div>
                    <p class="result-description">{desc}</p>
                    <div class="result-metadata" aria-label="Result metadata">
                        <span class="meta-pill">Source: {source}</span>
                    </div>
                    <div class="report-query-list">
                        <strong>Exact query</strong>
                        <div class="report-query-values">{variants_markup}</div>
                    </div>
                </article>
        """)
    rows_html = "".join(rows)

    html_footer = """
            </div>
        </section>
    </main>
""" + _home_navigation_script() + """
</body>
</html>
"""

    full_html = html_head + rows_html + html_footer

    with output_path.open("w", encoding="utf-8") as f:
        f.write(full_html)

    return str(output_path.resolve())
