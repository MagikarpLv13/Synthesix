import unittest

from query_operators import (
    SearchFilters,
    build_display_query,
    build_engine_query,
    result_matches_filters,
)


class QueryOperatorsTestCase(unittest.TestCase):
    def test_build_display_query_uses_canonical_operators(self):
        filters = SearchFilters(
            site="example.com",
            exclude_site="pinterest.com",
            title="profile page",
            url="admin",
            body="email address",
            filetype="pdf",
        )

        query = build_display_query('"john doe"', filters)

        self.assertEqual(
            query,
            '"john doe" site:example.com -site:pinterest.com '
            'intitle:"profile page" inurl:admin inbody:"email address" filetype:pdf',
        )

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
            exclude_site="pinterest.com",
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
            result_matches_filters({**row, "link": "https://pinterest.com/admin/report.pdf"}, filters)
        )
        self.assertFalse(
            result_matches_filters({**row, "link": "https://sub.example.com/admin/report.html"}, filters)
        )


if __name__ == "__main__":
    unittest.main()
