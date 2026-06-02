import unittest

from scoring import calculate_relevance, extract_scoring_terms


class ScoringTestCase(unittest.TestCase):
    def test_quoted_phrase_is_scored_as_exact_phrase(self):
        row = {
            "title": "Gravelord Lych | Bloons Wiki | Fandom",
            "description": (
                "Lych is a large MOAB-class bloon with a diamond-shaped hull "
                "similar to ZOMG."
            ),
            "link": "https://bloons.fandom.com/wiki/Gravelord_Lych",
        }

        self.assertEqual(calculate_relevance(row, '"starvos and lych"'), 0)

    def test_quoted_phrase_scores_when_exact_phrase_is_present(self):
        row = {
            "title": "Starvos and Lych archive",
            "description": "Reference page",
            "link": "https://example.com/starvos-and-lych",
        }

        self.assertGreater(calculate_relevance(row, '"starvos and lych"'), 0)

    def test_boolean_query_extracts_quoted_terms_individually(self):
        self.assertEqual(
            extract_scoring_terms('("python" AND "asyncio")'),
            ["python", "asyncio"],
        )

    def test_unquoted_lowercase_and_is_not_split(self):
        self.assertEqual(extract_scoring_terms("starvos and lych"), ["starvos and lych"])


if __name__ == "__main__":
    unittest.main()
