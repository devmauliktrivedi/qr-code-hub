# qr_web_app_final_aurora.py (Definitive Fix for Expander Header and Toast Visibility)

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import streamlit as st
import qrcode
from io import BytesIO
import mysql.connector
from mysql.connector import Error
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import SquareModuleDrawer, GappedSquareModuleDrawer, CircleModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
import secrets
from streamlit_cookies_manager import EncryptedCookieManager
from contextlib import contextmanager
from datetime import datetime
import re
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
import html

# --- Load Environment Variables ---
load_dotenv()

# -------------------------
# Page Config (MUST be the first Streamlit command)
# -------------------------
st.set_page_config(page_title="QR Code Hub | By Krishna", page_icon="🔗", layout="wide")

# -------------------------
# SECURITY MODEL: ENCRYPTION (from .env file)
# -------------------------
SECRET_KEY_STR = os.getenv("SECRET_KEY")
if not SECRET_KEY_STR:
    # In a real deployed environment, this would handle the missing key more gracefully.
    st.error("FATAL ERROR: SECRET_KEY not found in .env file. Please create the .env file and add your key.", icon="🔥")
    st.stop()
SECRET_KEY = SECRET_KEY_STR.encode()
fernet = Fernet(SECRET_KEY)

def encrypt_password(password: str) -> str:
    """Encrypts a password into a scrambled string."""
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    """Decrypts a scrambled string back to the original password."""
    try:
        return fernet.decrypt(encrypted_password.encode()).decode()
    except Exception:
        # Return original if decryption fails (e.g., if it was stored unencrypted initially)
        return encrypted_password

