import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from browser_manager import _ensure_synthesix_bookmark, _mark_profile_exited_cleanly


class BrowserManagerTestCase(unittest.TestCase):
    def test_mark_profile_exited_cleanly_updates_chrome_state_files(self):
        with TemporaryDirectory() as temp_dir:
            profile_dir = Path(temp_dir)
            preferences_path = profile_dir / "Default" / "Preferences"
            local_state_path = profile_dir / "Local State"
            preferences_path.parent.mkdir(parents=True)

            preferences_path.write_text(
                json.dumps({"profile": {"exit_type": "Crashed", "exited_cleanly": False}}),
                encoding="utf-8",
            )
            local_state_path.write_text(
                json.dumps({"exited_cleanly": False}),
                encoding="utf-8",
            )

            _mark_profile_exited_cleanly(temp_dir)

            preferences = json.loads(preferences_path.read_text(encoding="utf-8"))
            local_state = json.loads(local_state_path.read_text(encoding="utf-8"))

            self.assertEqual(preferences["profile"]["exit_type"], "Normal")
            self.assertTrue(preferences["profile"]["exited_cleanly"])
            self.assertTrue(preferences["bookmark_bar"]["show_on_all_tabs"])
            self.assertTrue(local_state["exited_cleanly"])

    def test_ensure_synthesix_bookmark_creates_home_bookmark(self):
        with TemporaryDirectory() as temp_dir:
            home_url = "file:///F:/Dev/Python/MSA/index.html"

            _ensure_synthesix_bookmark(temp_dir, home_url)

            bookmarks_path = Path(temp_dir) / "Default" / "Bookmarks"
            bookmarks = json.loads(bookmarks_path.read_text(encoding="utf-8"))
            children = bookmarks["roots"]["bookmark_bar"]["children"]

            self.assertEqual(len(children), 1)
            self.assertEqual(children[0]["name"], "Synthesix Home")
            self.assertEqual(children[0]["url"], home_url)

    def test_ensure_synthesix_bookmark_updates_existing_bookmark(self):
        with TemporaryDirectory() as temp_dir:
            bookmarks_path = Path(temp_dir) / "Default" / "Bookmarks"
            bookmarks_path.parent.mkdir(parents=True)
            bookmarks_path.write_text(
                json.dumps(
                    {
                        "roots": {
                            "bookmark_bar": {
                                "children": [
                                    {
                                        "id": "4",
                                        "name": "Synthesix Home",
                                        "type": "url",
                                        "url": "file:///old/index.html",
                                    }
                                ],
                                "id": "1",
                                "name": "Bookmarks bar",
                                "type": "folder",
                            }
                        },
                        "version": 1,
                    }
                ),
                encoding="utf-8",
            )

            _ensure_synthesix_bookmark(temp_dir, "file:///new/index.html")

            bookmarks = json.loads(bookmarks_path.read_text(encoding="utf-8"))
            children = bookmarks["roots"]["bookmark_bar"]["children"]

            self.assertEqual(len(children), 1)
            self.assertEqual(children[0]["url"], "file:///new/index.html")


if __name__ == "__main__":
    unittest.main()
