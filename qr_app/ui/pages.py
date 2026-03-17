from __future__ import annotations

import streamlit as st

from qr_app.constants import AVATAR_MAP, PALETTE_DISPLAY, PALETTE_HEX, PALETTE_NAMES
from qr_app.security import check_password_strength
from qr_app.services.auth import create_user, load_avatar_bytes, login_user, update_profile
from qr_app.services.comments import create_comment, delete_comment, load_comments, update_comment
from qr_app.services.qr_codes import clear_all_qrs, delete_qr, generate_qr_image, load_user_qrs, save_qr_record
from qr_app.ui.components import navigate_to, render_avatar_selector, render_feedback_card
from qr_app.utils import time_ago


def _default_avatar_bytes() -> bytes | None:
    selected_path = st.session_state.get("signup_selected_avatar", AVATAR_MAP["Boy"])
    return load_avatar_bytes(selected_path)


def _resolve_color_hex(color_name: str, default_hex: str) -> str:
    try:
        return PALETTE_HEX[PALETTE_NAMES.index(color_name)]
    except ValueError:
        return default_hex


def _render_page_banner(tag: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="page-banner">
            <span class="section-tag">{tag}</span>
            <h2>{title}</h2>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_home_page() -> None:
    st.markdown(
        """
        <div class="hero-panel">
            <div class="hero-shell">
                <div class="hero-main">
                    <span class="section-tag">Curated QR Experience</span>
                    <h1 class="hero-title">Turn a simple scan into a polished first impression.</h1>
                    <p class="hero-copy">
                        Create QR codes for invites, menus, portfolios, payments, and everyday sharing in a space that feels calm,
                        considered, and easy to move through.
                    </p>
                    <div class="use-case-grid">
                        <span class="use-case-pill">Menus</span>
                        <span class="use-case-pill">Events</span>
                        <span class="use-case-pill">Portfolios</span>
                        <span class="use-case-pill">Payments</span>
                    </div>
                </div>
                <div class="hero-focus-card">
                    <span class="section-tag">A Small Note</span>
                    <h3>Made by Krishna with care for people who enjoy creating useful things that feel special.</h3>
                    <p>
                        The goal is simple: help every QR feel presentable, welcoming, and ready for the real world without making the experience feel busy.
                    </p>
                    <div class="hero-focus-list">
                        <span>Clear from the first click</span>
                        <span>Pleasing to look at</span>
                        <span>Easy to share with confidence</span>
                    </div>
                </div>
            </div>
            <div class="hero-stat-row">
                <div class="hero-stat">
                    <strong>Styled Your Way</strong>
                    <span>Adjust color, shape, and spacing until the code feels like it belongs to you.</span>
                </div>
                <div class="hero-stat">
                    <strong>Ready in Moments</strong>
                    <span>Move from idea to crisp download quickly, without extra clutter or confusion.</span>
                </div>
                <div class="hero-stat">
                    <strong>Saved With Care</strong>
                    <span>Keep your favorite codes close so you can revisit them whenever you want.</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, action_left, action_right, _ = st.columns([0.18, 1, 1, 0.18], gap="large")
    if st.session_state.user:
        if action_left.button("Create a New QR", type="primary", use_container_width=True):
            navigate_to("QR Generator")
        if action_right.button("Open My Library", type="primary", use_container_width=True):
            navigate_to("My QR Codes")
    else:
        if action_left.button("Try It Now", type="primary", use_container_width=True):
            navigate_to("Quick QR Code")
        if action_right.button("Login / Sign Up", type="primary", use_container_width=True):
            navigate_to("Login")

    col_story, col_preview = st.columns([1.15, 0.85], gap="large")
    with col_story:
        st.markdown(
            """
            <div class="info-panel">
                <span class="section-tag">Designed for real moments</span>
                <h3>Useful in everyday life, not just on a demo screen.</h3>
                <p>
                    Whether you are preparing a cafe table card, a wedding invite, a product tag,
                    or your personal portfolio link, the experience stays focused and easy to follow.
                </p>
                <div class="use-case-grid">
                    <span class="use-case-pill">Menus</span>
                    <span class="use-case-pill">Events</span>
                    <span class="use-case-pill">Payments</span>
                    <span class="use-case-pill">Portfolios</span>
                    <span class="use-case-pill">Social Links</span>
                    <span class="use-case-pill">Product Tags</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_preview:
        st.markdown(
            """
            <div class="info-panel">
                <span class="section-tag">Quiet confidence</span>
                <h3>A cleaner flow makes the result feel better.</h3>
                <p>
                    Strong contrast, gentle structure, and a calm layout help the whole app feel more intentional
                    whether you need one quick code or a small collection saved for later.
                </p>
                <div class="use-case-grid">
                    <span class="use-case-pill">Easy previews</span>
                    <span class="use-case-pill">Comfortable controls</span>
                    <span class="use-case-pill">Saved favorites</span>
                    <span class="use-case-pill">Quick downloads</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 0.7rem;'></div>", unsafe_allow_html=True)
    feature_columns = st.columns(3)
    feature_columns[0].markdown(
        """
        <div class="feature-panel">
            <div class="feature-icon">QR</div>
            <h3>Shape the Mood</h3>
            <p>Give each code its own personality with colors and styling that feel deliberate.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    feature_columns[1].markdown(
        """
        <div class="feature-panel">
            <div class="feature-icon">GO</div>
            <h3>Move in One Flow</h3>
            <p>From text to preview to download, each step stays close and easy to understand.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    feature_columns[2].markdown(
        """
        <div class="feature-panel">
            <div class="feature-icon">TALK</div>
            <h3>Keep It Personal</h3>
            <p>Save the ones you love, leave feedback, and make the space feel a little more yours.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="story-banner">
            <span class="section-tag">Made with intention</span>
            <h3>A good QR should feel like a smooth handoff, not just a square on a page.</h3>
            <p>
                This space is here to help your invites, menus, links, and moments feel a little more polished,
                thoughtful, and ready to share with confidence.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_signup_page() -> None:
    _render_page_banner(
        "Join",
        "Create Your Account",
        "Set up your profile, choose an avatar, and unlock saved QR history and feedback features.",
    )
    new_username = st.text_input("Username", key="signup_username")
    new_password = st.text_input("Password", type="password", key="signup_password")
    percent, (strength, _) = check_password_strength(new_password)
    st.progress(percent / 100, text=f"Password Strength: {strength}")

    with st.expander("Choose Your Avatar", expanded=False):
        render_avatar_selector("signup")

    uploaded_avatar = st.file_uploader(
        "Or upload your own image:",
        type=["png", "jpg", "jpeg"],
        key="signup_avatar_upload",
    )

    if st.button("Sign Up", type="primary", use_container_width=True, key="signup_submit"):
        avatar_bytes = uploaded_avatar.getvalue() if uploaded_avatar else _default_avatar_bytes()
        success, message = create_user(new_username, new_password, avatar_bytes)
        if success:
            st.success(message)
            st.balloons()
            navigate_to("Login")
        else:
            st.error(message)


def render_login_page() -> None:
    _render_page_banner(
        "Welcome Back",
        "Login to Your Account",
        "Jump back into your QR workspace, saved history, and account settings.",
    )
    username = st.text_input("Username", placeholder="Enter your username", key="login_username")
    password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")

    if st.button("Login", type="primary", use_container_width=True, key="login_submit"):
        success, message = login_user(username, password)
        if success:
            st.success(message)
            navigate_to("Home")
        else:
            st.error(message)

    st.info("New user? Open the Sign Up page from the sidebar.")


def render_account_page() -> None:
    user = st.session_state.user
    if not user:
        st.warning("Please log in to view your account.")
        navigate_to("Login")
        return

    _render_page_banner(
        "Account",
        "My Account Settings",
        "Update your profile details, refresh your password, and switch avatars without leaving the app.",
    )
    left_col, right_col = st.columns([1, 2], gap="large")

    with left_col:
        st.subheader("Current Avatar")
        if user.get("profile_image"):
            st.image(user["profile_image"], use_container_width=True)
        else:
            st.info("No avatar set.")

    with right_col:
        st.subheader("Update Details")
        new_username = st.text_input("Username", value=user["username"], key="account_username")
        new_password = st.text_input(
            "New Password",
            type="password",
            placeholder="Leave blank to keep your current password",
            key="account_password",
        )

        with st.expander("Change Your Avatar", expanded=False):
            render_avatar_selector("update")

        uploaded_avatar = st.file_uploader(
            "Or upload a new image:",
            type=["png", "jpg", "jpeg"],
            key="account_avatar_upload",
        )

        if st.button("Save Changes", type="primary", use_container_width=True, key="account_save"):
            if uploaded_avatar:
                profile_bytes = uploaded_avatar.getvalue()
            elif st.session_state.get("update_avatar_explicitly_selected"):
                profile_bytes = load_avatar_bytes(st.session_state.get("update_selected_avatar"))
            else:
                profile_bytes = user.get("profile_image")

            success, message = update_profile(user["id"], new_username, new_password, profile_bytes)
            if success:
                st.session_state["update_avatar_explicitly_selected"] = False
                st.success(message)
                st.rerun()
            else:
                st.error(message)


def render_qr_page(page_key: str, simple: bool = False) -> None:
    if simple:
        _render_page_banner(
            "Quick Mode",
            "Quick QR Code",
            "Generate a clean QR code fast with minimal setup and download it right away.",
        )
    else:
        _render_page_banner(
            "Generator",
            "Ultimate QR Code Generator",
            "Customize color, shape, and spacing, then save polished QR codes directly to your account.",
        )

    st.markdown(
        f"""
        <div class="generator-shell">
            <div>
                <span class="section-tag">{'Fast Start' if simple else 'Creative Workspace'}</span>
                <h3>{'Make something useful in a moment.' if simple else 'Shape the look before you share it.'}</h3>
                <p>
                    {'Add your text or link, generate once, and download right away.' if simple else 'Write the content, refine the styling, and preview the result in a calmer, more considered workspace.'}
                </p>
            </div>
            <div class="generator-mini-note">
                <strong>{'Clean and quick' if simple else 'Designed to feel easy'}</strong>
                <span>{'A simple flow for when you just want the code fast.' if simple else 'Every step stays visible so the process feels smooth instead of crowded.'}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    main_col, preview_col = st.columns([0.55, 0.45], gap="large")
    user_id = st.session_state.user["id"] if st.session_state.user else "guest"
    qr_img_key = f"qr_img_{page_key}_{user_id}"
    qr_text_key = f"qr_text_{page_key}_{user_id}"

    with main_col:
        with st.container(border=True):
            st.markdown(
                """
                <div class="generator-section">
                    <span class="section-tag">Step 1</span>
                    <h3>Choose what the scan should open.</h3>
                    <p>Paste a link, message, invitation, or any text you want people to reach when they scan.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            user_input = st.text_area(
                "Enter Text or Link:",
                placeholder="https://example.com or Hello World!",
                height=110,
                key=f"text_{page_key}_{user_id}",
            )

            if not simple:
                st.markdown(
                    """
                    <div class="generator-control-strip">
                        <span>Color, shape, and spacing all stay in one place so the design feels easy to refine.</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                with st.expander("Colors, Shape, and Size", expanded=True):
                    color_cols = st.columns(3)
                    fg_index = color_cols[0].selectbox(
                        "Foreground Color",
                        range(len(PALETTE_DISPLAY)),
                        index=PALETTE_NAMES.index("Black"),
                        format_func=lambda index: PALETTE_DISPLAY[index],
                        key=f"fg_{page_key}_{user_id}",
                    )
                    bg_index = color_cols[1].selectbox(
                        "Background Color",
                        range(len(PALETTE_DISPLAY)),
                        index=PALETTE_NAMES.index("White"),
                        format_func=lambda index: PALETTE_DISPLAY[index],
                        key=f"bg_{page_key}_{user_id}",
                    )
                    qr_style = color_cols[2].selectbox(
                        "Module Shape",
                        ["square", "gapped", "circle"],
                        index=0,
                        key=f"style_{page_key}_{user_id}",
                    )
                    size_cols = st.columns(2)
                    box_size = size_cols[0].slider("Pixel Density", 5, 20, 10, key=f"box_{page_key}_{user_id}")
                    border = size_cols[1].slider("Outer Margin", 1, 10, 4, key=f"border_{page_key}_{user_id}")
            else:
                fg_index = PALETTE_NAMES.index("Black")
                bg_index = PALETTE_NAMES.index("White")
                qr_style = "square"
                box_size = 10
                border = 4

            fg_color = PALETTE_HEX[fg_index]
            bg_color = PALETTE_HEX[bg_index]
            fg_name = PALETTE_NAMES[fg_index]
            bg_name = PALETTE_NAMES[bg_index]

            if st.button("Generate QR Code", key=f"generate_{page_key}_{user_id}", type="primary", use_container_width=True):
                if not user_input.strip():
                    st.warning("Please enter text or a link.")
                else:
                    qr_image = generate_qr_image(user_input, fg_color, bg_color, box_size, border, qr_style)
                    st.session_state[qr_img_key] = qr_image
                    st.session_state[qr_text_key] = user_input
                    st.toast("QR code generated.")

                    if st.session_state.user and not simple:
                        save_qr_record(
                            st.session_state.user["id"],
                            user_input,
                            fg_name,
                            bg_name,
                            qr_style,
                            box_size,
                            border,
                        )
                        st.toast("Saved to your account.")

    with preview_col:
        with st.container(border=True):
            st.markdown(
                """
                <div class="preview-shell">
                    <span class="section-tag">Step 2</span>
                    <h3>Preview the result before you send it out.</h3>
                    <p>The final code appears here with its styling details and a ready-to-download action.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            qr_image = st.session_state.get(qr_img_key)
            if qr_image:
                qr_text_preview = st.session_state.get(qr_text_key, "")
                image_left, image_center, image_right = st.columns([0.06, 0.88, 0.06])
                with image_center:
                    st.image(qr_image, width=340)
                st.markdown(
                    f"""
                    <div class="preview-chip-row">
                        <span class="preview-chip">{fg_name}</span>
                        <span class="preview-chip">{bg_name}</span>
                        <span class="preview-chip">{qr_style.title()}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.caption(qr_text_preview[:72] + ("..." if len(qr_text_preview) > 72 else ""))
                st.download_button(
                    "Download as PNG",
                    data=qr_image,
                    file_name=f"qr_code_{page_key}.png",
                    mime="image/png",
                    key=f"download_{page_key}_{user_id}",
                    use_container_width=True,
                )
            else:
                st.markdown(
                    """
                    <div class="preview-placeholder">
                        <div class="preview-placeholder-box">Preview waiting</div>
                        <p>Generate a code and it will appear here ready to review and download.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_feedback_page() -> None:
    comments = load_comments()
    current_user_id = st.session_state.user["id"] if st.session_state.user else None
    feedback_count = len(comments)

    st.markdown(
        f"""
        <div class="feedback-hero">
            <span class="section-tag">Community Lounge</span>
            <h2>Read the latest feedback and share your own thoughts.</h2>
            <p>
                Browse what other people are saying, leave a quick note when you are signed in,
                and keep the conversation friendly, helpful, and useful for everyone.
            </p>
            <div class="hero-stat-row">
                <div class="hero-stat">
                    <strong>{feedback_count}</strong>
                    <span>Community {'note' if feedback_count == 1 else 'notes'} shared so far.</span>
                </div>
                <div class="hero-stat">
                    <strong>{'Your voice matters' if current_user_id else 'Open to explore'}</strong>
                    <span>{'Share an idea, a compliment, or a small suggestion that can make the app even better.' if current_user_id else 'Read what others are saying and sign in whenever you want to add your own note.'}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if current_user_id:
        st.markdown(
            """
            <div class="feedback-form-shell">
                <span class="section-tag">Leave a note</span>
                <h3>Tell us what felt good or what should improve.</h3>
                <p>Short, clear feedback helps the app get better faster.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("feedback_form", clear_on_submit=True):
            comment_text = st.text_area(
                "Your thoughts:",
                placeholder="Share a suggestion, a compliment, or one thing that would make this better...",
                height=110,
            )
            if st.form_submit_button("Submit Feedback", type="primary", use_container_width=True):
                success, message = create_comment(current_user_id, comment_text)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    else:
        st.info("You can explore all community feedback without logging in. Sign in when you want to post, edit, or delete your own note.")

    st.subheader("Community Feedback")
    if not comments:
        st.markdown(
            """
            <div class="feedback-empty">
                No feedback yet. Be the first person to leave a thoughtful note.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    for comment in comments:
        is_owner = current_user_id is not None and comment["user_id"] == current_user_id
        render_feedback_card(comment, is_owner=is_owner)

        if not is_owner:
            continue

        edit_state_key = f"editing_comment_{comment['id']}"
        edit_draft_key = f"editing_comment_draft_{comment['id']}"
        st.session_state.setdefault(edit_state_key, False)

        action_cols = st.columns([1.4, 1.0, 4.0])
        if action_cols[0].button("Edit Feedback", key=f"edit_toggle_{comment['id']}", use_container_width=True):
            st.session_state[edit_state_key] = not st.session_state[edit_state_key]
            if st.session_state[edit_state_key]:
                st.session_state[edit_draft_key] = comment["comment_text"]
            else:
                st.session_state.pop(edit_draft_key, None)
            st.rerun()

        if action_cols[1].button("Delete", key=f"delete_comment_{comment['id']}", use_container_width=True):
            success, message = delete_comment(comment["id"], current_user_id)
            if success:
                st.session_state.pop(edit_state_key, None)
                st.session_state.pop(edit_draft_key, None)
                st.success(message)
                st.rerun()
            else:
                st.error(message)

        if st.session_state.get(edit_state_key):
            st.markdown("Update your feedback below.")
            with st.form(key=f"edit_form_{comment['id']}"):
                edited_text = st.text_area("Edit comment:", key=edit_draft_key, height=90)
                button_cols = st.columns(2)
                if button_cols[0].form_submit_button("Save Update", type="primary", use_container_width=True):
                    success, message = update_comment(comment["id"], current_user_id, edited_text)
                    if success:
                        st.session_state[edit_state_key] = False
                        st.session_state.pop(edit_draft_key, None)
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                if button_cols[1].form_submit_button("Cancel", use_container_width=True):
                    st.session_state[edit_state_key] = False
                    st.session_state.pop(edit_draft_key, None)
                    st.rerun()


def render_saved_qrs_page() -> None:
    user = st.session_state.user
    if not user:
        st.warning("You must be logged in to view saved QR codes.")
        navigate_to("Login")
        return

    _render_page_banner(
        "Library",
        "My Saved QR Codes",
        "Browse your saved history, download previous QR codes again, or clean up records you no longer need.",
    )
    top_cols = st.columns([2, 1])
    top_cols[0].caption("Your saved collection stays close, so past designs are always easy to revisit.")
    if top_cols[1].button("Clear All History", use_container_width=True, key="clear_all_qrs"):
        success, message = clear_all_qrs(user["id"])
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)

    saved_qrs = load_user_qrs(user["id"])
    if not saved_qrs:
        st.info("You haven't saved any QR codes yet.")
        return

    for qr_record in saved_qrs:
        fg_hex = _resolve_color_hex(qr_record.get("fg_color_name", "Black"), "#000000")
        bg_hex = _resolve_color_hex(qr_record.get("bg_color_name", "White"), "#FFFFFF")
        box_size = qr_record.get("box_size") or 10
        border = qr_record.get("border") or 4
        qr_style = qr_record.get("qr_style") or "square"
        qr_image = generate_qr_image(qr_record["qr_text"], fg_hex, bg_hex, box_size, border, qr_style)

        with st.container(border=True):
            image_col, details_col = st.columns([1, 3], gap="large")
            with image_col:
                st.image(qr_image, width=150)
                st.download_button(
                    "Download",
                    data=qr_image,
                    file_name=f"my_qr_{qr_record['id']}.png",
                    mime="image/png",
                    key=f"download_saved_qr_{qr_record['id']}",
                    use_container_width=True,
                )
            with details_col:
                st.caption(f"Created: {time_ago(qr_record.get('created_at'))}")
                st.code(
                    qr_record["qr_text"][:90] + ("..." if len(qr_record["qr_text"]) > 90 else ""),
                    language="text",
                )
                st.markdown(
                    f"**Details:** {qr_record.get('fg_color_name')} on {qr_record.get('bg_color_name')} | Style: {qr_style}"
                )
                if st.button("Delete QR", key=f"delete_qr_{qr_record['id']}", use_container_width=True):
                    success, message = delete_qr(qr_record["id"], user["id"])
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
