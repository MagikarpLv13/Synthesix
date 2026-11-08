"""Launch native persistent personas without attaching to their authenticated pages."""

from __future__ import annotations

import subprocess
from pathlib import Path
from urllib.parse import urlsplit

from app.storage import BrowserStore


def validate_web_url(value: str) -> str:
    if not isinstance(value, str) or len(value) > 8192 or any(ord(c) <= 32 for c in value) or "\\" in value:
        raise ValueError("Only valid HTTP or HTTPS addresses can be opened.")
    try:
        parts = urlsplit(value)
        if parts.scheme not in {"http", "https"} or not parts.hostname or parts.username is not None or parts.password is not None:
            raise ValueError
        _ = parts.port
    except ValueError as exc:
        raise ValueError("Only valid HTTP or HTTPS addresses can be opened.") from exc
    return value


class ProfileLauncher:
    def __init__(self, store: BrowserStore, executable: Path) -> None:
        self.store = store
        self.executable = executable

    def open(self, profile_id: str, url: str | None = None) -> None:
        target = validate_web_url(url) if url is not None else "about:blank"
        profile_path = self.store.profile_path(profile_id)
        profile_path.mkdir(exist_ok=True)
        # Chromium reuses the running instance for this exact user-data-dir.
        subprocess.Popen([str(self.executable), f"--user-data-dir={profile_path}", "--no-first-run", "--no-default-browser-check", "--new-window", target], close_fds=True)
