import json
import logging
import os
from pathlib import Path
import shlex
import shutil
import stat
import subprocess
import sys
import time
import uuid

import zendriver as uc
from zendriver import cdp
from zendriver.core.config import Config

from settings import AppSettings, get_settings

logger = logging.getLogger(__name__)

FLATPAK_BRAVE_APP_ID = "com.brave.Browser"
BROWSER_COMMANDS = {
    "chrome": (
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
        "chrome",
    ),
    "brave": (
        "brave-browser",
        "brave-browser-stable",
        "brave",
    ),
}
LINUX_BROWSER_PATHS = {
    "chrome": (
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/snap/bin/chromium",
    ),
    "brave": (
        "/usr/bin/brave-browser",
        "/usr/bin/brave-browser-stable",
        "/opt/brave.com/brave/brave-browser",
        "/snap/bin/brave",
    ),
}

BROWSER_PROFILE_DATA_PATHS = (
    "Default/History",
    "Default/History-journal",
    "Default/Visited Links",
    "Default/Top Sites",
    "Default/Top Sites-journal",
    "Default/Shortcuts",
    "Default/Shortcuts-journal",
    "Default/Favicons",
    "Default/Favicons-journal",
    "Default/Cookies",
    "Default/Cookies-journal",
    "Default/Network/Cookies",
    "Default/Network/Cookies-journal",
    "Default/Cache",
    "Default/Code Cache",
    "Default/GPUCache",
    "Default/Service Worker",
    "Default/Local Storage",
    "Default/Session Storage",
    "Default/IndexedDB",
    "Default/Storage",
    "Default/databases",
    "Default/CacheStorage",
    "Default/SharedStorage",
    "Default/Shared Dictionary",
    "Default/Sessions",
)


def _browser_types_to_try(browser_type: str) -> tuple[str, ...]:
    normalized = browser_type.strip().lower()
    if normalized == "auto":
        return ("chrome", "brave")
    if normalized in BROWSER_COMMANDS:
        return (normalized,)
    return ()


def _find_native_browser_executable(browser_type: str) -> Path | None:
    for candidate_type in _browser_types_to_try(browser_type):
        for command in BROWSER_COMMANDS[candidate_type]:
            executable = shutil.which(command)
            if executable:
                return Path(executable)

        if sys.platform.startswith("linux"):
            for candidate in LINUX_BROWSER_PATHS[candidate_type]:
                path = Path(candidate)
                if path.is_file() and os.access(path, os.X_OK):
                    return path

    return None


def _flatpak_brave_is_installed(flatpak_executable: str) -> bool:
    try:
        result = subprocess.run(
            [flatpak_executable, "info", FLATPAK_BRAVE_APP_ID],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=3,
        )
    except (OSError, subprocess.TimeoutExpired):
        logger.debug("Unable to inspect the Brave Flatpak installation", exc_info=True)
        return False
    return result.returncode == 0


def _ensure_flatpak_brave_wrapper(settings: AppSettings, flatpak_executable: str) -> Path | None:
    wrapper_path = settings.base_dir / ".cache" / "synthesix" / "brave-flatpak"
    wrapper_content = (
        "#!/bin/sh\n"
        f"exec {shlex.quote(flatpak_executable)} run {FLATPAK_BRAVE_APP_ID} \"$@\"\n"
    )

    try:
        wrapper_path.parent.mkdir(parents=True, exist_ok=True)
        if not wrapper_path.exists() or wrapper_path.read_text(encoding="utf-8") != wrapper_content:
            wrapper_path.write_text(wrapper_content, encoding="utf-8", newline="\n")
        wrapper_path.chmod(
            wrapper_path.stat().st_mode
            | stat.S_IXUSR
            | stat.S_IXGRP
            | stat.S_IXOTH
        )
    except OSError:
        logger.warning("Unable to create the Brave Flatpak launcher: %s", wrapper_path, exc_info=True)
        return None

    return wrapper_path


