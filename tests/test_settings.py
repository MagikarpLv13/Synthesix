import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from settings import get_settings, reload_settings


class SettingsCacheTestCase(unittest.TestCase):
    """T-002: settings are built once per environment signature."""

    def test_same_environment_returns_cached_instance(self):
        with TemporaryDirectory() as temp_dir:
            with patch.dict("os.environ", {"SYNTHESIX_BASE_DIR": temp_dir}, clear=True):
                first = get_settings()
                second = get_settings()

                self.assertIs(first, second)

    def test_environment_change_invalidates_cache(self):
        with TemporaryDirectory() as first_dir, TemporaryDirectory() as second_dir:
            with patch.dict(
                "os.environ", {"SYNTHESIX_BASE_DIR": first_dir}, clear=True
            ):
                first = get_settings()
            with patch.dict(
                "os.environ", {"SYNTHESIX_BASE_DIR": second_dir}, clear=True
            ):
                second = get_settings()

            self.assertIsNot(first, second)
            self.assertNotEqual(first.base_dir, second.base_dir)

    def test_reload_settings_forces_a_rebuild(self):
        with TemporaryDirectory() as temp_dir:
            with patch.dict("os.environ", {"SYNTHESIX_BASE_DIR": temp_dir}, clear=True):
                first = get_settings()
                second = reload_settings()

                self.assertIsNot(first, second)
                self.assertEqual(first, second)


