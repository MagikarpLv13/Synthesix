import json
import logging
from contextlib import redirect_stderr
from io import StringIO
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch

from main import (
    _cached_history_payload,
    _log_level_from_args,
    apply_cli_runtime_overrides,
    configure_event_loop_policy,
    parse_cli_args,
)
from settings import get_settings


class MainCliTestCase(unittest.TestCase):
    def test_cli_log_levels(self):
        self.assertEqual(_log_level_from_args(parse_cli_args([])), logging.INFO)
        self.assertEqual(_log_level_from_args(parse_cli_args(["--quiet"])), logging.WARNING)
        self.assertEqual(_log_level_from_args(parse_cli_args(["--verbose"])), logging.DEBUG)

    def test_cli_rejects_conflicting_verbosity_flags(self):
        with redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit):
                parse_cli_args(["--quiet", "--verbose"])

    def test_debug_html_flag_enables_runtime_setting(self):
        args = parse_cli_args(["--debug-html"])

        with patch.dict("os.environ", {}, clear=True):
            apply_cli_runtime_overrides(args)
            settings = get_settings()

        self.assertTrue(settings.debug_html)

    def test_windows_event_loop_policy_is_configured_on_windows(self):
        policy = object()
        with patch("main.sys.platform", "win32"):
            with patch("main.asyncio.WindowsSelectorEventLoopPolicy", return_value=policy, create=True):
                with patch("main.asyncio.set_event_loop_policy") as set_policy:
                    configure_event_loop_policy()

        set_policy.assert_called_once_with(policy)


class HomeHistoryCacheTestCase(unittest.TestCase):
    def test_cached_history_payload_refreshes_when_file_changes(self):
        with TemporaryDirectory() as temp_dir:
            with patch.dict("os.environ", {"SYNTHESIX_BASE_DIR": temp_dir}, clear=True):
                settings = get_settings()

                cache = {}
                history_json, version = _cached_history_payload(settings, cache)
                self.assertEqual(json.loads(history_json), [])
                self.assertEqual(version, "")

                settings.history_json_path.parent.mkdir(parents=True, exist_ok=True)
                settings.history_json_path.write_text(
                    json.dumps([
                        {
                            "date": "2026-06-06 00:00",
                            "query": "first query",
                            "smart_query": '"first query"',
                            "nb_results": 1,
                            "link": "first.html",
                        }
                    ]),
                    encoding="utf-8",
                )

                refreshed_json, refreshed_version = _cached_history_payload(settings, cache)

        self.assertNotEqual(refreshed_version, version)
        self.assertEqual(json.loads(refreshed_json)[0]["query"], "first query")


if __name__ == "__main__":
    unittest.main()
