import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import AsyncMock, patch

import main


class BrowserCliTestCase(unittest.TestCase):
    def test_parser_keeps_logging_and_data_directory_options(self):
        args = main.parse_cli_args(["--verbose", "--debug-html", "--data-dir", "local"])
        self.assertTrue(args.verbose)
        self.assertTrue(args.debug_html)
        self.assertEqual(args.data_dir, Path("local"))

    def test_cli_configures_data_directory_and_runs_new_application(self):
        with TemporaryDirectory() as directory:
            with patch.dict(os.environ, {}, clear=True), patch("main.main", new_callable=AsyncMock) as run, patch("main.logging.basicConfig"):
                self.assertEqual(main.run_cli(["--data-dir", directory, "--debug-html"]), 0)
                self.assertEqual(os.environ["SYNTHESIX_BASE_DIR"], str(Path(directory).resolve()))
                self.assertEqual(os.environ["SYNTHESIX_DEBUG_HTML"], "1")
                run.assert_awaited_once_with(headless=False)

    def test_cli_returns_failure_when_browser_cannot_start(self):
        with TemporaryDirectory() as directory:
            with patch.dict(os.environ, {"SYNTHESIX_BASE_DIR": directory}), patch("main.main", new_callable=AsyncMock, side_effect=RuntimeError("startup")), patch("main.logging.basicConfig"), patch("main.logging.exception"):
                self.assertEqual(main.run_cli([]), 1)