class SettingsTestCase(unittest.TestCase):
    def test_default_settings_are_relative_to_current_directory(self):
        with TemporaryDirectory() as temp_dir:
            with patch.dict("os.environ", {"SYNTHESIX_BASE_DIR": temp_dir}, clear=True):
                settings = get_settings()

            base_dir = Path(temp_dir).resolve()
            self.assertEqual(settings.base_dir, base_dir)
            self.assertEqual(settings.history_dir, base_dir / "history")
            self.assertEqual(settings.history_json_path, base_dir / "history" / "history.json")
            self.assertEqual(settings.history_report_path, base_dir / "history" / "history.html")
            self.assertEqual(settings.robot_challenges_dir, base_dir / "history" / "robot_challenges")
            self.assertFalse(settings.debug_html)
            self.assertEqual(settings.debug_html_dir, base_dir / "history" / "debug_pages")
            self.assertEqual(settings.browser_profile_dir, base_dir / "zendriver-profile")
            self.assertEqual(settings.search_profile_dir, base_dir / "search-profile")
            self.assertEqual(settings.search_window_mode, "offscreen")
            self.assertEqual(settings.browser_type, "auto")
            self.assertIsNone(settings.browser_executable_path)
            self.assertEqual(settings.browser_connection_timeout, 0.25)
            self.assertEqual(settings.browser_connection_max_tries, 10)
            self.assertEqual(settings.default_engines, {
                "google": True,
                "bing": True,
                "brave": True,
                "duckduckgo": True,
            })
            self.assertEqual(settings.default_history_limit, 25)
            self.assertEqual(settings.default_max_results, 20)
            self.assertEqual(settings.home_poll_interval, 0.25)
            self.assertEqual(settings.empty_tabs_grace_seconds, 2.0)
            self.assertEqual(settings.page_load_timeout, 2.5)
            self.assertEqual(settings.page_load_interval, 0.1)
            self.assertEqual(settings.bing_results_timeout, 10.0)
            self.assertEqual(settings.bing_results_interval, 0.25)
            self.assertEqual(settings.brave_results_timeout, 45.0)
            self.assertEqual(settings.brave_results_interval, 0.25)
            self.assertEqual(settings.brave_robot_find_timeout, 0.2)
            self.assertEqual(settings.duckduckgo_results_timeout, 10.0)
            self.assertEqual(settings.duckduckgo_robot_timeout, 75.0)
            self.assertEqual(settings.duckduckgo_robot_interval, 0.5)
            self.assertEqual(settings.engine_search_timeout, 90.0)
            self.assertEqual(settings.engine_concurrency, 4)
            self.assertEqual(settings.engine_retry_attempts, 1)
            self.assertEqual(settings.engine_retry_delay, 0.5)
            self.assertEqual(settings.engine_retry_backoff, 2.0)

    def test_environment_overrides_runtime_settings(self):
        with TemporaryDirectory() as temp_dir:
            env = {
                "SYNTHESIX_BASE_DIR": temp_dir,
                "SYNTHESIX_DATABASE_PATH": "runtime/synthesix.db",
                "SYNTHESIX_INVESTIGATION_PAGES_DIR": "runtime/cases",
                "SYNTHESIX_EVIDENCE_DIR": "runtime/evidence",
                "SYNTHESIX_EXPORTS_DIR": "runtime/exports",
                "SYNTHESIX_HISTORY_DIR": "runtime/history",
                "SYNTHESIX_HISTORY_REPORT_PATH": "runtime/history-report.html",
                "SYNTHESIX_DEBUG_HTML": "true",
                "SYNTHESIX_DEBUG_HTML_DIR": "runtime/debug-pages",
                "SYNTHESIX_BROWSER_PROFILE_DIR": "runtime/profile",
                "SYNTHESIX_SEARCH_PROFILE_DIR": "runtime/search-profile",
                "SYNTHESIX_SEARCH_BROWSER": "shared",
                "SYNTHESIX_SEARCH_WINDOW_MODE": "headless",
                "SYNTHESIX_BROWSER": "brave",
                "SYNTHESIX_BROWSER_EXECUTABLE_PATH": "runtime/brave.exe",
                "SYNTHESIX_BROWSER_CONNECTION_TIMEOUT": "0.75",
                "SYNTHESIX_BROWSER_CONNECTION_MAX_TRIES": "20",
                "SYNTHESIX_EXTENSION_DIR": "runtime/extension",
                "SYNTHESIX_EXTENSION_MODE": "off",
                "SYNTHESIX_OVERLAY_MODE": "extension",
                "SYNTHESIX_DEFAULT_ENGINES": "google,duckduckgo",
                "SYNTHESIX_HISTORY_LIMIT": "7",
                "SYNTHESIX_DEFAULT_MAX_RESULTS": "12",
                "SYNTHESIX_HOME_POLL_INTERVAL": "0.5",
                "SYNTHESIX_EMPTY_TABS_GRACE_SECONDS": "3",
                "SYNTHESIX_PAGE_LOAD_TIMEOUT": "9",
                "SYNTHESIX_PAGE_LOAD_INTERVAL": "0.3",
                "SYNTHESIX_BING_RESULTS_TIMEOUT": "14",
                "SYNTHESIX_BING_RESULTS_INTERVAL": "0.4",
                "SYNTHESIX_BRAVE_RESULTS_TIMEOUT": "60",
                "SYNTHESIX_BRAVE_RESULTS_INTERVAL": "0.75",
                "SYNTHESIX_BRAVE_ROBOT_FIND_TIMEOUT": "0.4",
                "SYNTHESIX_DUCKDUCKGO_RESULTS_TIMEOUT": "12",
                "SYNTHESIX_DUCKDUCKGO_ROBOT_TIMEOUT": "70",
                "SYNTHESIX_DUCKDUCKGO_ROBOT_INTERVAL": "0.6",
                "SYNTHESIX_ENGINE_SEARCH_TIMEOUT": "30",
                "SYNTHESIX_ENGINE_CONCURRENCY": "2",
                "SYNTHESIX_ENGINE_RETRY_ATTEMPTS": "3",
                "SYNTHESIX_ENGINE_RETRY_DELAY": "0.2",
                "SYNTHESIX_ENGINE_RETRY_BACKOFF": "1.5",
                "SYNTHESIX_MONITOR_AUTOSTART": "true",
                "SYNTHESIX_MONITOR_POLL_INTERVAL": "15",
                "SYNTHESIX_MONITOR_BATCH_SIZE": "8",
                "SYNTHESIX_MONITOR_CONCURRENCY": "3",
                "SYNTHESIX_MONITOR_LEASE_SECONDS": "120",
                "SYNTHESIX_MONITOR_ATTEMPT_TIMEOUT": "45",
                "SYNTHESIX_MONITOR_RETRY_ATTEMPTS": "2",
                "SYNTHESIX_MONITOR_RETRY_DELAY": "0.4",
                "SYNTHESIX_MONITOR_RETRY_BACKOFF": "3",
                "SYNTHESIX_MONITOR_JITTER_SECONDS": "0.5",
                "SYNTHESIX_MONITOR_FAILURE_BACKOFF_SECONDS": "90",
                "SYNTHESIX_MONITOR_MAX_FAILURES": "6",
                "SYNTHESIX_MONITOR_HEADLESS": "false",
                "SYNTHESIX_SOCIAL_API_TIMEOUT": "7.5",
                "SYNTHESIX_YOUTUBE_API_KEY": "youtube-secret",
                "SYNTHESIX_X_BEARER_TOKEN": "x-secret",
                "SYNTHESIX_TIKTOK_RESEARCH_ACCESS_TOKEN": "tiktok-secret",
            }
            with patch.dict("os.environ", env, clear=True):
                settings = get_settings()

            base_dir = Path(temp_dir).resolve()
            self.assertEqual(settings.history_dir, base_dir / "runtime" / "history")
            self.assertEqual(settings.history_report_path, base_dir / "runtime" / "history-report.html")
            self.assertTrue(settings.debug_html)
            self.assertEqual(settings.debug_html_dir, base_dir / "runtime" / "debug-pages")
            self.assertEqual(settings.browser_profile_dir, base_dir / "runtime" / "profile")
            self.assertEqual(
                settings.search_profile_dir,
                base_dir / "runtime" / "search-profile",
            )
            self.assertEqual(settings.search_window_mode, "headless")
            self.assertEqual(settings.browser_type, "brave")
            self.assertEqual(settings.browser_executable_path, base_dir / "runtime" / "brave.exe")
            self.assertEqual(settings.browser_connection_timeout, 0.75)
            self.assertEqual(settings.browser_connection_max_tries, 20)
            self.assertEqual(settings.default_engines, {
                "google": True,
                "bing": False,
                "brave": False,
                "duckduckgo": True,
            })
            self.assertEqual(settings.default_history_limit, 7)
            self.assertEqual(settings.default_max_results, 12)
            self.assertEqual(settings.home_poll_interval, 0.5)
            self.assertEqual(settings.empty_tabs_grace_seconds, 3.0)
            self.assertEqual(settings.page_load_timeout, 9.0)
            self.assertEqual(settings.page_load_interval, 0.3)
            self.assertEqual(settings.bing_results_timeout, 14.0)
            self.assertEqual(settings.bing_results_interval, 0.4)
            self.assertEqual(settings.brave_results_timeout, 60.0)
            self.assertEqual(settings.brave_results_interval, 0.75)
            self.assertEqual(settings.brave_robot_find_timeout, 0.4)
            self.assertEqual(settings.duckduckgo_results_timeout, 12.0)
            self.assertEqual(settings.duckduckgo_robot_timeout, 70.0)
            self.assertEqual(settings.duckduckgo_robot_interval, 0.6)
            self.assertEqual(settings.engine_search_timeout, 30.0)
            self.assertEqual(settings.engine_concurrency, 2)
            self.assertEqual(settings.engine_retry_attempts, 3)
            self.assertEqual(settings.engine_retry_delay, 0.2)
            self.assertEqual(settings.engine_retry_backoff, 1.5)
            rendered = repr(settings)
            self.assertNotIn("youtube-secret", rendered)
            self.assertNotIn("x-secret", rendered)
            self.assertNotIn("tiktok-secret", rendered)


    def test_invalid_search_window_mode_falls_back_to_offscreen(self):
        with TemporaryDirectory() as temp_dir:
            with patch.dict(
                "os.environ",
                {
                    "SYNTHESIX_BASE_DIR": temp_dir,
                    "SYNTHESIX_SEARCH_WINDOW_MODE": "invalid",
                },
                clear=True,
            ):
                settings = get_settings()

        self.assertEqual(settings.search_window_mode, "offscreen")


if __name__ == "__main__":
    unittest.main()
