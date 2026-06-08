import unittest

from search_regions import build_engine_region_params, resolve_country


class SearchRegionsTestCase(unittest.TestCase):
    def test_resolves_sweden_names_codes_and_local_aliases(self):
        for value in ("Sweden", "SE", "Suede", "Su\u00e8de", "Sverige"):
            with self.subTest(value=value):
                region = resolve_country(value)
                self.assertIsNotNone(region)
                self.assertEqual(region.code, "SE")
                self.assertEqual(region.duckduckgo_region, "se-sv")

    def test_builds_engine_specific_country_params(self):
        self.assertEqual(
            build_engine_region_params("google", {"country": "Sweden"}),
            {"gl": "se"},
        )
        self.assertEqual(
            build_engine_region_params("bing", {"country": "Sweden"}),
            {"cc": "SE"},
        )
        self.assertEqual(
            build_engine_region_params("brave", {"country": "Sweden"}),
            {"country": "se"},
        )
        self.assertEqual(
            build_engine_region_params("duckduckgo", {"country": "Sweden"}),
            {"kl": "se-sv"},
        )

    def test_accepts_unknown_two_letter_country_code_for_iso_engines(self):
        self.assertEqual(
            build_engine_region_params("google", "AX"),
            {"gl": "ax"},
        )
        self.assertEqual(build_engine_region_params("duckduckgo", "AX"), {})

    def test_ignores_unknown_country_name(self):
        self.assertIsNone(resolve_country("not-a-country"))
        self.assertEqual(build_engine_region_params("google", "not-a-country"), {})


if __name__ == "__main__":
    unittest.main()
