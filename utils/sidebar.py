import streamlit as st
from auth.session import logout_user, load_css
from utils.notifications import generate_smart_suggestions


# ====================================================================
# SIDEBAR TOGGLE HELPERS
# ====================================================================

def apply_sidebar_visibility(is_collapsed: bool):
    if is_collapsed:
        st.markdown("""
<style>
section[data-testid="stSidebar"],
[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    width: 0px !important;
    min-width: 0px !important;
    max-width: 0px !important;
    overflow: hidden !important;
    transform: none !important;
    transition: none !important;
}
section[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div {
    width: 0px !important;
    min-width: 0px !important;
    overflow: hidden !important;
}
[data-testid="stMain"],
[data-testid="stAppViewContainer"] > section:last-child {
    margin-left: 0 !important;
    padding-left: 1rem !important;
    max-width: 100% !important;
    width: 100% !important;
    transition: none !important;
}
</style>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
<style>
section[data-testid="stSidebar"],
[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    width: 260px !important;
    min-width: 260px !important;
    max-width: 260px !important;
    transform: none !important;
    transition: none !important;
    overflow: hidden !important;
    position: relative !important;
    flex-shrink: 0 !important;
}
section[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    width: 260px !important;
    min-width: 260px !important;
    max-width: 260px !important;
    transform: none !important;
    overflow-x: hidden !important;
    overflow-y: auto !important;
    box-sizing: border-box !important;
}
section[data-testid="stSidebar"] .stButton > button {
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}
</style>
""", unsafe_allow_html=True)


def render_sidebar_toggle():
    """
    Renders a modern panel-collapse toggle button.
    Uses chevron arrows (\u2039 / \u203a) styled as a flat pill with subtle border.
    """
    is_collapsed = st.session_state.get('sidebar_collapsed', False)
    # \u2039 = collapse (panel is visible), \u203a = expand (panel is hidden)
    icon  = "\u2039" if not is_collapsed else "\u203a"
    title = "Collapse sidebar" if not is_collapsed else "Expand sidebar"

    # Inject toggle button style — use .st-key-{key} which is reliable across all browsers
    from utils.theme import get_palette
    _theme = st.session_state.get('theme', 'light')
    _p = get_palette(_theme)
    _bg   = _p['btn_bg']
    _col  = _p['accent']
    _bord = _p['btn_border']
    _hover_bg = _p.get('accent_soft', '#e0e7ff')
    _glow = "box-shadow:0 0 10px rgba(0,180,255,0.35) !important;" if _theme == 'dark' else ""
    st.markdown(f"""
<style>
/* Sidebar toggle button — keyed as btn_sidebar_toggle */
.st-key-btn_sidebar_toggle button,
.st-key-btn_sidebar_toggle > div > button {{
    width: 32px !important;
    height: 32px !important;
    min-height: 32px !important;
    padding: 0 !important;
    font-size: 18px !important;
    font-weight: 400 !important;
    line-height: 1 !important;
    border-radius: 8px !important;
    background: {_bg} !important;
    color: {_col} !important;
    border: 1px solid {_bord} !important;
    {_glow}
    transition: all 0.2s ease !important;
}}
.st-key-btn_sidebar_toggle button:hover,
.st-key-btn_sidebar_toggle > div > button:hover {{
    background: {_hover_bg} !important;
    border-color: {_col} !important;
    transform: scale(1.08) !important;
}}
.st-key-btn_sidebar_toggle button p,
.st-key-btn_sidebar_toggle button span {{
    color: {_col} !important;
}}
</style>
""", unsafe_allow_html=True)

    if st.button(icon, key="btn_sidebar_toggle", help=title):
        st.session_state['sidebar_collapsed'] = not is_collapsed
        st.rerun()


# ── Inline SVG icons for navigation ──────────────────────────────────────────
_ICON_HOME = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none"
  viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
  <polyline points="9 22 9 12 15 12 15 22"/></svg>"""

_ICON_FORYOU = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none"
  viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
</svg>"""

