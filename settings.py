import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict


ENGINE_NAMES = ("google", "bing", "brave", "duckduckgo")


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _env_path(name: str, default: str, base_dir: Path) -> Path:
    value = os.getenv(name, default)
    path = Path(value)
    if not path.is_absolute():
        path = base_dir / path
    return path


def _env_engines(name: str = "SYNTHESIX_DEFAULT_ENGINES") -> Dict[str, bool]:
    raw = os.getenv(name)
    if not raw:
        return {engine: True for engine in ENGINE_NAMES}

    selected = {item.strip().lower() for item in raw.split(",") if item.strip()}
    return {engine: engine in selected for engine in ENGINE_NAMES}


@dataclass(frozen=True)
class AppSettings:
    base_dir: Path
    history_dir: Path
    history_json_path: Path
    history_report_path: Path
    robot_challenges_dir: Path
    browser_profile_dir: Path
    default_engines: Dict[str, bool]
    default_history_limit: int
    default_max_results: int
    home_poll_interval: float
    empty_tabs_grace_seconds: float
    page_load_timeout: float
    page_load_interval: float
    brave_results_timeout: float
    brave_results_interval: float
    brave_robot_find_timeout: float

    def search_results_path(self, date_str: str) -> Path:
        return self.history_dir / f"search_results_{date_str}.html"


def get_settings() -> AppSettings:
    base_dir = Path(os.getenv("SYNTHESIX_BASE_DIR", ".")).resolve()
    history_dir = _env_path("SYNTHESIX_HISTORY_DIR", "history", base_dir)
    browser_profile_dir = _env_path("SYNTHESIX_BROWSER_PROFILE_DIR", "zendriver-profile", base_dir)

    return AppSettings(
        base_dir=base_dir,
        history_dir=history_dir,
        history_json_path=history_dir / "history.json",
        history_report_path=base_dir / "history.html",
        robot_challenges_dir=history_dir / "robot_challenges",
        browser_profile_dir=browser_profile_dir,
        default_engines=_env_engines(),
        default_history_limit=_env_int("SYNTHESIX_HISTORY_LIMIT", 25),
        default_max_results=_env_int("SYNTHESIX_DEFAULT_MAX_RESULTS", 20),
        home_poll_interval=_env_float("SYNTHESIX_HOME_POLL_INTERVAL", 0.25),
        empty_tabs_grace_seconds=_env_float("SYNTHESIX_EMPTY_TABS_GRACE_SECONDS", 2.0),
        page_load_timeout=_env_float("SYNTHESIX_PAGE_LOAD_TIMEOUT", 2.5),
        page_load_interval=_env_float("SYNTHESIX_PAGE_LOAD_INTERVAL", 0.1),
        brave_results_timeout=_env_float("SYNTHESIX_BRAVE_RESULTS_TIMEOUT", 45.0),
        brave_results_interval=_env_float("SYNTHESIX_BRAVE_RESULTS_INTERVAL", 0.25),
        brave_robot_find_timeout=_env_float("SYNTHESIX_BRAVE_ROBOT_FIND_TIMEOUT", 0.2),
    )
