import unittest
from datetime import date

from query_operators import (
    SearchFilters,
    build_display_query,
    build_engine_date_params,
    build_engine_query,
    result_matches_filters,
)


class QueryOperatorsTestCase(unittest.TestCase):
    def test_exclude_filter_adds_negative_search_term(self):
        filters = SearchFilters(exclude="fromage")

        self.assertEqual(
            build_display_query('"Sandwich au jambon"', filters),
            '"Sandwich au jambon" -fromage',
        )
        for engine in ("google", "bing", "brave", "duckduckgo"):
            with self.subTest(engine=engine):
                self.assertEqual(
                    build_engine_query('"Sandwich au jambon"', engine, filters),
                    '"Sandwich au jambon" -fromage',
                )

    def test_build_display_query_uses_canonical_operators(self):
        filters = SearchFilters(
            site="example.com",
            exclude="directory, archived page",
            title="profile page",
            url="admin",
            body="email address",
            filetype="pdf",
            after="2024-01-01",
            before="2024-12-31",
        )

        query = build_display_query('"john doe"', filters)

        self.assertEqual(
            query,
            '"john doe" site:example.com -directory -"archived page" '
            'intitle:"profile page" inurl:admin inbody:"email address" filetype:pdf '
            'after:2024-01-01 before:2024-12-31',
        )

    def test_build_engine_date_params_uses_engine_specific_formats(self):
        filters = SearchFilters(after="2024-01-02", before="2024-03-04")

        self.assertEqual(
            build_engine_date_params("google", filters),
            {"tbs": "cdr:1,cd_min:01/02/2024,cd_max:03/04/2024"},
        )
        self.assertEqual(
            build_engine_date_params("brave", filters),
            {"tf": "2024-01-02to2024-03-04"},
        )
        self.assertEqual(
            build_engine_date_params("duckduckgo", filters),
            {"df": "2024-01-02..2024-03-04"},
        )
        self.assertEqual(build_engine_date_params("bing", filters), {})

    def test_build_engine_date_params_completes_open_ranges(self):
        today = date(2026, 6, 8)

        self.assertEqual(
            build_engine_date_params(
                "brave",
                SearchFilters(after="2024-01-02"),
                today=today,
            ),
            {"tf": "2024-01-02to2026-06-08"},
        )
        self.assertEqual(
            build_engine_date_params(
                "duckduckgo",
                SearchFilters(before="2024-03-04"),
                today=today,
            ),
            {"df": "1970-01-01..2024-03-04"},
        )

    def test_invalid_date_range_is_not_applied(self):
        filters = SearchFilters(after="2025-01-01", before="2024-01-01")

        self.assertEqual(build_engine_date_params("google", filters), {})
        self.assertNotIn("after:", build_display_query('"john doe"', filters))

    def test_build_engine_query_uses_supported_url_operator(self):
        filters = SearchFilters(site="example.com", title="profile", url="admin", filetype="pdf")

        self.assertEqual(
            build_engine_query('"john doe"', "google", filters),
            '"john doe" site:example.com intitle:profile inurl:admin filetype:pdf',
        )
        self.assertEqual(
            build_engine_query('"john doe"', "duckduckgo", filters),
            '"john doe" site:example.com intitle:profile inurl:admin filetype:pdf',
        )

    def test_build_engine_query_falls_back_for_unsupported_url_operator(self):
        filters = SearchFilters(site="example.com", title="profile", url="admin")

        self.assertEqual(
            build_engine_query('"john doe"', "bing", filters),
            '"john doe" site:example.com intitle:profile admin',
        )
        self.assertEqual(
            build_engine_query('"john doe"', "brave", filters),
            '"john doe" site:example.com intitle:profile admin',
        )

    def test_result_matches_verifiable_filters(self):
        filters = SearchFilters(
            site="example.com",
            exclude="archived",
            title="profile",
            url="admin",
            filetype="pdf",
        )
        row = {
            "title": "John Doe profile",
            "link": "https://sub.example.com/admin/report.pdf",
            "description": "Reference",
        }

        self.assertTrue(result_matches_filters(row, filters))
        self.assertFalse(result_matches_filters({**row, "title": "John Doe"}, filters))
        self.assertFalse(
            result_matches_filters({**row, "description": "Archived reference"}, filters)
        )
        self.assertFalse(
            result_matches_filters({**row, "link": "https://sub.example.com/admin/report.html"}, filters)
        )


if __name__ == "__main__":
    unittest.main()
