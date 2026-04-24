"""
IntelliRec Theme Utility v5.1 — iOS 26 Glassmorphism System
Manages light/dark/system theme and injects all global CSS.
Toggle button fix: uses data-testid="baseButton-secondary" which
Streamlit actually renders as a real HTML attribute on <button> elements.
key= is purely internal Python — never appears in the DOM.
"""
import streamlit as st


def get_palette(theme: str) -> dict:
    if theme == 'light':
        return {
            'page_bg': '#f4f6fb',
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
            'sidebar_bg': '#f0f2f8',
            'sidebar_btn_bg': 'rgba(255, 255, 255, 0.55)',
            'sidebar_btn_text': '#1a1a2e',
            'sidebar_btn_border': 'rgba(99,102,241,0.18)',
            'card_bg': '#ffffff',
            'card_bg_hover': '#f0f2ff',
            'input_bg': '#ffffff',
            'stat_card_bg': '#ffffff',
            'text_primary': '#0f0f1a',
            'text_secondary': '#4b5563',
            'text_muted': '#9ca3af',
            'text_link': '#6366f1',
            'border': '#e5e7eb',
            'border_focus': '#6366f1',
            'btn_bg': '#ffffff',
            'btn_text': '#0f0f1a',
            'btn_border': '#d1d5db',
            'filter_btn_bg': '#f3f4f6',
            'filter_btn_text': '#1a1a2e',
            'filter_btn_active': '#6366f1',
            'nav_btn_bg': '#f3f4f6',
            'nav_btn_text': '#1a1a2e',
            'nav_btn_active': '#6366f1',
            'nav_btn_active_text': '#ffffff',
            'accent': '#6366f1',
            'accent_soft': '#e0e7ff',
            'price_color': '#6366f1',
            'star_color': '#f59e0b',
            'icon_bg_purple': '#eef2ff',
            'icon_bg_cyan': '#ecfeff',
            'icon_bg_green': '#dcfce7',
            'icon_bg_amber': '#fffbeb',
            'icon_bg_pink': '#fdf2f8',
            'badge_electronics_bg': '#dbeafe',
            'badge_electronics_text': '#1d4ed8',
            'badge_kitchen_bg': '#d1fae5',
            'badge_kitchen_text': '#065f46',
            'badge_positive_bg': '#d1fae5',
            'badge_positive_text': '#065f46',
            'badge_mixed_bg': '#fef3c7',
            'badge_mixed_text': '#92400e',
            'badge_critical_bg': '#fee2e2',
            'badge_critical_text': '#991b1b',
            'surface_bg': 'rgba(255,255,255,0.92)',
            'shadow': '0 2px 8px rgba(99,102,241,0.08)',
            'dataset_bg': '#fffbeb',
            'dataset_border': '#fde68a',
            'dataset_text': '#92400e',
            'danger_bg': '#fef2f2',
            'danger_border': '#fca5a5',
            'danger_text': '#dc2626',
            'action_btn_bg': '#6366f1',
            'action_btn_text': '#ffffff',
            'action_btn_border': '#4f46e5',
            'secondary_btn_bg': '#f3f4f6',
            'secondary_btn_text': '#1a1a2e',
            'secondary_btn_border': '#d1d5db',
            'danger_btn_bg': '#dc2626',
            'danger_btn_text': '#ffffff',
        }
    else:
        return {
            'page_bg': '#0f0f1a',
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
            'sidebar_bg': '#1a1a2e',
            'sidebar_btn_bg': 'rgba(255, 255, 255, 0.06)',
            'sidebar_btn_text': '#e2e8f0',
            'sidebar_btn_border': 'rgba(255,255,255,0.1)',
            'card_bg': '#1e1e35',
            'card_bg_hover': '#26263f',
            'input_bg': '#1e1e35',
            'stat_card_bg': '#1e1e35',
            'text_primary': '#f1f5f9',
            'text_secondary': '#a0aec0',
            'text_muted': '#6b7280',
            'text_link': '#a5b4fc',
            'border': '#2d2d4a',
            'border_focus': '#6366f1',
            'btn_bg': '#2d2d44',
            'btn_text': '#f1f5f9',
            'btn_border': '#4a4a6a',
            'filter_btn_bg': '#2d2d44',
            'filter_btn_text': '#f1f5f9',
            'filter_btn_active': '#6366f1',
            'nav_btn_bg': '#2d2d44',
            'nav_btn_text': '#f1f5f9',
            'nav_btn_active': '#6366f1',
            'nav_btn_active_text': '#ffffff',
            'accent': '#6366f1',
            'accent_soft': '#312e81',
            'price_color': '#a5b4fc',
            'star_color': '#f59e0b',
            'icon_bg_purple': '#1e1a4a',
            'icon_bg_cyan': '#0c2a3a',
            'icon_bg_green': '#0d3325',
            'icon_bg_amber': '#2d1f00',
            'icon_bg_pink': '#2d0f20',
            'badge_electronics_bg': '#1e3a5f',
            'badge_electronics_text': '#93c5fd',
            'badge_kitchen_bg': '#064e3b',
            'badge_kitchen_text': '#6ee7b7',
            'badge_positive_bg': '#064e3b',
            'badge_positive_text': '#6ee7b7',
            'badge_mixed_bg': '#78350f',
            'badge_mixed_text': '#fcd34d',
            'badge_critical_bg': '#7f1d1d',
            'badge_critical_text': '#fca5a5',
            'surface_bg': 'rgba(16,16,35,0.88)',
            'shadow': '0 2px 8px rgba(0,0,0,0.4)',
            'dataset_bg': 'rgba(30,20,0,0.6)',
            'dataset_border': 'rgba(245,158,11,0.3)',
            'dataset_text': '#fcd34d',
            'danger_bg': 'rgba(127,29,29,0.3)',
            'danger_border': 'rgba(252,165,165,0.3)',
            'danger_text': '#fca5a5',
            'action_btn_bg': '#6366f1',
            'action_btn_text': '#ffffff',
            'action_btn_border': '#4f46e5',
            'secondary_btn_bg': '#2d2d44',
            'secondary_btn_text': '#f1f5f9',
            'secondary_btn_border': '#4a4a6a',
            'danger_btn_bg': '#dc2626',
            'danger_btn_text': '#ffffff',
        }


