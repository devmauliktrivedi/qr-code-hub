from __future__ import annotations

from typing import Any

import streamlit as st

from qr_app.constants import PALETTE_DISPLAY, PALETTE_HEX, PALETTE_NAMES
from qr_app.services.admin import (
    READ_ONLY_GENERIC_COLUMNS,
    admin_access_mode_message,
    admin_delete_comment,
    admin_delete_qr_code,
    admin_delete_user,
    admin_update_comment,
    admin_update_qr_code,
    admin_update_user,
    browse_table_for_display,
    delete_row_by_primary_key,
    delete_session_record,
    execute_sql_query,
    get_comment_by_id,
    get_dashboard_metrics,
    get_primary_key_column,
    get_qr_code_by_id,
    get_row_by_primary_key,
    get_table_schema,
    get_user_by_id,
    is_admin_user,
    list_comments_for_admin,
    list_qr_codes,
    list_sessions,
    list_table_names,
    list_users,
    revoke_session,
    set_qr_deleted_state,
    update_row_by_primary_key,
)
from qr_app.services.qr_codes import generate_qr_image
from qr_app.ui.components import navigate_to


def _show_rows(rows: list[dict], height: int = 260) -> None:
    if not rows:
        st.info("No rows found.")
        return
    st.dataframe(rows, use_container_width=True, hide_index=True, height=height)


def _result_message(success: bool, message: str) -> None:
    if success:
        st.success(message)
    else:
        st.error(message)


def _resolve_color_index(color_name: str, fallback_name: str) -> int:
    try:
        return PALETTE_NAMES.index(color_name)
    except ValueError:
        return PALETTE_NAMES.index(fallback_name)


def _resolve_color_hex(color_name: str, fallback_name: str) -> str:
    return PALETTE_HEX[_resolve_color_index(color_name, fallback_name)]


