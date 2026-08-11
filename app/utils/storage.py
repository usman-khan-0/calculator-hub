"""Local SQLite persistence for calculation history and app settings.

Designed to work fully offline. On Android, the database file lives in
the app's private storage directory (resolved via ``App.user_data_dir``
by the caller); for local/desktop runs it defaults to the current
working directory.
"""

from __future__ import annotations

import datetime as _dt
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

DEFAULT_DB_NAME = "calculator_hub.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    calculator_type TEXT NOT NULL,
    expression TEXT NOT NULL,
    result TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


@dataclass
class HistoryRecord:
    id: int
    calculator_type: str
    expression: str
    result: str
    created_at: str


class Storage:
    """Thin wrapper around a SQLite database for history + settings."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        path = db_path or DEFAULT_DB_NAME
        Path(path).parent.mkdir(parents=True, exist_ok=True) if Path(path).parent != Path("") else None
        self._path = path
        self._conn = sqlite3.connect(self._path)
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    # -- history -------------------------------------------------------
    def add_history(self, calculator_type: str, expression: str, result: str) -> int:
        timestamp = _dt.datetime.now().isoformat(timespec="seconds")
        cursor = self._conn.execute(
            "INSERT INTO history (calculator_type, expression, result, created_at) VALUES (?, ?, ?, ?)",
            (calculator_type, expression, result, timestamp),
        )
        self._conn.commit()
        return cursor.lastrowid

    def get_history(self, calculator_type: Optional[str] = None, limit: int = 200) -> List[HistoryRecord]:
        if calculator_type:
            rows = self._conn.execute(
                "SELECT id, calculator_type, expression, result, created_at FROM history "
                "WHERE calculator_type = ? ORDER BY id DESC LIMIT ?",
                (calculator_type, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT id, calculator_type, expression, result, created_at FROM history "
                "ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [HistoryRecord(*row) for row in rows]

    def delete_history_entry(self, entry_id: int) -> None:
        self._conn.execute("DELETE FROM history WHERE id = ?", (entry_id,))
        self._conn.commit()

    def clear_history(self, calculator_type: Optional[str] = None) -> None:
        if calculator_type:
            self._conn.execute("DELETE FROM history WHERE calculator_type = ?", (calculator_type,))
        else:
            self._conn.execute("DELETE FROM history")
        self._conn.commit()

    # -- settings --------------------------------------------------------
    def set_setting(self, key: str, value: str) -> None:
        self._conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        self._conn.commit()

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        row = self._conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row[0] if row else default


__all__ = ["Storage", "HistoryRecord", "DEFAULT_DB_NAME"]
