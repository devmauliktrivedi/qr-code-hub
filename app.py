from __future__ import annotations

import streamlit as st

from qr_app.config import settings
from qr_app.db import initialize_database
from qr_app.services.admin import is_admin_user
from qr_app.state import initialize_session_state
from qr_app.ui.components import render_sidebar_navigation
from qr_app.ui.admin import render_admin_page
from qr_app.ui.pages import (
    render_account_page,
    render_feedback_page,
    render_home_page,
    render_login_page,
    render_qr_page,
    render_saved_qrs_page,
    render_signup_page,
)
from qr_app.ui.styles import inject_global_styles
from qr_app.services.auth import init_cookie_manager, logout_user, try_auto_login


st.set_page_config(
    page_title=settings.app_name,
    page_icon=settings.page_icon,
    layout="wide",
)


def main() -> None:
    initialize_database()
    initialize_session_state()
    inject_global_styles()

    cookies = init_cookie_manager()
    if cookies is not None:
        try:
            if not cookies.ready():
                st.caption("Preparing your session...")
                st.stop()
        except Exception:
            pass

    if settings.using_default_secret:
        st.sidebar.caption("Set a real `SECRET_KEY` before deploying.")

    try_auto_login()
    can_access_admin = is_admin_user(st.session_state.user)

    selected_page = render_sidebar_navigation(
        current_page=st.session_state.page,
        authenticated=st.session_state.user is not None,
        can_access_admin=can_access_admin,
    )

    if selected_page != st.session_state.page:
        st.session_state.page = selected_page
        st.rerun()

    if st.session_state.page == "Home":
        render_home_page()
    elif st.session_state.page == "Sign Up":
        render_signup_page()
    elif st.session_state.page == "Login":
        render_login_page()
    elif st.session_state.page == "Logout":
        logout_user()
    elif st.session_state.page == "QR Generator" and st.session_state.user:
        render_qr_page("gen", simple=False)
    elif st.session_state.page == "Quick QR Code":
        render_qr_page("guest", simple=True)
    elif st.session_state.page == "Feedback":
        render_feedback_page()
    elif st.session_state.page == "My Account" and st.session_state.user:
        render_account_page()
    elif st.session_state.page == "My QR Codes" and st.session_state.user:
        render_saved_qrs_page()
    elif st.session_state.page == "Admin" and can_access_admin:
        render_admin_page()
    else:
        if st.session_state.page == "Admin" and st.session_state.user:
            st.error("You do not have permission to access the admin panel.")
            render_home_page()
        elif st.session_state.page in {"My Account", "My QR Codes", "QR Generator", "Admin"}:
            st.warning("You must be logged in to access this page.")
            render_login_page()
        else:
            render_home_page()


if __name__ == "__main__":
    main()