_ICON_EXPLORE = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none"
  viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="11" cy="11" r="8"/>
  <line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>"""

_ICON_TRENDING = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none"
  viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
  <polyline points="17 6 23 6 23 12"/></svg>"""

_ICON_ANALYTICS = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none"
  viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <line x1="18" y1="20" x2="18" y2="10"/>
  <line x1="12" y1="20" x2="12" y2="4"/>
  <line x1="6"  y1="20" x2="6"  y2="14"/>
  <line x1="2"  y1="20" x2="22" y2="20"/></svg>"""

_ICON_PROFILE = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none"
  viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
  <circle cx="12" cy="7" r="4"/></svg>"""

_ICON_ABOUT = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none"
  viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"/>
  <line x1="12" y1="16" x2="12" y2="12"/>
  <line x1="12" y1="8" x2="12.01" y2="8"/></svg>"""

_ICON_CHAT = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none"
  viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>"""

_ICON_LOGOUT = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none"
  viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
  <polyline points="16 17 21 12 16 7"/>
  <line x1="21" y1="12" x2="9" y2="12"/></svg>"""

NAV_ITEMS = [
    ("🏠", "Home",         "home",         "pages/01_Home.py"),
    ("⭐", "For You",      "for_you",      "pages/02_For_You.py"),
    ("🔍", "Explore",      "explore",      "pages/03_Explore.py"),
    ("📈", "Trending",     "trending",     "pages/04_Trending.py"),
    ("📊", "Analytics",    "analytics",    "pages/05_Analytics.py"),
    ("✨", "AI Assistant", "ai_assistant", "pages/08_AI_Assistant.py"),
    ("👤", "My Profile",   "my_profile",   "pages/06_My_Profile.py"),
    ("ℹ️", "About",        "about",        "pages/07_About.py"),
]

_LOGO_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 44 44" width="44" height="44">
  <defs>
    <linearGradient id="sb-lg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%"   stop-color="#6C63FF"/>
      <stop offset="50%"  stop-color="#06B6D4"/>
      <stop offset="100%" stop-color="#8B5CF6"/>
      <animateTransform attributeName="gradientTransform" type="rotate"
        values="0 22 22;360 22 22" dur="6s" repeatCount="indefinite"/>
    </linearGradient>
    <filter id="sb-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="1.5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect x="2" y="2" width="40" height="40" rx="11" fill="url(#sb-lg)"/>
  <path d="M14 18h16l-2 12H16L14 18z" fill="none" stroke="white" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M17 18v-3a5 5 0 0 1 10 0v3" fill="none" stroke="white" stroke-width="1.8" stroke-linecap="round"/>
  <path d="M35 7 L36.5 10 L40 11 L36.5 12 L35 15 L33.5 12 L30 11 L33.5 10 Z"
        fill="white" opacity="0.85">
    <animate attributeName="opacity" values="0.85;0.4;0.85" dur="2.5s" repeatCount="indefinite"/>
    <animateTransform attributeName="transform" type="rotate"
      values="0 35 11;20 35 11;0 35 11" dur="3s" repeatCount="indefinite"/>
  </path>
  <path d="M8 8 L8.8 10.2 L11 11 L8.8 11.8 L8 14 L7.2 11.8 L5 11 L7.2 10.2 Z"
        fill="white" opacity="0.6">
    <animate attributeName="opacity" values="0.6;0.2;0.6" dur="3.5s" repeatCount="indefinite"/>
  </path>
</svg>
"""