def _render_section_intro(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="admin-panel">
            <span class="section-tag">Admin Workspace</span>
            <h3>{title}</h3>
            <p class="admin-note">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_overview_tab() -> None:
    metrics = get_dashboard_metrics()
    st.markdown(
        f"""
        <div class="admin-hero">
            <span class="section-tag">Control Center</span>
            <h2>Manage the full SQLite app from one place.</h2>
            <p>
                Use the tabs to browse rows, edit records without writing SQL, revoke sessions,
                and run direct SQLite queries when you need developer-level control.
            </p>
            <div class="admin-kpi-grid">
                <div class="admin-kpi">
                    <strong>{metrics['users']}</strong>
                    <span>Registered users</span>
                </div>
                <div class="admin-kpi">
                    <strong>{metrics['qr_codes']}</strong>
                    <span>Total QR records</span>
                </div>
                <div class="admin-kpi">
                    <strong>{metrics['comments']}</strong>
                    <span>Comments stored</span>
                </div>
                <div class="admin-kpi">
                    <strong>{metrics['active_sessions']}</strong>
                    <span>Active sessions</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    metric_cols = st.columns(3)
    metric_cols[0].metric("Sessions", metrics["sessions"])
    metric_cols[1].metric("Active Sessions", metrics["active_sessions"])
    metric_cols[2].metric("Active QR Codes", metrics["active_qr_codes"])
    st.caption("Use `Users`, `QR Data`, `Comments`, and `Sessions` for click-based admin work. Use `SQL Runner` for one-off queries.")


def _render_users_tab() -> None:
    users = list_users()
    _render_section_intro(
        "User Management",
        "Browse every account, reset passwords, replace avatars, or remove users with click-based controls.",
    )
    if not users:
        _show_rows(users)
        return

    left_col, right_col = st.columns([1.15, 0.85], gap="large")
    user_map = {row["id"]: row for row in users}

    with left_col:
        st.markdown(
            """
            <div class="admin-mini-panel">
                <h3>All Users</h3>
                <p class="admin-note">Quick browser view for every account currently stored.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        _show_rows(users, height=400)

    with right_col:
        st.markdown(
            """
            <div class="admin-mini-panel">
                <h3>Edit Selected User</h3>
                <p class="admin-note">Pick a user, update account details, or remove the account completely.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        selected_user_id = st.selectbox(
            "Select user",
            options=list(user_map.keys()),
            format_func=lambda user_id: f"{user_id} - {user_map[user_id]['username']}",
            key="admin_selected_user",
        )
        user = get_user_by_id(selected_user_id)
        if user is None:
            st.warning("Selected user no longer exists.")
            return

        info_cols = st.columns(3)
        info_cols[0].caption(f"Created: {user.get('created_at')}")
        info_cols[1].caption(f"QR Codes: {user_map[selected_user_id]['qr_count']}")
        info_cols[2].caption(f"Comments: {user_map[selected_user_id]['comment_count']}")
        if user.get("profile_image"):
            st.image(user["profile_image"], width=96, caption="Current avatar")
        else:
            st.caption("No avatar stored.")

        with st.form(f"admin_user_form_{selected_user_id}"):
            new_username = st.text_input("Username", value=user["username"])
            new_password = st.text_input("Reset Password (optional)", type="password")
            new_avatar = st.file_uploader(
                "Replace avatar (optional)",
                type=["png", "jpg", "jpeg"],
                key=f"admin_user_avatar_upload_{selected_user_id}",
            )
            clear_avatar = st.checkbox("Remove avatar")
            save_user = st.form_submit_button("Save User Changes", type="primary", use_container_width=True)

        if save_user:
            success, message = admin_update_user(
                selected_user_id,
                new_username,
                new_password=new_password,
                profile_image=new_avatar.getvalue() if new_avatar else None,
                clear_avatar=clear_avatar,
            )
            _result_message(success, message)
            if success:
                st.rerun()

        confirm_delete = st.checkbox(
            "I understand deleting this user will also remove related sessions, comments, and QR records.",
            key=f"confirm_delete_user_{selected_user_id}",
        )
        if st.button("Delete User Permanently", key=f"delete_user_{selected_user_id}", use_container_width=True):
            if not confirm_delete:
                st.error("Tick the confirmation box before deleting the user.")
            else:
                success, message = admin_delete_user(selected_user_id)
                _result_message(success, message)
                if success:
                    if st.session_state.get("user", {}).get("id") == selected_user_id:
                        st.session_state.user = None
                        st.session_state.session_id = None
                        st.session_state.page = "Home"
                    st.rerun()


def _render_qr_tab() -> None:
    _render_section_intro(
        "QR Data Management",
        "Inspect stored QR codes, edit their content and styling, then soft delete, restore, or hard delete records.",
    )
    limit = st.number_input("Rows to load", min_value=10, max_value=500, value=200, step=10, key="admin_qr_limit")
    qr_rows = list_qr_codes(limit=int(limit))
    if not qr_rows:
        _show_rows(qr_rows, height=320)
        return

    left_col, right_col = st.columns([1.15, 0.85], gap="large")
    qr_map = {row["id"]: row for row in qr_rows}

    with left_col:
        st.markdown(
            """
            <div class="admin-mini-panel">
                <h3>Stored QR Records</h3>
                <p class="admin-note">Loaded rows from the database, including deleted state and owner information.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        _show_rows(qr_rows, height=400)

    with right_col:
        st.markdown(
            """
            <div class="admin-mini-panel">
                <h3>Edit Selected QR</h3>
                <p class="admin-note">Preview the code, then update the text or styling before saving changes.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        selected_qr_id = st.selectbox(
            "Select QR record",
            options=list(qr_map.keys()),
            format_func=lambda qr_id: f"{qr_id} - {qr_map[qr_id]['username']} - {str(qr_map[qr_id]['qr_text'])[:40]}",
            key="admin_selected_qr",
        )
        qr_record = get_qr_code_by_id(selected_qr_id)
        if qr_record is None:
            st.warning("Selected QR record no longer exists.")
            return

        preview_image = generate_qr_image(
            qr_record["qr_text"],
            _resolve_color_hex(qr_record.get("fg_color_name", "Black"), "Black"),
            _resolve_color_hex(qr_record.get("bg_color_name", "White"), "White"),
            qr_record.get("box_size") or 10,
            qr_record.get("border") or 4,
            qr_record.get("qr_style") or "square",
        )
        st.image(preview_image, width=180, caption=f"Owner: {qr_record['username']}")

        with st.form(f"admin_qr_form_{selected_qr_id}"):
            new_qr_text = st.text_area("QR Text", value=qr_record["qr_text"], height=120)
            style_cols = st.columns(3)
            fg_index = style_cols[0].selectbox(
                "Foreground Color",
                range(len(PALETTE_DISPLAY)),
                index=_resolve_color_index(qr_record.get("fg_color_name", "Black"), "Black"),
                format_func=lambda index: PALETTE_DISPLAY[index],
                key=f"admin_qr_fg_{selected_qr_id}",
            )
            bg_index = style_cols[1].selectbox(
                "Background Color",
                range(len(PALETTE_DISPLAY)),
                index=_resolve_color_index(qr_record.get("bg_color_name", "White"), "White"),
                format_func=lambda index: PALETTE_DISPLAY[index],
                key=f"admin_qr_bg_{selected_qr_id}",
            )
            qr_style = style_cols[2].selectbox(
                "Module Shape",
                ["square", "gapped", "circle"],
                index=["square", "gapped", "circle"].index(qr_record.get("qr_style", "square"))
                if qr_record.get("qr_style", "square") in {"square", "gapped", "circle"}
                else 0,
                key=f"admin_qr_style_{selected_qr_id}",
            )
            size_cols = st.columns(2)
            box_size = size_cols[0].slider("Pixel Density", 5, 20, int(qr_record.get("box_size") or 10))
            border = size_cols[1].slider("Outer Margin", 1, 10, int(qr_record.get("border") or 4))
            save_qr = st.form_submit_button("Save QR Changes", type="primary", use_container_width=True)

        if save_qr:
            success, message = admin_update_qr_code(
                selected_qr_id,
                new_qr_text,
                PALETTE_NAMES[fg_index],
                PALETTE_NAMES[bg_index],
                qr_style,
                int(box_size),
                int(border),
            )
            _result_message(success, message)
            if success:
                st.rerun()

        action_cols = st.columns(2)
        if qr_record.get("deleted_at"):
            if action_cols[0].button("Restore QR", key=f"restore_qr_{selected_qr_id}", use_container_width=True):
                success, message = set_qr_deleted_state(selected_qr_id, deleted=False)
                _result_message(success, message)
                if success:
                    st.rerun()
        else:
            if action_cols[0].button("Soft Delete QR", key=f"soft_delete_qr_{selected_qr_id}", use_container_width=True):
                success, message = set_qr_deleted_state(selected_qr_id, deleted=True)
                _result_message(success, message)
                if success:
                    st.rerun()

        confirm_delete = st.checkbox(
            "Delete this QR record permanently from the database.",
            key=f"confirm_delete_qr_{selected_qr_id}",
        )
        if action_cols[1].button("Hard Delete QR", key=f"hard_delete_qr_{selected_qr_id}", use_container_width=True):
            if not confirm_delete:
                st.error("Tick the confirmation box before hard deleting the QR record.")
            else:
                success, message = admin_delete_qr_code(selected_qr_id)
                _result_message(success, message)
                if success:
                    st.rerun()


def _render_comments_tab() -> None:
    _render_section_intro(
        "Comment Management",
        "Review community feedback, fix wording when needed, or remove comments directly from the admin UI.",
    )
    limit = st.number_input("Rows to load", min_value=10, max_value=500, value=200, step=10, key="admin_comment_limit")
    comment_rows = list_comments_for_admin(limit=int(limit))
    if not comment_rows:
        _show_rows(comment_rows, height=320)
        return

    left_col, right_col = st.columns([1.15, 0.85], gap="large")
    comment_map = {row["id"]: row for row in comment_rows}

    with left_col:
        st.markdown(
            """
            <div class="admin-mini-panel">
                <h3>Recent Comments</h3>
                <p class="admin-note">Latest feedback items loaded from the database.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        _show_rows(comment_rows, height=400)

    with right_col:
        st.markdown(
            """
            <div class="admin-mini-panel">
                <h3>Edit Selected Comment</h3>
                <p class="admin-note">Choose a row from the list, update the text, or delete it entirely.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        selected_comment_id = st.selectbox(
            "Select comment",
            options=list(comment_map.keys()),
            format_func=lambda comment_id: f"{comment_id} - {comment_map[comment_id]['username']} - {str(comment_map[comment_id]['comment_text'])[:50]}",
            key="admin_selected_comment",
        )
        comment = get_comment_by_id(selected_comment_id)
        if comment is None:
            st.warning("Selected comment no longer exists.")
            return

        with st.form(f"admin_comment_form_{selected_comment_id}"):
            edited_text = st.text_area("Comment Text", value=comment["comment_text"], height=150)
            save_comment = st.form_submit_button("Save Comment", type="primary", use_container_width=True)

        if save_comment:
            success, message = admin_update_comment(selected_comment_id, edited_text)
            _result_message(success, message)
            if success:
                st.rerun()

        confirm_delete = st.checkbox(
            "Delete this comment permanently.",
            key=f"confirm_delete_comment_{selected_comment_id}",
        )
        if st.button("Delete Comment", key=f"delete_comment_admin_{selected_comment_id}", use_container_width=True):
            if not confirm_delete:
                st.error("Tick the confirmation box before deleting the comment.")
            else:
                success, message = admin_delete_comment(selected_comment_id)
                _result_message(success, message)
                if success:
                    st.rerun()


def _render_sessions_tab() -> None:
    _render_section_intro(
        "Session Management",
        "Inspect active and past sessions, revoke access, or remove stale session rows from the database.",
    )
    limit = st.number_input("Rows to load", min_value=10, max_value=500, value=200, step=10, key="admin_session_limit")
    session_rows = list_sessions(limit=int(limit))
    if not session_rows:
        _show_rows(session_rows, height=320)
        return

    left_col, right_col = st.columns([1.15, 0.85], gap="large")
    session_map = {row["id"]: row for row in session_rows}

    with left_col:
        st.markdown(
            """
            <div class="admin-mini-panel">
                <h3>Session Browser</h3>
                <p class="admin-note">See login history, active tokens, and logout status in one grid.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        _show_rows(session_rows, height=400)

    with right_col:
        st.markdown(
            """
            <div class="admin-mini-panel">
                <h3>Manage Selected Session</h3>
                <p class="admin-note">Revoke access quickly or delete the raw session row.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        selected_session_id = st.selectbox(
            "Select session",
            options=list(session_map.keys()),
            format_func=lambda session_id: f"{session_id} - {session_map[session_id]['username']} - {session_map[session_id]['login_time']}",
            key="admin_selected_session",
        )
        session = session_map[selected_session_id]

        st.caption(f"User: {session['username']} | Login Time: {session['login_time']} | Logout Time: {session['logout_time'] or 'Active'}")
        st.code(str(session["token"]), language="text")

        action_cols = st.columns(2)
        if action_cols[0].button("Revoke Session", key=f"revoke_session_{selected_session_id}", use_container_width=True):
            success, message = revoke_session(selected_session_id)
            _result_message(success, message)
            if success and st.session_state.get("session_id") == selected_session_id:
                st.session_state.user = None
                st.session_state.session_id = None
                st.session_state.page = "Login"
            st.rerun()

        confirm_delete = st.checkbox(
            "Delete this session row permanently.",
            key=f"confirm_delete_session_{selected_session_id}",
        )
        if action_cols[1].button("Delete Session Row", key=f"delete_session_{selected_session_id}", use_container_width=True):
            if not confirm_delete:
                st.error("Tick the confirmation box before deleting the session row.")
            else:
                success, message = delete_session_record(selected_session_id)
                _result_message(success, message)
                if success and st.session_state.get("session_id") == selected_session_id:
                    st.session_state.user = None
                    st.session_state.session_id = None
                    st.session_state.page = "Login"
                st.rerun()


def _normalize_generic_value(column: dict, raw_value: Any, widget_value: Any) -> Any:
    column_type = str(column.get("type", "")).upper()
    is_required = bool(column.get("notnull"))
    if column_type.startswith("INT"):
        return int(widget_value)
    text_value = str(widget_value).strip() if widget_value is not None else ""
    if not text_value and not is_required:
        return None
    if not text_value and raw_value is None:
        return None
    return text_value


def _render_generic_editor(row: dict, table_name: str, primary_key: str, schema: list[dict]) -> None:
    editable_columns = [column for column in schema if column["name"] != primary_key]
    collected_updates: dict[str, Any] = {}

    with st.form(f"generic_editor_{table_name}_{row[primary_key]}"):
        for column in editable_columns:
            column_name = column["name"]
            current_value = row.get(column_name)
            column_type = str(column.get("type", "")).upper()
            is_required = bool(column.get("notnull"))
            help_text = f"Type: {column_type or 'TEXT'}"

            if column_name in READ_ONLY_GENERIC_COLUMNS or column_type == "BLOB":
                display_value = f"<BLOB {len(current_value)} bytes>" if isinstance(current_value, bytes) else str(current_value or "")
                st.text_input(f"{column_name} (read only)", value=display_value, disabled=True, help=help_text)
                continue

            if column_type.startswith("INT"):
                widget_value = st.number_input(column_name, value=int(current_value if current_value is not None else 0), step=1, help=help_text)
            else:
                text_value = "" if current_value is None else str(current_value)
                if len(text_value) > 80 or column_name in {"qr_text", "comment_text", "token"}:
                    widget_value = st.text_area(column_name, value=text_value, height=120, help=help_text)
                else:
                    placeholder = "NULL allowed" if not is_required else ""
                    widget_value = st.text_input(column_name, value=text_value, placeholder=placeholder, help=help_text)
            collected_updates[column_name] = _normalize_generic_value(column, current_value, widget_value)

        save_row = st.form_submit_button("Save Row Changes", type="primary", use_container_width=True)

    if save_row:
        success, message = update_row_by_primary_key(table_name, row[primary_key], collected_updates)
        _result_message(success, message)
        if success:
            if table_name == "users" and st.session_state.get("user", {}).get("id") == row[primary_key]:
                refreshed_user = get_user_by_id(int(row[primary_key]))
                if refreshed_user is not None:
                    st.session_state.user = refreshed_user
            st.rerun()

    confirm_delete = st.checkbox(
        f"Delete row {row[primary_key]} permanently from {table_name}.",
        key=f"confirm_generic_delete_{table_name}_{row[primary_key]}",
    )
    if st.button("Delete This Row", key=f"generic_delete_{table_name}_{row[primary_key]}", use_container_width=True):
        if not confirm_delete:
            st.error("Tick the confirmation box before deleting the row.")
        else:
            success, message = delete_row_by_primary_key(table_name, row[primary_key])
            _result_message(success, message)
            if success:
                if table_name == "users" and st.session_state.get("user", {}).get("id") == row[primary_key]:
                    st.session_state.user = None
                    st.session_state.session_id = None
                    st.session_state.page = "Home"
                st.rerun()


def _render_browser_tab() -> None:
    _render_section_intro(
        "Data Browser",
        "Browse any table like a lightweight database UI, then click into a row to edit or delete it.",
    )
    table_names = list_table_names()
    filter_cols = st.columns([1.2, 1, 1.2])
    selected_table = filter_cols[0].selectbox("Choose a table", table_names, key="admin_browser_table")
    limit = filter_cols[1].number_input("Rows to load", min_value=10, max_value=1000, value=200, step=10, key="admin_browser_limit")

    schema = get_table_schema(selected_table)
    primary_key = get_primary_key_column(selected_table)
    rows = browse_table_for_display(selected_table, limit=int(limit))

    left_col, right_col = st.columns([1.15, 0.85], gap="large")
    with left_col:
        st.markdown(
            """
            <div class="admin-mini-panel">
                <h3>Table Rows</h3>
                <p class="admin-note">Browse the selected table in a MySQL-like grid view.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        _show_rows(rows, height=400)
        filter_cols[2].caption(f"Primary key: {primary_key or 'None'} | Read-only: {', '.join(sorted(READ_ONLY_GENERIC_COLUMNS))}")

    with right_col:
        st.markdown(
            """
            <div class="admin-mini-panel">
                <h3>Row Editor</h3>
                <p class="admin-note">Pick a primary key value to edit the row with direct form controls.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not primary_key:
            st.info("This table does not have a primary key, so the generic editor is disabled.")
            return

        selectable_ids = [row[primary_key] for row in rows]
        if not selectable_ids:
            return

        selected_row_id = st.selectbox("Select row to edit", options=selectable_ids, key=f"admin_browser_row_{selected_table}")
        raw_row = get_row_by_primary_key(selected_table, selected_row_id)
        if raw_row is None:
            st.warning("Selected row no longer exists.")
            return

        _render_generic_editor(raw_row, selected_table, primary_key, schema)


def _render_sql_tab() -> None:
    _render_section_intro(
        "SQL Query Runner",
        "Run one SQLite statement at a time when you want direct control beyond the click-based admin tools.",
    )
    default_query = st.session_state.get("admin_sql_query", "SELECT id, username, created_at FROM users;")
    left_col, right_col = st.columns([0.7, 1.3], gap="large")

    with left_col:
        st.markdown(
            """
            <div class="admin-mini-panel">
                <h3>Quick Tips</h3>
                <p class="admin-note">
                    Good examples:
                    <br><br>
                    <code>SELECT id, username FROM users;</code>
                    <br>
                    <code>SELECT * FROM qr_codes WHERE deleted_at IS NULL;</code>
                    <br>
                    <code>UPDATE comments SET comment_text = '...' WHERE id = 1;</code>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        query = st.text_area("SQL", value=default_query, height=220, key="admin_sql_text")
        if st.button("Run SQL", type="primary", use_container_width=True, key="admin_run_sql"):
            st.session_state["admin_sql_query"] = query
            success, message, rows = execute_sql_query(query)
            _result_message(success, message)
            if rows is not None:
                _show_rows(rows, height=360)
            elif success:
                st.info("Statement finished. Reload the browser tab if you want to verify the latest data.")


def render_admin_page() -> None:
    user = st.session_state.get("user")
    if not is_admin_user(user):
        st.error("You do not have permission to access the admin panel.")
        navigate_to("Home")
        return

    access_message = admin_access_mode_message()
    st.markdown(
        f"""
        <div class="page-banner">
            <span class="section-tag">Protected Admin</span>
            <h2>Admin Panel</h2>
            <p>
                This space gives you direct control over users, QR data, comments, sessions,
                and raw SQLite queries without leaving the app.
            </p>
            <p class="admin-note">{access_message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_overview, tab_users, tab_qr, tab_comments, tab_sessions, tab_browser, tab_sql = st.tabs(
        ["Overview", "Users", "QR Data", "Comments", "Sessions", "Data Browser", "SQL Runner"]
    )

    with tab_overview:
        _render_overview_tab()
    with tab_users:
        _render_users_tab()
    with tab_qr:
        _render_qr_tab()
    with tab_comments:
        _render_comments_tab()
    with tab_sessions:
        _render_sessions_tab()
    with tab_browser:
        _render_browser_tab()
    with tab_sql:
        _render_sql_tab()
