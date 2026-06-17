import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from evidence.changes import compare_page_text
from investigations.monitoring_view import generate_page_comparison_report


class PageMonitoringViewTestCase(unittest.TestCase):
    def test_generates_page_comparison_report(self):
        change = compare_page_text(
            "Original company address.",
            "Updated company address.",
        )
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            output_path = (
                base_dir
                / "data"
                / "evidence"
                / "case-1"
                / "comparison.html"
            )
            generated = generate_page_comparison_report(
                output_path=output_path,
                page_title="Company profile",
                page_url="https://example.com/profile",
                previous_captured_at="2026-06-09T10:00:00+00:00",
                current_captured_at="2026-06-10T10:00:00+00:00",
                previous_text="Original company address.",
                current_text="Updated company address.",
                change=change,
                base_dir=base_dir,
            )
            content = output_path.read_text(encoding="utf-8")

        self.assertEqual(generated, str(output_path))
        self.assertIn("Significant content change", content)
        self.assertIn("Company profile", content)
        self.assertIn("Original company address.", content)
        self.assertIn("Updated company address.", content)
        self.assertIn('href="../../../theme.css"', content)
        self.assertIn('src="../../../theme.js"', content)
        self.assertIn('src="../../../i18n.js"', content)
        self.assertIn('src="../../../assets/synthesix-mark.svg"', content)
        self.assertIn("comparison-diff", content)
        self.assertIn("status-badge--discarded", content)
        self.assertNotIn("<style>", content)