def inject_global_css(p: dict = None):
    """Injects all global CSS — iOS 26 glassmorphism system."""
    if p is None:
        p = get_palette(get_theme())

    theme_val = get_theme()

    st.markdown("", unsafe_allow_html=True)

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
header[data-testid="stHeader"]{{display:none !important;height:0 !important;min-height:0 !important;padding:0 !important;margin:0 !important;overflow:hidden !important;position:absolute !important;}}
[data-testid="stToolbar"]{{display:none !important;height:0 !important;min-height:0 !important;overflow:hidden !important;}}
[data-testid="stStatusWidget"]{{display:none !important;height:0 !important;overflow:hidden !important;}}
#MainMenu{{visibility:hidden !important;}}
footer{{visibility:hidden !important;}}
div[data-testid="stDecoration"]{{display:none !important;}}
[data-testid="collapsedControl"],
[data-testid="collapsedControl"] *,
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] *,
[data-testid="stSidebarCollapseButton"] span{{
    display:none !important;
    visibility:hidden !important;
    opacity:0 !important;
    pointer-events:none !important;
    width:0 !important;
    height:0 !important;
    overflow:hidden !important;
    font-size:0 !important;
    position:absolute !important;
}}

/* ============================================================
   PAGE BACKGROUND
============================================================ */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"]{{background-color:{p['page_bg']} !important;}}
/* ── Root fix: .stApp is where Streamlit injects toolbar offset ── */
.stApp {{
    padding-top: 0 !important;
    margin-top:  0 !important;
}}
[data-testid="stAppViewContainer"] {{
    padding-top: 0 !important;
    margin-top:  0 !important;
}}
[data-testid="stMain"] {{
    padding-top: 0 !important;
    margin-top:  0 !important;
}}
[data-testid="stMainBlockContainer"] {{
    padding-top: 0.75rem !important;
    padding-bottom: 2rem !important;
}}
.main .block-container {{
    padding-top: 0.75rem !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
}}
/* Sidebar — remove top padding that compensates for the header */
[data-testid="stSidebarContent"],
[data-testid="stSidebar"] > div > div:first-child {{
    padding-top: 0 !important;
    margin-top:  0 !important;
}}
[data-testid="stVerticalBlock"]{{background-color:transparent !important;}}
.element-container,.stMarkdown{{background-color:transparent !important;}}

