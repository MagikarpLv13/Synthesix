import unittest

from query_variants import normalize_query_variants, suggest_query_variants


class QueryVariantsTestCase(unittest.TestCase):
    def test_suggestions_are_bounded_and_keep_exact_queries_visible(self):
        suggestions = suggest_query_variants("Élodie Durand", limit=3)

        self.assertEqual(len(suggestions), 3)
        self.assertEqual(suggestions[0]["query"], "Elodie Durand")
        self.assertEqual(suggestions[1]["query"], "Durand Élodie")
        self.assertTrue(all("query" in item and "label" in item for item in suggestions))

    def test_advanced_queries_are_not_modified_automatically(self):
        self.assertEqual(
            suggest_query_variants('site:example.com "anna lindberg"', limit=5),
            (),
        )

    def test_selected_variants_are_validated_deduplicated_and_limited(self):
        variants = normalize_query_variants(
            "anna lindberg",
            [
                "lindberg anna",
                "anna lindberg",
                "",
                42,
                "a lindberg",
                "anna-lindberg",
            ],
            limit=3,
        )

        self.assertEqual(
            variants,
            ("anna lindberg", "lindberg anna", "a lindberg"),
        )


if __name__ == "__main__":
    unittest.main()
