import re
import json
from html import escape, unescape
import pandas as pd
from datetime import datetime
import os
from typing import List, Optional


def _html_escape(value) -> str:
    return escape(str(value), quote=True)


def _theme_assets(asset_prefix: str = "") -> str:
    return f"""
    <link rel="stylesheet" href="{asset_prefix}theme.css">
    <script src="{asset_prefix}theme.js"></script>
"""


def _home_navigation_script() -> str:
    return """
    <script>
        (() => {
            const state = { pendingAction: null };

            window.synthesixPage = {
                consumeAction() {
                    const action = state.pendingAction;
                    state.pendingAction = null;
                    return action;
                }
            };

            document.querySelectorAll("[data-home-link]").forEach((link) => {
                link.addEventListener("click", (event) => {
                    event.preventDefault();
                    state.pendingAction = { action: "focus_home" };
                });
            });
        })();
    </script>
"""


def load_search_history(limit: int = 25) -> List[dict]:
    path = "history/history.json"
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            history = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []

    searches = []
    seen_queries = set()
    for entry in reversed(history):
        query = str(entry.get("query", "")).strip()
        if not query or query in seen_queries:
            continue
        seen_queries.add(query)
        searches.append(
            {
                "query": query,
                "smart_query": str(entry.get("smart_query", "")).strip(),
                "date": str(entry.get("date", "")).strip(),
                "nb_results": entry.get("nb_results", ""),
            }
        )
        if len(searches) >= limit:
            break

    return searches

def add_to_history(query: str, smart_query: str, nb_results: int, link: str):
    """Add a search to the history
    
    Args:
        query (str): The query
        nb_results (int): The number of results
        link (str): The link to the search results
    """
    
    path = "history/history.json"
    date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    data = {
        "date": date_str,
        "query": query,
        "smart_query": smart_query,
        "nb_results": nb_results,
        "link": link
    }

    # Load the history
    if not os.path.exists(path):
        # Create the history directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Create an empty history file
        history = []
    else:
        # Load the existing history
        with open(path, "r", encoding="utf-8") as f:
            history = json.load(f)
    
    history.append(data)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)
        
        
def generate_history_html():
    """Generate an HTML report of the history
    
    Returns:
        str: The path to the generated HTML report
    """
    path = "history/history.json"
    output_path = "history.html"
    
    # Charger l'historique
    if not os.path.exists(path):
        history = []
    else:
        with open(path, "r", encoding="utf-8") as f:
            history = json.load(f)

    # Début du HTML
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
    {_theme_assets()}
</head>
<body>
    <main class="app app--wide">
        <header class="topbar">
            <div class="brand">
                <h1 class="brand-name">Synthesix</h1>
                <span class="brand-subtitle">Search history</span>
            </div>
            <div class="top-actions">
                <a href="index.html" data-home-link class="nav-link">Search</a>
                <button type="button" class="theme-toggle" data-theme-toggle aria-pressed="false">Dark mode</button>
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
    # Ajouter les lignes du tableau
    for entry in reversed(history):
        date = _html_escape(entry.get('date', ''))
        query = _html_escape(entry.get('query', ''))
        smart_query = _html_escape(entry.get('smart_query', ''))
        nb_results = _html_escape(entry.get('nb_results', ''))
        link = _html_escape(entry.get('link', '#'))
        html += f"""
            <tr>
                <td>{date}</td>
                <td>{query}</td>
                <td>{smart_query}</td>
                <td>{nb_results}</td>
                <td><a href="{link}" target="_blank" rel="noopener noreferrer">View results</a></td>
            </tr>
        """
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
    # Écrire le fichier HTML
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path

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
    except Exception as e:
        print("Error parsing JSON:", e)
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
    if any(op in lowered for op in ["site:", "inurl:", "intitle:", "\"", "("]):
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

    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = "history/search_results_" + date_str + ".html"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    safe_search_term = _html_escape(search_term)
    safe_output_path = _html_escape(output_path)

    html_head = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Results for: {safe_search_term}</title>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    {_theme_assets("../")}
</head>
<body>
    <main class="app app--wide">
        <header class="topbar">
            <div class="brand">
                <h1 class="brand-name">Synthesix</h1>
                <span class="brand-subtitle">Search results</span>
            </div>
            <div class="top-actions">
                <a href="../index.html" data-home-link class="nav-link">Search</a>
                <a href="../history.html" class="nav-link">History</a>
                <button type="button" class="theme-toggle" data-theme-toggle aria-pressed="false">Dark mode</button>
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
            <div class="table-shell">
                <table id="results" class="data-table display">
                    <thead>
                        <tr>
                            <th>Title</th>
                            <th>Description</th>
                            <th>Link</th>
                            <th>Source</th>
                            <th>Score</th>
                        </tr>
                    </thead>
                    <tbody>
"""

    if nb_results == 0:
        rows_html = """
        <tr>
            <td colspan="5" class="empty-row">
                No relevant results found
            </td>
        </tr>
        """
        html_footer = """
                    </tbody>
                </table>
            </div>
        </section>
    </main>
""" + _home_navigation_script() + """
</body>
</html>
"""
        full_html = html_head + rows_html + html_footer
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_html)
            
        output_path = os.path.abspath(output_path)
        return output_path
        
        
    rows_html = ""
    for _, row in df.iterrows():
        title = _html_escape(row["title"])
        desc = _html_escape(row["description"])
        link = _html_escape(row["link"])
        source = _html_escape(row["source"])
        score = f"{row['relevance_score']:.2f}"
        link_html = f'<a href="{link}" target="_blank" rel="noopener noreferrer">{link}</a>'
        rows_html += f"""
        <tr>
            <td>{title}</td>
            <td class="description">{desc}</td>
            <td class="link">{link_html}</td>
            <td>{source}</td>
            <td>{score}</td>
        </tr>
        """

    html_footer = """
                    </tbody>
                </table>
            </div>
        </section>
    </main>
    <script>
        $(document).ready(function() {
            $('#results').DataTable({
                pageLength: 50,
                lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
                order: [[4, 'desc']]
            });
        });
    </script>
""" + _home_navigation_script() + """
</body>
</html>
"""

    full_html = html_head + rows_html + html_footer

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    output_path = os.path.abspath(output_path)

    return output_path