def _get_avatar_html(initials: str, size: int = 36) -> str:
    photo_b64 = st.session_state.get("profile_photo_b64")
    if photo_b64:
        return (
            f'<img src="data:image/png;base64,{photo_b64}" '
            f'style="width:{size}px;height:{size}px;border-radius:50%;'
            f'object-fit:cover;border:2px solid rgba(108,99,255,0.2);flex-shrink:0;display:block;" />'
        )
    return (
        f'<div style="width:{size}px;height:{size}px;border-radius:50%;'
        f'background:linear-gradient(135deg,#6C63FF,#06B6D4);'
        f'display:flex;align-items:center;justify-content:center;'
        f'color:white;font-weight:700;font-size:{int(size*0.36)}px;'
        f'flex-shrink:0;border:2px solid rgba(255,255,255,0.3);">{initials}</div>'
    )


def render_sidebar(current_page: str = "home", hide_ai_fab: bool = False):
    load_css()
    generate_smart_suggestions()

    from utils.theme import get_palette
    _theme = st.session_state.get("theme", "light")
    _p = get_palette(_theme)

    # Per-theme sidebar CSS — belt-and-suspenders over inject_global_css()
    if _theme == "dark":
        _sb_bg      = "#0d0d1f"
        _sb_text    = "#f0efff"
        _btn_bg     = "rgba(255,255,255,0.06)"
        _btn_border = "rgba(255,255,255,0.1)"
    else:
        _sb_bg      = "#f0f2f8"
        _sb_text    = "#0f0f1a"
        _btn_bg     = "rgba(255,255,255,0.55)"
        _btn_border = "rgba(99,102,241,0.18)"

    st.markdown(f"""
<style>
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"],
[data-testid="stSidebarUserContent"] {{
    background-color: {_sb_bg} !important;
    background: {_sb_bg} !important;
}}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{
    color: {_sb_text} !important;
}}
section[data-testid="stSidebar"] .stButton > button {{
    background-color: {_btn_bg} !important;
    background: {_btn_bg} !important;
    color: {_sb_text} !important;
    border: 1px solid {_btn_border} !important;
}}
section[data-testid="stSidebar"] .stButton > button p,
section[data-testid="stSidebar"] .stButton > button span {{
    color: {_sb_text} !important;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{
    background-color: rgba(99,102,241,0.15) !important;
    border-color: rgba(99,102,241,0.4) !important;
    color: #6366f1 !important;
}}
section[data-testid="stSidebar"] .stButton > button:hover p,
section[data-testid="stSidebar"] .stButton > button:hover span {{
    color: #6366f1 !important;
}}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 3px 12px rgba(99,102,241,0.35) !important;
}}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] p,
section[data-testid="stSidebar"] .stButton > button[kind="primary"] span {{
    color: #ffffff !important;
}}
</style>
""", unsafe_allow_html=True)

    full_name  = (st.session_state.get("full_name") or "Guest User").strip() or "Guest User"
    email      = st.session_state.get("user_email") or ""
    words      = [w for w in full_name.split() if w]
    initials   = "".join([w[0] for w in words[:2]]).upper() or "GU"
    is_guest   = st.session_state.get("user_id") == "guest"

    with st.sidebar:
        st.markdown(f"""
<div style="display:flex;align-items:center;gap:10px;padding:16px 16px 12px;">
  {_LOGO_SVG}
  <div>
    <div style="font-size:16px;font-weight:800;
                background:linear-gradient(135deg,#6C63FF,#06B6D4,#8B5CF6);
                background-size:200%;
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                letter-spacing:-0.4px;line-height:1.1;">IntelliRec</div>
    <div style="font-size:10px;color:{_p['text_muted']};font-weight:600;letter-spacing:0.8px;
                text-transform:uppercase;margin-top:1px;">AI Platform</div>
  </div>
</div>""", unsafe_allow_html=True)

        user_tag = "Guest" if is_guest else "Pro"
        tag_color = "#F59E0B" if is_guest else "#10B981"
        st.markdown(f"""
<div style="margin:0 10px 14px;padding:12px 14px;
            background-color:{_p['surface_bg']};
            backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
            border:1px solid {_p['border']};border-radius:14px;
            box-shadow:{_p['shadow']};">
  <div style="display:flex;align-items:center;gap:10px;">
    {_get_avatar_html(initials, 40)}
    <div style="overflow:hidden;min-width:0;flex:1;">
      <div style="font-weight:700;font-size:13.5px;color:{_p['text_primary']};
                  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
        {full_name}
      </div>
      <div style="font-size:11px;color:{_p['text_secondary']};
                  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:1px;">
        {email or "guest@intellirec.com"}
      </div>
    </div>
    <span style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:100px;
                 background:{tag_color}22;color:{tag_color};flex-shrink:0;">
      {user_tag}
    </span>
  </div>
</div>""", unsafe_allow_html=True)

        st.markdown('<div style="height:2px"></div>', unsafe_allow_html=True)

        st.markdown('<div style="padding:0 8px;">', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:10px;font-weight:600;color:{_p["text_muted"]};'
            'letter-spacing:0.8px;text-transform:uppercase;'
            'padding:0 8px;margin-bottom:4px;">Navigation</div>',
            unsafe_allow_html=True
        )

        for emoji, label, page_key, page_path in NAV_ITEMS:
            is_active = (current_page == page_key)
            btn_label = f"{emoji}  {label}"
            btn_type = "primary" if is_active else "secondary"
            if st.button(btn_label, key=f"nav_{page_key}", use_container_width=True, type=btn_type):
                if not is_active:
                    st.switch_page(page_path)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div style="flex:1;min-height:20px;"></div>', unsafe_allow_html=True)
        st.markdown('<hr>', unsafe_allow_html=True)

        st.markdown('<div style="padding:0 8px 6px;">', unsafe_allow_html=True)

        from utils.theme import inject_theme_toggle
        inject_theme_toggle()

        st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

        if st.session_state.get("_confirm_signout"):
            st.markdown(
                f'<p style="font-size:12px;font-weight:600;color:{_p["text_primary"]};'
                f'text-align:center;margin:4px 0 8px;padding:0 4px;">'
                f'Are you sure you want to exit?</p>',
                unsafe_allow_html=True,
            )
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("Yes, Exit", key="confirm_signout_yes",
                             use_container_width=True, type="primary"):
                    st.session_state["_confirm_signout"] = False
                    logout_user()
                    st.toast("Signed out successfully!", icon="✅")
                    st.rerun()
            with col_no:
                if st.button("Cancel", key="confirm_signout_no",
                             use_container_width=True, type="secondary"):
                    st.session_state["_confirm_signout"] = False
                    st.rerun()
        else:
            _ICON_LOGOUT_LARGE = (
                '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none"'
                ' viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"'
                ' stroke-linecap="round" stroke-linejoin="round">'
                '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>'
                '<polyline points="16 17 21 12 16 7"/>'
                '<line x1="21" y1="12" x2="9" y2="12"/>'
                '</svg>'
            )
            with st.container():
                st.markdown('<div class="signout-container">', unsafe_allow_html=True)
                st.markdown(
                    f'<div style="display:flex;justify-content:center;margin-bottom:4px;'
                    f'color:{_p["text_secondary"]};">{_ICON_LOGOUT_LARGE}</div>',
                    unsafe_allow_html=True,
                )
                if st.button("Sign Out", key="sign_out_clean", use_container_width=True):
                    st.session_state["_confirm_signout"] = True
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
<div style="text-align:center;padding:6px 0 10px;
            font-size:10px;color:{_p['text_muted']};letter-spacing:0.3px;">
  Powered by AI &middot; IntelliRec v2.0
