from __future__ import annotations

import sqlite3
from typing import Any

import streamlit as st

from qr_app.config import settings
from qr_app.db import get_db_connection, row_to_dict, rows_to_dicts
from qr_app.security import hash_password
from qr_app.services.comments import load_comments
from qr_app.services.qr_codes import load_user_qrs


SYSTEM_TABLE_PREFIX = "sqlite_"
READ_ONLY_GENERIC_COLUMNS = {"password_hash", "profile_image"}


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _table_exists(table_name: str) -> bool:
    return table_name in list_table_names(include_internal=True)


def _invalidate_app_caches() -> None:
    load_comments.clear()
    load_user_qrs.clear()


def _serialize_value(value: Any) -> Any:
    if isinstance(value, bytes):
        kilobytes = len(value) / 1024
        return f"<BLOB {kilobytes:.1f} KB>"
    return value


def _serialize_rows(rows: list[dict]) -> list[dict]:
    return [{key: _serialize_value(value) for key, value in row.items()} for row in rows]


def is_admin_user(user: dict | None) -> bool:
    if not user:
        return False
    username = str(user.get("username", "")).strip().lower()
    return username in settings.admin_usernames


def admin_access_mode_message() -> str | None:
    configured = ", ".join(settings.admin_usernames)
    return f"Admin access is restricted to configured usernames: {configured}"


def get_dashboard_metrics() -> dict[str, int]:
    metrics: dict[str, int] = {}
    with get_db_connection() as connection:
        cursor = connection.cursor()
        for table_name in ("users", "qr_codes", "comments", "sessions"):
            cursor.execute(f"SELECT COUNT(*) AS total FROM {_quote_identifier(table_name)}")
            metrics[table_name] = int(cursor.fetchone()["total"])
        cursor.execute("SELECT COUNT(*) AS total FROM sessions WHERE logout_time IS NULL")
        metrics["active_sessions"] = int(cursor.fetchone()["total"])
        cursor.execute("SELECT COUNT(*) AS total FROM qr_codes WHERE deleted_at IS NULL")
        metrics["active_qr_codes"] = int(cursor.fetchone()["total"])
    return metrics


def list_users() -> list[dict]:
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                u.id,
                u.username,
                u.created_at,
                LENGTH(u.profile_image) AS profile_image_bytes,
                (
                    SELECT COUNT(*)
                    FROM qr_codes q
                    WHERE q.user_id = u.id
                ) AS qr_count,
                (
                    SELECT COUNT(*)
                    FROM comments c
                    WHERE c.user_id = u.id
                ) AS comment_count
            FROM users u
            ORDER BY datetime(u.created_at) DESC, u.id DESC
            """
        )
        return rows_to_dicts(cursor.fetchall())


def get_user_by_id(user_id: int) -> dict | None:
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return row_to_dict(cursor.fetchone())


def admin_update_user(
    user_id: int,
    username: str,
    new_password: str = "",
    profile_image: bytes | None = None,
    clear_avatar: bool = False,
) -> tuple[bool, str]:
    cleaned_username = username.strip()
    if not cleaned_username:
        return False, "Username cannot be empty."

    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = row_to_dict(cursor.fetchone())
        if user is None:
            return False, "User not found."

        cursor.execute(
            "SELECT id FROM users WHERE username = ? AND id <> ?",
            (cleaned_username, user_id),
        )
        if cursor.fetchone():
            return False, "Username already taken."

        password_hash = user["password_hash"]
        if new_password.strip():
            password_hash = hash_password(new_password.strip())

        next_profile_image = user["profile_image"]
        if clear_avatar:
            next_profile_image = None
        elif profile_image is not None:
            next_profile_image = profile_image

        cursor.execute(
            """
            UPDATE users
            SET username = ?, password_hash = ?, profile_image = ?
            WHERE id = ?
            """,
            (cleaned_username, password_hash, next_profile_image, user_id),
        )
        connection.commit()

    if st.session_state.get("user", {}).get("id") == user_id:
        refreshed_user = get_user_by_id(user_id)
        if refreshed_user is not None:
            st.session_state.user = refreshed_user

    _invalidate_app_caches()
    return True, "User updated successfully."


def admin_delete_user(user_id: int) -> tuple[bool, str]:
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        connection.commit()
        if cursor.rowcount == 0:
            return False, "User not found."

    _invalidate_app_caches()
    return True, "User deleted successfully."


def list_qr_codes(limit: int = 200) -> list[dict]:
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                q.id,
                q.user_id,
                u.username,
                q.qr_text,
                q.fg_color_name,
                q.bg_color_name,
                q.qr_style,
                q.box_size,
                q.border,
                q.created_at,
                q.deleted_at
            FROM qr_codes q
            JOIN users u ON u.id = q.user_id
            ORDER BY datetime(q.created_at) DESC, q.id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return rows_to_dicts(cursor.fetchall())


def get_qr_code_by_id(qr_id: int) -> dict | None:
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT q.*, u.username
            FROM qr_codes q
            JOIN users u ON u.id = q.user_id
            WHERE q.id = ?
            """,
            (qr_id,),
        )
        return row_to_dict(cursor.fetchone())


