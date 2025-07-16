import re
import json
from html import unescape
import pandas as pd
from datetime import datetime
import os

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
    all_or = " OR ".join(f'"{t}"' for t in terms)
    return f"({all_and}) OR {all_or}"


def is_advanced_query(query: str) -> bool:
    return any(
        op in query.lower()
        for op in ["site:", "inurl:", "intitle:", "AND", "OR", "NOT", "\"", "("]
    )


def generate_html_report(df: pd.DataFrame) -> str | None:
    if len(df) == 0:
        return None
    
    html_head = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Search Results</title>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
        }
        h1 {
            text-align: center;
        }
        td.description {
            max-width: 500px;
            white-space: normal;
        }
    </style>
</head>
<body>
    <h1>Search Results</h1>
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
                pageLength: 25
            });
        });
    </script>
</body>
</html>
"""

    full_html = html_head + rows_html + html_footer
    
    output_path = "search_results_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".html"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)
        
    output_path = os.path.abspath(output_path)
        
    return output_path
