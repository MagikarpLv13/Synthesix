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