def admin_update_qr_code(
    qr_id: int,
    qr_text: str,
    fg_color_name: str,
    bg_color_name: str,
    qr_style: str,
    box_size: int,
    border: int,
) -> tuple[bool, str]:
    if not qr_text.strip():
        return False, "QR text cannot be empty."

    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE qr_codes
            SET qr_text = ?, fg_color_name = ?, bg_color_name = ?, qr_style = ?, box_size = ?, border = ?
            WHERE id = ?
            """,
            (qr_text.strip(), fg_color_name, bg_color_name, qr_style, int(box_size), int(border), qr_id),
        )
        connection.commit()
        if cursor.rowcount == 0:
            return False, "QR record not found."

    _invalidate_app_caches()
    return True, "QR record updated."


def set_qr_deleted_state(qr_id: int, deleted: bool) -> tuple[bool, str]:
    statement = (
        "UPDATE qr_codes SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?"
        if deleted
        else "UPDATE qr_codes SET deleted_at = NULL WHERE id = ?"
    )
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(statement, (qr_id,))
        connection.commit()
        if cursor.rowcount == 0:
            return False, "QR record not found."

    _invalidate_app_caches()
    return True, "QR status updated."


def admin_delete_qr_code(qr_id: int) -> tuple[bool, str]:
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM qr_codes WHERE id = ?", (qr_id,))
        connection.commit()
        if cursor.rowcount == 0:
            return False, "QR record not found."

    _invalidate_app_caches()
    return True, "QR record deleted permanently."


def list_comments_for_admin(limit: int = 200) -> list[dict]:
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                c.id,
                c.user_id,
                u.username,
                c.comment_text,
                c.created_at
            FROM comments c
            JOIN users u ON u.id = c.user_id
            ORDER BY datetime(c.created_at) DESC, c.id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return rows_to_dicts(cursor.fetchall())


def get_comment_by_id(comment_id: int) -> dict | None:
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                c.id,
                c.user_id,
                u.username,
                c.comment_text,
                c.created_at
            FROM comments c
            JOIN users u ON u.id = c.user_id
            WHERE c.id = ?
            """,
            (comment_id,),
        )
        return row_to_dict(cursor.fetchone())


def admin_update_comment(comment_id: int, comment_text: str) -> tuple[bool, str]:
    if not comment_text.strip():
        return False, "Comment text cannot be empty."

    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE comments SET comment_text = ? WHERE id = ?",
            (comment_text.strip(), comment_id),
        )
        connection.commit()
        if cursor.rowcount == 0:
            return False, "Comment not found."

    _invalidate_app_caches()
    return True, "Comment updated."


def admin_delete_comment(comment_id: int) -> tuple[bool, str]:
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
        connection.commit()
        if cursor.rowcount == 0:
            return False, "Comment not found."

    _invalidate_app_caches()
    return True, "Comment deleted."


def list_sessions(limit: int = 200) -> list[dict]:
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                s.id,
                s.user_id,
                u.username,
                s.token,
                s.login_time,
                s.logout_time
            FROM sessions s
            JOIN users u ON u.id = s.user_id
            ORDER BY datetime(s.login_time) DESC, s.id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return rows_to_dicts(cursor.fetchall())


def revoke_session(session_id: int) -> tuple[bool, str]:
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE sessions
            SET logout_time = COALESCE(logout_time, CURRENT_TIMESTAMP)
            WHERE id = ?
            """,
            (session_id,),
        )
        connection.commit()
        if cursor.rowcount == 0:
            return False, "Session not found."

    return True, "Session revoked."


def delete_session_record(session_id: int) -> tuple[bool, str]:
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        connection.commit()
        if cursor.rowcount == 0:
            return False, "Session not found."

    return True, "Session deleted."


def list_table_names(include_internal: bool = False) -> list[str]:
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
            """
        )
        table_names = [row["name"] for row in cursor.fetchall()]
    if include_internal:
        return table_names
    return [name for name in table_names if not name.startswith(SYSTEM_TABLE_PREFIX)]


