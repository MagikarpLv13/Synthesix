"""Start the local Synthesix multi-query browser."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path


def parse_cli_args(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Synthesix multi-query browser")
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument("--quiet", action="store_true", help="Show warnings and errors only.")
    verbosity.add_argument("--verbose", action="store_true", help="Show debug logs.")
    parser.add_argument("--debug-html", action="store_true", help="Keep search-engine HTML for diagnosis.")
    parser.add_argument("--data-dir", type=Path, help="Directory for local history and browser profiles.")
    parser.add_argument("--headless", action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args(argv)


async def main(*, headless: bool = False) -> None:
    from app.runtime import BrowserApplication
    from settings import get_settings

    await BrowserApplication(get_settings()).run(headless=headless)


def run_cli(argv: list[str] | None = None) -> int:
    args = parse_cli_args(argv)
    if args.data_dir:
        os.environ["SYNTHESIX_BASE_DIR"] = str(args.data_dir.resolve())
    elif "SYNTHESIX_BASE_DIR" not in os.environ:
        root = Path(os.getenv("LOCALAPPDATA", str(Path.home()))) / "Synthesix" if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
        os.environ["SYNTHESIX_BASE_DIR"] = str(root)
    if args.debug_html:
        os.environ["SYNTHESIX_DEBUG_HTML"] = "1"
    root = Path(os.environ["SYNTHESIX_BASE_DIR"])
    log_dir = root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    level = logging.DEBUG if args.verbose else logging.WARNING if args.quiet else logging.INFO
    file_handler = logging.FileHandler(log_dir / "browser.log", encoding="utf-8")
    logging.basicConfig(level=level, format="%(levelname)s:%(name)s:%(message)s", handlers=[logging.StreamHandler(), file_handler])
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main(headless=args.headless))
    except KeyboardInterrupt:
        return 0
    except Exception:
        logging.exception("Synthesix could not start. Install Chrome or Brave, or set SYNTHESIX_BROWSER_EXECUTABLE_PATH.")
        return 1
    finally:
        logging.getLogger().removeHandler(file_handler)
        file_handler.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli())
