import unittest

from exports.zeroneurone_tagsets import (
    ZERONEURONE_TAGSETS,
    ZERONEURONE_TAGSET_VISUALS,
    canonical_zeroneurone_tag,
    canonical_zeroneurone_tags,
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
        self.assertEqual(
            zeroneurone_tagset_visual("Entreprise"),
            {
                "color": "#8b5cf6",
                "shape": "square",
                "icon": "Building2",
            },
        )


if __name__ == "__main__":
    unittest.main()
