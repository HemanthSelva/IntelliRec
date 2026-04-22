import streamlit as st
import base64
from auth.session import logout_user, load_css
from utils.notifications import get_unread_count, get_recent, mark_all_read, generate_smart_suggestions

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

_ICON_LOGOUT = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none"
  viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
  <polyline points="16 17 21 12 16 7"/>
  <line x1="21" y1="12" x2="9" y2="12"/></svg>"""

# ── Nav items: (icon_svg, label, page_key, page_path) ─────────────────────────
NAV_ITEMS = [
    (_ICON_HOME,      "Home",       "home",       "pages/01_Home.py"),
    (_ICON_FORYOU,    "For You",    "for_you",    "pages/02_For_You.py"),
    (_ICON_EXPLORE,   "Explore",    "explore",    "pages/03_Explore.py"),
    (_ICON_TRENDING,  "Trending",   "trending",   "pages/04_Trending.py"),
    (_ICON_ANALYTICS, "Analytics",  "analytics",  "pages/05_Analytics.py"),
    (_ICON_PROFILE,   "My Profile", "my_profile", "pages/06_My_Profile.py"),
    (_ICON_ABOUT,     "About",      "about",      "pages/07_About.py"),
]

# ── Animated IntelliRec logo SVG ──────────────────────────────────────────────
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
    """Return avatar HTML: photo if uploaded, else gradient initials."""
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


def render_sidebar(current_page: str = "home"):
    load_css()
    generate_smart_suggestions()

    from utils.theme import get_palette
    _theme = st.session_state.get("theme", "dark")
    _p = get_palette(_theme)

    full_name  = (st.session_state.get("full_name") or "Guest User").strip() or "Guest User"
    email      = st.session_state.get("user_email") or ""
    words      = [w for w in full_name.split() if w]
    initials   = "".join([w[0] for w in words[:2]]).upper() or "GU"
    is_guest   = st.session_state.get("user_id") == "guest"

    with st.sidebar:
        # Sidebar visual styling lives in utils/theme.py (glass system).
        # ── TOP: Logo ─────────────────────────────────────────────────────────
        st.markdown(f"""
<div style="display:flex;align-items:center;gap:10px;padding:16px 16px 12px;">
  {_LOGO_SVG}
  <div>
    <div style="font-size:16px;font-weight:800;
                background:linear-gradient(135deg,#6C63FF,#06B6D4,#8B5CF6);
                background-size:200%;
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                letter-spacing:-0.4px;line-height:1.1;">IntelliRec</div>
    <div style="font-size:10px;color:#9CA3AF;font-weight:600;letter-spacing:0.8px;
                text-transform:uppercase;margin-top:1px;">AI Platform</div>
  </div>
</div>""", unsafe_allow_html=True)

        # ── USER PROFILE CARD ─────────────────────────────────────────────────
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

        # ── NAVIGATION ────────────────────────────────────────────────────────
        st.markdown('<div style="padding:0 8px;">', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:10px;font-weight:600;color:{_p["text_muted"]};'
            'letter-spacing:0.8px;text-transform:uppercase;'
            'padding:0 8px;margin-bottom:4px;">Navigation</div>',
            unsafe_allow_html=True
        )

        for icon_svg, label, page_key, page_path in NAV_ITEMS:
            is_active = (current_page == page_key)
            
            # Use columns for both to maintain alignment
            col_icon, col_btn = st.columns([0.15, 0.85])
            with col_icon:
                color = "var(--nav-active-color)" if is_active else "var(--nav-color)"
                st.markdown(f'<div style="padding:10px 0 0 4px;color:{color};">{icon_svg}</div>', unsafe_allow_html=True)
            with col_btn:
                btn_type = "primary" if is_active else "secondary"
                if st.button(label, key=f"nav_{page_key}", use_container_width=True, type=btn_type):
                    if not is_active:
                        st.switch_page(page_path)

        st.markdown("</div>", unsafe_allow_html=True)

        # ── SPACER ────────────────────────────────────────────────────────────
        st.markdown('<div style="flex:1;min-height:20px;"></div>', unsafe_allow_html=True)
        st.markdown('<hr>', unsafe_allow_html=True)

        # ── BOTTOM: Theme + Sign Out ──────────────────────────────────────────
        st.markdown('<div style="padding:0 8px 6px;">', unsafe_allow_html=True)

        # Theme toggle — styled pill
        from utils.theme import inject_theme_toggle
        inject_theme_toggle()

        st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

        # Sign out — red glass styling lives in utils/theme.py (keyed selector)
        st.markdown('<div class="ir-signout-wrapper">', unsafe_allow_html=True)
        if st.button("↓ Sign Out", key="btn_sign_out",
                     use_container_width=True, type="secondary"):
            logout_user()
            st.toast("Signed out successfully!", icon="✓")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Powered by tag ────────────────────────────────────────────────────────
        st.markdown(f"""
<div style="text-align:center;padding:6px 0 10px;
            font-size:10px;color:{_p['text_muted']};letter-spacing:0.3px;">
  Powered by AI &middot; IntelliRec v2.0
</div>""", unsafe_allow_html=True)
