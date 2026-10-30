"""Small independent store; never opens or migrates the investigation database."""

from __future__ import annotations

import json
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class BrowserStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.profiles_root = path.parent / "browser-profiles"
        path.parent.mkdir(parents=True, exist_ok=True)
        self.profiles_root.mkdir(exist_ok=True)
        with self._connect() as db:
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version not in {0, 1}:
                raise ValueError("Unsupported browser database version.")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id TEXT PRIMARY KEY, name TEXT NOT NULL,
                    name_key TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS searches (
                    id INTEGER PRIMARY KEY, created_at TEXT NOT NULL,
                    request TEXT NOT NULL, results TEXT NOT NULL,
                    coverage TEXT NOT NULL, errors TEXT NOT NULL
                );
                PRAGMA user_version = 1;
            """)

    @contextmanager
    def _connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def _name(name: str) -> str:
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 80 or any(ord(c) < 32 for c in name):
            raise ValueError("Enter a profile name of 1 to 80 characters.")
        return name.strip()

    def profiles(self) -> list[dict]:
        with self._connect() as db:
            return [dict(row) for row in db.execute("SELECT id, name FROM profiles ORDER BY created_at, id")]

    def create_profile(self, name: str) -> dict:
        name = self._name(name)
        profile = {"id": uuid4().hex, "name": name}
        try:
            with self._connect() as db:
                db.execute("INSERT INTO profiles VALUES (?, ?, ?, ?)", (profile["id"], name, name.casefold(), datetime.now(timezone.utc).isoformat()))
        except sqlite3.IntegrityError as exc:
            raise ValueError("A profile with this name already exists.") from exc
        return profile

    def rename_profile(self, profile_id: str, name: str) -> None:
        self.profile_path(profile_id)
        name = self._name(name)
        try:
            with self._connect() as db:
                db.execute("UPDATE profiles SET name = ?, name_key = ? WHERE id = ?", (name, name.casefold(), profile_id))
        except sqlite3.IntegrityError as exc:
            raise ValueError("A profile with this name already exists.") from exc

    def profile_path(self, profile_id: str) -> Path:
        if not isinstance(profile_id, str) or not re.fullmatch(r"[0-9a-f]{32}", profile_id):
            raise ValueError("Unknown browser profile.")
        with self._connect() as db:
            if not db.execute("SELECT 1 FROM profiles WHERE id = ?", (profile_id,)).fetchone():
                raise ValueError("Unknown browser profile.")
        root = self.profiles_root.resolve()
        path = (root / profile_id).resolve()
        if path.parent != root:
            raise ValueError("Invalid browser profile directory.")
        return path

    def save_search(self, request: dict, results: list[dict], coverage: list[dict], errors: dict) -> int:
        with self._connect() as db:
            cursor = db.execute("INSERT INTO searches (created_at, request, results, coverage, errors) VALUES (?, ?, ?, ?, ?)", (datetime.now(timezone.utc).isoformat(), *(json.dumps(item, ensure_ascii=False) for item in (request, results, coverage, errors))))
            return int(cursor.lastrowid)

    def history(self) -> list[dict]:
        with self._connect() as db:
            rows = db.execute("SELECT id, created_at, request, json_array_length(results) AS count FROM searches ORDER BY id DESC LIMIT 50")
            return [{**dict(row), "request": json.loads(row["request"])} for row in rows]

    def search(self, run_id: int) -> dict:
        if type(run_id) is not int or run_id < 1:
            raise ValueError("Unknown saved search.")
        with self._connect() as db:
            row = db.execute("SELECT * FROM searches WHERE id = ?", (run_id,)).fetchone()
        if row is None:
            raise ValueError("Unknown saved search.")
        return {**dict(row), **{key: json.loads(row[key]) for key in ("request", "results", "coverage", "errors")}}
