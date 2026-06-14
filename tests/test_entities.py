import unittest

from analysis.entities import extract_entity_candidates


class EntityExtractionTestCase(unittest.TestCase):
    def test_extracts_deterministic_candidates_with_normalized_values(self):
        candidates = extract_entity_candidates(
            {
                "url": "https://Example.com/profile?id=42",
                "title": "Jane profile",
                "description": (
                    "Contact Jane.Doe@example.com or +33 6 12 34 56 78. "
                    "Server 192.0.2.4 and 2001:db8::1. "
                    "Profile @jane_doe. Identifier "
                    "123e4567-e89b-12d3-a456-426614174000. "
                    "Office coordinates: 48.8566, 2.3522."
                ),
                "notes": "",
            }
        )
        by_type = {
            candidate.entity_type: candidate
            for candidate in candidates
        }

        self.assertEqual(
            by_type["email"].normalized_value,
            "jane.doe@example.com",
        )
        self.assertEqual(by_type["phone"].normalized_value, "+33612345678")
        self.assertEqual(
            by_type["url"].normalized_value,
            "https://example.com/profile?id=42",
        )
        self.assertEqual(by_type["domain"].normalized_value, "example.com")
        self.assertEqual(by_type["ipv4"].normalized_value, "192.0.2.4")
        self.assertEqual(by_type["ipv6"].normalized_value, "2001:db8::1")
        self.assertEqual(by_type["handle"].normalized_value, "@jane_doe")
        self.assertEqual(
            by_type["identifier"].normalized_value,
            "123e4567-e89b-12d3-a456-426614174000",
        )
        self.assertEqual(
            by_type["coordinates"].normalized_value,
            "48.856600,2.352200",
        )
        self.assertIn("Contact Jane.Doe@example.com", by_type["email"].source_text)

    def test_deduplicates_candidates_across_source_fields(self):
        candidates = extract_entity_candidates(
            {
                "title": "Contact analyst@example.org",
                "description": "Email analyst@example.org for details.",
            }
        )

        emails = [
            candidate
            for candidate in candidates
            if candidate.entity_type == "email"
        ]
        self.assertEqual(len(emails), 1)

    def test_does_not_treat_integer_pairs_as_coordinates(self):
        candidates = extract_entity_candidates(
            {"description": "Reference 12, 34 in the paper."}
        )

        self.assertFalse(
            any(
                candidate.entity_type == "coordinates"
                for candidate in candidates
            )
        )


if __name__ == "__main__":
    unittest.main()
