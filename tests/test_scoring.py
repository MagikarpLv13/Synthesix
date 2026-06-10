import unittest

from scoring import (
    DEFAULT_SCORING_WEIGHTS,
    ScoreBreakdown,
    ScoreComponent,
    add_context_to_breakdown,
    build_relevance_explainer,
    build_relevance_scorer,
    calculate_relevance,
    extract_scoring_terms,
)


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

    def test_prebuilt_scorer_matches_calculate_relevance(self):
        row = {
            "title": "Starvos and Lych archive",
            "description": "Reference page",
            "link": "https://example.com/starvos-and-lych",
        }

        scorer = build_relevance_scorer('"starvos and lych"')

        self.assertEqual(scorer(row), calculate_relevance(row, '"starvos and lych"'))

    def test_breakdown_explains_each_scoring_component(self):
        row = {
            "title": "Starvos and Lych archive",
            "description": "Starvos and Lych reference",
            "link": "https://example.com/starvos-and-lych",
        }

        breakdown = build_relevance_explainer('"starvos and lych"')(row)

        self.assertEqual(
            [component.key for component in breakdown.components],
            ["exact_title", "exact_description", "url_match"],
        )
        self.assertEqual(breakdown.total, calculate_relevance(row, '"starvos and lych"'))
        self.assertEqual(
            breakdown.components[0].score,
            DEFAULT_SCORING_WEIGHTS.exact_title,
        )

    def test_consensus_bonus_is_capped_and_does_not_create_relevance(self):
        empty_breakdown = ScoreBreakdown(())
        relevant_breakdown = ScoreBreakdown((
            ScoreComponent("exact_title", "Exact query term in title", 4.5),
        ))

        empty_with_consensus = add_context_to_breakdown(
            empty_breakdown,
            engine_count=4,
            filters_matched=False,
        )
        relevant_with_consensus = add_context_to_breakdown(
            relevant_breakdown,
            engine_count=4,
            filters_matched=False,
        )

        self.assertEqual(empty_with_consensus.total, 0)
        self.assertEqual(relevant_with_consensus.total, 6.5)
        self.assertEqual(
            relevant_with_consensus.components[-1].key,
            "engine_consensus",
        )


if __name__ == "__main__":
    unittest.main()
