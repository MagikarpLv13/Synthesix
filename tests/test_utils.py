import os
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pandas as pd

from utils import (
    add_to_history,
    clear_synthesix_history,
    generate_history_html,
    generate_html_report,
    is_advanced_query,
    load_search_history,
    smart_parse,
)


class UtilsTestCase(unittest.TestCase):
    def test_clear_synthesix_history_removes_search_files_only(self):
        current_dir = os.getcwd()
        with TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            try:
                add_to_history("query", '"query"', 1, "result.html")
                generate_history_html()
                results_path = Path("history") / "search_results_20260609_120000.html"
                results_path.write_text("results", encoding="utf-8")
                challenge_path = Path("history") / "robot_challenges" / "challenge.html"
                challenge_path.parent.mkdir(parents=True)
                challenge_path.write_text("challenge", encoding="utf-8")

                removed = clear_synthesix_history()

                self.assertEqual(removed, 3)
                self.assertFalse((Path("history") / "history.json").exists())
                self.assertFalse(results_path.exists())
                self.assertTrue((Path("history") / "history.html").exists())
                self.assertTrue(challenge_path.exists())
                self.assertEqual(load_search_history(limit=10), [])
            finally:
                os.chdir(current_dir)

    def test_is_advanced_query_detects_boolean_operators(self):
        self.assertTrue(is_advanced_query("python AND asyncio"))
        self.assertTrue(is_advanced_query("site:example.com python"))
        self.assertTrue(is_advanced_query("filetype:pdf python"))
        self.assertTrue(is_advanced_query("intext:email python"))
        self.assertTrue(is_advanced_query("pesto after:2024-01-01"))
        self.assertTrue(is_advanced_query("sandwich au jambon -fromage"))
        self.assertFalse(is_advanced_query("starvos and lynch"))
        self.assertFalse(is_advanced_query("python or cdp"))
        self.assertFalse(is_advanced_query("python asyncio tutorial"))

    def test_smart_parse_quotes_comma_separated_terms(self):
        self.assertEqual(smart_parse("python, asyncio"), '("python" AND "asyncio")')
        self.assertEqual(smart_parse("starvos and lynch"), '"starvos and lynch"')

    def test_generate_html_report_escapes_untrusted_content(self):
        current_dir = os.getcwd()
        with TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            try:
                df = pd.DataFrame(
                    [
                        {
                            "title": "<script>alert(1)</script>",
                            "description": 'A&B "desc"',
                            "link": 'https://example.com/?q=<x>&a="b"',
                            "source": "Google",
                            "relevance_score": 5.0,
                            "score_breakdown": [
                                {
                                    "key": "exact_title",
                                    "label": "<Exact title>",
                                    "score": 4.5,
                                }
                            ],
                        }
                    ]
                )

                output_path = generate_html_report(df, '<query "&>', 0.123, 1)
                content = Path(output_path).read_text(encoding="utf-8")

                self.assertIn("history", output_path)
                self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", content)
                self.assertIn("&lt;query &quot;&amp;&gt;", content)
                self.assertIn("rel=\"noopener noreferrer\"", content)
                self.assertIn("../theme.css", content)
                self.assertIn("../theme.js", content)
                self.assertIn("../i18n.js", content)
                self.assertIn("../assets/favicon.svg", content)
                self.assertIn("../assets/synthesix-mark.svg", content)
                self.assertIn('class="brand-logo"', content)
                self.assertNotIn("data-theme-toggle", content)
                self.assertIn('class="result-card', content)
                self.assertIn("data-triage-item", content)
                self.assertIn('class="insight-grid"', content)
                self.assertNotIn("datatables", content.lower())
                self.assertNotIn("jquery", content.lower())
                self.assertIn("data-home-link", content)
                self.assertIn("window.synthesixPage", content)
                self.assertIn("&lt;Exact title&gt;", content)
                self.assertIn("not factual accuracy", content)
                self.assertNotIn("<script>alert(1)</script>", content)
            finally:
                os.chdir(current_dir)

    def test_generate_html_report_sorts_scores_numerically_descending(self):
        current_dir = os.getcwd()
        with TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            try:
                df = pd.DataFrame(
                    [
                        {
                            "title": "Low",
                            "description": "Low score",
                            "link": "https://example.com/low",
                            "source": "Google",
                            "relevance_score": 2.0,
                            "score_breakdown": [],
                            "query_variants": ['"query"'],
                        },
                        {
                            "title": "High",
                            "description": "High score",
                            "link": "https://example.com/high",
                            "source": "Bing",
                            "relevance_score": 10.0,
                            "score_breakdown": [],
                            "query_variants": ['"query"'],
                        },
                    ]
                )

                output_path = generate_html_report(df, '"query"', 0.1, 2)
                content = Path(output_path).read_text(encoding="utf-8")

                self.assertLess(content.index(">High</a>"), content.index(">Low</a>"))
                self.assertIn(">10.00</span>", content)
                self.assertIn('class="result-list"', content)
                self.assertIn("navigate results", content)
            finally:
                os.chdir(current_dir)

    def test_coverage_errors_expose_targeted_retry_action(self):
        current_dir = os.getcwd()
        with TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            try:
                df = pd.DataFrame(
                    columns=[
                        "title",
                        "description",
                        "link",
                        "source",
                        "relevance_score",
                        "score_breakdown",
                        "query_variants",
                    ]
                )
                df.attrs["query_coverage"] = (
                    {
                        "query": '"anna lindberg"',
                        "engines": {
                            "google": {"status": "ok", "count": 2},
                            "bing": {"status": "timeout", "count": 0},
                        },
                    },
                    {
                        "query": '"lindberg anna"',
                        "engines": {
                            "google": {"status": "challenge", "count": 0},
                            "bing": {"status": "ok", "count": 1},
                        },
                    },
                )
                df.attrs["search_context"] = {
                    "original_query": "anna lindberg",
                    "filters": {"site": "example.com"},
                    "num_results": 7,
                    "investigation_id": "case-1",
                }

                output_path = generate_html_report(
                    df,
                    '"anna lindberg" site:example.com',
                    0.1,
                    0,
                )
                content = Path(output_path).read_text(encoding="utf-8")

                self.assertEqual(
                    content.count('data-page-action="retry_search_combination"'),
                    2,
                )
                self.assertIn("&quot;engine&quot;:&quot;bing&quot;", content)
                self.assertIn(
                    "&quot;query&quot;:&quot;\\&quot;anna lindberg"
                    "\\&quot;&quot;",
                    content,
                )
                self.assertIn("&quot;investigationId&quot;:&quot;case-1&quot;", content)
                self.assertIn("data-page-status", content)
                self.assertIn("This report action is invalid.", content)
            finally:
                os.chdir(current_dir)

    def test_history_html_escapes_entries(self):
        current_dir = os.getcwd()
        with TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            try:
                add_to_history("<query>", 'site:"example"', 1, 'file://C:/tmp/"result".html')
                output_path = generate_history_html()
                content = Path(output_path).read_text(encoding="utf-8")

                self.assertIn("&lt;query&gt;", content)
                self.assertIn("site:&quot;example&quot;", content)
                self.assertIn("file://C:/tmp/&quot;result&quot;.html", content)
                self.assertIn("theme.css", content)
                self.assertIn("theme.js", content)
                self.assertIn("i18n.js", content)
                self.assertIn("../assets/favicon.svg", content)
                self.assertIn("../assets/synthesix-mark.svg", content)
                self.assertNotIn("data-theme-toggle", content)
                self.assertIn('class="data-table display"', content)
                self.assertIn("data-home-link", content)
                self.assertIn("window.synthesixPage", content)
            finally:
                os.chdir(current_dir)

    def test_generate_history_html_creates_output_directory_without_history_file(self):
        current_dir = os.getcwd()
        with TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            try:
                output_path = generate_history_html()
                content = Path(output_path).read_text(encoding="utf-8")

                self.assertIn("0 saved searches", content)
            finally:
                os.chdir(current_dir)

    def test_load_search_history_returns_recent_unique_queries(self):
        current_dir = os.getcwd()
        with TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            try:
                add_to_history("first query", '"first query"', 3, "first.html")
                add_to_history("second query", '"second query"', 4, "second.html")
                add_to_history("first query", '"first query"', 5, "first-latest.html")

                history = load_search_history(limit=10)

                self.assertEqual([entry["query"] for entry in history], ["first query", "second query"])
                self.assertEqual(history[0]["nb_results"], 5)
            finally:
                os.chdir(current_dir)

    def test_load_search_history_preserves_filters(self):
        current_dir = os.getcwd()
        with TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            try:
                add_to_history(
                    "john doe",
                    '"john doe" site:example.com inurl:admin',
                    2,
                    "result.html",
                    {"site": "example.com", "url": "admin"},
                )

                history = load_search_history(limit=10)

                self.assertEqual(history[0]["query"], "john doe")
                self.assertEqual(history[0]["display_query"], "john doe")
                self.assertEqual(history[0]["filters"], {"site": "example.com", "url": "admin"})
            finally:
                os.chdir(current_dir)

    def test_load_search_history_preserves_investigation_id(self):
        current_dir = os.getcwd()
        with TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            try:
                add_to_history(
                    "company",
                    '"company"',
                    2,
                    "result.html",
                    investigation_id="case-123",
                )

                history = load_search_history(limit=10)

                self.assertEqual(history[0]["investigation_id"], "case-123")
            finally:
                os.chdir(current_dir)

    def test_load_search_history_keeps_same_query_with_different_filters(self):
        current_dir = os.getcwd()
        with TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            try:
                add_to_history("john doe", '"john doe" site:example.com', 1, "one.html", {"site": "example.com"})
                add_to_history("john doe", '"john doe" site:example.org', 1, "two.html", {"site": "example.org"})

                history = load_search_history(limit=10)

                self.assertEqual(len(history), 2)
                self.assertEqual([entry["filters"]["site"] for entry in history], ["example.org", "example.com"])
            finally:
                os.chdir(current_dir)

    def test_load_search_history_honors_limit(self):
        current_dir = os.getcwd()
        with TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            try:
                add_to_history("one", '"one"', 1, "one.html")
                add_to_history("two", '"two"', 2, "two.html")

                history = load_search_history(limit=1)

                self.assertEqual(len(history), 1)
                self.assertEqual(history[0]["query"], "two")
            finally:
                os.chdir(current_dir)

    def test_history_is_sorted_chronologically_with_legacy_dates(self):
        current_dir = os.getcwd()
        with TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            try:
                history_path = Path("history") / "history.json"
                history_path.parent.mkdir(parents=True, exist_ok=True)
                history_path.write_text(
                    json.dumps(
                        [
                            {
                                "date": "02/01/2026 10:00",
                                "query": "january query",
                                "smart_query": '"january query"',
                                "nb_results": 1,
                                "link": "january.html",
                            },
                            {
                                "date": "15/12/2025 10:00",
                                "query": "december query",
                                "smart_query": '"december query"',
                                "nb_results": 1,
                                "link": "december.html",
                            },
                            {
                                "date": "01/02/2026 09:00",
                                "query": "february query",
                                "smart_query": '"february query"',
                                "nb_results": 1,
                                "link": "february.html",
                            },
                        ]
                    ),
                    encoding="utf-8",
                )

                history = load_search_history(limit=10)
                output_path = generate_history_html()
                content = Path(output_path).read_text(encoding="utf-8")

                self.assertEqual(
                    [entry["query"] for entry in history],
                    ["february query", "january query", "december query"],
                )
                self.assertLess(content.index("february query"), content.index("january query"))
                self.assertIn('data-order="', content)
            finally:
                os.chdir(current_dir)

    def test_corrupted_history_file_is_ignored(self):
        current_dir = os.getcwd()
        with TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            try:
                history_path = Path("history") / "history.json"
                history_path.parent.mkdir(parents=True, exist_ok=True)
                history_path.write_text("{not-json", encoding="utf-8")

                self.assertEqual(load_search_history(limit=10), [])
                add_to_history("fresh query", '"fresh query"', 2, "fresh.html")

                history = load_search_history(limit=10)
                self.assertEqual([entry["query"] for entry in history], ["fresh query"])
            finally:
                os.chdir(current_dir)

    def test_report_links_follow_configured_history_directory(self):
        current_dir = os.getcwd()
        with TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            try:
                with patch.dict("os.environ", {"SYNTHESIX_HISTORY_DIR": "runtime/history"}):
                    df = pd.DataFrame(
                        [
                            {
                                "title": "Title",
                                "description": "Description",
                                "link": "https://example.com",
                                "source": "Google",
                                "relevance_score": 1.0,
                            }
                        ]
                    )

                    output_path = generate_html_report(df, '"configured"', 0.1, 1)
                    content = Path(output_path).read_text(encoding="utf-8")

                self.assertIn("../../theme.css", content)
                self.assertIn("../../theme.js", content)
                self.assertIn("../../i18n.js", content)
                self.assertIn("../../assets/favicon.svg", content)
                self.assertIn("../../assets/synthesix-mark.svg", content)
                self.assertIn('href="../../index.html"', content)
                self.assertIn('href="history.html"', content)
            finally:
                os.chdir(current_dir)


if __name__ == "__main__":
    unittest.main()
