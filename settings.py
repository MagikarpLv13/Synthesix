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


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_str(name: str, default: str) -> str:
    return os.getenv(name, default).strip() or default


def _env_optional_path(name: str, base_dir: Path) -> Path | None:
    value = os.getenv(name)
    if not value:
        return None
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base_dir / path
    return path


def _env_path(name: str, default: str, base_dir: Path) -> Path:
    value = os.getenv(name, default)
    path = Path(value).expanduser()
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
    database_path: Path
    investigation_pages_dir: Path
    evidence_dir: Path
    exports_dir: Path
    history_dir: Path
    history_json_path: Path
    history_report_path: Path
    robot_challenges_dir: Path
    debug_html: bool
    debug_html_dir: Path
    browser_profile_dir: Path
    browser_type: str
    browser_executable_path: Path | None
    browser_connection_timeout: float
    browser_connection_max_tries: int
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
    duckduckgo_results_timeout: float
    duckduckgo_robot_timeout: float
    duckduckgo_robot_interval: float
    engine_search_timeout: float
    engine_concurrency: int
    engine_retry_attempts: int
    engine_retry_delay: float
    engine_retry_backoff: float
    max_query_variants: int

    def search_results_path(self, date_str: str) -> Path:
        return self.history_dir / f"search_results_{date_str}.html"

    def investigation_page_path(self, investigation_id: str) -> Path:
        return self.investigation_pages_dir / f"{investigation_id}.html"


def get_settings() -> AppSettings:
    base_dir = Path(os.getenv("SYNTHESIX_BASE_DIR", ".")).resolve()
    history_dir = _env_path("SYNTHESIX_HISTORY_DIR", "history", base_dir)
    history_report_path = _env_path(
        "SYNTHESIX_HISTORY_REPORT_PATH",
        str(history_dir / "history.html"),
        base_dir,
    )
    browser_profile_dir = _env_path("SYNTHESIX_BROWSER_PROFILE_DIR", "zendriver-profile", base_dir)

    return AppSettings(
        base_dir=base_dir,
        database_path=_env_path(
            "SYNTHESIX_DATABASE_PATH",
            "data/synthesix.db",
            base_dir,
        ),
        investigation_pages_dir=_env_path(
            "SYNTHESIX_INVESTIGATION_PAGES_DIR",
            "data/investigation_pages",
            base_dir,
        ),
        evidence_dir=_env_path(
            "SYNTHESIX_EVIDENCE_DIR",
            "data/evidence",
            base_dir,
        ),
        exports_dir=_env_path(
            "SYNTHESIX_EXPORTS_DIR",
            "data/exports",
            base_dir,
        ),
        history_dir=history_dir,
        history_json_path=history_dir / "history.json",
        history_report_path=history_report_path,
        robot_challenges_dir=history_dir / "robot_challenges",
        debug_html=_env_bool("SYNTHESIX_DEBUG_HTML"),
        debug_html_dir=_env_path(
            "SYNTHESIX_DEBUG_HTML_DIR",
            str(history_dir / "debug_pages"),
            base_dir,
        ),
        browser_profile_dir=browser_profile_dir,
        browser_type=_env_str("SYNTHESIX_BROWSER", "auto"),
        browser_executable_path=_env_optional_path("SYNTHESIX_BROWSER_EXECUTABLE_PATH", base_dir),
        browser_connection_timeout=_env_float("SYNTHESIX_BROWSER_CONNECTION_TIMEOUT", 0.25),
        browser_connection_max_tries=_env_int("SYNTHESIX_BROWSER_CONNECTION_MAX_TRIES", 10),
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
        duckduckgo_results_timeout=_env_float(
            "SYNTHESIX_DUCKDUCKGO_RESULTS_TIMEOUT",
            10.0,
        ),
        duckduckgo_robot_timeout=_env_float("SYNTHESIX_DUCKDUCKGO_ROBOT_TIMEOUT", 75.0),
        duckduckgo_robot_interval=_env_float("SYNTHESIX_DUCKDUCKGO_ROBOT_INTERVAL", 0.5),
        engine_search_timeout=_env_float("SYNTHESIX_ENGINE_SEARCH_TIMEOUT", 90.0),
        engine_concurrency=_env_int("SYNTHESIX_ENGINE_CONCURRENCY", len(ENGINE_NAMES)),
        engine_retry_attempts=_env_int("SYNTHESIX_ENGINE_RETRY_ATTEMPTS", 1),
        engine_retry_delay=_env_float("SYNTHESIX_ENGINE_RETRY_DELAY", 0.5),
        engine_retry_backoff=_env_float("SYNTHESIX_ENGINE_RETRY_BACKOFF", 2.0),
        max_query_variants=max(1, _env_int("SYNTHESIX_MAX_QUERY_VARIANTS", 6)),
    )
