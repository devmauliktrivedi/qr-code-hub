from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from qr_app.config import settings
from qr_app.constants import AVATAR_MAP
from qr_app.utils import get_initials, time_ago


def navigate_to(page_name: str) -> None:
    st.session_state.page = page_name
    st.rerun()


def resolve_avatar_path(relative_path: str) -> Path:
    return settings.app_dir / relative_path


def render_sidebar_navigation(current_page: str, authenticated: bool, can_access_admin: bool = False) -> str:
    st.sidebar.markdown("<h1>QR Code Hub</h1>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    if authenticated:
        pages = ["Home", "QR Generator", "My QR Codes", "Feedback", "My Account", "Logout"]
        if can_access_admin:
            pages.insert(-1, "Admin")
    else:
        pages = ["Home", "Quick QR Code", "Feedback", "Login", "Sign Up"]

    selected_page = current_page if current_page in pages else "Home"
    selected_index = pages.index(selected_page)
    return st.sidebar.radio(
        "Navigation",
        pages,
        index=selected_index,
        label_visibility="collapsed",
    )


def render_avatar_selector(key_prefix: str = "signup") -> None:
    selected_key = f"{key_prefix}_selected_avatar"
    changed_key = f"{key_prefix}_avatar_explicitly_selected"
    st.session_state.setdefault(selected_key, AVATAR_MAP["Boy"])
    st.session_state.setdefault(changed_key, False)

    st.subheader("Choose an Avatar")
    columns = st.columns(6)

    for index, (name, relative_path) in enumerate(AVATAR_MAP.items()):
        with columns[index % 6]:
            avatar_path = resolve_avatar_path(relative_path)
            if avatar_path.exists():
                st.image(str(avatar_path), width=80)
            if st.button("Select", key=f"{key_prefix}_select_avatar_{name}", use_container_width=True):
                st.session_state[selected_key] = relative_path
                st.session_state[changed_key] = True
                st.toast("Avatar selected.")

    st.markdown("---")
    st.markdown("**Selected Avatar**")
    st.image(str(resolve_avatar_path(st.session_state[selected_key])), width=100)
    st.markdown("---")


def render_feedback_card(comment: dict, is_owner: bool = False) -> None:
    username = comment.get("username") or "Community Member"
    safe_username = html.escape(username)
    safe_time = html.escape(time_ago(comment.get("created_at")))
    safe_text = html.escape(comment.get("comment_text") or "").replace("\n", "<br>")
    owner_badge = "<span class='feedback-owner-badge'>Your feedback</span>" if is_owner else ""

    with st.container(border=True):
        avatar_col, content_col = st.columns([0.14, 0.86], gap="small")

        with avatar_col:
            if comment.get("profile_image"):
                st.image(comment["profile_image"], width=56)
            else:
                initials = html.escape(get_initials(username))
                st.markdown(
                    f"<div class='feedback-avatar-fallback'>{initials}</div>",
                    unsafe_allow_html=True,
                )

        with content_col:
            st.markdown(
                f"""
                <div class="feedback-meta">
                    <span class="feedback-author">{safe_username}</span>
                    <span class="feedback-time">{safe_time}</span>
                    {owner_badge}
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='feedback-text'>{safe_text}</div>",
                unsafe_allow_html=True,
            )
