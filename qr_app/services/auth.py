from __future__ import annotations

from pathlib import Path

import streamlit as st
from streamlit_cookies_manager import CookieManager

from qr_app.config import settings
from qr_app.constants import AVATAR_MAP
from qr_app.db import get_db_connection, row_to_dict
from qr_app.security import check_password_strength, generate_session_token, hash_password, verify_password
from qr_app.state import clear_qr_preview_state


def init_cookie_manager() -> CookieManager | None:
    if st.session_state.cookie_manager_initialized and st.session_state.cookies is not None:
        try:
            if st.session_state.cookies.ready():
                return st.session_state.cookies
        except Exception:
            pass

    try:
        cookies = CookieManager(prefix=settings.cookie_prefix)
    except Exception:
        return None

    st.session_state.cookies = cookies
    st.session_state.cookie_manager_initialized = True
    return cookies


def _sync_cookie_state() -> None:
    cookies = init_cookie_manager()
    if cookies is None:
        return

    try:
        if not cookies.ready():
            return
    except Exception:
        return

    pending_token = st.session_state.get("pending_cookie_token")
    should_clear = bool(st.session_state.get("pending_cookie_clear"))

    try:
        if pending_token:
            cookies["qr_token"] = pending_token
            cookies.save()
            st.session_state.pending_cookie_token = None
            st.session_state.pending_cookie_clear = False
        elif should_clear:
            cookies["qr_token"] = ""
            cookies.save()
            st.session_state.pending_cookie_clear = False
    except Exception:
        return


def _set_cookie_token(token: str) -> None:
    st.session_state.pending_cookie_token = token
    st.session_state.pending_cookie_clear = False
    _sync_cookie_state()


def _clear_cookie_token() -> None:
    st.session_state.pending_cookie_token = None
    st.session_state.pending_cookie_clear = True
    _sync_cookie_state()


def _get_request_cookie_token() -> str | None:
    try:
        cookie_store = getattr(st, "context").cookies
    except Exception:
        return None

    cookie_name = f"{settings.cookie_prefix}qr_token"
    token = cookie_store.get(cookie_name)
    if token:
        return str(token)
    return None


def load_avatar_bytes(avatar_relative_path: str | None) -> bytes | None:
    if not avatar_relative_path:
        avatar_relative_path = AVATAR_MAP["Boy"]
    avatar_path = settings.app_dir / Path(avatar_relative_path)
    if not avatar_path.exists():
        return None
    return avatar_path.read_bytes()


def create_user(username: str, password: str, profile_image: bytes | None) -> tuple[bool, str]:
    cleaned_username = username.strip()
    if not cleaned_username or not password:
        return False, "Username and password are required."

    strength_percent, _ = check_password_strength(password)
    if strength_percent < 75:
        return False, "Password is too weak. Use 8+ characters, a number, an uppercase letter, and a symbol."

    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (cleaned_username,))
        if cursor.fetchone():
            return False, f"Username '{cleaned_username}' already exists."

        cursor.execute(
            """
            INSERT INTO users (username, password_hash, profile_image)
            VALUES (?, ?, ?)
            """,
            (cleaned_username, hash_password(password), profile_image),
        )
        connection.commit()
    return True, "Account created successfully. Please log in."


def login_user(username: str, password: str) -> tuple[bool, str]:
    cleaned_username = username.strip()
    if not cleaned_username or not password:
        return False, "Please enter username and password."

    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (cleaned_username,))
        user_row = cursor.fetchone()
        user = row_to_dict(user_row)
        if not user or not verify_password(password, user["password_hash"]):
            return False, "Incorrect username or password."

        token = generate_session_token()
        cursor.execute(
            """
            INSERT INTO sessions (user_id, token)
            VALUES (?, ?)
            """,
            (user["id"], token),
        )
        session_id = cursor.lastrowid
        connection.commit()

    st.session_state.user = user
    st.session_state.session_id = session_id
    clear_qr_preview_state()
    _set_cookie_token(token)
    return True, f"Welcome back, {user['username']}!"


def try_auto_login() -> bool:
    _sync_cookie_state()

    if st.session_state.get("user"):
        return True

    token = _get_request_cookie_token()
    if not token:
        cookies = init_cookie_manager()
        if cookies is None:
            return True
        try:
            if cookies.ready():
                token = cookies.get("qr_token")
        except Exception:
            token = None

    if not token:
        return True

    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT u.*, s.id AS session_id
            FROM sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token = ?
              AND s.logout_time IS NULL
            LIMIT 1
            """,
            (token,),
        )
        row = cursor.fetchone()
        if row is None:
            return True

    payload = dict(row)
    st.session_state.user = {key: value for key, value in payload.items() if key != "session_id"}
    st.session_state.session_id = payload["session_id"]
    return True


def logout_user() -> None:
    session_id = st.session_state.get("session_id")
    if session_id:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE sessions
                SET logout_time = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (session_id,),
            )
            connection.commit()

    _clear_cookie_token()
    clear_qr_preview_state()
    st.session_state.user = None
    st.session_state.session_id = None
    st.session_state.page = "Home"
    st.success("Logged out successfully!")
    st.rerun()


def update_profile(
    user_id: int,
    new_username: str,
    new_password: str,
    new_profile_bytes: bytes | None,
) -> tuple[bool, str]:
    cleaned_username = new_username.strip()
    if not cleaned_username:
        return False, "Username cannot be empty."

    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        current_user = row_to_dict(cursor.fetchone())
        if current_user is None:
            return False, "User not found."

        cursor.execute(
            "SELECT id FROM users WHERE username = ? AND id <> ?",
            (cleaned_username, user_id),
        )
        if cursor.fetchone():
            return False, "Username already taken."

        password_hash = current_user["password_hash"]
        if new_password.strip():
            strength_percent, _ = check_password_strength(new_password)
            if strength_percent < 75:
                return False, "New password is too weak."
            password_hash = hash_password(new_password)

        cursor.execute(
            """
            UPDATE users
            SET username = ?, password_hash = ?, profile_image = ?
            WHERE id = ?
            """,
            (
                cleaned_username,
                password_hash,
                new_profile_bytes,
                user_id,
            ),
        )
        connection.commit()

        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        refreshed_user = row_to_dict(cursor.fetchone())

    st.session_state.user = refreshed_user
    return True, "Profile updated successfully."