# -------------------------
# THEME and CSS (FINAL FIXES APPLIED HERE)
# -------------------------
AURORA_THEME_CSS = """
<style>
    @keyframes slideIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .stApp {
        background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #1d4ed8);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
        color: #e2e8f0;
    }

    /* General Text Color (for headers and default markdown) */
    h1, h2, h3, h4, h5, h6, .stMarkdown, label, [data-testid="stMarkdownContainer"] p, .st-emotion-cache-1629p8f span {
        color: #f8fafc !important; /* Keep most text white against the dark background */
    }

    /* Main content card */
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.18);
        padding: 2.5rem;
        animation: slideIn 0.6s ease-out;
        transition: border 0.3s ease;
    }
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"]:hover {
        border: 1px solid rgba(167, 139, 250, 0.5);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(5px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    [data-testid="stSidebar"] h1 {
         color: #f8fafc !important; 
    }
     /* Ensure sidebar radio text is white */
    [data-testid="stSidebar"] .st-emotion-cache-1kyxreq .st-emotion-cache-1629p8f {
        color: #f8fafc !important;
    }
    /* Highlight selected page in sidebar */
    .st-emotion-cache-1kyxreq .st-emotion-cache-1gulkj5 {
        background-color: rgba(79, 70, 229, 0.5);
        border-radius: 8px;
    }

    /* *************************************************************** */
    /* *** START OF CONTRAST FIXES FOR INPUTS AND PRIMARY BUTTONS *** */
    /* *************************************************************** */

    /* Primary Button styling (LOGIN/SIGNUP/GENERATE BUTTONS) */
    .stButton>button[kind="primary"], .stFormSubmitButton>button[kind="primary"], .stDownloadButton>button {
        background: linear-gradient(90deg, #4f46e5, #7c3aed);
        color: black !important; /* CHANGED: From white to BLACK, as requested */
        box-shadow: 0 0 10px rgba(79, 70, 229, 0.5);
        border-radius: 10px; font-weight: bold; border: 1px solid transparent;
        transition: all 0.3s ease-in-out;
        min-height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .stButton>button[kind="primary"]:hover, .stFormSubmitButton>button[kind="primary"]:hover, .stDownloadButton>button:hover {
        box-shadow: 0 0 25px rgba(124, 58, 237, 0.8);
        transform: translateY(-2px);
    }
    .stButton>button[kind="primary"] *, .stFormSubmitButton>button[kind="primary"] *, .stDownloadButton>button * {
        color: black !important;
        font-weight: bold;
        letter-spacing: 0.3px;
    }
    
    /* Avatar Select Buttons (Secondary Buttons) */
    .stButton>button:not([kind="primary"]), .stFormSubmitButton>button:not([kind="primary"]) {
        background: linear-gradient(180deg, rgba(30, 41, 59, 0.96), rgba(51, 65, 85, 0.88)) !important;
        color: #FFFFFF !important; /* Keep secondary button text white */
        border: 1px solid rgba(167, 139, 250, 0.65) !important;
        border-radius: 10px;
        transition: all 0.3s ease-in-out;
        min-height: 44px;
    }
    .stButton>button:not([kind="primary"]) *, .stFormSubmitButton>button:not([kind="primary"]) * {
        color: #FFFFFF !important;
    }
    .stButton>button:not([kind="primary"]):hover, .stFormSubmitButton>button:not([kind="primary"]):hover {
        background: linear-gradient(180deg, rgba(76, 29, 149, 0.96), rgba(109, 40, 217, 0.92)) !important;
        transform: translateY(-2px);
    }

    /* --- INPUT, TEXTAREA, AND DROPDOWN VISIBILITY --- */
    
    /* 1. Style the input box background (Text Input, Text Area, Selectbox) */
    /* CHANGED: Made the background light for readability with black text */
    .stTextInput input, .stTextArea textarea, [data-testid="stSelectbox"] > div {
        background-color: #F8FAFC !important; /* Light background for black text */
        border: 1px solid #4f46e5;
        border-radius: 10px;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.4);
    }

    /* 2. Force the text you type in Text Input/Text Area to be BLACK for contrast */
    .stTextInput input, .stTextArea textarea {
        color: #000000 !important; /* CHANGED: From white to BLACK, as requested */
        -webkit-text-fill-color: #000000 !important; 
    }
    
    /* 3. Force the selected value in the Selectbox (Dropdown) to be BLACK */
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div, /* Selected value */
    [data-testid="stSelectbox"] input[role="combobox"] { /* Placeholder when nothing selected */
        color: #000000 !important; /* CHANGED: From white to BLACK */
        -webkit-text-fill-color: #000000 !important;
    }
    
    /* Style the placeholder text */
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: #9ca3af !important; /* Keep placeholder grey */
        opacity: 1;
    }

    /* 4. Target the options in the expanded dropdown list (popover) */
    /* Keep dropdown popover dark for consistency with overall theme */
    div[data-baseweb="popover"] li {
        color: #FFFFFF !important; 
        background-color: #203a43 !important; 
    }
    
    /* Style the hover state for options */
    div[data-baseweb="popover"] li:hover {
        background-color: #4f46e5 !important;
    }

    /* *************************************************************** */
    /* *** END OF CONTRAST FIXES *** */
    /* *************************************************************** */


    /* --- Expander Header Background and Text Color --- */
    [data-testid="stExpander"] summary p { 
        color: #FFFFFF !important; 
    }
    [data-testid="stExpander"] summary { 
        background-color: transparent !important; 
        border: none !important; 
        box-shadow: none !important;
    }
    [data-testid="stExpander"] summary:hover {
        background-color: rgba(255, 255, 255, 0.1) !important; 
    }
    [data-testid="stExpander"] summary:active, [data-testid="stExpander"] summary:focus {
        background-color: rgba(255, 255, 255, 0.2) !important; 
        box-shadow: none !important;
    }

    /* --- Toast/Notification Visibility Fix --- */
    div[data-baseweb="toast"] {
        background-color: #1e293b !important; 
        color: #f8fafc !important; 
        border: 1px solid #4f46e5;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    }
    div[data-baseweb="toast"] * {
        color: #f8fafc !important; 
        -webkit-text-fill-color: #f8fafc !important;
    }

    /* --- Expander Content Visibility --- */
    [data-testid="stExpander"] div[role="region"] > div {
        color: #FFFFFF !important; 
        background-color: transparent !important; 
    }
    [data-testid="stExpander"] div[role="region"] h3, 
    [data-testid="stExpander"] div[role="region"] strong,
    [data-testid="stExpander"] div[role="region"] .stMarkdown p {
        color: #FFFFFF !important;
    }


    /* Focus state for all inputs */
    .stTextInput input:focus, .stTextArea textarea:focus, [data-testid="stSelectbox"] > div:focus-within {
        border-color: #a78bfa;
        box-shadow: 0 0 10px 2px rgba(124, 58, 237, 0.5), inset 0 1px 3px rgba(0,0,0,0.4);
    }

    /* --- File Uploader Visibility --- */
    [data-testid="stFileUploader"] label, 
    [data-testid="stFileUploader"] div,
    .stFileUploader {
        color: #f8fafc !important;
    }
    [data-testid="stFileUploader"] button {
        background: linear-gradient(90deg, #4f46e5, #7c3aed) !important;
        color: black !important;
        font-weight: bold !important;
        border-radius: 10px !important;
    }
    [data-testid="stFileUploader"] button:hover {
        box-shadow: 0 0 15px rgba(124, 58, 237, 0.6) !important;
    }

    /* --- Home and feedback presentation --- */
    .section-tag {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.38rem 0.9rem;
        border-radius: 999px;
        background: rgba(148, 163, 184, 0.12);
        border: 1px solid rgba(148, 163, 184, 0.18);
        color: #bfdbfe;
        font-size: 0.78rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    .hero-panel,
    .info-panel,
    .feature-panel,
    .story-banner,
    .feedback-hero,
    .feedback-form-shell,
    .feedback-card,
    .feedback-empty {
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.18);
        box-shadow: 0 20px 45px rgba(15, 23, 42, 0.28);
    }

    .hero-panel {
        padding: 2.6rem;
        border-radius: 30px;
        background:
            radial-gradient(circle at top right, rgba(56, 189, 248, 0.28), transparent 32%),
            radial-gradient(circle at bottom left, rgba(244, 114, 182, 0.18), transparent 30%),
            linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(30, 41, 59, 0.78));
        margin-bottom: 1rem;
    }

    .hero-title {
        margin: 0.85rem 0 0.7rem;
        font-size: clamp(2.6rem, 4vw, 4.2rem);
        line-height: 1.05;
        letter-spacing: -0.04em;
        color: #ffffff;
    }

    .hero-copy,
    .info-panel p,
    .feature-panel p,
    .story-banner p,
    .feedback-hero p,
    .feedback-form-shell p {
        color: #dbeafe;
        line-height: 1.7;
    }

    .hero-stat-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.9rem;
        margin-top: 1.5rem;
    }

    .hero-stat {
        flex: 1 1 180px;
        min-width: 180px;
        padding: 1rem 1.05rem;
        border-radius: 18px;
        background: rgba(15, 23, 42, 0.45);
        border: 1px solid rgba(125, 211, 252, 0.15);
    }

    .hero-stat strong {
        display: block;
        margin-bottom: 0.25rem;
        font-size: 1.1rem;
        color: #ffffff;
    }

    .hero-stat span {
        color: #cbd5e1;
        font-size: 0.92rem;
        line-height: 1.55;
    }

    .info-panel {
        height: 100%;
        padding: 1.6rem;
        border-radius: 24px;
        background: linear-gradient(160deg, rgba(10, 18, 33, 0.92), rgba(37, 99, 235, 0.28));
    }

    .info-panel h3,
    .feature-panel h3,
    .story-banner h3,
    .feedback-form-shell h3,
    .feedback-hero h2 {
        margin: 0.8rem 0 0.55rem;
        color: #ffffff;
    }

    .use-case-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 0.65rem;
        margin-top: 1rem;
    }

    .use-case-pill {
        padding: 0.45rem 0.85rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #f8fafc;
        font-size: 0.88rem;
    }

    .feature-panel {
        height: 100%;
        padding: 1.45rem;
        border-radius: 22px;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.88), rgba(15, 23, 42, 0.64));
    }

    .feature-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        margin-bottom: 0.9rem;
        border-radius: 14px;
        background: rgba(59, 130, 246, 0.16);
        font-size: 1.45rem;
    }

    .story-banner {
        margin-top: 1.2rem;
        padding: 1.9rem;
        border-radius: 26px;
        background: linear-gradient(140deg, rgba(91, 33, 182, 0.32), rgba(15, 23, 42, 0.9) 55%, rgba(8, 47, 73, 0.8));
    }

    .feedback-hero {
        margin-bottom: 1rem;
        padding: 1.9rem;
        border-radius: 26px;
        background: linear-gradient(145deg, rgba(14, 116, 144, 0.28), rgba(15, 23, 42, 0.95) 60%, rgba(30, 64, 175, 0.32));
    }

    .feedback-form-shell {
        margin: 0.6rem 0 1rem;
        padding: 1.25rem 1.35rem;
        border-radius: 22px;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.86), rgba(30, 41, 59, 0.76));
    }

    .feedback-card {
        margin: 0.9rem 0 0.45rem;
        padding: 1.15rem 1.2rem;
        border-radius: 22px;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.92), rgba(15, 23, 42, 0.74));
    }

    .feedback-card-head {
        display: flex;
        gap: 0.95rem;
        align-items: flex-start;
    }

    .feedback-avatar {
        width: 56px;
        height: 56px;
        flex: 0 0 56px;
    }

    .feedback-avatar img,
    .feedback-avatar-fallback {
        width: 56px;
        height: 56px;
        border-radius: 16px;
        object-fit: cover;
        border: 1px solid rgba(125, 211, 252, 0.22);
    }

    .feedback-avatar-fallback {
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        color: #ffffff;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.88), rgba(236, 72, 153, 0.85));
    }

    .feedback-copy-block {
        flex: 1;
    }

    .feedback-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 0.65rem;
        align-items: center;
        margin-bottom: 0.45rem;
    }

    .feedback-author {
        font-weight: 700;
        color: #ffffff;
    }

    .feedback-time {
        color: #cbd5e1;
        font-size: 0.88rem;
    }

    .feedback-owner-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.28rem 0.72rem;
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
        margin-top: 0.8rem;
        padding: 1.4rem;
        border-radius: 20px;
        background: rgba(15, 23, 42, 0.72);
        color: #dbeafe;
        text-align: center;
    }

    @media (max-width: 768px) {
        .hero-panel,
        .info-panel,
        .story-banner,
        .feedback-hero,
        .feedback-form-shell,
        .feedback-card {
            padding: 1.35rem;
        }

        .hero-title {
            font-size: 2.25rem;
        }

        .feedback-card-head {
            flex-direction: column;
        }
    }
</style>
"""
st.markdown(AURORA_THEME_CSS, unsafe_allow_html=True)