def _resolve_browser_executable(settings: AppSettings) -> Path | None:
    if settings.browser_executable_path is not None:
        return settings.browser_executable_path

    executable = _find_native_browser_executable(settings.browser_type)
    if executable is not None:
        return executable

    if not sys.platform.startswith("linux"):
        return None
    if "brave" not in _browser_types_to_try(settings.browser_type):
        return None

    flatpak_executable = shutil.which("flatpak")
    if not flatpak_executable or not _flatpak_brave_is_installed(flatpak_executable):
        return None

    return _ensure_flatpak_brave_wrapper(settings, flatpak_executable)


def _update_json_file(path: Path, update_callback) -> None:
    if not path.exists():
        return

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        logger.debug("Unable to read Chrome profile state file: %s", path, exc_info=True)
        return

    update_callback(data)

    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f)
    except OSError:
        logger.debug("Unable to write Chrome profile state file: %s", path, exc_info=True)


def _mark_profile_exited_cleanly(profile_dir: str) -> None:
    profile_path = Path(profile_dir)

    def update_preferences(data: dict) -> None:
        profile = data.setdefault("profile", {})
        profile["exit_type"] = "Normal"
        profile["exited_cleanly"] = True
        bookmark_bar = data.setdefault("bookmark_bar", {})
        bookmark_bar["show_on_all_tabs"] = True

    def update_local_state(data: dict) -> None:
        data["exited_cleanly"] = True

    _update_json_file(profile_path / "Default" / "Preferences", update_preferences)
    _update_json_file(profile_path / "Local State", update_local_state)


def _clear_profile_browsing_data(profile_dir: str) -> int:
    profile_root = Path(profile_dir).resolve()
    removed = 0

    for relative_path in BROWSER_PROFILE_DATA_PATHS:
        target = (profile_root / relative_path).resolve()
        try:
            target.relative_to(profile_root)
        except ValueError:
            logger.error("Refusing to remove browser data outside the profile: %s", target)
            continue

        try:
            if target.is_dir():
                shutil.rmtree(target)
                removed += 1
            elif target.is_file():
                target.unlink()
                removed += 1
        except OSError:
            logger.warning("Unable to remove browser profile data: %s", target, exc_info=True)

    return removed


def _chrome_timestamp() -> str:
    return str(int((time.time() + 11644473600) * 1000000))


def _bookmark_folder(name: str, folder_id: str) -> dict:
    now = _chrome_timestamp()
    return {
        "children": [],
        "date_added": now,
        "date_last_used": "0",
        "date_modified": now,
        "guid": str(uuid.uuid4()),
        "id": folder_id,
        "name": name,
        "type": "folder",
    }


def _max_bookmark_id(value) -> int:
    if isinstance(value, dict):
        current = int(value.get("id", 0)) if str(value.get("id", "")).isdigit() else 0
        child_max = max((_max_bookmark_id(child) for child in value.get("children", [])), default=0)
        return max(current, child_max)
    if isinstance(value, list):
        return max((_max_bookmark_id(item) for item in value), default=0)
    return 0


def _ensure_synthesix_bookmark(profile_dir: str, home_url: str) -> None:
    profile_path = Path(profile_dir)
    bookmarks_path = profile_path / "Default" / "Bookmarks"
    bookmarks_path.parent.mkdir(parents=True, exist_ok=True)

    if bookmarks_path.exists():
        try:
            with bookmarks_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            logger.debug("Unable to read Chrome bookmarks file: %s", bookmarks_path, exc_info=True)
            return
    else:
        data = {
            "roots": {
                "bookmark_bar": _bookmark_folder("Bookmarks bar", "1"),
                "other": _bookmark_folder("Other bookmarks", "2"),
                "synced": _bookmark_folder("Mobile bookmarks", "3"),
            },
            "version": 1,
        }

    roots = data.setdefault("roots", {})
    data.pop("checksum", None)
    bookmark_bar = roots.setdefault("bookmark_bar", _bookmark_folder("Bookmarks bar", "1"))
    children = bookmark_bar.setdefault("children", [])

    for child in children:
        if child.get("name") == "Synthesix Home" or child.get("url") == home_url:
            child["name"] = "Synthesix Home"
            child["url"] = home_url
            child["type"] = "url"
            break
    else:
        children.append(
            {
                "date_added": _chrome_timestamp(),
                "date_last_used": "0",
                "guid": str(uuid.uuid4()),
                "id": str(_max_bookmark_id(data) + 1),
                "name": "Synthesix Home",
                "type": "url",
                "url": home_url,
            }
        )

    try:
        with bookmarks_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=3)
    except OSError:
        logger.debug("Unable to write Chrome bookmarks file: %s", bookmarks_path, exc_info=True)