</div>""", unsafe_allow_html=True)

    apply_sidebar_visibility(st.session_state.get('sidebar_collapsed', False))

    if not hide_ai_fab and current_page != "ai_assistant":
        _is_light = st.session_state.get('theme', 'light') == 'light'

        # Theme-aware FAB — light mode uses deeper purple + heavier shadow
        if _is_light:
            fab_bg       = 'linear-gradient(135deg, #4338ca, #7c3aed)'
            fab_shadow   = '0 8px 32px rgba(67,56,202,0.55), 0 3px 10px rgba(0,0,0,0.18)'
            fab_border   = '2.5px solid rgba(67, 56, 202, 0.4)'
            fab_hover_bg = 'linear-gradient(135deg, #3730a3, #6d28d9)'
            fab_hover_sh = '0 12px 40px rgba(67,56,202,0.7), 0 4px 14px rgba(0,0,0,0.2)'
            fab_glow_mid = '0 10px 36px rgba(67,56,202,0.65), 0 3px 10px rgba(0,0,0,0.18), 0 0 22px rgba(99,102,241,0.4)'
        else:
            fab_bg       = 'linear-gradient(135deg, #6366f1, #8b5cf6)'
            fab_shadow   = '0 6px 20px rgba(99,102,241,0.45)'
            fab_border   = '2px solid rgba(255, 255, 255, 0.2)'
            fab_hover_bg = 'linear-gradient(135deg, #4f46e5, #7c3aed)'
            fab_hover_sh = '0 8px 30px rgba(99,102,241,0.7)'
            fab_glow_mid = '0 8px 24px rgba(99,102,241,0.6), 0 0 18px rgba(99,102,241,0.35)'

        st.markdown(f"""
