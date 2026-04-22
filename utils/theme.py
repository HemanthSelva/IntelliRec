"""
IntelliRec Theme Utility v5.0 — iOS 26 Glassmorphism System
Manages light/dark/system theme and injects all global CSS.
"""
import streamlit as st


def get_palette(theme: str) -> dict:
    if theme == 'light':
        return {
            'page_bg': '#f4f6fb',
            # iOS 26 glass tokens (light)
            'glass_bg':          'rgba(255, 255, 255, 0.62)',
            'glass_bg_strong':   'rgba(255, 255, 255, 0.82)',
            'glass_bg_subtle':   'rgba(255, 255, 255, 0.38)',
            'glass_border':      'rgba(255, 255, 255, 0.75)',
            'glass_border_soft': 'rgba(99, 102, 241, 0.15)',
            'glass_shadow':      '0 4px 24px rgba(0,0,0,0.08), 0 1px 4px rgba(0,0,0,0.04)',
            'glass_shadow_lg':   '0 8px 40px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.06)',
            'glass_blur':        'blur(20px)',
            'glass_blur_strong': 'blur(32px)',
            'nav_active_bg':     'linear-gradient(135deg, #6366f1, #8b5cf6)',
            'nav_active_text':   '#ffffff',
            'sidebar_bg': 'rgba(248, 248, 252, 0.88)',
            'sidebar_btn_bg': 'rgba(255, 255, 255, 0.55)', 'sidebar_btn_text': '#1a1a2e', 'sidebar_btn_border': 'rgba(99,102,241,0.18)',
            'card_bg': '#ffffff', 'card_bg_hover': '#f0f2ff',
            'input_bg': '#ffffff', 'stat_card_bg': '#ffffff',
            'text_primary': '#0f0f1a', 'text_secondary': '#4b5563',
            'text_muted': '#9ca3af', 'text_link': '#6366f1',
            'border': '#e5e7eb', 'border_focus': '#6366f1',
            'btn_bg': '#ffffff', 'btn_text': '#0f0f1a', 'btn_border': '#d1d5db',
            'filter_btn_bg': '#f3f4f6', 'filter_btn_text': '#1a1a2e', 'filter_btn_active': '#6366f1',
            'nav_btn_bg': '#f3f4f6', 'nav_btn_text': '#1a1a2e',
            'nav_btn_active': '#6366f1', 'nav_btn_active_text': '#ffffff',
            'accent': '#6366f1', 'accent_soft': '#e0e7ff',
            'price_color': '#6366f1', 'star_color': '#f59e0b',
            'icon_bg_purple': '#eef2ff', 'icon_bg_cyan': '#ecfeff',
            'icon_bg_green': '#dcfce7', 'icon_bg_amber': '#fffbeb', 'icon_bg_pink': '#fdf2f8',
            'badge_electronics_bg': '#dbeafe', 'badge_electronics_text': '#1d4ed8',
            'badge_kitchen_bg': '#d1fae5', 'badge_kitchen_text': '#065f46',
            'badge_positive_bg': '#d1fae5', 'badge_positive_text': '#065f46',
            'badge_mixed_bg': '#fef3c7', 'badge_mixed_text': '#92400e',
            'badge_critical_bg': '#fee2e2', 'badge_critical_text': '#991b1b',
            'surface_bg': 'rgba(255,255,255,0.92)', 'shadow': '0 2px 8px rgba(99,102,241,0.08)',
            'dataset_bg': '#fffbeb', 'dataset_border': '#fde68a', 'dataset_text': '#92400e',
            'danger_bg': '#fef2f2', 'danger_border': '#fca5a5', 'danger_text': '#dc2626',
            'action_btn_bg': '#6366f1', 'action_btn_text': '#ffffff', 'action_btn_border': '#4f46e5',
            'secondary_btn_bg': '#f3f4f6', 'secondary_btn_text': '#1a1a2e', 'secondary_btn_border': '#d1d5db',
            'danger_btn_bg': '#dc2626', 'danger_btn_text': '#ffffff',
        }
    else:
        return {
            'page_bg': '#0f0f1a',
            # iOS 26 glass tokens (dark)
            'glass_bg':          'rgba(20, 20, 40, 0.68)',
            'glass_bg_strong':   'rgba(25, 25, 50, 0.88)',
            'glass_bg_subtle':   'rgba(20, 20, 40, 0.42)',
            'glass_border':      'rgba(255, 255, 255, 0.08)',
            'glass_border_soft': 'rgba(99, 102, 241, 0.22)',
            'glass_shadow':      '0 4px 24px rgba(0,0,0,0.35), 0 1px 4px rgba(0,0,0,0.2)',
            'glass_shadow_lg':   '0 8px 40px rgba(0,0,0,0.5), 0 2px 8px rgba(0,0,0,0.3)',
            'glass_blur':        'blur(20px)',
            'glass_blur_strong': 'blur(32px)',
            'nav_active_bg':     'linear-gradient(135deg, #6366f1, #8b5cf6)',
            'nav_active_text':   '#ffffff',
            'sidebar_bg': 'rgba(18, 18, 36, 0.92)',
            'sidebar_btn_bg': 'rgba(255, 255, 255, 0.06)', 'sidebar_btn_text': '#e2e8f0', 'sidebar_btn_border': 'rgba(255,255,255,0.1)',
            'card_bg': '#1e1e35', 'card_bg_hover': '#26263f',
            'input_bg': '#1e1e35', 'stat_card_bg': '#1e1e35',
            'text_primary': '#f1f5f9', 'text_secondary': '#a0aec0',
            'text_muted': '#6b7280', 'text_link': '#a5b4fc',
            'border': '#2d2d4a', 'border_focus': '#6366f1',
            'btn_bg': '#2d2d44', 'btn_text': '#f1f5f9', 'btn_border': '#4a4a6a',
            'filter_btn_bg': '#2d2d44', 'filter_btn_text': '#f1f5f9', 'filter_btn_active': '#6366f1',
            'nav_btn_bg': '#2d2d44', 'nav_btn_text': '#f1f5f9',
            'nav_btn_active': '#6366f1', 'nav_btn_active_text': '#ffffff',
            'accent': '#6366f1', 'accent_soft': '#312e81',
            'price_color': '#a5b4fc', 'star_color': '#f59e0b',
            'icon_bg_purple': '#1e1a4a', 'icon_bg_cyan': '#0c2a3a',
            'icon_bg_green': '#0d3325', 'icon_bg_amber': '#2d1f00', 'icon_bg_pink': '#2d0f20',
            'badge_electronics_bg': '#1e3a5f', 'badge_electronics_text': '#93c5fd',
            'badge_kitchen_bg': '#064e3b', 'badge_kitchen_text': '#6ee7b7',
            'badge_positive_bg': '#064e3b', 'badge_positive_text': '#6ee7b7',
            'badge_mixed_bg': '#78350f', 'badge_mixed_text': '#fcd34d',
            'badge_critical_bg': '#7f1d1d', 'badge_critical_text': '#fca5a5',
            'surface_bg': 'rgba(16,16,35,0.88)', 'shadow': '0 2px 8px rgba(0,0,0,0.4)',
            'dataset_bg': 'rgba(30,20,0,0.6)', 'dataset_border': 'rgba(245,158,11,0.3)',
            'dataset_text': '#fcd34d',
            'danger_bg': 'rgba(127,29,29,0.3)', 'danger_border': 'rgba(252,165,165,0.3)',
            'danger_text': '#fca5a5',
            'action_btn_bg': '#6366f1', 'action_btn_text': '#ffffff', 'action_btn_border': '#4f46e5',
            'secondary_btn_bg': '#2d2d44', 'secondary_btn_text': '#f1f5f9', 'secondary_btn_border': '#4a4a6a',
            'danger_btn_bg': '#dc2626', 'danger_btn_text': '#ffffff',
        }


