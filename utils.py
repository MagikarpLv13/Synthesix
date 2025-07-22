import re
import json
from html import unescape
import pandas as pd
from datetime import datetime
import os

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
        with open(path, "r") as f:
            history = json.load(f)
    
    history.append(data)
    with open(path, "w") as f:
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
    html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>History</title>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #fafafa; color: #333; }
        h1 { text-align: center; margin-bottom: 30px; font-weight: normal; }
        table { width: 100%; border-collapse: collapse; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05); background-color: #fff; border-radius: 8px; overflow: hidden; }
        thead { background-color: #f0f0f0; }
        th, td { text-align: left; padding: 12px 16px; }
        th { font-weight: 600; font-size: 14px; color: #444; border-bottom: 1px solid #ddd; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>History</h1>
    <table id="historyTable">
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
        html += f"""
            <tr>
                <td>{entry.get('date', '')}</td>
                <td>{entry.get('query', '')}</td>
                <td>{entry.get('smart_query', '')}</td>
                <td>{entry.get('nb_results', '')}</td>
                <td><a href=\"{entry.get('link', '#')}\" target=\"_blank\">View results</a></td>
            </tr>
        """
    html += '''
        </tbody>
    </table>
    <script>
        $(document).ready(function() {
            $('#historyTable').DataTable({
                order: [[0, 'desc']],
                pageLength: 50,
                lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]]
            });
        });
    </script>
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
    return any(
        op in query.lower()
        for op in ["site:", "inurl:", "intitle:", "AND", "OR", "NOT", "\"", "("]
    )


def generate_html_report(df: pd.DataFrame, search_term: str, total_time: float, nb_results: int) -> str | None:
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

    html_head = (
        """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Search Results for: """
        + search_term
        + """</title>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #fafafa;
            color: #333;
        }

        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-weight: normal;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            background-color: #fff;
            border-radius: 8px;
            overflow: hidden;
        }

        thead {
            background-color: #f0f0f0;
        }

        th, td {
            text-align: left;
            padding: 12px 16px;
        }

        th {
            font-weight: 600;
            font-size: 14px;
            color: #444;
            border-bottom: 1px solid #ddd;
        }

        tr:nth-child(even) {
            background-color: #f9f9f9;
        }

        tr:hover {
            background-color: #f1f1f1;
        }

        td.description {
            max-width: 500px;
            white-space: normal;
        }

        a {
            color: #0066cc;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>Search Results for: """
        + search_term
        + """</h1>
    <p>Total time: """
        + f"{total_time:.3f}"
        + """ seconds</p>
    <p>HTML report created: """
        + output_path
        + """</p>
    <p>Search date: """
        + date_str
        + """</p>
    <p>Number of results: """
        + str(nb_results)
        + """</p>
    <table id="results" class="display">
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
    )

    if nb_results == 0:
        rows_html = """
        <tr>
            <td colspan="5" style="text-align: center; font-size: 1.5em; padding: 20px;">
                No relevant results found
            </td>
        </tr>
        """
        html_footer = """
        </tbody>
    </table>
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
        title = row["title"]
        desc = row["description"]
        link = row["link"]
        source = row["source"]
        score = f"{row['relevance_score']:.2f}"
        link_html = f'<a href="{link}" target="_blank">{link}</a>'
        rows_html += f"""
        <tr>
            <td>{title}</td>
            <td class="description">{desc}</td>
            <td>{link_html}</td>
            <td>{source}</td>
            <td>{score}</td>
        </tr>
        """

    html_footer = """
        </tbody>
    </table>
    <script>
        $(document).ready(function() {
            $('#results').DataTable({
                pageLength: 50,
                lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
                order: [[4, 'desc']]
            });
        });
    </script>
</body>
</html>
"""

    full_html = html_head + rows_html + html_footer

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    output_path = os.path.abspath(output_path)

    return output_path