def _build_zendriver_config(settings: AppSettings) -> Config:
    browser_executable_path = _resolve_browser_executable(settings)
    if browser_executable_path is not None:
        logger.info("Using browser executable: %s", browser_executable_path)

    try:
        config = Config(
            browser=settings.browser_type.strip().lower(),
            browser_executable_path=(
                str(browser_executable_path)
                if browser_executable_path is not None
                else None
            ),
            browser_connection_timeout=settings.browser_connection_timeout,
            browser_connection_max_tries=settings.browser_connection_max_tries,
        )
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            "Synthesix could not find Chrome or Brave. Install a native, Snap, or "
            "Flatpak browser, or set SYNTHESIX_BROWSER_EXECUTABLE_PATH to the "
            "browser executable or an executable wrapper."
        ) from exc

    config.user_data_dir = str(settings.browser_profile_dir)
    return config


class HeadlessBrowserManager:
    def __init__(self):
        self.browser : uc.Browser = None
        self.profile_dir: str | None = None
        self.home_url: str | None = None
        self.settings: AppSettings | None = None

    @classmethod
    async def create(cls, home_url: str | None = None, settings: AppSettings | None = None):
        self = cls()
        settings = settings or get_settings()
        self.settings = settings
        self.home_url = home_url
        custom_profile = settings.browser_profile_dir
        os.makedirs(custom_profile, exist_ok=True)
        self.profile_dir = str(custom_profile)
        _mark_profile_exited_cleanly(str(custom_profile))
        if home_url:
            _ensure_synthesix_bookmark(str(custom_profile), home_url)

        config = _build_zendriver_config(settings)

        """⚠️ Headless mode is not working with Brave, instant flag as a robot 🤖.
        """
        # config.headless = True

        self.browser = await uc.start(config=config)
        return self

    async def get_driver(self):
        return self.browser

    async def _clear_live_browser_data(self) -> None:
        if self.browser is None:
            return

        try:
            await self.browser.cookies.clear()
        except Exception:
            logger.warning("Unable to clear live browser cookies", exc_info=True)

        connection = next(
            (tab for tab in self.browser.tabs if not getattr(tab, "closed", False)),
            self.browser.connection,
        )
        if connection is not None:
            try:
                await connection.send(cdp.network.clear_browser_cache())
            except Exception:
                logger.warning("Unable to clear live browser cache", exc_info=True)

    async def clear_browser_data(self):
        if self.settings is None or self.profile_dir is None:
            raise RuntimeError("Browser manager is not initialized.")

        await self._clear_live_browser_data()
        await self.stop()
        removed = _clear_profile_browsing_data(self.profile_dir)
        _mark_profile_exited_cleanly(self.profile_dir)
        if self.home_url:
            _ensure_synthesix_bookmark(self.profile_dir, self.home_url)

        config = _build_zendriver_config(self.settings)
        self.browser = await uc.start(config=config)
        logger.info("Browser profile data cleared (%s paths removed).", removed)
        return self.browser

    async def stop(self):
        try:
            if self.browser is not None:
                await self.browser.stop()
        except Exception:
            logger.warning("Unable to stop browser cleanly", exc_info=True)
        finally:
            self.browser = None
            if self.profile_dir:
                _mark_profile_exited_cleanly(self.profile_dir)
