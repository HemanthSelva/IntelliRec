"""
IntelliRec Theme Utility v2.0
Manages light/dark/system theme and injects global CSS.
IMPORTANT: Uses pure CSS injection (no JavaScript) because Streamlit
           strips <script> tags from st.markdown output.
"""
import streamlit as st


def inject_global_css():
    """
    Injects global CSS from assets/style.css and hides default Streamlit chrome.
    Also injects theme-specific CSS based on st.session_state.theme.
    Must be called at the top of every page.
    """
    # Default theme is 'light'
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"

    try:
        with open("assets/style.css", "r", encoding="utf-8") as f:
            css_content = f.read()
    except FileNotFoundError:
        css_content = ""

    theme = st.session_state.get("theme", "light")

    if theme == "light":
        theme_css = """
/* ── LIGHT MODE OVERRIDE ─────────────────────────────────────────────────── */
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
.stApp,
.stApp > div {
  background-color: #F0F2FF !important;
  background: #F0F2FF !important;
}
/* Force light color variables */
:root {
    --text-primary: #0F0F1A;
    --text-secondary: #5A5A72;
    --text-tertiary: #9090A8;
    --bg-page: #F0F2FF;
    --bg-card: rgba(255,255,255,0.92);
    --bg-surface: rgba(255,255,255,0.82);
    --input-bg: rgba(255,255,255,0.95);
    --input-border-style: 1.5px solid rgba(108,99,255,0.2);
    --border-color: rgba(108,99,255,0.12);
    --price-color: #6C63FF;
    --stat-card-bg: rgba(255,255,255,0.95);
    --icon-stroke: #6C63FF;
    --nav-bg: transparent;
    --nav-color: #0F0F1A;
    --nav-border: 1px solid rgba(0,0,0,0.08);
    --nav-active-bg: #EEF2FF;
    --nav-active-color: #6C63FF;
    --icon-btn-bg: rgba(255,255,255,1);
    --icon-btn-border: 1px solid rgba(108,99,255,0.20);
    --icon-btn-shadow: 0 2px 10px rgba(108,99,255,0.12);
    --pill-bg: rgba(255,255,255,0.9);
    --pill-color: #374151;
    --pill-border: 1.5px solid #E5E7EB;
    --pill-active-bg: #6C63FF;
    --pill-active-color: #FFFFFF;
    --pill-active-border: none;
    --stat-bg: rgba(255,255,255,0.95);
    --stat-border: 1px solid rgba(108,99,255,0.12);
    --stat-num: #0F0F1A;
    --stat-lbl: #6B7280;
}
section[data-testid="stSidebar"] > div {
    background-color: #FFFFFF !important;
    background: rgba(255,255,255,0.95) !important;
}
section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
}
/* Sidebar text in light mode */
section[data-testid="stSidebar"] * {
    color: #0F0F1A !important;
}
/* Override Streamlit's default sidebar color */
[data-testid="stSidebarContent"] {
    background-color: #FFFFFF !important;
}
"""
    elif theme == "dark":
        theme_css = """
/* ── DARK MODE OVERRIDE ──────────────────────────────────────────────────── */
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
.stApp,
.stApp > div {
  background-color: #08081A !important;
  background: #08081A !important;
}
/* Force dark color variables */
:root {
    --text-primary: #F0EFFF;
    --text-secondary: #9090B8;
    --text-tertiary: #606080;
    --bg-page: #08081A;
    --bg-card: rgba(20,20,42,0.92);
    --bg-surface: rgba(16,16,35,0.88);
    --input-bg: rgba(20,20,45,0.8);
    --input-border-style: 1.5px solid rgba(108,99,255,0.25);
    --border-color: rgba(108,99,255,0.18);
    --price-color: #A8A6FF;
    --stat-card-bg: rgba(20,20,42,0.85);
    --icon-stroke: #A8A6FF;
    --nav-bg: rgba(255,255,255,0.05);
    --nav-color: #E0DEFF;
    --nav-border: 1px solid rgba(108,99,255,0.15);
    --nav-active-bg: rgba(108,99,255,0.2);
    --nav-active-color: #A8A6FF;
    --icon-btn-bg: rgba(25,25,55,0.95);
    --icon-btn-border: 1px solid rgba(108,99,255,0.30);
    --icon-btn-shadow: 0 2px 10px rgba(0,0,0,0.45);
    --pill-bg: rgba(255,255,255,0.08);
    --pill-color: #C0BEFF;
    --pill-border: 1px solid rgba(108,99,255,0.2);
    --pill-active-bg: #6C63FF;
    --pill-active-color: #FFFFFF;
    --pill-active-border: none;
    --stat-bg: rgba(20,20,42,0.85);
    --stat-border: 1px solid rgba(108,99,255,0.18);
    --stat-num: #F0EFFF;
    --stat-lbl: #9090B8;
}
section[data-testid="stSidebar"] > div {
    background-color: #0D0D1F !important;
    background: rgba(10,10,24,0.98) !important;
}
section[data-testid="stSidebar"] {
    background-color: #0D0D1F !important;
}
section[data-testid="stSidebar"] * {
    color: #F0EFFF !important;
}
[data-testid="stSidebarContent"] {
    background-color: #0D0D1F !important;
}

/* Dark mode card/sidebar/input overrides */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-baseweb="input"] {
  background: rgba(20,20,42,0.80) !important;
  border-color: rgba(108,99,255,0.20) !important;
  color: #F0EFFF !important;
}
[data-baseweb="select"] > div,
[data-baseweb="tag"] {
  background: rgba(20,20,42,0.80) !important;
  border-color: rgba(108,99,255,0.20) !important;
  color: #F0EFFF !important;
}
div.stButton > button[kind="secondary"] {
  background: rgba(20,20,42,0.80) !important;
  border-color: rgba(108,99,255,0.20) !important;
  color: #C8C6F0 !important;
}
div.stButton > button[kind="secondary"]:hover {
  background: rgba(108,99,255,0.12) !important;
  border-color: rgba(108,99,255,0.35) !important;
  color: #A8A6FF !important;
}
[data-testid="stMarkdownContainer"] {
  color: #C8C6F0 !important;
}
[data-testid="stMetricValue"] { color: #F0EFFF !important; }
[data-testid="stMetricLabel"] { color: #8A88B0 !important; }
[data-testid="stTabs"] [data-baseweb="tab"] { color: #8A88B0 !important; }
[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
  color: #A8A6FF !important;
  border-bottom-color: #6C63FF !important;
}
"""
    else:
        # System: use CSS media queries, no JS
        theme_css = """
/* ── SYSTEM THEME (media query) ──────────────────────────────────────────── */
@media (prefers-color-scheme: dark) {
  [data-testid="stAppViewContainer"],
  [data-testid="stAppViewContainer"] > .main,
  .stApp, .stApp > div {
    background-color: #08081A !important;
  }
  section[data-testid="stSidebar"] {
    background: rgba(10,10,24,0.95) !important;
  }
  :root {
    --bg-page: #08081A;
    --bg-surface: rgba(16,16,35,0.88);
    --bg-card: rgba(20,20,42,0.92);
    --text-primary: #F0EFFF;
    --text-secondary: #9090B8;
    --stat-card-bg: rgba(20,20,42,0.85);
    --icon-stroke: #A8A6FF;
  }
}
@media (prefers-color-scheme: light) {
  [data-testid="stAppViewContainer"],
  [data-testid="stAppViewContainer"] > .main,
  .stApp, .stApp > div {
    background-color: #F0F2FF !important;
  }
  :root {
    --bg-page: #F0F2FF;
    --text-primary: #0F0F1A;
    --text-secondary: #5A5A72;
    --stat-card-bg: rgba(255,255,255,0.9);
    --icon-stroke: #6C63FF;
  }
}
"""

    # Material Icons via <link> is more reliable than @import inside <style>
    st.markdown("""
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined">
""", unsafe_allow_html=True)

    full_css = f"""
<style>
/* Hide Streamlit Chrome */
[data-testid="stSidebarNav"] {{ display: none !important; }}
header[data-testid="stHeader"] {{ display: none !important; }}
#MainMenu {{ visibility: hidden !important; }}
footer {{ visibility: hidden !important; }}
div[data-testid="stDecoration"] {{ display: none !important; }}
[data-testid="collapsedControl"] {{ display: none !important; }}

{css_content}

{theme_css}

/* ── Missing CSS class definitions (theme-aware via CSS vars) ── */
.section-title {{
    font-size: 18px !important;
    font-weight: 700 !important;
    color: var(--text-primary, #0F0F1A) !important;
    margin: 0 !important;
    line-height: 1.3 !important;
}}
.product-title {{
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary, #0F0F1A);
    margin: 0 0 6px;
    line-height: 1.5;
}}
.product-price {{
    font-size: 13px;
    color: var(--text-secondary, #5A5A72);
    margin: 0;
    line-height: 1.6;
}}
.trending-item {{
    padding: 4px 0;
}}
.trending-item .product-title {{
    color: var(--text-primary, #0F0F1A) !important;
    font-size: 15px;
    font-weight: 600;
    margin: 0 0 4px;
}}
.trending-item .product-price {{
    color: var(--text-secondary, #5A5A72) !important;
    font-size: 13px;
    margin: 0;
}}
</style>
"""
    st.markdown(full_css, unsafe_allow_html=True)


