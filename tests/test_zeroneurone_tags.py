import unittest

from exports.zeroneurone_tagsets import (
    ZERONEURONE_TAGSETS,
    ZERONEURONE_TAGSET_SUGGESTED_PROPERTIES,
    ZERONEURONE_TAGSET_VISUALS,
    canonical_zeroneurone_tag,
    canonical_zeroneurone_tags,
    zeroneurone_property_type,
    zeroneurone_tagset_suggested_properties,
    zeroneurone_tagset_visual,
)


class ZeroNeuroneTagSetTestCase(unittest.TestCase):
    def test_registry_matches_zeroneurone_2_41_9_defaults(self):
        self.assertEqual(
            ZERONEURONE_TAGSETS,
            (
                "Personne",
                "Entreprise",
                "Compte bancaire",
                "Véhicule",
                "Téléphone",
                "Email",
                "Site web",
                "Compte en ligne",
                "Wallet crypto",
                "Document d'identité",
                "Lieu",
                "Transaction",
                "Événement",
                "Dirigeant",
                "Militaire",
                "Fonctionnaire",
                "Élu",
                "Avocat",
                "PEP",
                "Sanctionné",
                "Suspect",
                "Témoin",
                "Victime",
                "Filiale",
                "Offshore",
                "Zone",
            ),
        )

    def test_canonicalizes_english_and_french_aliases(self):
        self.assertEqual(canonical_zeroneurone_tag("Person"), "Personne")
        self.assertEqual(canonical_zeroneurone_tag("personne"), "Personne")
        self.assertEqual(
            canonical_zeroneurone_tag("Organisation"),
            "Entreprise",
        )
        self.assertEqual(
            canonical_zeroneurone_tag("company"),
            "Entreprise",
        )
        self.assertEqual(
            canonical_zeroneurone_tag("witness"),
            "Témoin",
        )
        self.assertEqual(
            canonical_zeroneurone_tag("custom tag"),
            "custom tag",
        )

    def test_deduplicates_aliases_without_removing_custom_tags(self):
        self.assertEqual(
            canonical_zeroneurone_tags(
                ("Person", "personne", "Follow-up")
            ),
            ("Personne", "Follow-up"),
        )

    def test_uses_exact_builtin_visuals(self):
        self.assertEqual(
            set(ZERONEURONE_TAGSET_VISUALS),
            set(ZERONEURONE_TAGSETS),
        )
        self.assertEqual(
            zeroneurone_tagset_visual("Person"),
            {
                "color": "#3b82f6",
                "shape": "circle",
                "icon": "User",
            },
        )

    def test_exposes_default_properties_for_tagsets(self):
        self.assertEqual(
            set(ZERONEURONE_TAGSET_SUGGESTED_PROPERTIES),
            set(ZERONEURONE_TAGSETS),
        )
        self.assertEqual(
            zeroneurone_tagset_suggested_properties("Avocat"),
            (
                {"key": "Barreau", "type": "text"},
                {"key": "Spécialité", "type": "text"},
                {"key": "Cabinet", "type": "text"},
                {"key": "Date d'inscription", "type": "date"},
            ),
        )
        self.assertEqual(
            zeroneurone_tagset_visual("Entreprise"),
            {
                "color": "#8b5cf6",
                "shape": "square",
                "icon": "Building2",
            },
        )

    def test_property_type_lookup_uses_tagset_declared_type(self):
        # Declared tagset types win over heuristic inference.
        self.assertEqual(zeroneurone_property_type("Capital social"), "number")
        self.assertEqual(zeroneurone_property_type("Nationalité"), "country")
        self.assertEqual(zeroneurone_property_type("Date de création"), "date")
        self.assertEqual(zeroneurone_property_type("URL profil"), "link")
        # Case-insensitive, trims whitespace.
        self.assertEqual(zeroneurone_property_type("  siren  "), "text")
        # Unknown keys return an empty string (caller falls back).
        self.assertEqual(zeroneurone_property_type("Mystery field"), "")
        self.assertEqual(zeroneurone_property_type(""), "")


if __name__ == "__main__":
    unittest.main()
