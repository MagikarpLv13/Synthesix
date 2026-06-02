import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from utils import add_to_history, generate_history_html, generate_html_report, is_advanced_query, smart_parse


class UtilsTestCase(unittest.TestCase):
    def test_is_advanced_query_detects_boolean_operators(self):
        self.assertTrue(is_advanced_query("python AND asyncio"))
        self.assertTrue(is_advanced_query("site:example.com python"))
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
                        }
                    ]
                )

                output_path = generate_html_report(df, '<query "&>', 0.123, 1)
                content = Path(output_path).read_text(encoding="utf-8")

                self.assertIn("history", output_path)
                self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", content)
                self.assertIn("&lt;query &quot;&amp;&gt;", content)
                self.assertIn("rel=\"noopener noreferrer\"", content)
                self.assertNotIn("<script>alert(1)</script>", content)
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
            finally:
                os.chdir(current_dir)


if __name__ == "__main__":
    unittest.main()