/* ============================================================
   SIDEBAR — Frosted glass panel
============================================================ */
section[data-testid="stSidebar"],
[data-testid="stSidebar"] {{
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    background-color: {p['sidebar_bg']} !important;
    background: {p['sidebar_bg']} !important;
}}
section[data-testid="stSidebar"] > div {{
    display: block !important;
    visibility: visible !important;
}}
[data-testid="stSidebar"] > div:first-child {{
    background-color: {p['sidebar_bg']} !important;
    background: {p['sidebar_bg']} !important;
    backdrop-filter:{p['glass_blur_strong']} !important;
    -webkit-backdrop-filter:{p['glass_blur_strong']} !important;
    border-right:1px solid {p['glass_border']} !important;
    padding:0 !important;
    overflow-y:auto !important;
    overflow-x:hidden !important;
}}
[data-testid="stSidebar"] > div > div:first-child {{
    background-color: {p['sidebar_bg']} !important;
}}
[data-testid="stSidebarContent"] {{
    background-color: {p['sidebar_bg']} !important;
    background: {p['sidebar_bg']} !important;
}}
section[data-testid="stSidebar"] {{
    background-color: {p['sidebar_bg']} !important;
    background: {p['sidebar_bg']} !important;
}}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3{{color:{p['sidebar_btn_text']} !important;}}
section[data-testid="stSidebar"] hr{{margin:6px 16px !important;border:none !important;border-top:1px solid {p['glass_border']} !important;}}

/* ============================================================
   CSS VARIABLES
============================================================ */
:root:root {{
    --bg-surface:       {p['glass_bg_strong']};
    --bg-surface-hover: {p['glass_bg']};
    --bg-page:          {p['page_bg']};
    --bg-card:          {p['card_bg']};
    --bg:               {p['page_bg']};
    --surface:          {p['card_bg']};
    --surface-2:        {p['secondary_btn_bg']};
    --surface-3:        {p['secondary_btn_bg']};
    --text-1:           {p['text_primary']};
    --text-2:           {p['text_secondary']};
    --text-3:           {p['text_muted']};
    --text-4:           {p['text_muted']};
    --text-primary:     {p['text_primary']};
    --text-secondary:   {p['text_secondary']};
    --text-tertiary:    {p['text_muted']};
    --border:           {p['border']};
    --border-2:         {p['border']};
    --border-color:     {p['border']};
    --primary:          {p['accent']};
    --primary-light:    {p['accent_soft']};
    --nav-active-color: {p['accent']};
    --nav-color:        {p['text_secondary']};
    --price-color:      {p['price_color']};
    --icon-btn-bg:      {p['btn_bg']};
    --icon-btn-border:  1px solid {p['btn_border']};
    --icon-btn-shadow:  {p['shadow']};
    --bg-card-hover:    {p['card_bg_hover']};
    --shadow-lg:        {p['shadow']};
}}

