import asyncio
import json
import unittest
from types import SimpleNamespace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from browser_manager import (
    FLATPAK_BRAVE_APP_ID,
    _build_zendriver_config,
    _clear_profile_browsing_data,
    _ensure_synthesix_bookmark,
    _expected_extension_id,
    _expected_extension_revision,
    _extension_build_ready,
    _extension_id_from_key,
    _find_native_browser_executable,
    _mark_profile_exited_cleanly,
    _resolve_browser_executable,
    detect_synthesix_extension,
)
from settings import get_settings


TEST_EXTENSION_KEY = (
    "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlA12Fb3SSH/E+Y6N7xWgF24Yh9G3YF9O3uhD10Jy45ZiPN830YF"
    "kDn0+U4LbURaT4nOy+gEDNwLiy9FfhHBDUP6bFNnfK8GIohJwgrWweCv3WbBDgBCACYL/NQLBoUq3c6aSMCI39mQ6udOH3c8"
    "p0a0zWNcVXsefFgjXNKxpWFcS80XmAycbmGGk1I7VD5Z4d39z3PmEmf3ekMMjDjc9cfAPHSp3w9ZXt2HO59n6aenmIXHBVNm"
    "daEP5xtUQEq1Ai/NgJPCdtvkPBYtYogLqHZInit1aKM41f0DImzgu7pyXUSlvGnQLLce9L0ypr/saRCYXP38eZb/B784JekL"
    "IGQIDAQAB"
)


class BrowserManagerTestCase(unittest.TestCase):
    def _write_extension_build(self, base_dir: Path) -> Path:
        extension_dir = base_dir / "extension"
        (extension_dir / "dist").mkdir(parents=True)
        (extension_dir / "manifest.json").write_text(
            json.dumps(
                {
                    "manifest_version": 3,
                    "key": TEST_EXTENSION_KEY,
                    # The worker filename is revision-stamped by the build and
                    # resolved from the manifest by _extension_build_ready.
                    "background": {"service_worker": "dist/background-test.js"},
                }
            ),
            encoding="utf-8",
        )
        (extension_dir / "dist" / "background-test.js").write_text("", encoding="utf-8")
        (extension_dir / "dist" / "content.js").write_text("", encoding="utf-8")
        return extension_dir

    def test_clear_profile_browsing_data_preserves_bookmarks_and_login_data(self):
        with TemporaryDirectory() as temp_dir:
            profile_dir = Path(temp_dir)
            default_dir = profile_dir / "Default"
            (default_dir / "Cache").mkdir(parents=True)
            (default_dir / "Cache" / "entry").write_text("cache", encoding="utf-8")
            (default_dir / "History").write_text("history", encoding="utf-8")
            (default_dir / "Network").mkdir()
            (default_dir / "Network" / "Cookies").write_text("cookies", encoding="utf-8")
            (default_dir / "Bookmarks").write_text("bookmarks", encoding="utf-8")
            (default_dir / "Login Data").write_text("passwords", encoding="utf-8")

            removed = _clear_profile_browsing_data(temp_dir)

            self.assertGreaterEqual(removed, 3)
            self.assertFalse((default_dir / "Cache").exists())
            self.assertFalse((default_dir / "History").exists())
            self.assertFalse((default_dir / "Network" / "Cookies").exists())
            self.assertTrue((default_dir / "Bookmarks").exists())
            self.assertTrue((default_dir / "Login Data").exists())

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
            self._write_extension_build(Path(temp_dir))
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
        self.assertIn(
            f"--load-extension={str(settings.extension_dir.resolve()).replace(chr(92), '/')}",
            config.browser_args,
        )
        self.assertIn(
            "--disable-features=DisableLoadExtensionCommandLineSwitch",
            config.browser_args,
        )

    def test_zendriver_config_skips_extension_when_mode_off(self):
        with TemporaryDirectory() as temp_dir:
            self._write_extension_build(Path(temp_dir))
            env = {
                "SYNTHESIX_BASE_DIR": temp_dir,
                "SYNTHESIX_EXTENSION_MODE": "off",
                "SYNTHESIX_BROWSER_EXECUTABLE_PATH": "bin/chrome.exe",
            }
            with patch.dict("os.environ", env, clear=True):
                settings = get_settings()

            config = _build_zendriver_config(settings)

        self.assertFalse(any(arg.startswith("--load-extension=") for arg in config.browser_args))

    def test_zendriver_config_skips_extension_when_build_is_missing(self):
        with TemporaryDirectory() as temp_dir:
            env = {
                "SYNTHESIX_BASE_DIR": temp_dir,
                "SYNTHESIX_BROWSER_EXECUTABLE_PATH": "bin/chrome.exe",
            }
            with patch.dict("os.environ", env, clear=True):
                settings = get_settings()

            config = _build_zendriver_config(settings)

        self.assertFalse(_extension_build_ready(settings.extension_dir))
        self.assertFalse(any(arg.startswith("--load-extension=") for arg in config.browser_args))

    def test_extension_build_ready_requires_manifest_declared_worker(self):
        with TemporaryDirectory() as temp_dir:
            extension_dir = self._write_extension_build(Path(temp_dir))
            self.assertTrue(_extension_build_ready(extension_dir))

            (extension_dir / "dist" / "background-test.js").unlink()
            self.assertFalse(_extension_build_ready(extension_dir))

    def test_expected_extension_revision_reads_dist_revision_json(self):
        with TemporaryDirectory() as temp_dir:
            extension_dir = self._write_extension_build(Path(temp_dir))
            env = {"SYNTHESIX_BASE_DIR": temp_dir}
            with patch.dict("os.environ", env, clear=True):
                settings = get_settings()

            self.assertIsNone(_expected_extension_revision(settings))

            (extension_dir / "dist" / "revision.json").write_text(
                json.dumps({"revision": "abc123"}), encoding="utf-8"
            )
            self.assertEqual(_expected_extension_revision(settings), "abc123")

    def test_extension_id_is_derived_from_manifest_key(self):
        with TemporaryDirectory() as temp_dir:
            self._write_extension_build(Path(temp_dir))
            env = {"SYNTHESIX_BASE_DIR": temp_dir}
            with patch.dict("os.environ", env, clear=True):
                settings = get_settings()

            expected_id = _extension_id_from_key(TEST_EXTENSION_KEY)
            self.assertEqual(_expected_extension_id(settings), expected_id)
            self.assertIsNotNone(expected_id)
            self.assertEqual(len(expected_id), 32)
            self.assertTrue(set(expected_id) <= set("abcdefghijklmnop"))

    def test_detect_synthesix_extension_matches_expected_target(self):
        with TemporaryDirectory() as temp_dir:
            self._write_extension_build(Path(temp_dir))
            env = {"SYNTHESIX_BASE_DIR": temp_dir}
            with patch.dict("os.environ", env, clear=True):
                settings = get_settings()
            extension_id = _expected_extension_id(settings)

            class FakeBrowser:
                async def _get_targets(self):
                    return [
                        SimpleNamespace(url="chrome-extension://other/background.js"),
                        SimpleNamespace(url=f"chrome-extension://{extension_id}/dist/background.js"),
                    ]

            available = asyncio.run(detect_synthesix_extension(FakeBrowser(), settings))

        self.assertTrue(available)

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
