import unittest
from pathlib import Path
from lxml import html


class HomeUiTestCase(unittest.TestCase):
    def test_home_loads_local_classic_bundle_and_single_browser_component(self):
        root = Path(__file__).resolve().parents[1]
        tree = html.fromstring((root / "index.html").read_text(encoding="utf-8"))
        self.assertEqual(len(tree.xpath("//sx-browser-app")), 1)
        self.assertEqual(tree.xpath("//script[@type='module']"), [])
        self.assertEqual(tree.xpath("//script/@src"), ["theme.js", "i18n.js", "assets/synthesix-ui.js"])
        for source in tree.xpath("//script/@src"):
            self.assertTrue((root / source).is_file(), source)

    def test_browser_has_only_search_profiles_and_history_navigation(self):
        source = (Path(__file__).resolve().parents[1] / "frontend/src/components/sx-browser-app.ts").read_text(encoding="utf-8")
        for action in ['"search"', '"create_profile"', '"rename_profile"', '"open_result"', '"load_search"']:
            self.assertIn(action, source)
        self.assertNotIn("investigation", source.lower())
        self.assertNotIn("unsafeHTML", source)
