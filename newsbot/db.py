from __future__ import annotations

import sqlite3
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS seen (
    url TEXT PRIMARY KEY,
    title TEXT NOT NULL DEFAULT '',
    category TEXT NOT NULL DEFAULT '',
    first_seen INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS kv (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


class Store:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def is_seen(self, url: str) -> bool:
        row = self._conn.execute("SELECT 1 FROM seen WHERE url = ?", (url,)).fetchone()
        return row is not None

    def mark_seen(self, url: str, title: str, category: str) -> None:
        self._conn.execute(
            """
            INSERT OR IGNORE INTO seen (url, title, category, first_seen)
            VALUES (?, ?, ?, ?)
            """,
            (url, title, category, int(time.time())),
        )
        self._conn.commit()

    def mark_many(self, items: list[tuple[str, str, str]]) -> None:
        now = int(time.time())
        self._conn.executemany(
            """
            INSERT OR IGNORE INTO seen (url, title, category, first_seen)
            VALUES (?, ?, ?, ?)
            """,
            [(url, title, category, now) for url, title, category in items],
        )
        self._conn.commit()

    def get_kv(self, key: str) -> str | None:
        row = self._conn.execute("SELECT value FROM kv WHERE key = ?", (key,)).fetchone()
        return None if row is None else str(row["value"])

    def set_kv(self, key: str, value: str) -> None:
        self._conn.execute(
            "INSERT INTO kv(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        self._conn.commit()