/* ============================================================
   SIDEBAR NAV BUTTONS
============================================================ */
[data-testid="stSidebar"] .stButton > button{{
    background-color:{p['sidebar_btn_bg']} !important;
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
    background-color:rgba(99,102,241,0.15) !important;
    background:rgba(99,102,241,0.15) !important;
    border-color:rgba(99,102,241,0.4) !important;
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
   THEME TOGGLE BUTTONS in sidebar
============================================================ */
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton > button{{
    background:{p['sidebar_btn_bg']} !important;
    color:{p['sidebar_btn_text']} !important;
    border:1px solid {p['sidebar_btn_border']} !important;
    border-radius:12px !important;
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
   MAIN AREA BUTTONS — secondary (default)
============================================================ */
[data-testid="stMain"] div[data-testid="stButton"] > button,
[data-testid="stMain"] div.stButton > button{{
    background:{p['secondary_btn_bg']} !important;
    color:{p['secondary_btn_text']} !important;
    border:1.5px solid {p['border']} !important;
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
[data-testid="stMain"] div[data-testid="stButton"] > button:hover,
[data-testid="stMain"] div.stButton > button:hover{{
    background:{p['card_bg_hover']} !important;
    border-color:{p['accent']} !important;
    color:{p['accent']} !important;
    transform:none !important;
}}
[data-testid="stMain"] div[data-testid="stButton"] > button p,
[data-testid="stMain"] div[data-testid="stButton"] > button span,
[data-testid="stMain"] div.stButton > button p,
[data-testid="stMain"] div.stButton > button span{{
    color:{p['secondary_btn_text']} !important;
    font-size:13px !important;
    animation:none !important;
}}
[data-testid="stMain"] div[data-testid="stButton"] > button:hover p,
[data-testid="stMain"] div[data-testid="stButton"] > button:hover span,
[data-testid="stMain"] div.stButton > button:hover p,
[data-testid="stMain"] div.stButton > button:hover span{{
    color:{p['accent']} !important;
}}

/* MAIN AREA primary buttons */
[data-testid="stMain"] div[data-testid="stButton"] > button[kind="primary"],
[data-testid="stMain"] div.stButton > button[kind="primary"]{{
    background:linear-gradient(135deg,rgba(99,102,241,0.92),rgba(139,92,246,0.92)) !important;
    color:#ffffff !important;
    border:1px solid rgba(255,255,255,0.18) !important;
    box-shadow:0 2px 12px rgba(99,102,241,0.3),inset 0 1px 0 rgba(255,255,255,0.15) !important;
    font-weight:600 !important;
}}
[data-testid="stMain"] div[data-testid="stButton"] > button[kind="primary"] p,
[data-testid="stMain"] div[data-testid="stButton"] > button[kind="primary"] span,
[data-testid="stMain"] div.stButton > button[kind="primary"] p,
[data-testid="stMain"] div.stButton > button[kind="primary"] span{{color:#ffffff !important;}}
[data-testid="stMain"] div[data-testid="stButton"] > button[kind="primary"]:hover,
[data-testid="stMain"] div.stButton > button[kind="primary"]:hover{{
    background:linear-gradient(135deg,rgba(79,70,229,0.95),rgba(109,40,217,0.95)) !important;
    color:#ffffff !important;
    box-shadow:0 4px 20px rgba(99,102,241,0.45) !important;
}}
[data-testid="stMain"] div[data-testid="stButton"] > button[kind="primary"]:hover p,
[data-testid="stMain"] div[data-testid="stButton"] > button[kind="primary"]:hover span,
[data-testid="stMain"] div.stButton > button[kind="primary"]:hover p,
[data-testid="stMain"] div.stButton > button[kind="primary"]:hover span{{color:#ffffff !important;}}

/* ============================================================
   TOGGLE BUTTON FIX — data-testid="baseButton-secondary" is the
   ONLY real HTML attribute Streamlit renders on <button> elements.
   key= is purely Python-internal and NEVER appears in the DOM.
   This block targets ALL secondary buttons in the main area
   including the sidebar toggle, topbar icons, +Save, Similar etc.
   The toggle gets square dimensions via the column-scoped rule.
============================================================ */
[data-testid="stMain"] button[data-testid="baseButton-secondary"] {{
    background-color: {p['btn_bg']} !important;
    background:       {p['btn_bg']} !important;
    color:            {p['btn_text']} !important;
    border:           1.5px solid {p['btn_border']} !important;
    border-radius:    12px !important;
    animation:        none !important;
    transform:        none !important;
    backdrop-filter:  blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    box-shadow:       {p['glass_shadow']} !important;
    transition:       background-color 0.18s ease,
                      border-color 0.18s ease,
                      color 0.18s ease !important;
}}
[data-testid="stMain"] button[data-testid="baseButton-secondary"] p,
[data-testid="stMain"] button[data-testid="baseButton-secondary"] span,
[data-testid="stMain"] button[data-testid="baseButton-secondary"] div {{
    color:     {p['btn_text']} !important;
    font-size: 13px !important;
    animation: none !important;
}}
[data-testid="stMain"] button[data-testid="baseButton-secondary"]:hover {{
    background-color: {p['card_bg_hover']} !important;
    background:       {p['card_bg_hover']} !important;
    border-color:     {p['accent']} !important;
    color:            {p['accent']} !important;
}}
[data-testid="stMain"] button[data-testid="baseButton-secondary"]:hover p,
[data-testid="stMain"] button[data-testid="baseButton-secondary"]:hover span {{
    color: {p['accent']} !important;
}}

/* Toggle button square shape — it lives in a single narrow column */
[data-testid="stMain"] [data-testid="column"] button[data-testid="baseButton-secondary"] {{
    min-width:     44px !important;
    max-width:     44px !important;
    min-height:    44px !important;
    max-height:    44px !important;
    width:         44px !important;
    height:        44px !important;
    padding:       0 !important;
    font-size:     18px !important;
    border-radius: 10px !important;
    display:       flex !important;
    align-items:   center !important;
    justify-content: center !important;
}}
[data-testid="stMain"] [data-testid="column"] button[data-testid="baseButton-secondary"] p,
[data-testid="stMain"] [data-testid="column"] button[data-testid="baseButton-secondary"] span {{
    font-size:   18px !important;
    line-height: 1 !important;
    color:       {p['btn_text']} !important;
}}

/* Toggle switches */
[data-testid="stToggle"] label[data-baseweb="checkbox"] > div:nth-child(2) {{
    background-color: {p['border']} !important;
}}
[data-testid="stToggle"] label[data-baseweb="checkbox"]:has(input:checked) > div:nth-child(2) {{
    background-color: {p['accent']} !important;
}}
[data-testid="stToggle"] label[data-baseweb="checkbox"] > div:nth-child(2) > div {{
    background-color: #ffffff !important;
}}

/* ============================================================
   GLASS METRIC CARDS
============================================================ */
[data-testid="stMetric"]{{
    background:{p['glass_bg']} !important;
    backdrop-filter:{p['glass_blur']} !important;
    -webkit-backdrop-filter:{p['glass_blur']} !important;
    border:1px solid {p['glass_border']} !important;
    border-radius:12px !important;
    box-shadow:{p['glass_shadow']} !important;
    padding:18px !important;
}}
[data-testid="stMetricValue"]{{color:{p['text_primary']} !important;}}
[data-testid="stMetricLabel"]{{color:{p['text_secondary']} !important;}}
[data-testid="stMetricDelta"]{{color:{p['text_muted']} !important;}}

/* ============================================================
   SEARCH INPUT — Nuclear fix targeting every wrapper level
============================================================ */
[data-testid="stTextInput"] {{background: transparent !important;}}
[data-testid="stTextInput"] > div {{
    background-color: {p['input_bg']} !important;
    border-radius: 12px !important;
    border: 1.5px solid {p['border']} !important;
}}
[data-testid="stTextInput"] > div > div {{
    background-color: {p['input_bg']} !important;
    border-radius: 12px !important;
    border: none !important;
}}
[data-testid="stTextInput"] input {{
    background-color: {p['input_bg']} !important;
    color: {p['text_primary']} !important;
    border: none !important;
    border-radius: 12px !important;
    caret-color: {p['accent']} !important;
}}
[data-testid="stTextInput"] input::placeholder {{
    color: {p['text_muted']} !important;
    opacity: 1 !important;
}}
[data-testid="stTextInput"] > div:focus-within {{
    background-color: {p['input_bg']} !important;
    border-color: {p['accent']} !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}}
[data-testid="stTextInput"] [class*="st-"] {{
    background-color: {p['input_bg']} !important;
}}
[data-testid="stTextInput"] input[type="text"],
[data-testid="stTextInput"] input[type="search"],
[data-testid="stTextInput"] input[role="textbox"] {{
    background-color: {p['input_bg']} !important;
    color: {p['text_primary']} !important;
}}
.stTextInput input,
.stTextInput > div,
.stTextInput > div > div {{
    background-color: {p['input_bg']} !important;
    color: {p['text_primary']} !important;
}}
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stDateInput"] > div,
[data-testid="stTextArea"] textarea {{
    background-color: {p['input_bg']} !important;
    color: {p['text_primary']} !important;
    border: 1.5px solid {p['border']} !important;
    border-radius: 12px !important;
}}
[data-baseweb="input"],
[data-baseweb="base-input"] {{
    background-color: {p['input_bg']} !important;
    border-radius: 12px !important;
}}
[data-baseweb="input"] input,
[data-baseweb="base-input"] input {{
    background-color: {p['input_bg']} !important;
    color: {p['text_primary']} !important;
}}

/* ============================================================
   GLASS EXPANDER
============================================================ */
[data-testid="stExpander"]{{
    background:{p['glass_bg']} !important;
    backdrop-filter:{p['glass_blur']} !important;
    -webkit-backdrop-filter:{p['glass_blur']} !important;
    border:1px solid {p['glass_border']} !important;
    border-radius:12px !important;
    box-shadow:{p['glass_shadow']} !important;
}}
[data-testid="stExpander"] summary{{border-radius:12px !important;}}
[data-testid="stExpander"] summary p{{
    color:{p['text_primary']} !important;
    font-weight:600 !important;
    font-size:14px !important;
}}
[data-testid="stExpander"] summary > span > span:first-child {{
    color: {p['text_secondary']} !important;
    -webkit-text-fill-color: {p['text_secondary']} !important;
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
    border-radius:12px !important;
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
    border-radius:12px !important;
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
    border-radius:12px !important;
    backdrop-filter:blur(12px) !important;
}}
[data-testid="stDataFrame"] *,.stDataFrame *{{color:{p['text_primary']} !important;background-color:transparent !important;}}

/* ============================================================
   GLOBAL TEXT
============================================================ */
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5,.stApp h6{{color:{p['text_primary']} !important;}}
[data-testid="stMain"] p,
[data-testid="stMain"] span:not(.material-icons):not(.material-symbols-rounded):not(.material-symbols-outlined):not(.ir-gemini-icon),
[data-testid="stMain"] label,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span {{
    color: {p['text_primary']} !important;
    opacity: 1 !important;
}}
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4,
[data-testid="stMain"] h5,
[data-testid="stMain"] h6 {{
    color: {p['text_primary']} !important;
    font-weight: 700 !important;
}}

[data-testid="stProgressBar"],.stProgress{{display:none !important;}}
hr,[data-testid="stDivider"]{{border-color:{p['glass_border']} !important;}}
a{{color:{p['text_link']} !important;}}
.stRadio label,.stCheckbox label,.stToggle label{{color:{p['text_primary']} !important;}}

/* ============================================================
   CHAT INPUT
============================================================ */
[data-testid="stBottom"],
[data-testid="stBottom"] > div {{
    background: {p['page_bg']} !important;
}}
[data-testid="stChatInput"] {{
    background: {p['glass_bg_strong']} !important;
    border: 1.5px solid {p['glass_border_soft']} !important;
    border-radius: 14px !important;
}}
[data-testid="stChatInput"] div,
[data-testid="stChatInput"] form,
[data-testid="stChatInput"] [data-baseweb],
[data-testid="stChatInput"] [data-baseweb] > div {{
    background: transparent !important;
    background-color: transparent !important;
    border-color: transparent !important;
    box-shadow: none !important;
}}
[data-testid="stChatInput"] textarea {{
    background: transparent !important;
    color: {p['text_primary']} !important;
    -webkit-text-fill-color: {p['text_primary']} !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{
    color: {p['text_muted']} !important;
    -webkit-text-fill-color: {p['text_muted']} !important;
}}

/* ============================================================
   CATEGORY PILL BUTTONS
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

.ir-theme-pill{{display:flex;gap:2px;margin:0 8px 12px;}}

.section-title{{font-size:18px !important;font-weight:700 !important;color:{p['text_primary']} !important;margin:0 !important;line-height:1.3 !important;}}
.product-title{{font-size:15px;font-weight:600;color:{p['text_primary']} !important;margin:0 0 6px;line-height:1.5;}}
.product-price{{font-size:13px;color:{p['text_secondary']} !important;margin:0;line-height:1.6;}}
.trending-item .product-title{{color:{p['text_primary']} !important;font-size:15px;font-weight:600;margin:0 0 4px;}}
.trending-item .product-price{{color:{p['text_secondary']} !important;font-size:13px;margin:0;}}

/* ============================================================
   PRODUCT CARD BUTTON ROW ALIGNMENT
============================================================ */
[data-testid="stMain"] [data-testid="stHorizontalBlock"]:has(.stButton) .stButton {{
    display: flex !important;
    align-items: stretch !important;
    width: 100% !important;
}}
[data-testid="stMain"] [data-testid="stHorizontalBlock"]:has(.stButton) .stButton > button {{
    width: 100% !important;
    min-height: 36px !important;
    height: 100% !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    padding: 7px 10px !important;
    font-size: 12.5px !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    justify-content: center !important;
    text-align: center !important;
}}
[data-testid="stMain"] [data-testid="column"] {{
    min-width: 0 !important;
}}

/* Page fade-in */
[data-testid="stMain"]{{animation:ir_fadeSlideIn 0.4s ease-out;}}
@keyframes ir_fadeSlideIn{{
    from{{opacity:0;transform:translateY(12px);}}
    to{{opacity:1;transform:translateY(0);}}
}}

/* ============================================================
   SCOPED COMPONENT FIXES
============================================================ */
[data-testid="stSidebar"] .signout-container .stButton > button {{
    display: block !important;
    width: 100% !important;
    padding: 10px 14px !important;
    border-radius: 10px !important;
    border: 1px solid {p['sidebar_btn_border']} !important;
    background: {p['sidebar_btn_bg']} !important;
    color: {p['sidebar_btn_text']} !important;
    text-align: center !important;
    cursor: pointer !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}}
[data-testid="stSidebar"] .signout-container .stButton > button p,
[data-testid="stSidebar"] .signout-container .stButton > button span {{
    color: {p['sidebar_btn_text']} !important;
}}
[data-testid="stSidebar"] .signout-container .stButton > button:hover {{
    background: rgba(239,68,68,0.12) !important;
    border-color: rgba(239,68,68,0.4) !important;
    color: #ef4444 !important;
}}
[data-testid="stSidebar"] .signout-container .stButton > button:hover p,
[data-testid="stSidebar"] .signout-container .stButton > button:hover span {{
    color: #ef4444 !important;
}}

[data-testid="stMain"] .topbar-clean .stButton > button {{
    padding: 8px 10px !important;
    border-radius: 8px !important;
    background: transparent !important;
    border: none !important;
    color: {p['text_primary']} !important;
    cursor: pointer !important;
}}
[data-testid="stMain"] .topbar-clean .stButton > button p,
[data-testid="stMain"] .topbar-clean .stButton > button span {{
    color: {p['text_primary']} !important;
}}
[data-testid="stMain"] .topbar-clean .stButton > button:hover {{
    background: {p['glass_bg']} !important;
}}

[data-testid="stMain"] .ai-prompts-clean .stButton > button {{
    width: 100% !important;
    padding: 12px !important;
    border-radius: 12px !important;
    border: 1px solid {p['border']} !important;
    background: {p['secondary_btn_bg']} !important;
    color: {p['secondary_btn_text']} !important;
    text-align: center !important;
}}
[data-testid="stMain"] .ai-prompts-clean .stButton > button p,
[data-testid="stMain"] .ai-prompts-clean .stButton > button span {{
    color: {p['secondary_btn_text']} !important;
}}
[data-testid="stMain"] .ai-prompts-clean .stButton > button:hover {{
    background: {p['accent_soft']} !important;
    border-color: {p['accent']} !important;
    color: {p['accent']} !important;
}}

{system_extra}
</style>
""", unsafe_allow_html=True)

    # ── JS: force-zero the header gap that Streamlit's own JS re-adds ──────────
    import streamlit.components.v1 as _components
    _components.html("""
<script>
(function () {
    var SELECTORS = [
        '.stApp',
        '[data-testid="stAppViewContainer"]',
        '[data-testid="stMain"]',
        '[data-testid="stHeader"]',
        '[data-testid="stToolbar"]',
        '[data-testid="stStatusWidget"]',
        '[data-testid="stSidebarContent"]',
    ];

    function killGap() {
        SELECTORS.forEach(function (sel) {
            var el = window.parent.document.querySelector(sel);
            if (!el) return;
            el.style.setProperty('padding-top',  '0', 'important');
            el.style.setProperty('margin-top',   '0', 'important');
            if (sel === '[data-testid="stHeader"]' ||
                sel === '[data-testid="stToolbar"]' ||
                sel === '[data-testid="stStatusWidget"]') {
                el.style.setProperty('height',     '0', 'important');
                el.style.setProperty('min-height', '0', 'important');
                el.style.setProperty('overflow',   'hidden', 'important');
                el.style.setProperty('display',    'none', 'important');
            }
        });
        // Scroll main window to top
        window.parent.scrollTo(0, 0);
    }

    // Run immediately + after a short delay to catch Streamlit's late JS
    killGap();
    setTimeout(killGap, 100);
    setTimeout(killGap, 400);
    setTimeout(killGap, 800);

    // Keep watching: re-apply whenever Streamlit mutates the app element
    var appEl = window.parent.document.querySelector('.stApp');
    if (appEl) {
        new MutationObserver(killGap).observe(appEl, {
            attributes: true,
            attributeFilter: ['style'],
            subtree: false
        });
    }
})();
</script>
""", height=0)

def inject_theme():
    """Legacy: delegates to inject_global_css()."""
    inject_global_css()


def get_theme() -> str:
    t = st.session_state.get("theme", "light")
    if t == "system":
        t = "light"
        st.session_state["theme"] = "light"
    return t


def set_theme(theme: str):
    st.session_state["theme"] = theme
    st.rerun()


def get_theme_css_class() -> str:
    return "dark-mode" if get_theme() == "dark" else ""


def inject_theme_toggle(key_prefix: str = "sb"):
    current = get_theme()
    st.markdown('<div class="ir-theme-pill">', unsafe_allow_html=True)
    c1, c3 = st.columns([1, 1])
    with c1:
        if st.button("☀ Light", key=f"{key_prefix}_theme_light",
                     type="primary" if current == "light" else "secondary",
                     use_container_width=True):
            set_theme("light")
    with c3:
        if st.button("🌙 Dark", key=f"{key_prefix}_theme_dark",
                     type="primary" if current == "dark" else "secondary",
                     use_container_width=True):
            set_theme("dark")
    st.markdown("</div>", unsafe_allow_html=True)