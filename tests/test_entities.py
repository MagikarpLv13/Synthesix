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

    def test_does_not_treat_year_ranges_or_bare_runs_as_phones(self):
        candidates = extract_entity_candidates(
            {
                "description": (
                    "Actif de 2008-2010 puis 2012 à 2015. "
                    "Référence 20082010 dans le dossier. "
                    "Joignable au 01 23 45 67 89."
                )
            }
        )
        phones = [
            candidate.normalized_value
            for candidate in candidates
            if candidate.entity_type == "phone"
        ]
        # Only the real (leading-zero) number survives.
        self.assertEqual(phones, ["0123456789"])

    def test_ignores_file_extensions_as_domains(self):
        candidates = extract_entity_candidates(
            {
                "description": (
                    "Voir rapport.pdf et logo.png. "
                    "Site officiel : example.com."
                )
            }
        )
        domains = {
            candidate.normalized_value
            for candidate in candidates
            if candidate.entity_type == "domain"
        }
        self.assertIn("example.com", domains)
        self.assertNotIn("rapport.pdf", domains)
        self.assertNotIn("logo.png", domains)

    def test_extracts_valid_french_business_identifiers(self):
        candidates = extract_entity_candidates(
            {
                "description": (
                    "SIREN 732 829 320. SIRET 732 829 320 00074. "
                    "Numéro de TVA : FR44 732829320."
                )
            }
        )
        by_type = {
            candidate.entity_type: candidate
            for candidate in candidates
        }

        self.assertEqual(by_type["siren"].normalized_value, "732829320")
        self.assertEqual(
            by_type["siret"].normalized_value,
            "73282932000074",
        )
        self.assertEqual(
            by_type["vat_number"].normalized_value,
            "FR44732829320",
        )
        self.assertTrue(by_type["siret"].attributes["checksum_valid"])
        self.assertEqual(
            by_type["vat_number"].attributes["siren"],
            "732829320",
        )
        self.assertFalse(
            any(candidate.entity_type == "phone" for candidate in candidates)
        )

    def test_rejects_invalid_french_business_identifiers(self):
        candidates = extract_entity_candidates(
            {
                "description": (
                    "SIREN 732 829 321. SIRET 732 829 320 00075. "
                    "TVA FR45 732829320."
                )
            }
        )

        self.assertFalse(
            any(
                candidate.entity_type in {"siren", "siret", "vat_number"}
                for candidate in candidates
            )
        )

    def test_extracts_dates_and_preserves_ambiguity(self):
        candidates = extract_entity_candidates(
            {
                "description": (
                    "Created on 2025-06-14, reviewed on 14 juin 2025, "
                    "and filed on 04/05/2025."
                )
            }
        )
        dates = [
            candidate
            for candidate in candidates
            if candidate.entity_type == "date"
        ]
        normalized = {candidate.normalized_value for candidate in dates}

        self.assertIn("2025-06-14", normalized)
        ambiguous = next(
            candidate
            for candidate in dates
            if candidate.normalized_value.startswith("ambiguous:")
        )
        self.assertTrue(ambiguous.attributes["ambiguous"])
        self.assertEqual(len(ambiguous.attributes["interpretations"]), 2)

    def test_extracts_structured_french_postal_address(self):
        candidates = extract_entity_candidates(
            {
                "description": (
                    "Siège social : 10 rue de la Paix, 75002 Paris."
                )
            }
        )
        address = next(
            candidate
            for candidate in candidates
            if candidate.entity_type == "address"
        )

        self.assertEqual(address.attributes["postal_code"], "75002")
        self.assertEqual(address.attributes["locality"], "Paris")
        self.assertEqual(address.attributes["country"], "FR")

    def test_infers_property_label_from_nearby_field_name(self):
        candidates = extract_entity_candidates(
            {
                "description": (
                    "Date de création : 2025-06-14. "
                    "Siège social : 10 rue de la Paix, 75002 Paris."
                )
            }
        )
        date_candidate = next(
            candidate
            for candidate in candidates
            if candidate.entity_type == "date"
        )
        address = next(
            candidate
            for candidate in candidates
            if candidate.entity_type == "address"
        )

        self.assertEqual(
            date_candidate.attributes["property_key"],
            "Date de création",
        )
        self.assertEqual(address.attributes["property_key"], "Siège social")

    def test_infers_canonical_date_property_labels(self):
        candidates = extract_entity_candidates(
            {
                "description": (
                    "Radiée depuis le 21/01/2008. "
                    "arié (donnée 2008) Création : 01/10/2008."
                )
            }
        )
        dates = [
            candidate
            for candidate in candidates
            if candidate.entity_type == "date"
        ]
        by_value = {
            candidate.value: candidate
            for candidate in dates
        }

        self.assertEqual(
            by_value["21/01/2008"].attributes["property_key"],
            "Radiation",
        )
        self.assertEqual(
            by_value["01/10/2008"].attributes["property_key"],
            "Création",
        )


if __name__ == "__main__":
    unittest.main()