# -------------------------
# SESSION STATE & DB CONNECTION
# -------------------------
if "user" not in st.session_state: st.session_state.user = None
if "session_id" not in st.session_state: st.session_state.session_id = None
if "page" not in st.session_state: st.session_state.page = "Home"
if "selected_avatar" not in st.session_state: st.session_state.selected_avatar = "avatars/boy.png"
if "cookie_manager_initialized" not in st.session_state: st.session_state.cookie_manager_initialized = False
if "cookies" not in st.session_state: st.session_state.cookies = None
if "qr_img_gen" not in st.session_state: st.session_state.qr_img_gen = None
if "qr_text_gen" not in st.session_state: st.session_state.qr_text_gen = None
if "qr_img_guest" not in st.session_state: st.session_state.qr_img_guest = None
if "qr_text_guest" not in st.session_state: st.session_state.qr_text_guest = None

DB_PASSWORD = os.getenv("DB_PASSWORD")
if not DB_PASSWORD:
    st.error("FATAL ERROR: DB_PASSWORD not found in .env file.", icon="🔥")
    st.stop()

@contextmanager
def get_db_connection():
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password=DB_PASSWORD, database="qr_app")
        yield conn
    except Error as e:
        st.error(f"Database connection error: {e}", icon="🔥")
        yield None
    finally:
        if 'conn' in locals() and conn and conn.is_connected():
            conn.close()

# -------------------------
# AVATAR DEFINITIONS AND NEW COLOR PALETTE
# -------------------------
AVATAR_MAP = {
    "Boy": "avatars/boy.png", "Boy 2": "avatars/boy_2.png", "Cat": "avatars/cat.png",
    "Data Analyst": "avatars/data_analyst.png", "Developer": "avatars/developer.png",
    "Doctor": "avatars/doctor.png", "Girl": "avatars/girl.png", "Girl 1": "avatars/girl_1.png",
    "Girl 3": "avatars/girl_3.png", "Kid": "avatars/kid.png", "Kid Girl": "avatars/kid_girl.png",
    "Man": "avatars/man.png", "Man 2": "avatars/man_2.png", "Ninja": "avatars/ninja.png",
    "Panda": "avatars/panda.png", "Small Boy": "avatars/small_boy.png",
    "Wizard": "avatars/wizard.png", "Women": "avatars/women.png"
}

COLOR_PALETTE = [
    ("Black", "#000000", "⬛"), ("White", "#FFFFFF", "⬜"), ("Red", "#FF0000", "🔴"),
    ("Green", "#008000", "🟢"), ("Blue", "#0000FF", "🔵"), ("Yellow", "#FFFF00", "🟡"), 
    ("Orange", "#FFA500", "🟠"), ("Purple", "#800080", "🟣"), ("Cyan", "#00FFFF", "🔷"),
    ("Magenta", "#FF00FF", "🟪"), ("Gray", "#808080", "◼️"), ("Brown", "#A52A2A", "🟫"),
    ("Pink", "#FFC0CB", "🌸"), ("Light Blue", "#ADD8E6", "🔹"), ("Light Green", "#90EE90", "💚"),
    ("Gold", "#FFD700", "⭐"), ("Crimson", "#DC143C", "🔴"), ("Hot Pink", "#FF1493", "🌺"),
    ("Lime", "#7FFF00", "🟩"), ("Orange Red", "#FF4500", "🟧"), ("Sea Green", "#2E8B57", "🌿"),
]

palette_name = [item[0] for item in COLOR_PALETTE]
palette_hex = [item[1] for item in COLOR_PALETTE]
palette_display = [f"{name} {emoji} ({hex_val})" for name, hex_val, emoji in COLOR_PALETTE]