def get_table_schema(table_name: str) -> list[dict]:
    if not _table_exists(table_name):
        return []
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(f"PRAGMA table_info({_quote_identifier(table_name)})")
        return rows_to_dicts(cursor.fetchall())


def get_primary_key_column(table_name: str) -> str | None:
    for column in get_table_schema(table_name):
        if column.get("pk"):
            return str(column["name"])
    return None


def browse_table(table_name: str, limit: int = 200) -> list[dict]:
    if not _table_exists(table_name):
        return []
    limit = max(1, min(int(limit), 1000))
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {_quote_identifier(table_name)} LIMIT ?", (limit,))
        return rows_to_dicts(cursor.fetchall())


def browse_table_for_display(table_name: str, limit: int = 200) -> list[dict]:
    return _serialize_rows(browse_table(table_name, limit=limit))


def get_row_by_primary_key(table_name: str, row_id: Any) -> dict | None:
    primary_key = get_primary_key_column(table_name)
    if not primary_key:
        return None
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            f"SELECT * FROM {_quote_identifier(table_name)} WHERE {_quote_identifier(primary_key)} = ?",
            (row_id,),
        )
        return row_to_dict(cursor.fetchone())


def update_row_by_primary_key(
    table_name: str,
    row_id: Any,
    updates: dict[str, Any],
) -> tuple[bool, str]:
    primary_key = get_primary_key_column(table_name)
    if not primary_key:
        return False, "This table has no primary key."
    if not updates:
        return False, "No changes to save."

    schema = {column["name"]: column for column in get_table_schema(table_name)}
    filtered_updates = {}
    for column_name, value in updates.items():
        if column_name == primary_key or column_name in READ_ONLY_GENERIC_COLUMNS:
            continue
        if column_name not in schema:
            continue
        filtered_updates[column_name] = value

    if not filtered_updates:
        return False, "No editable changes were detected."

    assignments = ", ".join(f"{_quote_identifier(column)} = ?" for column in filtered_updates)
    parameters = list(filtered_updates.values()) + [row_id]

    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            f"""
            UPDATE {_quote_identifier(table_name)}
            SET {assignments}
            WHERE {_quote_identifier(primary_key)} = ?
            """,
            parameters,
        )
        connection.commit()
        if cursor.rowcount == 0:
            return False, "Row not found."

    _invalidate_app_caches()
    if table_name == "users" and st.session_state.get("user", {}).get("id") == row_id:
        refreshed_user = get_user_by_id(int(row_id))
        if refreshed_user is not None:
            st.session_state.user = refreshed_user
    return True, "Row updated successfully."


def delete_row_by_primary_key(table_name: str, row_id: Any) -> tuple[bool, str]:
    primary_key = get_primary_key_column(table_name)
    if not primary_key:
        return False, "This table has no primary key."
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            f"DELETE FROM {_quote_identifier(table_name)} WHERE {_quote_identifier(primary_key)} = ?",
            (row_id,),
        )
        connection.commit()
        if cursor.rowcount == 0:
            return False, "Row not found."

    _invalidate_app_caches()
    return True, "Row deleted successfully."


def execute_sql_query(query: str) -> tuple[bool, str, list[dict] | None]:
    cleaned_query = query.strip().rstrip(";")
    if not cleaned_query:
        return False, "Write a SQL statement first.", None
    if cleaned_query.count(";") > 0:
        return False, "Run one SQL statement at a time in this panel.", None

    command = cleaned_query.split(None, 1)[0].upper()
    read_only_commands = {"SELECT", "PRAGMA", "WITH", "EXPLAIN"}

    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(cleaned_query)
            if command in read_only_commands or cursor.description is not None:
                rows = rows_to_dicts(cursor.fetchall())
                return True, f"Query executed. {len(rows)} row(s) returned.", _serialize_rows(rows)

            connection.commit()
            _invalidate_app_caches()
            return True, f"Statement executed successfully. {cursor.rowcount} row(s) affected.", None
    except sqlite3.Error as exc:
        return False, f"SQL error: {exc}", None
