import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from settings import get_settings


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
            self.assertEqual(settings.browser_profile_dir, base_dir / "zendriver-profile")
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
            self.assertEqual(settings.brave_results_timeout, 45.0)
            self.assertEqual(settings.brave_results_interval, 0.25)
            self.assertEqual(settings.brave_robot_find_timeout, 0.2)
            self.assertEqual(settings.engine_search_timeout, 90.0)
            self.assertEqual(settings.engine_retry_attempts, 1)
            self.assertEqual(settings.engine_retry_delay, 0.5)
            self.assertEqual(settings.engine_retry_backoff, 2.0)

    def test_environment_overrides_runtime_settings(self):
        with TemporaryDirectory() as temp_dir:
            env = {
                "SYNTHESIX_BASE_DIR": temp_dir,
                "SYNTHESIX_HISTORY_DIR": "runtime/history",
                "SYNTHESIX_HISTORY_REPORT_PATH": "runtime/history-report.html",
                "SYNTHESIX_BROWSER_PROFILE_DIR": "runtime/profile",
                "SYNTHESIX_DEFAULT_ENGINES": "google,duckduckgo",
                "SYNTHESIX_HISTORY_LIMIT": "7",
                "SYNTHESIX_DEFAULT_MAX_RESULTS": "12",
                "SYNTHESIX_HOME_POLL_INTERVAL": "0.5",
                "SYNTHESIX_EMPTY_TABS_GRACE_SECONDS": "3",
                "SYNTHESIX_PAGE_LOAD_TIMEOUT": "9",
                "SYNTHESIX_PAGE_LOAD_INTERVAL": "0.3",
                "SYNTHESIX_BRAVE_RESULTS_TIMEOUT": "60",
                "SYNTHESIX_BRAVE_RESULTS_INTERVAL": "0.75",
                "SYNTHESIX_BRAVE_ROBOT_FIND_TIMEOUT": "0.4",
                "SYNTHESIX_ENGINE_SEARCH_TIMEOUT": "30",
                "SYNTHESIX_ENGINE_RETRY_ATTEMPTS": "3",
                "SYNTHESIX_ENGINE_RETRY_DELAY": "0.2",
                "SYNTHESIX_ENGINE_RETRY_BACKOFF": "1.5",
            }
            with patch.dict("os.environ", env, clear=True):
                settings = get_settings()

            base_dir = Path(temp_dir).resolve()
            self.assertEqual(settings.history_dir, base_dir / "runtime" / "history")
            self.assertEqual(settings.history_report_path, base_dir / "runtime" / "history-report.html")
            self.assertEqual(settings.browser_profile_dir, base_dir / "runtime" / "profile")
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
            self.assertEqual(settings.brave_results_timeout, 60.0)
            self.assertEqual(settings.brave_results_interval, 0.75)
            self.assertEqual(settings.brave_robot_find_timeout, 0.4)
            self.assertEqual(settings.engine_search_timeout, 30.0)
            self.assertEqual(settings.engine_retry_attempts, 3)
            self.assertEqual(settings.engine_retry_delay, 0.2)
            self.assertEqual(settings.engine_retry_backoff, 1.5)


if __name__ == "__main__":
    unittest.main()
