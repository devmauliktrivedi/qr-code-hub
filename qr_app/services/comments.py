from __future__ import annotations

import streamlit as st

from qr_app.db import get_db_connection, rows_to_dicts


@st.cache_data(ttl=60)
def load_comments() -> list[dict]:
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                c.id,
                c.user_id,
                c.comment_text,
                c.created_at,
                u.username,
                u.profile_image
            FROM comments c
            JOIN users u ON u.id = c.user_id
            ORDER BY datetime(c.created_at) DESC, c.id DESC
            """
        )
        return rows_to_dicts(cursor.fetchall())


def create_comment(user_id: int, comment_text: str) -> tuple[bool, str]:
    cleaned_text = comment_text.strip()
    if not cleaned_text:
        return False, "Comment cannot be empty."

    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO comments (user_id, comment_text)
            VALUES (?, ?)
            """,
            (user_id, cleaned_text),
        )
        connection.commit()

    load_comments.clear()
    return True, "Feedback posted successfully."


def update_comment(comment_id: int, user_id: int, new_text: str) -> tuple[bool, str]:
    cleaned_text = new_text.strip()
    if not cleaned_text:
        return False, "Edited comment cannot be empty."

    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id FROM comments WHERE id = ? AND user_id = ?",
            (comment_id, user_id),
        )
        if cursor.fetchone() is None:
            return False, "You can edit only your own feedback."

        cursor.execute(
            """
            UPDATE comments
            SET comment_text = ?
            WHERE id = ? AND user_id = ?
            """,
            (cleaned_text, comment_id, user_id),
        )
        connection.commit()

    load_comments.clear()
    return True, "Feedback updated."


def delete_comment(comment_id: int, user_id: int) -> tuple[bool, str]:
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM comments WHERE id = ? AND user_id = ?",
            (comment_id, user_id),
        )
        connection.commit()
        if cursor.rowcount == 0:
            return False, "You can delete only your own feedback."

    load_comments.clear()
    return True, "Feedback deleted."
