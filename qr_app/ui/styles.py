from __future__ import annotations

import streamlit as st


GLOBAL_CSS = """
<style>
    @keyframes auroraShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes softRise {
        from {
            opacity: 0;
            transform: translateY(18px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(34, 211, 238, 0.18), transparent 28%),
            radial-gradient(circle at bottom right, rgba(244, 114, 182, 0.18), transparent 26%),
            linear-gradient(-45deg, #08111f, #10233d, #17375d, #0f4c81);
        background-size: 400% 400%;
        animation: auroraShift 16s ease infinite;
        color: #e2e8f0;
    }

    header[data-testid="stHeader"] {
        display: none;
    }

    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"],
    #MainMenu,
    footer {
        display: none !important;
    }

    .stApp, .stMarkdown, p, label, h1, h2, h3, h4, h5, h6 {
        color: #f8fafc;
    }

    section[data-testid="stSidebar"] {
        background:
            radial-gradient(circle at top left, rgba(59, 130, 246, 0.12), transparent 28%),
            linear-gradient(180deg, rgba(8, 15, 29, 0.96), rgba(10, 19, 36, 0.9));
        border-right: 1px solid rgba(148, 163, 184, 0.15);
        backdrop-filter: blur(12px);
        box-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.03);
    }

    section[data-testid="stSidebar"] h1 {
        margin-bottom: 0.35rem;
        font-size: 2rem;
        letter-spacing: -0.04em;
    }

    section[data-testid="stSidebar"] p {
        color: #cbd5e1;
    }

    section[data-testid="stSidebar"] hr {
        border-color: rgba(148, 163, 184, 0.12);
        margin: 1rem 0 1.2rem;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 0.45rem;
    }

    section[data-testid="stSidebar"] label[data-baseweb="radio"] {
        background: rgba(15, 23, 42, 0.68);
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 16px;
        padding: 0.48rem 0.82rem;
        margin-bottom: 0.2rem;
        transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
    }

    section[data-testid="stSidebar"] label[data-baseweb="radio"]:hover {
        transform: translateX(3px);
        border-color: rgba(125, 211, 252, 0.35);
        background: rgba(30, 41, 59, 0.9);
    }

    section[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.45), rgba(15, 23, 42, 0.92));
        border-color: rgba(125, 211, 252, 0.42);
        box-shadow: 0 10px 24px rgba(2, 8, 23, 0.18);
    }

    section[data-testid="stSidebar"] label[data-baseweb="radio"] p {
        font-weight: 600;
    }

    .block-container {
        padding-top: 0.65rem;
        padding-bottom: 2.5rem;
        max-width: 1180px;
    }

    div[data-testid="stVerticalBlock"] {
        gap: 1rem;
    }

    .stButton > button,
    .stFormSubmitButton > button,
    .stDownloadButton > button {
        min-height: 46px;
        border-radius: 14px;
        border: 1px solid transparent;
        font-weight: 700;
        transition: all 0.25s ease;
    }

    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"],
    .stDownloadButton > button {
        background: linear-gradient(90deg, #67e8f9, #60a5fa 52%, #818cf8);
        color: #020617 !important;
        box-shadow: 0 14px 30px rgba(56, 189, 248, 0.24);
    }

    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button[kind="primary"]:hover,
    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 14px 28px rgba(129, 140, 248, 0.28);
    }

    .stButton > button:not([kind="primary"]),
    .stFormSubmitButton > button:not([kind="primary"]) {
        background: rgba(15, 23, 42, 0.88);
        color: #f8fafc !important;
        border: 1px solid rgba(96, 165, 250, 0.45);
    }

    .stTextInput input,
    .stTextArea textarea,
    div[data-baseweb="select"] > div {
        background: #f8fafc !important;
        color: #020617 !important;
        border-radius: 12px !important;
        border: 1px solid #60a5fa !important;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #64748b !important;
    }

    div[data-baseweb="popover"] li {
        background: #0f172a !important;
        color: #f8fafc !important;
    }

    div[data-baseweb="toast"] {
        background: #0f172a !important;
        color: #f8fafc !important;
        border: 1px solid #60a5fa;
        border-radius: 14px;
    }

    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary svg {
        color: #f8fafc !important;
    }

    [data-testid="stFileUploader"] button {
        background: linear-gradient(90deg, #38bdf8, #818cf8) !important;
        color: #020617 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
    }

    div[data-testid="stForm"],
    div[data-testid="stDataFrame"],
    div[data-testid="stMetric"],
    div[data-testid="stAlert"] {
        border-radius: 20px !important;
    }

    div[data-testid="stForm"] {
        background: rgba(15, 23, 42, 0.68);
        border: 1px solid rgba(148, 163, 184, 0.18);
        box-shadow: 0 16px 40px rgba(2, 8, 23, 0.22);
        padding: 1.1rem;
        backdrop-filter: blur(14px);
    }

    div[data-testid="stDataFrame"] {
        background: rgba(15, 23, 42, 0.52);
        border: 1px solid rgba(148, 163, 184, 0.16);
        padding: 0.35rem;
        backdrop-filter: blur(12px);
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.88), rgba(30, 41, 59, 0.72));
        border: 1px solid rgba(148, 163, 184, 0.16);
        padding: 0.9rem 1rem;
        box-shadow: 0 16px 35px rgba(2, 8, 23, 0.18);
        backdrop-filter: blur(12px);
    }

    div[data-testid="stMetricLabel"] p,
    div[data-testid="stMetricLabel"] label,
    div[data-testid="stMetricLabel"] div {
        color: #cbd5e1 !important;
        font-weight: 700 !important;
        letter-spacing: 0.01em;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    div[data-testid="stMetricDelta"] {
        color: #93c5fd !important;
    }

    div[data-baseweb="tab-list"] {
        gap: 0.55rem;
        background: rgba(15, 23, 42, 0.58);
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 20px;
        padding: 0.45rem;
        backdrop-filter: blur(12px);
    }

    button[role="tab"] {
        min-height: 46px;
        border-radius: 14px !important;
        color: #cbd5e1 !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
    }

    button[role="tab"]:hover {
        background: rgba(51, 65, 85, 0.66) !important;
    }

    button[role="tab"][aria-selected="true"] {
        background: linear-gradient(90deg, #67e8f9, #60a5fa 52%, #818cf8) !important;
        color: #020617 !important;
        box-shadow: 0 10px 24px rgba(96, 165, 250, 0.22);
    }

    div[data-testid="stTabs"] div[role="tabpanel"] {
        padding-top: 1rem;
    }

    .section-tag {
        display: inline-flex;
        align-items: center;
        padding: 0.35rem 0.88rem;
        border-radius: 999px;
        border: 1px solid rgba(148, 163, 184, 0.25);
        background: rgba(148, 163, 184, 0.12);
        color: #bfdbfe;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
    }

    .hero-panel,
    .info-panel,
    .feature-panel,
    .story-banner,
    .feedback-hero,
    .feedback-form-shell,
    .feedback-empty,
    .page-banner,
    .admin-hero,
    .admin-panel,
    .admin-mini-panel,
    div[data-testid="stForm"],
    div[data-testid="stDataFrame"],
    div[data-testid="stMetric"] {
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.18);
        box-shadow: 0 18px 45px rgba(2, 8, 23, 0.25);
        animation: softRise 0.55s ease both;
    }

    .hero-panel {
        padding: 2.4rem;
        border-radius: 32px;
        background:
            radial-gradient(circle at top right, rgba(56, 189, 248, 0.26), transparent 34%),
            radial-gradient(circle at bottom left, rgba(236, 72, 153, 0.14), transparent 30%),
            linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(24, 36, 61, 0.84));
        margin: 0 auto 1.1rem;
        max-width: 100%;
        backdrop-filter: blur(14px);
    }

    .hero-shell {
        display: grid;
        grid-template-columns: minmax(0, 1.45fr) minmax(260px, 0.9fr);
        gap: 1.2rem;
        align-items: stretch;
    }

    .hero-main {
        max-width: 680px;
    }

    .hero-main .use-case-grid {
        margin-top: 1rem;
    }

    .hero-focus-card {
        padding: 1.3rem;
        border-radius: 24px;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.72), rgba(37, 99, 235, 0.18));
        border: 1px solid rgba(125, 211, 252, 0.15);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
    }

    .hero-focus-card h3 {
        margin: 0.9rem 0 0.45rem;
        font-size: 1.45rem;
        color: #ffffff;
        letter-spacing: -0.03em;
    }

    .hero-focus-card p {
        color: #dbeafe;
        line-height: 1.7;
    }

    .hero-focus-list {
        display: grid;
        gap: 0.65rem;
        margin-top: 1rem;
    }

    .hero-focus-list span {
        display: inline-flex;
        align-items: center;
        padding: 0.75rem 0.9rem;
        border-radius: 16px;
        background: rgba(15, 23, 42, 0.45);
        border: 1px solid rgba(148, 163, 184, 0.12);
        color: #e2e8f0;
    }

    .hero-title {
        margin: 0.9rem 0 0.8rem;
        font-size: clamp(2.4rem, 4vw, 4.1rem);
        line-height: 0.98;
        letter-spacing: -0.04em;
        color: #ffffff;
    }

    .hero-copy,
    .info-panel p,
    .feature-panel p,
    .story-banner p,
    .feedback-hero p,
    .feedback-form-shell p,
    .feedback-empty {
        color: #dbeafe;
        line-height: 1.72;
    }

    .hero-copy {
        max-width: 640px;
        font-size: 1.05rem;
    }

    .hero-stat-row,
    .use-case-grid,
    .feedback-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 0.7rem;
    }

    .hero-stat-row {
        margin-top: 1.25rem;
    }

    .hero-stat {
        flex: 1 1 180px;
        min-width: 180px;
        padding: 1rem;
        border-radius: 18px;
        background: rgba(15, 23, 42, 0.48);
        border: 1px solid rgba(125, 211, 252, 0.15);
        backdrop-filter: blur(10px);
    }

    .hero-stat strong,
    .feedback-author,
    .info-panel h3,
    .feature-panel h3,
    .story-banner h3,
    .feedback-hero h2,
    .feedback-form-shell h3 {
        color: #ffffff;
    }

    .hero-stat span,
    .feedback-time {
        color: #cbd5e1;
    }

    .info-panel,
    .feature-panel {
        height: 100%;
    }

    .info-panel {
        padding: 1.5rem;
        border-radius: 24px;
        background: linear-gradient(160deg, rgba(10, 18, 33, 0.94), rgba(37, 99, 235, 0.25));
        backdrop-filter: blur(12px);
    }

    .info-panel h3,
    .story-banner h3 {
        letter-spacing: -0.03em;
    }

    .feature-panel {
        padding: 1.45rem;
        border-radius: 22px;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.9), rgba(15, 23, 42, 0.72));
        transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease;
    }

    .feature-panel:hover,
    .info-panel:hover,
    .story-banner:hover,
    .page-banner:hover,
    .admin-panel:hover,
    .admin-mini-panel:hover {
        transform: translateY(-2px);
        border-color: rgba(125, 211, 252, 0.28);
        box-shadow: 0 22px 48px rgba(2, 8, 23, 0.28);
    }

    .feature-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 54px;
        height: 54px;
        margin-bottom: 0.9rem;
        padding: 0 0.8rem;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(103, 232, 249, 0.16), rgba(129, 140, 248, 0.18));
        border: 1px solid rgba(125, 211, 252, 0.15);
        font-size: 0.88rem;
        font-weight: 800;
        letter-spacing: 0.1em;
    }

    .use-case-pill {
        padding: 0.42rem 0.8rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #f8fafc;
        font-size: 0.88rem;
    }

    .story-banner {
        margin-top: 0.95rem;
        padding: 1.9rem;
        border-radius: 26px;
        background: linear-gradient(140deg, rgba(14, 116, 144, 0.34), rgba(15, 23, 42, 0.92));
        backdrop-filter: blur(12px);
    }

    .story-banner p {
        max-width: 760px;
    }

    .generator-shell,
    .generator-section,
    .preview-shell,
    .generator-control-strip,
    .preview-placeholder {
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.16);
    }

    .generator-shell {
        display: grid;
        grid-template-columns: minmax(0, 1.3fr) minmax(240px, 0.8fr);
        gap: 1rem;
        padding: 1.2rem 1.25rem;
        border-radius: 24px;
        margin-bottom: 0.8rem;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.68));
        box-shadow: 0 18px 42px rgba(2, 8, 23, 0.22);
        backdrop-filter: blur(12px);
        animation: softRise 0.55s ease both;
    }

    .generator-shell h3,
    .generator-section h3,
    .preview-shell h3 {
        margin: 0.75rem 0 0.35rem;
        color: #ffffff;
        letter-spacing: -0.03em;
    }

    .generator-shell p,
    .generator-section p,
    .preview-shell p,
    .generator-mini-note span,
    .preview-placeholder p {
        color: #dbeafe;
        line-height: 1.7;
    }

    .generator-mini-note {
        display: grid;
        gap: 0.35rem;
        align-content: start;
        padding: 1rem;
        border-radius: 18px;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.66), rgba(37, 99, 235, 0.14));
        border: 1px solid rgba(125, 211, 252, 0.12);
    }

    .generator-mini-note strong {
        color: #ffffff;
        font-size: 1rem;
    }

    .generator-section,
    .preview-shell {
        margin-bottom: 1rem;
        padding: 1rem 1.05rem;
        border-radius: 18px;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.58), rgba(30, 41, 59, 0.4));
    }

    .generator-control-strip {
        margin: 0.9rem 0 0.8rem;
        padding: 0.8rem 0.9rem;
        border-radius: 16px;
        background: rgba(15, 23, 42, 0.46);
        color: #cbd5e1;
        font-size: 0.95rem;
    }

    .preview-chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin: 0.85rem 0 0.5rem;
    }

    .preview-chip {
        display: inline-flex;
        align-items: center;
        padding: 0.45rem 0.78rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(148, 163, 184, 0.16);
        color: #e2e8f0;
        font-size: 0.88rem;
    }

    .preview-placeholder {
        display: grid;
        place-items: center;
        gap: 0.8rem;
        padding: 1.4rem 1rem;
        border-radius: 22px;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.62), rgba(30, 41, 59, 0.48));
        text-align: center;
    }

    .preview-placeholder-box {
        display: grid;
        place-items: center;
        width: min(100%, 260px);
        aspect-ratio: 1 / 1;
        border-radius: 24px;
        border: 1px dashed rgba(125, 211, 252, 0.35);
        background:
            linear-gradient(135deg, rgba(15, 23, 42, 0.86), rgba(30, 41, 59, 0.66));
        color: #cbd5e1;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    .feedback-hero {
        margin-bottom: 1rem;
        padding: 1.8rem;
        border-radius: 26px;
        background: linear-gradient(145deg, rgba(14, 116, 144, 0.26), rgba(15, 23, 42, 0.95));
    }

    .feedback-form-shell {
        margin: 0.6rem 0 1rem;
        padding: 1.2rem 1.35rem;
        border-radius: 22px;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.86), rgba(30, 41, 59, 0.76));
    }

    .feedback-avatar-fallback {
        width: 56px;
        height: 56px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        color: #ffffff;
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.88), rgba(236, 72, 153, 0.85));
    }

    .feedback-owner-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.28rem 0.7rem;
        border-radius: 999px;
        background: rgba(16, 185, 129, 0.14);
        border: 1px solid rgba(16, 185, 129, 0.28);
        color: #bbf7d0;
        font-size: 0.8rem;
    }

    .feedback-text {
        color: #e2e8f0;
        line-height: 1.7;
    }

    .feedback-empty {
        padding: 1.35rem;
        border-radius: 20px;
        background: rgba(15, 23, 42, 0.72);
        text-align: center;
    }

    .page-banner,
    .admin-hero,
    .admin-panel,
    .admin-mini-panel {
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.18);
        box-shadow: 0 18px 45px rgba(2, 8, 23, 0.24);
    }

    .page-banner,
    .admin-hero {
        padding: 1.7rem 1.85rem;
        border-radius: 28px;
        background:
            radial-gradient(circle at top right, rgba(56, 189, 248, 0.18), transparent 35%),
            linear-gradient(135deg, rgba(15, 23, 42, 0.96), rgba(30, 41, 59, 0.84));
        margin-bottom: 0.5rem;
        backdrop-filter: blur(14px);
    }

    .page-banner h2,
    .admin-hero h2 {
        margin: 0.7rem 0 0.45rem;
        color: #ffffff;
        font-size: clamp(1.8rem, 2.8vw, 2.6rem);
        letter-spacing: -0.03em;
    }

    .page-banner p,
    .admin-hero p,
    .admin-note {
        color: #dbeafe;
        line-height: 1.7;
    }

    .admin-panel,
    .admin-mini-panel {
        padding: 1.15rem 1.2rem;
        border-radius: 22px;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.88), rgba(30, 41, 59, 0.72));
        backdrop-filter: blur(12px);
    }

    .admin-mini-panel {
        padding: 1rem 1.05rem;
        min-height: 100%;
    }

    .admin-panel h3,
    .admin-mini-panel h3 {
        margin: 0 0 0.3rem;
        color: #ffffff;
    }

    .admin-kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 0.8rem;
        margin-top: 1rem;
    }

    .admin-kpi {
        padding: 1rem;
        border-radius: 18px;
        background: rgba(15, 23, 42, 0.48);
        border: 1px solid rgba(96, 165, 250, 0.16);
    }

    .admin-kpi strong {
        display: block;
        font-size: 1.3rem;
        color: #ffffff;
        margin-bottom: 0.2rem;
    }

    .admin-kpi span {
        color: #cbd5e1;
        font-size: 0.9rem;
    }

    @media (max-width: 768px) {
        .hero-panel,
        .info-panel,
        .feature-panel,
        .story-banner,
        .feedback-hero,
        .feedback-form-shell,
        .page-banner,
        .admin-hero,
        .admin-panel,
        .admin-mini-panel {
            padding: 1.35rem;
        }

        .hero-shell {
            grid-template-columns: 1fr;
        }

        .generator-shell {
            grid-template-columns: 1fr;
        }

        .hero-title {
            font-size: 2.2rem;
        }
    }
</style>
"""


def inject_global_styles() -> None:
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
