import unittest
from pathlib import Path

from lxml import etree, html


class HomeUiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        index_path = Path(__file__).resolve().parents[1] / "index.html"
        cls.content = index_path.read_text(encoding="utf-8")
        cls.tree = html.fromstring(cls.content)

    def test_country_filter_is_searchable_and_wired_to_payload(self):
        country_inputs = self.tree.xpath("//input[@id='filter-country']")
        self.assertEqual(len(country_inputs), 1)
        self.assertEqual(country_inputs[0].get("list"), "country-options")

        sweden_options = self.tree.xpath(
            "//datalist[@id='country-options']/option[@value='Sweden']"
        )
        self.assertEqual(len(sweden_options), 1)
        self.assertIn('country: "filter-country"', self.content)

    def test_filters_can_be_cleared_without_resetting_search_controls(self):
        buttons = self.tree.xpath("//button[@id='clear-search-filters']")

        self.assertEqual(len(buttons), 1)
        self.assertIn('clearSearchFiltersButton.addEventListener("click"', self.content)
        self.assertIn("setFilters({});", self.content)

    def test_automatic_dorks_are_enabled_by_default_and_wired_to_payload(self):
        inputs = self.tree.xpath("//input[@id='automatic-dorks']")

        self.assertEqual(len(inputs), 1)
        self.assertEqual(inputs[0].get("type"), "checkbox")
        self.assertEqual(inputs[0].get("checked"), "checked")
        self.assertIn(
            "automaticDorks: automaticDorksInput.checked",
            self.content,
        )

    def test_query_variants_require_explicit_selection(self):
        panels = self.tree.xpath("//details[@id='query-variants-panel']")
        suggestions = self.tree.xpath("//button[@id='suggest-query-variants']")
        manual_inputs = self.tree.xpath("//input[@id='manual-query-variant']")

        self.assertEqual(len(panels), 1)
        self.assertEqual(len(suggestions), 1)
        self.assertEqual(len(manual_inputs), 1)
        self.assertIn('queueAction("suggest_query_variants"', self.content)
        self.assertIn("queryVariants: selectedQueryVariants()", self.content)
        self.assertIn("checkbox.checked = Boolean(selected)", self.content)
        self.assertIn("setQueryVariants", self.content)

    def test_vpn_status_uses_browser_public_ip_and_exposes_all_states(self):
        status_buttons = self.tree.xpath("//button[@id='vpn-status']")

        self.assertEqual(len(status_buttons), 1)
        self.assertIn("https://api.ipapi.is", self.content)
        self.assertIn("payload.is_vpn", self.content)
        for status in ("checking", "active", "inactive", "unknown"):
            with self.subTest(status=status):
                self.assertIn(f'"{status}"', self.content)

    def test_brand_assets_and_palette_are_wired_to_home(self):
        project_dir = Path(__file__).resolve().parents[1]
        theme = (project_dir / "theme.css").read_text(encoding="utf-8")

        self.assertEqual(
            self.tree.xpath("//link[@rel='icon']/@href"),
            ["assets/favicon.svg"],
        )
        self.assertEqual(
            self.tree.xpath("//img[contains(@class, 'brand-logo')]/@src"),
            ["assets/synthesix-mark.svg"],
        )
        for color in ("#2563EB", "#0F172A", "#06B6D4", "#64748B", "#000000", "#FFFFFF"):
            with self.subTest(color=color):
                self.assertIn(color, theme)

    def test_language_detection_and_settings_are_shared(self):
        project_dir = Path(__file__).resolve().parents[1]
        i18n = (project_dir / "i18n.js").read_text(encoding="utf-8")

        self.assertEqual(
            self.tree.xpath("//script[@src='i18n.js']/@src"),
            ["i18n.js"],
        )
        self.assertIn('"synthesix-language"', i18n)
        self.assertIn("navigator.languages", i18n)
        self.assertIn("window.localStorage.setItem(storageKey", i18n)
        self.assertIn("synthesix-settings-dialog", i18n)
        self.assertIn('dataset.settingsButton = ""', i18n)
        self.assertIn(
            'supportedLanguages = ["en", "zh", "es", "fr", "pt", "de"]',
            i18n,
        )
        for language in (
            "English",
            "中文（普通话）",
            "Español",
            "Français",
            "Português",
            "Deutsch",
        ):
            with self.subTest(language=language):
                self.assertIn(language, i18n)
        self.assertNotIn('<option value="hi">', i18n)
        self.assertIn("Paramètres", i18n)
        self.assertIn("Intl.DisplayNames", i18n)
        self.assertIn("window.alert =", i18n)
        self.assertIn("window.confirm =", i18n)
        self.assertIn("BroadcastChannel", i18n)
        self.assertIn('window.addEventListener("storage"', i18n)
        self.assertEqual(self.tree.xpath("//*[@data-theme-toggle]"), [])

    def test_investigation_controls_are_wired_to_backend_actions(self):
        self.assertEqual(
            len(self.tree.xpath("//select[@id='investigation-select']")),
            1,
        )
        self.assertEqual(
            len(self.tree.xpath("//dialog[@id='investigation-dialog']")),
            1,
        )
        for action in (
            "open_investigation",
            "create_investigation",
            "update_investigation",
            "archive_investigation",
            "delete_investigation",
        ):
            with self.subTest(action=action):
                self.assertIn(f'queueAction("{action}"', self.content)

        self.assertIn('action: "select_investigation"', self.content)
        self.assertIn("investigationId: investigationSelect.value", self.content)
        self.assertIn("setInvestigations", self.content)
        self.assertIn("setSelectedInvestigation", self.content)
        self.assertEqual(
            len(
                self.tree.xpath(
                    "//datalist[@id='tag-suggestions']/option"
                )
            ),
            26,
        )
        self.assertEqual(
            len(
                self.tree.xpath(
                    "//select[@id='investigation-tag-suggestion']"
                )
            ),
            1,
        )
        self.assertEqual(
            len(self.tree.xpath("//button[@id='add-investigation-tag']")),
            1,
        )
        self.assertNotIn("ZeroNeurone TagSet", self.content)
        self.assertIn("tags.push(selected)", self.content)

    def test_local_archive_search_is_offline_and_filterable(self):
        self.assertEqual(
            len(self.tree.xpath("//input[@id='local-search-query']")),
            1,
        )
        self.assertEqual(
            len(self.tree.xpath("//select[@id='local-search-investigation']")),
            1,
        )
        self.assertEqual(
            len(self.tree.xpath("//button[@id='rebuild-local-index']")),
            1,
        )
        self.assertIn('queueAction("local_archive_search"', self.content)
        self.assertIn('queueAction("rebuild_local_search_index"', self.content)
        self.assertIn("never", self.content)
        self.assertIn("external search engine", self.content)

    def test_svg_brand_assets_are_valid_xml(self):
        assets_dir = Path(__file__).resolve().parents[1] / "assets"
        filenames = (
            "favicon.svg",
            "synthesix-app-icon.svg",
            "synthesix-logo.svg",
            "synthesix-logo-dark.svg",
            "synthesix-mark.svg",
            "synthesix-mark-black.svg",
            "synthesix-mark-white.svg",
        )

        for filename in filenames:
            with self.subTest(filename=filename):
                etree.parse(str(assets_dir / filename))


if __name__ == "__main__":
    unittest.main()