<style>
/* ── AI ASSISTANT FAB — Fixed bottom-right pill ──────── */
/* Uses .st-key-ai_fab (keyed container class) for reliable targeting */

.st-key-ai_fab {{
    position: fixed !important;
    bottom: 24px !important;
    right: 24px !important;
    z-index: 9999 !important;
    width: auto !important;
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
}}

/* Target every possible child: a, div, span, p, button */
.st-key-ai_fab a,
.st-key-ai_fab [data-testid="stPageLink"] > a,
.st-key-ai_fab [data-testid="stPageLink-nav"] > a {{
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 8px !important;
    background: {fab_bg} !important;
    color: white !important;
    padding: 12px 22px !important;
    border-radius: 100px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    box-shadow: {fab_shadow} !important;
    text-decoration: none !important;
    transition: transform 0.25s ease, box-shadow 0.25s ease !important;
    border: {fab_border} !important;
    letter-spacing: 0.3px !important;
}}

/* Float + glow animation */
@keyframes fab-float-glow {{
    0%   {{ transform: translateY(0px);  box-shadow: {fab_shadow}; }}
    50%  {{ transform: translateY(-5px); box-shadow: {fab_glow_mid}; }}
    100% {{ transform: translateY(0px);  box-shadow: {fab_shadow}; }}
}}
.st-key-ai_fab a,
.st-key-ai_fab [data-testid="stPageLink"] > a,
.st-key-ai_fab [data-testid="stPageLink-nav"] > a {{
    animation: fab-float-glow 3s ease-in-out infinite !important;
}}

/* Hover */
.st-key-ai_fab a:hover,
.st-key-ai_fab [data-testid="stPageLink"] > a:hover,
.st-key-ai_fab [data-testid="stPageLink-nav"] > a:hover {{
    background: {fab_hover_bg} !important;
    transform: translateY(-3px) scale(1.06) !important;
    box-shadow: {fab_hover_sh} !important;
    animation: none !important;
}}

/* Text inside — always white, no underline */
.st-key-ai_fab a p,
.st-key-ai_fab a span,
.st-key-ai_fab [data-testid="stPageLink"] a p,
.st-key-ai_fab [data-testid="stPageLink"] a span {{
    text-decoration: none !important;
    color: white !important;
    margin: 0 !important;
    font-weight: 700 !important;
}}

/* Also hide the outer wrapper's own background if Streamlit adds one */
.st-key-ai_fab > div,
.st-key-ai_fab [data-testid="stPageLink"] {{
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
    width: auto !important;
}}
</style>
""", unsafe_allow_html=True)

        with st.container(key="ai_fab"):
            st.page_link("pages/08_AI_Assistant.py", label="AI Assistant", icon="✨")