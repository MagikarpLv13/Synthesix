import zendriver as uc
import os
import json
import logging
from pathlib import Path
import time
import uuid
from zendriver.core.config import Config

logger = logging.getLogger(__name__)


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

class HeadlessBrowserManager:
    def __init__(self):
        self.browser : uc.Browser = None
        self.profile_dir: str | None = None

    @classmethod
    async def create(cls, home_url: str | None = None):
        self = cls()
        custom_profile = os.path.join(os.getcwd(), "zendriver-profile")
        os.makedirs(custom_profile, exist_ok=True)
        self.profile_dir = custom_profile
        _mark_profile_exited_cleanly(custom_profile)
        if home_url:
            _ensure_synthesix_bookmark(custom_profile, home_url)

        config = Config()
        config.user_data_dir = custom_profile

        """⚠️ Headless mode is not working with Brave, instant flag as a robot 🤖.
        """
        # config.headless = True

        self.browser = await uc.start(config=config)
        return self

    async def get_driver(self):
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
