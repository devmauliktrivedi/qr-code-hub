from __future__ import annotations

import streamlit as st


DEFAULT_SESSION_STATE = {
    "user": None,
    "session_id": None,
    "page": "Home",
    "cookie_manager_initialized": False,
    "cookies": None,
    "pending_cookie_token": None,
    "pending_cookie_clear": False,
}


def initialize_session_state() -> None:
    for key, value in DEFAULT_SESSION_STATE.items():
        st.session_state.setdefault(key, value)


def clear_qr_preview_state(user_id: int | str | None = None) -> None:
    removable_keys = [
        "qr_img_gen",
        "qr_text_gen",
        "qr_img_guest",
        "qr_text_guest",
    ]
    for key in removable_keys:
        st.session_state.pop(key, None)

    if user_id is None:
        prefixes = ("qr_img_", "qr_text_", "text_", "fg_", "bg_", "style_", "box_", "border_")
        for key in list(st.session_state.keys()):
            if key.startswith(prefixes):
                st.session_state.pop(key, None)
        return

    user_text = str(user_id)
    for key in list(st.session_state.keys()):
        if user_text in key and key.startswith(
            ("qr_img_", "qr_text_", "text_", "fg_", "bg_", "style_", "box_", "border_")
        ):
            st.session_state.pop(key, None)