def inject_theme():
    """
    Injects theme-specific CSS based on st.session_state.theme.
    Pure CSS approach — no JavaScript (Streamlit strips <script> tags).
    """
    theme = st.session_state.get("theme", "light")

    if theme == "light":
        css = """
<style>
:root {
    --text-primary: #0F0F1A;
    --text-secondary: #5A5A72;
    --text-tertiary: #9090A8;
    --bg-page: #F0F2FF;
    --bg-card: rgba(255,255,255,0.92);
    --bg-surface: rgba(255,255,255,0.82);
    --input-bg: rgba(255,255,255,0.95);
    --input-border-style: 1.5px solid rgba(108,99,255,0.2);
    --border-color: rgba(108,99,255,0.12);
    --price-color: #6C63FF;
    --stat-card-bg: rgba(255,255,255,0.95);
}
section[data-testid="stSidebar"] > div {
    background-color: #FFFFFF !important;
    background: rgba(255,255,255,0.95) !important;
}
section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
}
/* Sidebar text in light mode */
section[data-testid="stSidebar"] * {
    color: #0F0F1A !important;
}
/* Override Streamlit's default sidebar color */
[data-testid="stSidebarContent"] {
    background-color: #FFFFFF !important;
}
</style>
"""
    elif theme == "dark":
        css = """
<style>
:root {
    --text-primary: #F0EFFF;
    --text-secondary: #9090B8;
    --text-tertiary: #606080;
    --bg-page: #08081A;
    --bg-card: rgba(20,20,42,0.92);
    --bg-surface: rgba(16,16,35,0.88);
    --input-bg: rgba(20,20,45,0.8);
    --input-border-style: 1.5px solid rgba(108,99,255,0.25);
    --border-color: rgba(108,99,255,0.18);
    --price-color: #A8A6FF;
    --stat-card-bg: rgba(20,20,42,0.85);
}
section[data-testid="stSidebar"] > div {
    background-color: #0D0D1F !important;
    background: rgba(10,10,24,0.98) !important;
}
section[data-testid="stSidebar"] {
    background-color: #0D0D1F !important;
}
section[data-testid="stSidebar"] * {
    color: #F0EFFF !important;
}
[data-testid="stSidebarContent"] {
    background-color: #0D0D1F !important;
}
</style>
"""
    else:  # system
        css = """
<style>
@media (prefers-color-scheme: dark) {
    :root {
        --text-primary: #F0EFFF;
        --text-secondary: #9090B8;
        --text-tertiary: #606080;
        --bg-page: #08081A;
        --bg-card: rgba(20,20,42,0.92);
        --bg-surface: rgba(16,16,35,0.88);
        --input-bg: rgba(20,20,45,0.8);
        --input-border-style: 1.5px solid rgba(108,99,255,0.25);
        --border-color: rgba(108,99,255,0.18);
        --price-color: #A8A6FF;
        --stat-card-bg: rgba(20,20,42,0.85);
    }
    section[data-testid="stSidebar"] > div {
        background-color: #0D0D1F !important;
        background: rgba(10,10,24,0.98) !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #0D0D1F !important;
    }
    section[data-testid="stSidebar"] * {
        color: #F0EFFF !important;
    }
    [data-testid="stSidebarContent"] {
        background-color: #0D0D1F !important;
    }
}
@media (prefers-color-scheme: light) {
    :root {
        --text-primary: #0F0F1A;
        --text-secondary: #5A5A72;
        --text-tertiary: #9090A8;
        --bg-page: #F0F2FF;
        --bg-card: rgba(255,255,255,0.92);
        --bg-surface: rgba(255,255,255,0.82);
        --input-bg: rgba(255,255,255,0.95);
        --input-border-style: 1.5px solid rgba(108,99,255,0.2);
        --border-color: rgba(108,99,255,0.12);
        --price-color: #6C63FF;
        --stat-card-bg: rgba(255,255,255,0.95);
    }
    section[data-testid="stSidebar"] > div {
        background-color: #FFFFFF !important;
        background: rgba(255,255,255,0.95) !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
    }
    /* Sidebar text in light mode */
    section[data-testid="stSidebar"] * {
        color: #0F0F1A !important;
    }
    /* Override Streamlit's default sidebar color */
    [data-testid="stSidebarContent"] {
        background-color: #FFFFFF !important;
    }
}
</style>
"""

    st.markdown(css, unsafe_allow_html=True)


