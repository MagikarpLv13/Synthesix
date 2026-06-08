import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from browser_manager import (
    FLATPAK_BRAVE_APP_ID,
    _build_zendriver_config,
    _ensure_synthesix_bookmark,
    _find_native_browser_executable,
    _mark_profile_exited_cleanly,
    _resolve_browser_executable,
)
from settings import get_settings


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

    def test_zendriver_config_uses_runtime_browser_settings(self):
        with TemporaryDirectory() as temp_dir:
            env = {
                "SYNTHESIX_BASE_DIR": temp_dir,
                "SYNTHESIX_BROWSER_PROFILE_DIR": "profile",
                "SYNTHESIX_BROWSER": "brave",
                "SYNTHESIX_BROWSER_EXECUTABLE_PATH": "bin/brave.exe",
                "SYNTHESIX_BROWSER_CONNECTION_TIMEOUT": "0.75",
                "SYNTHESIX_BROWSER_CONNECTION_MAX_TRIES": "20",
            }
            with patch.dict("os.environ", env, clear=True):
                settings = get_settings()

            config = _build_zendriver_config(settings)

        self.assertEqual(config.user_data_dir, str(settings.browser_profile_dir))
        self.assertEqual(config.browser_executable_path, str(settings.browser_executable_path))
        self.assertEqual(config.browser_connection_timeout, 0.75)
        self.assertEqual(config.browser_connection_max_tries, 20)

    def test_native_browser_discovery_supports_brave_browser_stable(self):
        with TemporaryDirectory() as temp_dir:
            executable = Path(temp_dir) / "brave-browser-stable"
            executable.write_text("", encoding="utf-8")

            with patch(
                "browser_manager.shutil.which",
                side_effect=lambda command: (
                    str(executable) if command == "brave-browser-stable" else None
                ),
            ):
                resolved = _find_native_browser_executable("brave")

        self.assertEqual(resolved, executable)

    def test_flatpak_brave_wrapper_is_generated_when_no_native_binary_exists(self):
        with TemporaryDirectory() as temp_dir:
            env = {
                "SYNTHESIX_BASE_DIR": temp_dir,
                "SYNTHESIX_BROWSER": "brave",
            }
            with patch.dict("os.environ", env, clear=True):
                settings = get_settings()

            flatpak_executable = "/usr/bin/flatpak"
            with (
                patch("browser_manager.sys.platform", "linux"),
                patch(
                    "browser_manager.shutil.which",
                    side_effect=lambda command: (
                        flatpak_executable if command == "flatpak" else None
                    ),
                ),
                patch("browser_manager._flatpak_brave_is_installed", return_value=True),
            ):
                resolved = _resolve_browser_executable(settings)

            self.assertIsNotNone(resolved)
            content = resolved.read_text(encoding="utf-8")

        self.assertIn(f"run {FLATPAK_BRAVE_APP_ID}", content)
        self.assertIn('"$@"', content)


if __name__ == "__main__":
    unittest.main()
