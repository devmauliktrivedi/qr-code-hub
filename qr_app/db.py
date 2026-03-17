from __future__ import annotations

import sqlite3
from contextlib import contextmanager

from qr_app.config import ensure_runtime_dirs, settings


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(settings.database_path, timeout=30, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def initialize_database() -> None:
    ensure_runtime_dirs()
    sql_files = sorted(settings.sql_dir.glob("*.sql"))
    if not sql_files:
        return

    with _connect() as connection:
        connection.execute("PRAGMA journal_mode = WAL;")
        connection.execute("PRAGMA synchronous = NORMAL;")
        for sql_file in sql_files:
            connection.executescript(sql_file.read_text(encoding="utf-8"))
        connection.commit()


@contextmanager
def get_db_connection() -> sqlite3.Connection:
    connection = _connect()
    try:
        yield connection
    finally:
        connection.close()


def row_to_dict(row: sqlite3.Row | None) -> dict | None:
    return dict(row) if row is not None else None


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict]:
    return [dict(row) for row in rows]