# -------------------------
# Core Helper Functions 
# -------------------------
# Initialize Cookie Manager once per session (not cached to avoid widget warning)
def init_cookie_manager():
    """Initialize the encrypted cookie manager once per session using session state."""
    if st.session_state.cookie_manager_initialized and st.session_state.cookies is not None:
        return st.session_state.cookies
    
    try:
        cookies = EncryptedCookieManager(prefix="qr_app_secure_", password=SECRET_KEY_STR)
        # Don't check .ready() here as it might not be initialized yet
        st.session_state.cookies = cookies
        st.session_state.cookie_manager_initialized = True
        return cookies
    except Exception as e:
        # Silently handle cookie manager issues
        return None

# ## FIXED: Replaced @st.cache with @st.cache_data ##
@st.cache_data(ttl=3600)
def generate_qr_img(data, fg_color, bg_color, box_size=10, border=4, style="square"):
    drawer_map = {"square": SquareModuleDrawer(), "gapped": GappedSquareModuleDrawer(), "circle": CircleModuleDrawer()}
    drawer = drawer_map.get(style, SquareModuleDrawer())
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=box_size, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(
        image_factory=StyledPilImage, 
        module_drawer=drawer, 
        color_mask=SolidFillColorMask(
            front_color=tuple(int(fg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)), 
            back_color=tuple(int(bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        )
    )
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def time_ago(dt):
    if not dt: return ""
    # Ensure dt is offset-naive if it's offset-aware, matching datetime.now()
    if dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None:
        dt = dt.replace(tzinfo=None) # Make dt offset-naive
    diff = datetime.now() - dt # datetime.now() is offset-naive
    seconds = diff.total_seconds()
    if seconds < 0: return "in the future" # Handle potential timezone issues
    if seconds < 60: return "just now"
    minutes = seconds / 60
    if minutes < 60: return f"{int(minutes)} min ago"
    hours = minutes / 60
    if hours < 24: return f"{int(hours)} hr ago"
    days = hours / 24
    if days < 30: return f"{int(days)} {'day' if int(days) == 1 else 'days'} ago"
    return dt.strftime("%b %d, %Y")


def check_password_strength(password):
    score = 0
    if len(password) >= 8: score += 1
    if re.search(r"\d", password): score += 1
    if re.search(r"[A-Z]", password): score += 1
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): score += 1
    strength_map = {0: (25, "Very Weak", "#ef4444"), 1: (25, "Very Weak", "#ef4444"), 2: (50, "Weak", "#f97316"), 3: (75, "Medium", "#f59e0b"), 4: (100, "Strong", "#22c55e")}
    percent, strength, color = strength_map.get(score, (0, "Very Weak", "red"))
    return percent, (strength, color)

def get_initials(name):
    parts = [part[0].upper() for part in (name or "").split() if part]
    return "".join(parts[:2]) or "QR"

def render_feedback_card(comment, is_owner=False):
    username = comment.get("username") or "Community Member"
    safe_username = html.escape(username)
    safe_time = html.escape(time_ago(comment.get("created_at")))
    safe_text = html.escape(comment.get("comment_text") or "").replace("\n", "<br>")
    owner_badge = "<span class='feedback-owner-badge'>Your feedback</span>" if is_owner else ""

    with st.container(border=True):
        avatar_col, content_col = st.columns([0.14, 0.86], gap="small")

        with avatar_col:
            if comment.get("profile_image"):
                st.image(bytes(comment["profile_image"]), width=56)
            else:
                st.markdown(
                    f"<div class='feedback-avatar-fallback'>{html.escape(get_initials(username))}</div>",
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
                f'<div class="feedback-text">{safe_text}</div>',
                unsafe_allow_html=True,
            )

# -------------------------
# DB & Auth Functions
# -------------------------
def signup(username, password, profile_img_bytes):
    if not username or not password: st.warning("Username and password are required."); return
    percent, (strength, _) = check_password_strength(password)
    if percent < 75: st.warning("Password is too weak."); return
    with get_db_connection() as conn:
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE username=%s", (username,))
            if cur.fetchone(): st.warning(f"Username **{username}** already exists."); return
            encrypted_pw = encrypt_password(password)
            cur.execute("INSERT INTO users (username, encrypted_password, profile_image) VALUES (%s, %s, %s)", (username, encrypted_pw, profile_img_bytes))
            conn.commit()
            st.success("Account created successfully! Please log in."); st.balloons()
        else: st.error("Database connection failed. Cannot sign up.")

def login(username, password):
    with get_db_connection() as conn:
        if conn:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM users WHERE username=%s", (username,))
            user = cur.fetchone()
            if user:
                decrypted_pw = decrypt_password(user.get('encrypted_password', ''))
                if decrypted_pw and password == decrypted_pw:
                    token = secrets.token_hex(32)
                    cur.execute("INSERT INTO sessions (user_id, token) VALUES (%s, %s)", (user["id"], token))
                    st.session_state.user = user
                    st.session_state.session_id = cur.lastrowid
                    conn.commit()
                    
                    # Clear any previous user's QR data for security
                    st.session_state["qr_img_gen"] = None
                    st.session_state["qr_text_gen"] = None
                    st.session_state["qr_img_guest"] = None
                    st.session_state["qr_text_guest"] = None
                    
                    # Try to save token to cookies (non-critical if it fails)
                    try:
                        cookies = init_cookie_manager()
                        if cookies is not None:
                            try:
                                if cookies.ready():
                                    cookies["qr_token"] = token
                                    cookies.save()
                            except Exception:
                                pass  # Cookie save failed, but user is logged in via session state
                    except Exception:
                        pass  # Cookie manager error, but user is logged in
                    
                    st.success(f"🎉 Welcome back, {user['username']}!"); st.rerun()
                else: st.error("Incorrect username or password.")
            else: st.error("Incorrect username or password.")
        else: st.error("Database connection failed. Cannot log in.")

def auto_login():
    try:
        if st.session_state.get('user'):
            return  # User already logged in
        
        cookies = init_cookie_manager()
        if cookies is None:
            return  # Cookie manager failed to initialize
        
        try:
            if not cookies.ready():
                return  # Cookies not ready yet
        except Exception:
            return  # Cookie manager not ready, will retry on next rerun
        
        token = cookies.get("qr_token")
        if token:
            with get_db_connection() as conn:
                if conn:
                    cur = conn.cursor(dictionary=True)
                    cur.execute("SELECT u.*, s.id AS session_id FROM sessions s JOIN users u ON s.user_id = u.id WHERE s.token = %s AND s.logout_time IS NULL", (token,))
                    res = cur.fetchone()
                    if res:
                        st.session_state.user = {k: v for k, v in res.items() if k != "session_id"}
                        st.session_state.session_id = res.get("session_id")
    except Exception:
        pass  # Silent fail for auto-login, will show login page

def logout():
    session_id = st.session_state.get("session_id")
    if session_id:
        with get_db_connection() as conn:
            if conn:
                cur = conn.cursor()
                cur.execute("UPDATE sessions SET logout_time=NOW() WHERE id=%s", (session_id,))
                conn.commit()
    
    try:
        cookies = init_cookie_manager()
        if cookies is not None:
            try:
                if cookies.ready():
                    cookies["qr_token"] = ""
                    cookies.save()
            except Exception:
                pass  # Cookie clearing failed, but session is logged out
    except Exception:
        pass  # Cookie manager error, but continue with logout
    
    # Clear all user-specific session data for security
    st.session_state.user = None
    st.session_state.session_id = None
    # Clear any QR code data from previous user
    st.session_state["qr_img_gen"] = None
    st.session_state["qr_text_gen"] = None
    st.session_state["qr_img_guest"] = None
    st.session_state["qr_text_guest"] = None
    st.success("Logged out successfully!"); st.rerun()

def update_profile_db(user_id, new_username, new_password, new_profile_bytes):
    with get_db_connection() as conn:
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE username=%s AND id<>%s", (new_username, user_id))
            if cur.fetchone(): st.error("Username already taken."); return
            encrypted_pw = encrypt_password(new_password)
            cur.execute("UPDATE users SET username=%s, encrypted_password=%s, profile_image=%s WHERE id=%s", (new_username, encrypted_pw, new_profile_bytes, user_id))
            conn.commit()
            st.success("Profile updated successfully!")
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
            st.session_state.user = cur.fetchone(); st.rerun()
        else: st.error("Database connection failed. Cannot update profile.")

# ## FIXED: Replaced @st.cache with @st.cache_data ##
@st.cache_data(ttl=60)
def load_comments():
    with get_db_connection() as conn:
        if conn:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT c.id, u.username, u.profile_image, c.comment_text, c.created_at, c.user_id FROM comments c JOIN users u ON c.user_id = u.id ORDER BY c.created_at DESC")
            return cur.fetchall()
    return []

# ## FIXED: Replaced @st.cache with @st.cache_data ##
@st.cache_data(ttl=60)
def load_user_qrs(user_id):
    if not user_id: return []
    with get_db_connection() as conn:
        if conn:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM qr_codes WHERE user_id=%s AND deleted_at IS NULL ORDER BY created_at DESC", (user_id,))
            return cur.fetchall()
    return []

def post_comment(user_id, comment_text):
    cleaned_text = comment_text.strip()
    if not cleaned_text: st.error("Comment cannot be empty."); return False
    with get_db_connection() as conn:
        if conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO comments (user_id, comment_text) VALUES (%s, %s)", (user_id, cleaned_text))
            conn.commit(); load_comments.clear(); return True
    return False

def update_comment_db(comment_id, user_id, new_text):
    cleaned_text = new_text.strip()
    if not cleaned_text: st.error("Edited comment cannot be empty."); return False
    with get_db_connection() as conn:
        if conn and user_id:
            cur = conn.cursor()
            cur.execute("SELECT id FROM comments WHERE id=%s AND user_id=%s", (comment_id, user_id))
            if not cur.fetchone():
                st.error("You can edit only your own feedback.")
                return False
            cur.execute("UPDATE comments SET comment_text=%s WHERE id=%s AND user_id=%s", (cleaned_text, comment_id, user_id))
            conn.commit(); load_comments.clear(); return True
    return False


def delete_qr_db(qr_id, user_id):
    """Soft delete QR code - only for owner"""
    with get_db_connection() as conn:
        if conn:
            cur = conn.cursor()
            cur.execute("UPDATE qr_codes SET deleted_at=NOW() WHERE id=%s AND user_id=%s", (qr_id, user_id))
            conn.commit()
            load_user_qrs.clear()
            # Clear QR preview session state to avoid stale preview
            if 'user' in st.session_state:
                user_id_str = str(st.session_state.user['id'])
                for key in list(st.session_state.keys()):
                    if 'qr_img_' in key and user_id_str in key:
                        del st.session_state[key]
                    elif 'qr_text_' in key and user_id_str in key:
                        del st.session_state[key]
            st.session_state["qr_img_gen"] = None
            st.session_state["qr_text_gen"] = None
            st.session_state["qr_img_guest"] = None
            st.session_state["qr_text_guest"] = None
            return cur.rowcount > 0
    return False


def delete_comment_db(comment_id, user_id):
    with get_db_connection() as conn:
        if conn and user_id:
            cur = conn.cursor()
            cur.execute("DELETE FROM comments WHERE id=%s AND user_id=%s", (comment_id, user_id))
            conn.commit()
            if cur.rowcount:
                load_comments.clear()
                return True
            st.error("You can delete only your own feedback.")
    return False

# --------------------------------------------------------------------------------------------------
# UI Components
# --------------------------------------------------------------------------------------------------
def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun()

def home_ui():
    st.markdown(
        """
        <div class="hero-panel">
            <span class="section-tag">Premium QR Experience</span>
            <h1 class="hero-title">Make every scan feel intentional.</h1>
            <p class="hero-copy">
                Create polished QR codes for menus, event invites, portfolios, payment links, and everyday sharing.
                Save the ones you love, refine the look, and keep every scan feeling clean, bold, and ready to use.
            </p>
            <div class="hero-stat-row">
                <div class="hero-stat">
                    <strong>Custom Looks</strong>
                    <span>Adjust colors, shape, and size until the QR matches your vibe.</span>
                </div>
                <div class="hero-stat">
                    <strong>Fast Downloads</strong>
                    <span>Generate in seconds and grab a crisp PNG without extra steps.</span>
                </div>
                <div class="hero-stat">
                    <strong>Personal Space</strong>
                    <span>Signed-in users can keep favorite QR codes neatly organized.</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.user:
        cols_cta = st.columns(2)
        if cols_cta[0].button("Start Generating 🔗", type="primary", use_container_width=True): navigate_to("QR Generator")
        if cols_cta[1].button("View My Saved Codes 📂", type="primary", use_container_width=True): navigate_to("My QR Codes")
    else:
        cols_cta = st.columns(2)
        if cols_cta[0].button("Quick QR Generator ⚡", type="primary", use_container_width=True, key="home_quick_qr"): navigate_to("Quick QR Code")
        if cols_cta[1].button("Login / Sign Up 🔑", type="primary", use_container_width=True, key="home_login"): navigate_to("Login")

    col_story, col_preview = st.columns([1.15, 0.85], gap="large")
    with col_story:
        st.markdown(
            """
            <div class="info-panel">
                <span class="section-tag">Built for real moments</span>
                <h3>From first idea to final scan</h3>
                <p>
                    Whether you are designing a cafe table card, a wedding invite, a product label,
                    or your personal portfolio link, this space helps you move from idea to scan-ready
                    design without feeling cluttered.
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
                <span class="section-tag">What makes it shine</span>
                <h3>Less noise. More personality.</h3>
                <p>
                    Clean controls, strong contrast, and a simple saved history help the experience feel smooth
                    whether you want one quick code or a full collection ready for later.
                </p>
                <div class="use-case-grid">
                    <span class="use-case-pill">One-click download</span>
                    <span class="use-case-pill">Simple customization</span>
                    <span class="use-case-pill">Saved history</span>
                    <span class="use-case-pill">Readable previews</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 0.7rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.markdown(
        """
        <div class="feature-panel">
            <div class="feature-icon">🎨</div>
            <h3>Style With Confidence</h3>
            <p>Mix color, shape, and spacing to make the code feel branded instead of generic.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col2.markdown(
        """
        <div class="feature-panel">
            <div class="feature-icon">⚡</div>
            <h3>Move Fast</h3>
            <p>Go from text or link to download-ready QR in a few clicks with a clear preview.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col3.markdown(
        """
        <div class="feature-panel">
            <div class="feature-icon">💬</div>
            <h3>Stay Connected</h3>
            <p>Share feedback, keep your favorites, and make the app feel more personal over time.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="story-banner">
            <span class="section-tag">Made for standout moments</span>
            <h3>Turn one scan into a smooth connection.</h3>
            <p>
                From cafe tables and product cards to event invites and personal portfolios,
                this space is designed to help your QR codes feel clean, memorable, and ready to share.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def visual_avatar_selector(key_prefix=""):
    st.subheader("Choose an Avatar") 
    if f"{key_prefix}_selected_avatar" not in st.session_state:
        st.session_state[f"{key_prefix}_selected_avatar"] = AVATAR_MAP["Boy"]

    cols = st.columns(6)
    for i, (name, path) in enumerate(AVATAR_MAP.items()):
        with cols[i % 6]:
            try:
                st.image(path, width=80)
                # Use secondary button style for Select buttons
                if st.button(f"Select", key=f"{key_prefix}_select_avatar_{name}", use_container_width=True):
                    st.session_state[f"{key_prefix}_selected_avatar"] = path
                    st.toast("Avatar selected!", icon="👍") # Corrected Message
            except FileNotFoundError:
                 st.error(f"!") # Simplified error for missing file
            except Exception as e:
                 st.error(f"Error: {e}") # General error
    
    st.markdown("---")
    st.markdown(f"**Selected Avatar:**")
    st.image(st.session_state[f"{key_prefix}_selected_avatar"], width=100)
    st.markdown("---")

def signup_ui():
    st.header("📝 Create Your Account")
    new_username = st.text_input("Username")
    new_password = st.text_input("Password", type="password")
    percent, (strength, color) = check_password_strength(new_password)
    st.progress(percent / 100, text=f"Password Strength: {strength}")
    
    # Expander styling fixed in CSS
    with st.expander("🎨 Choose your Avatar (Click to expand)"):
        visual_avatar_selector(key_prefix="signup")
    
    new_profile_upl = st.file_uploader("Or upload your own image:", type=["png", "jpg", "jpeg"])

    if st.button("Sign Up", type="primary", use_container_width=True):
        if not new_username or not new_password:
            st.warning("Please fill in username and password.")
            return

        avatar_bytes = None
        if new_profile_upl:
            avatar_bytes = new_profile_upl.getvalue()
        else:
            selected_path = st.session_state.get("signup_selected_avatar", AVATAR_MAP["Boy"])
            try:
                # Assuming 'avatars' folder is in the same directory as the script
                # If not, provide the full path
                base_path = os.path.dirname(__file__) 
                full_path = os.path.join(base_path, selected_path)
                with open(full_path, "rb") as f:
                    avatar_bytes = f.read()
            except FileNotFoundError:
                st.error(f"Default avatar file not found: {selected_path}. Make sure the 'avatars' folder exists in the same directory as the script and contains the image file.")
                return
            except Exception as e:
                st.error(f"Error reading avatar file: {e}")
                return
        
        signup(new_username, new_password, avatar_bytes)

def account_ui():
    st.header("👤 My Account Settings")
    user = st.session_state.user
    decrypted_pw = decrypt_password(user.get('encrypted_password', ''))

    colA, colB = st.columns([1, 2])
    with colA:
        st.subheader("Current Avatar")
        if user.get("profile_image"):
            st.image(bytes(user["profile_image"]), use_container_width=True)
        else:
            st.markdown("No avatar set.")
            
    with colB:
        st.subheader("Update Details")
        new_username = st.text_input("Username", value=user["username"])
        new_password = st.text_input("New Password", type="password", value=decrypted_pw, help="Enter a new password or leave the current one to keep it.")
        
        # Expander styling fixed in CSS
        with st.expander("🎨 Change your Avatar (Click to expand)"):
            visual_avatar_selector(key_prefix="update")

        new_profile_upl = st.file_uploader("Or upload a new image:", type=["png", "jpg", "jpeg"])
        
        if st.button("Save Changes", type="primary", use_container_width=True):
            new_profile_bytes = None
            if new_profile_upl:
                new_profile_bytes = new_profile_upl.getvalue()
            else:
                selected_path = st.session_state.get("update_selected_avatar", None)
                if selected_path:
                    try:
                        # Assuming 'avatars' folder is in the same directory as the script
                        base_path = os.path.dirname(__file__)
                        full_path = os.path.join(base_path, selected_path)
                        with open(full_path, "rb") as f:
                            new_profile_bytes = f.read()
                    except FileNotFoundError:
                        st.error(f"Selected avatar file not found: {selected_path}. Reverting to old avatar.")
                        new_profile_bytes = user.get("profile_image")
                    except Exception as e:
                         st.error(f"Error reading avatar file: {e}")
                         new_profile_bytes = user.get("profile_image") # Fallback
                else:
                    new_profile_bytes = user.get("profile_image")

            if not new_password.strip():
                st.error("Password cannot be empty!")
            else:
                update_profile_db(user["id"], new_username, new_password, new_profile_bytes)

def login_ui():
    st.header("🔑 Login to Your Account")
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    if st.button("Login", type="primary", use_container_width=True, key="login_btn"):
        if username.strip() and password.strip():
            login(username, password)
        else:
            st.warning("Please enter username and password.")

    st.info("New user? Use the 'Sign Up' link in the sidebar.")

def qr_ui(page_key: str, simple=False):
    st.header("✨ Ultimate QR Code Generator" if not simple else "🔗 Quick QR Code")
    st.markdown("---")
    col_main, col_preview = st.columns([0.6, 0.4], gap="large")
    
    # Use user-specific keys to prevent data leaking between users
    user_id = st.session_state.user["id"] if st.session_state.user else "guest"
    qr_img_key = f"qr_img_{page_key}_{user_id}"
    qr_text_key = f"qr_text_{page_key}_{user_id}"
    
    with col_main:
        st.subheader("1. Enter Content")
        user_input = st.text_area("Enter Text or Link:", placeholder="https://example.com or Hello World!", height=100, key=f"text_{page_key}_{user_id}")
        
        # Customization Controls
        if not simple:
            # Expander styling fixed in CSS
            with st.expander("🎨 Colors, Shape, and Size", expanded=True):
                cols_colors = st.columns(3)
                # Selectbox uses new CSS fix for text visibility
                fg_idx = cols_colors[0].selectbox("Foreground Color:", range(len(palette_display)), index=palette_name.index("Black"), format_func=lambda i: palette_display[i], key=f"fg_{page_key}_{user_id}")
                bg_idx = cols_colors[1].selectbox("Background Color:", range(len(palette_display)), index=palette_name.index("White"), format_func=lambda i: palette_display[i], key=f"bg_{page_key}_{user_id}")
                qr_style = cols_colors[2].selectbox("Module Shape:", ["square", "gapped", "circle"], index=0, key=f"style_{page_key}_{user_id}")
                cols_size = st.columns(2)
                box_size = cols_size[0].slider("Pixel Density", 5, 20, 10, key=f"box_{page_key}_{user_id}")
                border = cols_size[1].slider("Outer Margin", 1, 10, 4, key=f"border_{page_key}_{user_id}")
        else:
            # Simple Mode defaults
            fg_idx, bg_idx, qr_style, box_size, border = palette_name.index("Black"), palette_name.index("White"), "square", 10, 4
            
        fg_color, bg_color = palette_hex[fg_idx], palette_hex[bg_idx]
        fg_name, bg_name = palette_name[fg_idx], palette_name[bg_idx] 
        
        if st.button("🚀 Generate QR Code", key=f"gen_{page_key}_{user_id}", type="primary", use_container_width=True):
            if user_input.strip():
                byte_im = generate_qr_img(user_input, fg_color, bg_color, box_size, border, qr_style)
                st.session_state[qr_img_key] = byte_im
                st.session_state[qr_text_key] = user_input
                st.toast("QR Code Generated!", icon="✅") # Toast visibility fixed in CSS
                
                if st.session_state.user and not simple:
                    with get_db_connection() as conn:
                        if conn:
                            cur = conn.cursor()
                            # Ensure all required fields are passed for insertion
                            cur.execute("INSERT INTO qr_codes (user_id, qr_text, fg_color_name, bg_color_name, qr_style, box_size, border) VALUES (%s,%s,%s,%s,%s,%s,%s)", 
                                        (st.session_state.user["id"], user_input, fg_name, bg_name, qr_style, box_size, border))
                            conn.commit()
                            # Correct clear method call if caching user-specific data
                            load_user_qrs.clear() # Clear cache generally, or adjust if needed for args
                            st.toast("Saved to your account!", icon="💾") # Toast visibility fixed in CSS
            elif not user_input.strip():
                st.warning("Please enter text or a link.")
            
    with col_preview:
        st.subheader("2. Preview & Download")
        if st.session_state.get(qr_img_key):
            qr_image = st.session_state[qr_img_key]
            qr_text_preview = st.session_state.get(qr_text_key, "")
            st.image(qr_image, caption=qr_text_preview[:40] + "...", use_container_width=True)
            # Use secondary button style for Download
            st.download_button("⬇️ Download as PNG", data=qr_image, file_name=f"qr_code_{page_key}.png", mime="image/png", key=f"dl_{page_key}_{user_id}", use_container_width=True)
        else: st.info("Your generated QR Code will appear here.")

def display_feedback():
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
                if post_comment(current_user_id, comment_text):
                    st.success("Feedback posted successfully!")
                    st.rerun()
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
        if edit_state_key not in st.session_state:
            st.session_state[edit_state_key] = False

        action_cols = st.columns([1.4, 1, 4])
        if action_cols[0].button("Edit Feedback", key=f"edit_toggle_{comment['id']}", use_container_width=True):
            st.session_state[edit_state_key] = not st.session_state[edit_state_key]
            if st.session_state[edit_state_key]:
                st.session_state[edit_draft_key] = comment["comment_text"]
            else:
                st.session_state.pop(edit_draft_key, None)
            st.rerun()

        if action_cols[1].button("Delete", key=f"delete_cmt_{comment['id']}", use_container_width=True):
            st.session_state.pop(edit_state_key, None)
            st.session_state.pop(edit_draft_key, None)
            if delete_comment_db(comment["id"], current_user_id):
                st.success("Feedback deleted.")
                st.rerun()

        if st.session_state.get(edit_state_key):
            st.markdown("Update your feedback below.")
            with st.form(key=f"edit_form_{comment['id']}"):
                edited_text = st.text_area(
                    "Edit comment:",
                    key=edit_draft_key,
                    height=90,
                )
                col_btn1, col_btn2 = st.columns(2)
                if col_btn1.form_submit_button("Save Update", type="primary", use_container_width=True):
                    if update_comment_db(comment["id"], current_user_id, edited_text):
                        st.session_state[edit_state_key] = False
                        st.session_state.pop(edit_draft_key, None)
                        st.success("Feedback updated.")
                        st.rerun()
                if col_btn2.form_submit_button("Cancel", use_container_width=True):
                    st.session_state[edit_state_key] = False
                    st.session_state.pop(edit_draft_key, None)
                    st.rerun()


def display_user_qrs():
    st.header("📁 My Saved QR Codes")
    if not st.session_state.user:
        st.error("You must be logged in to view your saved codes."); return
    
    # Get current user's ID for security validation
    current_user_id = st.session_state.user['id']
    
    user_qrs = load_user_qrs(current_user_id)
    if not user_qrs: st.info("You haven't saved any QR codes yet.")
    else:
        for qr in user_qrs:
            # SECURITY: Verify the QR code belongs to the current user before displaying
            if qr.get('user_id') != current_user_id:
                st.error("Security Error: Unauthorized access to QR code data")
                continue
            
            with st.container(border=True):
                col1, col2 = st.columns([1, 3])
                
                try:
                    fg_hex = palette_hex[palette_name.index(qr.get('fg_color_name', 'Black'))]
                    bg_hex = palette_hex[palette_name.index(qr.get('bg_color_name', 'White'))]
                except ValueError:
                    fg_hex, bg_hex = "#000000", "#FFFFFF"

                # Check if box_size and border are None or invalid, provide defaults
                box_size = qr.get('box_size') if isinstance(qr.get('box_size'), int) else 10
                border = qr.get('border') if isinstance(qr.get('border'), int) else 4
                qr_style = qr.get('qr_style', 'square')


                byte_im = generate_qr_img(qr['qr_text'], fg_hex, bg_hex, box_size, border, qr_style)
                
                with col1:
                    st.image(byte_im, width=150)
                    st.download_button("⬇️ Download", data=byte_im, file_name=f"my_qr_{qr['id']}.png", mime="image/png", key=f"dl_myqr_{qr['id']}", use_container_width=True)
                with col2:
                    st.caption(f"Created: {time_ago(qr['created_at'])}")
                    st.code(qr['qr_text'][:50] + ('...' if len(qr['qr_text']) > 50 else ''), language='text')
                    st.markdown(f"**Details:** {qr.get('fg_color_name')} on {qr.get('bg_color_name')} | Style: {qr_style}")

                col_btn1, col_btn2 = st.columns(2)
                if col_btn1.button("🗑️ Delete QR", key=f"delete_qr_{qr['id']}", use_container_width=True):
                    if delete_qr_db(qr['id'], current_user_id):
                        st.success("QR deleted successfully!")
                        st.rerun()
                if col_btn2.button("Clear All", key=f"clear_all_{qr['id']}", use_container_width=True):
                    with get_db_connection() as conn:
                        if conn:
                            cur = conn.cursor()
                            cur.execute("UPDATE qr_codes SET deleted_at=NOW() WHERE user_id=%s", (current_user_id,))
                            conn.commit()
                            load_user_qrs.clear()
                            st.success("All QR history cleared!")
                            st.rerun()


# -------------------------
# Main App Structure and Routing
# -------------------------
# Initialize cookie manager early (only runs once per session due to session state check)
# Only call auto_login if user is not already logged in
try:
    if st.session_state.user is None:
        auto_login()
except Exception:
    pass  # Silently ignore auto-login errors, user will see login page

st.sidebar.markdown(f"<h1>🔗 QR Code Hub</h1>", unsafe_allow_html=True)
st.sidebar.markdown("---")

if st.session_state.user:
    nav_pages = ["Home", "QR Generator", "My QR Codes", "Feedback", "My Account", "Logout"]
    nav_icons = ["🏠", "🔧", "📁", "💬", "⚙️", "🚪"]
else:
    nav_pages = ["Home", "Quick QR Code", "Feedback", "Login", "Sign Up"]
    nav_icons = ["🏠", "⚡", "💬", "🔑", "📝"]

nav_options = [f"{icon} {page}" for icon, page in zip(nav_icons, nav_pages)]
try:
    # Check if st.session_state.page is a valid page, otherwise default to "Home"
    if st.session_state.page in nav_pages:
        current_index = nav_pages.index(st.session_state.page)
    else:
        st.session_state.page = "Home" # Reset to default if invalid
        current_index = 0
except ValueError:
    st.session_state.page = "Home" # Reset to default if index fails
    current_index = 0

selected_nav = st.sidebar.radio("Navigation", nav_options, index=current_index, label_visibility="collapsed")
selected_page = selected_nav.split(" ", 1)[1]

if selected_page != st.session_state.page:
    st.session_state.page = selected_page
    st.rerun()

# --- Page Routing ---
if st.session_state.page == "Home": home_ui()
elif st.session_state.page == "Sign Up": signup_ui()
elif st.session_state.page == "Login": login_ui()
elif st.session_state.page == "Logout": logout()
elif st.session_state.page == "QR Generator" and st.session_state.user: qr_ui("gen", simple=False)
elif st.session_state.page == "Quick QR Code": qr_ui("guest", simple=True)
elif st.session_state.page == "Feedback": display_feedback()
elif st.session_state.page == "My Account" and st.session_state.user: account_ui()
elif st.session_state.page == "My QR Codes" and st.session_state.user: display_user_qrs()
else:
    # Fallback for any invalid page state or unauthorized access
    if not st.session_state.user and st.session_state.page in ["My Account", "My QR Codes", "QR Generator"]:
         st.warning("You must be logged in to access this page.")
         login_ui()
    else:
        home_ui() # Default to home page


# python -m streamlit run qr_web_app_interactive.py(to run the code )