def get_theme() -> str:
    """Return current theme: 'light', 'dark', or 'system'."""
    return st.session_state.get("theme", "light")


def set_theme(theme: str):
    """Set theme and rerun."""
    st.session_state["theme"] = theme
    st.rerun()


def get_theme_css_class() -> str:
    """Return CSS class for current theme."""
    theme = get_theme()
    if theme == "dark":
        return "dark-mode"
    return ""


def inject_theme_toggle(key_prefix: str = "sb"):
    """
    Renders a compact 3-option theme toggle pill (Light / System / Dark).
    Uses actual st.buttons for reliable click handling.
    key_prefix: unique prefix to avoid duplicate key errors.
    """
    current = get_theme()

    inactive_bg = "rgba(0,0,0,0.05)" if current == "light" else "rgba(255,255,255,0.05)"
    inactive_color = "#374151" if current == "light" else "#A0A0B8"
    inactive_border = "1px solid #E5E7EB" if current == "light" else "1px solid rgba(255,255,255,0.1)"

    st.markdown(f"""
<style>
.ir-theme-pill {{
    display: flex;
    gap: 2px;
    margin: 0 8px 12px;
}}
.ir-theme-pill div[data-testid="stButton"] > button {{
    border-radius: 8px !important;
    height: 34px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 0 8px !important;
    width: 100% !important;
    min-height: unset !important;
    line-height: unset !important;
    box-shadow: none !important;
}}
.ir-theme-pill div[data-testid="stButton"] > button[kind="primary"] {{
    background: #6C63FF !important;
    color: white !important;
    border: none !important;
}}
.ir-theme-pill div[data-testid="stButton"] > button[kind="secondary"] {{
    background: {inactive_bg} !important;
    color: {inactive_color} !important;
    border: {inactive_border} !important;
}}
</style>
<div class="ir-theme-pill">""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button("☀ Light", key=f"{key_prefix}_theme_light",
                     type="primary" if current == "light" else "secondary",
                     use_container_width=True):
            set_theme("light")
    with c2:
        if st.button("⬛ System", key=f"{key_prefix}_theme_system",
                     type="primary" if current == "system" else "secondary",
                     use_container_width=True):
            set_theme("system")
    with c3:
        if st.button("🌙 Dark", key=f"{key_prefix}_theme_dark",
                     type="primary" if current == "dark" else "secondary",
                     use_container_width=True):
            set_theme("dark")

    st.markdown("</div>", unsafe_allow_html=True)
