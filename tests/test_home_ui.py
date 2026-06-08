import unittest
from pathlib import Path

from lxml import html


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


if __name__ == "__main__":
    unittest.main()