def inject_global_css(p: dict = None):
    """Injects all global CSS — iOS 26 glassmorphism system."""
    if p is None:
        if "theme" not in st.session_state:
            st.session_state["theme"] = "light"
        p = get_palette(st.session_state.get("theme", "light"))

    theme_val = st.session_state.get("theme", "light")

    st.markdown("""
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined">
""", unsafe_allow_html=True)

    if theme_val == "system":
        system_extra = """
@media (prefers-color-scheme: dark) {
  .stApp,[data-testid="stAppViewContainer"],.main .block-container{background-color:#0f0f1a !important;}
  section[data-testid="stSidebar"],[data-testid="stSidebarContent"]{background-color:#0d0d1f !important;}
}
@media (prefers-color-scheme: light) {
  .stApp,[data-testid="stAppViewContainer"],.main .block-container{background-color:#f4f6fb !important;}
  section[data-testid="stSidebar"],[data-testid="stSidebarContent"]{background-color:#ffffff !important;}
}
"""
    else:
        system_extra = ""

    st.markdown(f"""
<style>
/* ============================================================
   HIDE STREAMLIT CHROME
============================================================ */
[data-testid="stSidebarNav"]{{display:none !important;}}
header[data-testid="stHeader"]{{display:none !important;height:0 !important;background:transparent !important;}}
#MainMenu{{visibility:hidden !important;}}
footer{{visibility:hidden !important;}}
div[data-testid="stDecoration"]{{display:none !important;}}
[data-testid="collapsedControl"]{{display:none !important;}}

/* ============================================================
   PAGE BACKGROUND
============================================================ */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"]{{background-color:{p['page_bg']} !important;}}
[data-testid="stMainBlockContainer"]{{padding-top:1.5rem !important;}}
.main .block-container{{padding-top:1.5rem !important;}}
[data-testid="stVerticalBlock"]{{background-color:transparent !important;}}
.element-container,.stMarkdown{{background-color:transparent !important;}}

/* ============================================================
   SIDEBAR — Frosted glass panel
============================================================ */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"],
section[data-testid="stSidebar"] > div{{
    background:{p['sidebar_bg']} !important;
    backdrop-filter:{p['glass_blur_strong']} !important;
    -webkit-backdrop-filter:{p['glass_blur_strong']} !important;
    border-right:1px solid {p['glass_border']} !important;
}}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3{{color:{p['sidebar_btn_text']} !important;}}
section[data-testid="stSidebar"] hr{{margin:6px 16px !important;border:none !important;border-top:1px solid {p['glass_border']} !important;}}
section[data-testid="stSidebar"] > div:first-child{{padding:0 !important;overflow-y:auto !important;overflow-x:hidden !important;}}

/* CSS custom properties for product cards */
:root {{
    --bg-card: {p['card_bg']};
    --text-primary: {p['text_primary']};
    --text-secondary: {p['text_secondary']};
    --text-tertiary: {p['text_muted']};
    --price-color: {p['price_color']};
    --border-color: {p['border']};
    --border: {p['border']};
    --icon-btn-bg: {p['btn_bg']};
    --icon-btn-border: 1px solid {p['btn_border']};
    --icon-btn-shadow: {p['shadow']};
    --bg-card-hover: {p['card_bg_hover']};
    --primary: {p['accent']};
    --primary-light: {p['accent_soft']};
    --shadow-lg: {p['shadow']};
}}

/* ============================================================
   SIDEBAR NAV BUTTONS — Glass pills (12px radius)
============================================================ */
[data-testid="stSidebar"] .stButton > button{{
    background:{p['sidebar_btn_bg']} !important;
    backdrop-filter:blur(12px) !important;
    -webkit-backdrop-filter:blur(12px) !important;
    color:{p['sidebar_btn_text']} !important;
    border:1px solid {p['sidebar_btn_border']} !important;
    border-radius:12px !important;
    width:100% !important;
    min-height:42px !important;
    font-size:14px !important;
    font-weight:500 !important;
    padding:10px 16px !important;
    text-align:left !important;
    box-shadow:0 1px 4px rgba(0,0,0,0.04) !important;
    transition:background-color 0.18s ease,border-color 0.18s ease,color 0.18s ease,box-shadow 0.18s ease !important;
    animation:none !important;
    transform:none !important;
}}
[data-testid="stSidebar"] .stButton > button p,
[data-testid="stSidebar"] .stButton > button span,
[data-testid="stSidebar"] .stButton > button div{{
    color:{p['sidebar_btn_text']} !important;
    font-size:14px !important;
    animation:none !important;
}}
[data-testid="stSidebar"] .stButton > button:hover{{
    background:rgba(99,102,241,0.12) !important;
    border-color:rgba(99,102,241,0.35) !important;
    color:#6366f1 !important;
    transform:none !important;
}}
[data-testid="stSidebar"] .stButton > button:hover p,
[data-testid="stSidebar"] .stButton > button:hover span,
[data-testid="stSidebar"] .stButton > button:hover div{{color:#6366f1 !important;}}

[data-testid="stSidebar"] .stButton > button[kind="primary"]{{
    background:{p['nav_active_bg']} !important;
    color:#ffffff !important;
    border:none !important;
    box-shadow:0 3px 12px rgba(99,102,241,0.35) !important;
}}
[data-testid="stSidebar"] .stButton > button[kind="primary"] p,
[data-testid="stSidebar"] .stButton > button[kind="primary"] span,
[data-testid="stSidebar"] .stButton > button[kind="primary"] div{{color:#ffffff !important;}}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover{{
    background:linear-gradient(135deg,#4f46e5,#7c3aed) !important;
    color:#ffffff !important;
}}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover p,
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover span{{color:#ffffff !important;}}

/* ============================================================
   SIGN OUT BUTTON — Red glass (keyed)
============================================================ */
[data-testid="stSidebar"] .stButton > button[kind="secondaryFormSubmit"][key="btn_sign_out"],
[data-testid="stSidebar"] .stButton > button[key="btn_sign_out"],
.ir-signout-wrapper .stButton > button{{
    background:rgba(220,38,38,0.12) !important;
    backdrop-filter:blur(12px) !important;
    color:#dc2626 !important;
    border:1px solid rgba(220,38,38,0.3) !important;
    border-left:3px solid #dc2626 !important;
    border-radius:12px !important;
    font-weight:600 !important;
    animation:none !important;
}}
[data-testid="stSidebar"] .stButton > button[key="btn_sign_out"] p,
[data-testid="stSidebar"] .stButton > button[key="btn_sign_out"] span,
.ir-signout-wrapper .stButton > button p,
.ir-signout-wrapper .stButton > button span{{
    color:#dc2626 !important;
    animation:none !important;
}}
[data-testid="stSidebar"] .stButton > button[key="btn_sign_out"]:hover,
.ir-signout-wrapper .stButton > button:hover{{
    background:rgba(220,38,38,0.2) !important;
    border-color:rgba(220,38,38,0.45) !important;
    box-shadow:0 2px 12px rgba(220,38,38,0.25) !important;
    color:#dc2626 !important;
}}
[data-testid="stSidebar"] .stButton > button[key="btn_sign_out"]:hover p,
[data-testid="stSidebar"] .stButton > button[key="btn_sign_out"]:hover span,
.ir-signout-wrapper .stButton > button:hover p,
.ir-signout-wrapper .stButton > button:hover span{{color:#dc2626 !important;}}

/* ============================================================
   THEME TOGGLE BUTTONS (Light/System/Dark) in sidebar
============================================================ */
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton > button{{
    background:{p['sidebar_btn_bg']} !important;
    color:{p['sidebar_btn_text']} !important;
    border:1px solid {p['sidebar_btn_border']} !important;
    border-radius:10px !important;
    min-height:36px !important;
    font-size:12px !important;
    font-weight:500 !important;
    padding:5px 8px !important;
    text-align:center !important;
    animation:none !important;
}}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton > button p,
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton > button span,
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton > button div{{
    color:{p['sidebar_btn_text']} !important;
    font-size:12px !important;
    animation:none !important;
}}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton > button[kind="primary"]{{
    background:linear-gradient(135deg,#6366f1,#8b5cf6) !important;
    color:#ffffff !important;
    border:none !important;
}}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton > button[kind="primary"] p,
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton > button[kind="primary"] span,
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton > button[kind="primary"] div{{color:#ffffff !important;}}

/* ============================================================
   MAIN AREA BUTTONS — Default glass (12px rounded)
============================================================ */
[data-testid="stMain"] .stButton > button{{
    background:{p['glass_bg']} !important;
    backdrop-filter:blur(14px) !important;
    -webkit-backdrop-filter:blur(14px) !important;
    color:{p['text_primary']} !important;
    border:1px solid {p['glass_border_soft']} !important;
    border-radius:12px !important;
    min-height:40px !important;
    font-size:13px !important;
    font-weight:500 !important;
    padding:9px 18px !important;
    box-shadow:{p['glass_shadow']} !important;
    transition:background-color 0.18s ease,border-color 0.18s ease,color 0.18s ease,box-shadow 0.18s ease !important;
    animation:none !important;
    transform:none !important;
}}
[data-testid="stMain"] .stButton > button:hover{{
    background:{p['glass_bg_strong']} !important;
    border-color:rgba(99,102,241,0.4) !important;
    box-shadow:{p['glass_shadow_lg']} !important;
    transform:none !important;
}}
[data-testid="stMain"] .stButton > button p,
[data-testid="stMain"] .stButton > button span,
[data-testid="stMain"] .stButton > button div{{
    color:{p['text_primary']} !important;
    font-size:13px !important;
    animation:none !important;
    transform:none !important;
}}

/* Primary action buttons in main area — gradient pill */
[data-testid="stMain"] .stButton > button[kind="primary"]{{
    background:linear-gradient(135deg,rgba(99,102,241,0.92),rgba(139,92,246,0.92)) !important;
    color:#ffffff !important;
    border:1px solid rgba(255,255,255,0.18) !important;
    box-shadow:0 2px 12px rgba(99,102,241,0.3),inset 0 1px 0 rgba(255,255,255,0.15) !important;
    font-weight:600 !important;
}}
[data-testid="stMain"] .stButton > button[kind="primary"] p,
[data-testid="stMain"] .stButton > button[kind="primary"] span{{color:#ffffff !important;}}
[data-testid="stMain"] .stButton > button[kind="primary"]:hover{{
    background:linear-gradient(135deg,rgba(79,70,229,0.95),rgba(109,40,217,0.95)) !important;
    box-shadow:0 4px 20px rgba(99,102,241,0.45) !important;
}}

/* ============================================================
   TOPBAR ROW — first horizontal block of icon buttons
   (still 14px rounded glass; avatar overrides to circle below)
============================================================ */
[data-testid="stMain"] [data-testid="stHorizontalBlock"] .stButton > button{{
    background:{p['glass_bg_strong']} !important;
    backdrop-filter:blur(20px) !important;
    -webkit-backdrop-filter:blur(20px) !important;
    border:1.5px solid {p['glass_border']} !important;
    border-radius:14px !important;
    min-height:46px !important;
    min-width:52px !important;
    font-size:20px !important;
    padding:6px 14px !important;
    box-shadow:{p['glass_shadow']} !important;
    color:{p['text_primary']} !important;
    animation:none !important;
    transform:none !important;
}}
[data-testid="stMain"] [data-testid="stHorizontalBlock"] .stButton > button:hover{{
    background:rgba(99,102,241,0.1) !important;
    border-color:rgba(99,102,241,0.4) !important;
    box-shadow:0 4px 20px rgba(99,102,241,0.2) !important;
    transform:none !important;
}}
[data-testid="stMain"] [data-testid="stHorizontalBlock"] .stButton > button p,
[data-testid="stMain"] [data-testid="stHorizontalBlock"] .stButton > button span{{
    color:{p['text_primary']} !important;
    font-size:20px !important;
    animation:none !important;
    transform:none !important;
}}

/* ============================================================
   AVATAR BUTTON ONLY — circular gradient (keyed)
   ONLY this selector applies border-radius:50% to a button.
============================================================ */
[data-testid="stMain"] .stButton > button[key="topbar_avatar_btn"]{{
    background:linear-gradient(135deg,#6366f1,#8b5cf6) !important;
    border:2px solid rgba(255,255,255,0.3) !important;
    border-radius:50% !important;
    width:46px !important;
    height:46px !important;
    min-width:46px !important;
    min-height:46px !important;
    max-width:46px !important;
    font-size:13px !important;
    font-weight:700 !important;
    color:#ffffff !important;
    box-shadow:0 3px 14px rgba(99,102,241,0.45) !important;
    padding:0 !important;
    animation:none !important;
}}
[data-testid="stMain"] .stButton > button[key="topbar_avatar_btn"] p,
[data-testid="stMain"] .stButton > button[key="topbar_avatar_btn"] span{{
    color:#ffffff !important;
    font-size:13px !important;
    font-weight:700 !important;
    animation:none !important;
}}
[data-testid="stMain"] .stButton > button[key="topbar_avatar_btn"]:hover{{
    box-shadow:0 4px 20px rgba(99,102,241,0.6) !important;
    opacity:0.94 !important;
}}

/* ============================================================
   GLASS METRIC CARDS
============================================================ */
[data-testid="stMetric"]{{
    background:{p['glass_bg']} !important;
    backdrop-filter:{p['glass_blur']} !important;
    -webkit-backdrop-filter:{p['glass_blur']} !important;
    border:1px solid {p['glass_border']} !important;
    border-radius:18px !important;
    box-shadow:{p['glass_shadow']} !important;
    padding:18px !important;
}}
[data-testid="stMetricValue"]{{color:{p['text_primary']} !important;}}
[data-testid="stMetricLabel"]{{color:{p['text_secondary']} !important;}}
[data-testid="stMetricDelta"]{{color:{p['text_muted']} !important;}}

/* ============================================================
   GLASS INPUTS — Search, text, number, date, textarea
============================================================ */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stDateInput"] > div,
[data-testid="stTextArea"] textarea,
[data-baseweb="input"]{{
    background:{p['glass_bg_strong']} !important;
    backdrop-filter:blur(12px) !important;
    -webkit-backdrop-filter:blur(12px) !important;
    border:1.5px solid {p['glass_border_soft']} !important;
    border-radius:12px !important;
    color:{p['text_primary']} !important;
    box-shadow:inset 0 1px 3px rgba(0,0,0,0.05) !important;
}}
[data-testid="stTextInput"] input::placeholder{{color:{p['text_muted']} !important;}}

/* ============================================================
   GLASS EXPANDER
============================================================ */
[data-testid="stExpander"]{{
    background:{p['glass_bg']} !important;
    backdrop-filter:{p['glass_blur']} !important;
    -webkit-backdrop-filter:{p['glass_blur']} !important;
    border:1px solid {p['glass_border']} !important;
    border-radius:16px !important;
    box-shadow:{p['glass_shadow']} !important;
}}
[data-testid="stExpander"] summary{{border-radius:16px !important;}}
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span{{
    color:{p['text_primary']} !important;
    font-weight:600 !important;
    font-size:14px !important;
}}

/* ============================================================
   GLASS SELECTBOX / MULTISELECT
============================================================ */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div,
[data-baseweb="select"] > div,
[data-baseweb="tag"]{{
    background:{p['glass_bg_strong']} !important;
    backdrop-filter:blur(12px) !important;
    border:1px solid {p['glass_border_soft']} !important;
    border-radius:12px !important;
    color:{p['text_primary']} !important;
}}
[data-testid="stSelectbox"] *,
[data-testid="stMultiSelect"] *{{color:{p['text_primary']} !important;}}
[data-testid="stSelectbox"] svg{{fill:{p['text_primary']} !important;}}

/* ============================================================
   FILE UPLOADER
============================================================ */
[data-testid="stFileUploader"]{{
    background:{p['glass_bg']} !important;
    border:1px solid {p['glass_border']} !important;
    border-radius:14px !important;
    backdrop-filter:blur(12px) !important;
}}
[data-testid="stFileUploader"] *{{color:{p['text_primary']} !important;}}
[data-testid="stFileUploaderDropzone"]{{background:{p['glass_bg_strong']} !important;border-color:{p['glass_border_soft']} !important;}}

/* ============================================================
   GLASS TABS
============================================================ */
.stTabs [data-baseweb="tab-list"]{{
    background:{p['glass_bg']} !important;
    backdrop-filter:blur(12px) !important;
    border-radius:12px !important;
    padding:4px !important;
    border:1px solid {p['glass_border']} !important;
}}
.stTabs [data-baseweb="tab"]{{
    color:{p['text_secondary']} !important;
    border-radius:10px !important;
}}
.stTabs [aria-selected="true"]{{
    background:{p['glass_bg_strong']} !important;
    color:{p['accent']} !important;
    box-shadow:{p['glass_shadow']} !important;
    border-bottom:2px solid {p['accent']} !important;
}}
[data-testid="stTabs"] [data-baseweb="tab-border"]{{background-color:{p['accent']} !important;}}

/* ============================================================
   DATAFRAME GLASS
============================================================ */
[data-testid="stDataFrame"],.stDataFrame{{
    background:{p['glass_bg']} !important;
    border:1px solid {p['glass_border']} !important;
    border-radius:14px !important;
    backdrop-filter:blur(12px) !important;
}}
[data-testid="stDataFrame"] *,.stDataFrame *{{color:{p['text_primary']} !important;background-color:transparent !important;}}

/* ============================================================
   GLOBAL TEXT
============================================================ */
.stApp p,.stApp span,.stApp div,.stApp label,.stMarkdown p{{color:{p['text_primary']} !important;}}
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5,.stApp h6{{color:{p['text_primary']} !important;}}
[data-testid="stMain"] h1,[data-testid="stMain"] h2,[data-testid="stMain"] h3,
[data-testid="stMain"] h4,[data-testid="stMain"] p,[data-testid="stMain"] label,
[data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] span{{
    color:{p['text_primary']} !important;
    opacity:1 !important;
}}

/* PROGRESS BAR — Hide bug */
[data-testid="stProgressBar"],.stProgress{{display:none !important;}}

/* MISC */
hr,[data-testid="stDivider"]{{border-color:{p['glass_border']} !important;}}
a{{color:{p['text_link']} !important;}}
.stRadio label,.stCheckbox label,.stToggle label{{color:{p['text_primary']} !important;}}

/* ============================================================
   CATEGORY PILL BUTTONS (kept from prior system)
============================================================ */
div[data-testid="column"] .ir-pill-wrapper div.stButton > button{{
    border-radius:100px !important;padding:6px 14px !important;font-size:12.5px !important;
    font-weight:500 !important;border:1.5px solid {p['border']} !important;
    background-color:{p['filter_btn_bg']} !important;color:{p['filter_btn_text']} !important;
    box-shadow:none !important;min-height:unset !important;line-height:1.4 !important;
}}
div[data-testid="column"] .ir-pill-wrapper div.stButton > button:hover{{
    border-color:{p['accent']} !important;color:{p['accent']} !important;
    background-color:{p['accent_soft']} !important;transform:none !important;
}}
div[data-testid="column"] .ir-pill-active div.stButton > button{{
    background-color:{p['accent']} !important;color:#ffffff !important;
    border:none !important;font-weight:600 !important;
    box-shadow:0 2px 8px rgba(99,102,241,0.25) !important;
}}
div[data-testid="column"] .ir-pill-active div.stButton > button:hover{{background-color:#4f46e5 !important;color:#ffffff !important;}}

/* THEME TOGGLE PILL WRAPPER */
.ir-theme-pill{{display:flex;gap:2px;margin:0 8px 12px;}}

/* TEXT CLASSES */
.section-title{{font-size:18px !important;font-weight:700 !important;color:{p['text_primary']} !important;margin:0 !important;line-height:1.3 !important;}}
.product-title{{font-size:15px;font-weight:600;color:{p['text_primary']} !important;margin:0 0 6px;line-height:1.5;}}
.product-price{{font-size:13px;color:{p['text_secondary']} !important;margin:0;line-height:1.6;}}
.trending-item .product-title{{color:{p['text_primary']} !important;font-size:15px;font-weight:600;margin:0 0 4px;}}
.trending-item .product-price{{color:{p['text_secondary']} !important;font-size:13px;margin:0;}}

/* Material icons */
.material-icons{{font-family:'Material Icons' !important;font-style:normal !important;font-size:18px !important;display:inline-block !important;vertical-align:middle !important;color:inherit !important;}}

/* Smooth page fade-in */
[data-testid="stMain"]{{animation:ir_fadeSlideIn 0.4s ease-out;}}
@keyframes ir_fadeSlideIn{{
    from{{opacity:0;transform:translateY(12px);}}
    to{{opacity:1;transform:translateY(0);}}
}}

/* ============================================================
   GLOBAL ANIMATION KILL on buttons (last word)
============================================================ */
.stButton > button,
.stButton > button *,
.stButton > button p,
.stButton > button span,
.stButton > button div{{
    animation:none !important;
    animation-name:none !important;
    animation-duration:0s !important;
    -webkit-animation:none !important;
}}

{system_extra}
</style>
""", unsafe_allow_html=True)

    # Light-mode nuclear text contrast
    if theme_val == 'light':
        st.markdown("""
<style>
[data-testid="stMain"] p,
[data-testid="stMain"] span:not(.material-icons),
[data-testid="stMain"] label{color:#1a1a2e !important;}
[data-testid="stMain"] h1,[data-testid="stMain"] h2,[data-testid="stMain"] h3{color:#0f0f1a !important;}
[data-testid="stMetricValue"]{color:#0f0f1a !important;}
[data-testid="stMetricLabel"]{color:#4b5563 !important;}
[data-testid="stExpander"] summary p,[data-testid="stExpander"] summary span{color:#0f0f1a !important;font-weight:600 !important;}
[data-testid="stSelectbox"] *,[data-testid="stSlider"] *,[data-testid="stRadio"] *,[data-testid="stMultiSelect"] *{color:#0f0f1a !important;}
.js-plotly-plot text{fill:#0f0f1a !important;}

/* Light-mode glass page overlay (radial accents) */
.stApp::before{
    content:'';
    position:fixed;
    top:0;left:0;width:100%;height:100%;
    background:
        radial-gradient(ellipse at 20% 50%, rgba(99,102,241,0.06) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(139,92,246,0.05) 0%, transparent 50%),
        radial-gradient(ellipse at 60% 80%, rgba(6,182,212,0.04) 0%, transparent 50%);
    pointer-events:none;
    z-index:0;
}
</style>
""", unsafe_allow_html=True)


def inject_theme():
    """Legacy: delegates to inject_global_css()."""
    inject_global_css()


def get_theme() -> str:
    return st.session_state.get("theme", "light")


def set_theme(theme: str):
    st.session_state["theme"] = theme
    st.rerun()


def get_theme_css_class() -> str:
    return "dark-mode" if get_theme() == "dark" else ""


def inject_theme_toggle(key_prefix: str = "sb"):
    current = get_theme()

    st.markdown('<div class="ir-theme-pill">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("☀ Light", key=f"{key_prefix}_theme_light",
                     type="primary" if current == "light" else "secondary",
                     use_container_width=True):
            set_theme("light")
    with c2:
        if st.button("💻 System", key=f"{key_prefix}_theme_system",
                     type="primary" if current == "system" else "secondary",
                     use_container_width=True):
            set_theme("system")
    with c3:
        if st.button("🌙 Dark", key=f"{key_prefix}_theme_dark",
                     type="primary" if current == "dark" else "secondary",
                     use_container_width=True):
            set_theme("dark")
    st.markdown("</div>", unsafe_allow_html=True)
