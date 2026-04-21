"""
IntelliRec Top Bar Component v5.0 — Single Icon Row (No Duplicates)
- Exactly 4 items: Wishlist · Bell · Cart · Avatar (all 40×40px)
- Only ONE implementation — Streamlit buttons styled as glass icon buttons
- No separate HTML-only icon layer (that caused the duplicate)
- Profile dropdown with Sign Out (red styled)
"""

import streamlit as st
from utils.notifications import get_unread_count, get_recent, mark_all_read

# ── SVG Icon Definitions ───────────────────────────────────────────────────────
_SVG_WISHLIST = """<svg width="18" height="18" viewBox="0 0 24 24"
     fill="none" stroke="var(--icon-stroke, #6C63FF)" stroke-width="2"
     stroke-linecap="round" stroke-linejoin="round">
  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
</svg>"""

_SVG_BELL = """<svg width="18" height="18" viewBox="0 0 24 24"
     fill="none" stroke="var(--icon-stroke, #6C63FF)" stroke-width="2"
     stroke-linecap="round" stroke-linejoin="round">
  <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
  <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
</svg>"""

_SVG_CART = """<svg width="18" height="18" viewBox="0 0 24 24"
     fill="none" stroke="var(--icon-stroke, #6C63FF)" stroke-width="2"
     stroke-linecap="round" stroke-linejoin="round">
  <circle cx="9" cy="21" r="1"/>
  <circle cx="20" cy="21" r="1"/>
  <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
</svg>"""

_SVG_SIGNOUT = """<svg width="16" height="16" viewBox="0 0 24 24"
     fill="none" stroke="currentColor" stroke-width="2"
     stroke-linecap="round" stroke-linejoin="round">
  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
  <polyline points="16 17 21 12 16 7"/>
  <line x1="21" y1="12" x2="9" y2="12"/>
</svg>"""

# ── Topbar CSS ─────────────────────────────────────────────────────────────────
_TOPBAR_CSS = """
<style>
/* Notification / dropdown panel */
.ir-notif-card {
    background: var(--bg-card, rgba(255,255,255,0.95));
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--border, rgba(108,99,255,0.12));
    border-radius: 16px;
    box-shadow: var(--shadow-lg, 0 8px 40px rgba(108,99,255,0.16));
    overflow: hidden;
    margin-bottom: 12px;
}

/* ── SINGLE icon row: hide the raw button face, show SVG + badge from label ── */
.ir-topbar-icons {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 8px;
    padding: 4px 0;
}

/* 4 Buttons container CSS injected by targeting the inner horizontal block */
div[data-testid="column"]:nth-child(2) > div[data-testid="stVerticalBlock"] > div > div > div[data-testid="stHorizontalBlock"] {
    gap: 8px !important;
    align-items: center !important;
    justify-content: flex-end !important;
}

div[data-testid="column"]:nth-child(2) > div[data-testid="stVerticalBlock"] > div > div > div[data-testid="stHorizontalBlock"] div[data-testid="column"] div[data-testid="stButton"] > button {
    width: 40px !important;
    height: 40px !important;
    border-radius: 12px !important;
    background: var(--icon-btn-bg, rgba(255,255,255,0.9)) !important;
    border: var(--icon-btn-border, 1px solid rgba(0,0,0,0.08)) !important;
    box-shadow: var(--icon-btn-shadow, 0 2px 8px rgba(0,0,0,0.06)) !important;
    color: transparent !important;
    padding: 0 !important;
    position: relative;
    min-height: 40px !important;
}
div[data-testid="column"]:nth-child(2) > div[data-testid="stVerticalBlock"] > div > div > div[data-testid="stHorizontalBlock"] div[data-testid="column"] div[data-testid="stButton"] > button p {
    display: none !important;
}

/* Wishlist SVG */
div[data-testid="column"]:nth-child(2) > div[data-testid="stVerticalBlock"] > div > div > div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(1) div[data-testid="stButton"] > button::before {
    content: '';
    position: absolute;
    width: 20px; height: 20px;
    background: url('data:image/svg+xml;utf8,<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23EC4899" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>') center/cover no-repeat;
    top: 9px; left: 9px;
}
/* Bell SVG */
div[data-testid="column"]:nth-child(2) > div[data-testid="stVerticalBlock"] > div > div > div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(2) div[data-testid="stButton"] > button::before {
    content: '';
    position: absolute;
    width: 20px; height: 20px;
    background: url('data:image/svg+xml;utf8,<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%23F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>') center/cover no-repeat;
    top: 9px; left: 9px;
}
/* Cart SVG */
div[data-testid="column"]:nth-child(2) > div[data-testid="stVerticalBlock"] > div > div > div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(3) div[data-testid="stButton"] > button::before {
    content: '';
    position: absolute;
    width: 20px; height: 20px;
    background: url('data:image/svg+xml;utf8,<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%236C63FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>') center/cover no-repeat;
    top: 9px; left: 9px;
}

/* Avatar Circle */
div[data-testid="column"]:nth-child(2) > div[data-testid="stVerticalBlock"] > div > div > div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(4) div[data-testid="stButton"] > button {
    border-radius: 50% !important;
    background: linear-gradient(135deg, #6C63FF, #06B6D4) !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    border: 2px solid rgba(255,255,255,0.4) !important;
    box-shadow: 0 2px 12px rgba(108,99,255,0.3) !important;
}
div[data-testid="column"]:nth-child(2) > div[data-testid="stVerticalBlock"] > div > div > div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(4) div[data-testid="stButton"] > button p {
    display: block !important;
}

/* Badges */
.bell-has-unread div[data-testid="column"]:nth-child(2) div[data-testid="stButton"] > button::after {
    content: '';
    position: absolute; top: -3px; right: -3px;
    background: #EF4444; color: white;
    font-size: 9px; font-weight: 700;
    width: 16px; height: 16px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    line-height: 16px;
}
.cart-has-items div[data-testid="column"]:nth-child(3) div[data-testid="stButton"] > button::after {
    content: '';
    position: absolute; top: -3px; right: -3px;
    background: #6C63FF; color: white;
    font-size: 9px; font-weight: 700;
    width: 16px; height: 16px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    line-height: 16px;
}

/* Sign out button red styling */
.ir-signout-btn > button {
    background: rgba(239,68,68,0.08) !important;
    border: 1px solid rgba(239,68,68,0.2) !important;
    color: #EF4444 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
.ir-signout-btn > button:hover {
    background: rgba(239,68,68,0.15) !important;
    border-color: rgba(239,68,68,0.35) !important;
    color: #DC2626 !important;
    transform: none !important;
    box-shadow: none !important;
}
</style>
"""


def render_topbar(page_title: str = "", subtitle: str = ""):
    """
    Renders the shared top bar for every page.
    Left: page title + subtitle
    Right: EXACTLY 4 items — Wishlist · Bell · Cart · Avatar (40×40px each)
    NO duplicate HTML icon layer — only the functional Streamlit buttons.
    """
    st.markdown(_TOPBAR_CSS, unsafe_allow_html=True)

    full_name      = (st.session_state.get("full_name") or "Guest User").strip() or "Guest User"
    words          = [w for w in full_name.split() if w]
    initials       = "".join([w[0] for w in words[:2]]).upper() or "GU"
    unread         = get_unread_count()
    is_guest       = st.session_state.get("user_id") == "guest"
    role_label     = "Guest" if is_guest else "Member"
    wishlist_count = len(st.session_state.get("wishlist_ids") or set())

    try:
        from utils.cart import get_cart_count
        cart_count = get_cart_count()
    except Exception:
        cart_count = 0

    # ── Row: title | icon buttons ─────────────────────────────────────────────
    left_col, right_col = st.columns([4, 3])

    with left_col:
        st.markdown(f"""
<div style="padding:2px 0 14px;">
  <h1 style="color:var(--text-primary);font-size:32px;
  font-weight:700;margin:0;">{page_title}</h1>
  <p style="color:var(--text-secondary);font-size:16px;
  margin-top:8px;margin-bottom:0;">{subtitle}</p>
</div>""", unsafe_allow_html=True)

    with right_col:
        # Add badge visibility css classes
        if unread > 0:
            st.markdown('<div class="bell-has-unread"></div>', unsafe_allow_html=True)
            st.markdown(f'<style>.bell-has-unread + div div[data-testid="column"]:nth-child(2) div[data-testid="stButton"] > button::after {{ content: "{unread}"; }}</style>', unsafe_allow_html=True)
            
        if cart_count > 0:
            st.markdown('<div class="cart-has-items"></div>', unsafe_allow_html=True)
            st.markdown(f'<style>.cart-has-items + div div[data-testid="column"]:nth-child(3) div[data-testid="stButton"] > button::after {{ content: "{cart_count}"; }}</style>', unsafe_allow_html=True)

        st.markdown('<div style="display:flex;align-items:center;gap:8px;justify-content:flex-end;">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns([1, 1, 1, 1])

        with c1:
            if st.button(" ", key="topbar_wl_btn",
                         help="Wishlist", type="secondary",
                         use_container_width=True):
                st.switch_page("pages/06_My_Profile.py")

        with c2:
            if st.button(" ", key="topbar_notif_btn",
                         help="Notifications", type="secondary",
                         use_container_width=True):
                st.session_state["show_topbar_notif"] = \
                    not st.session_state.get("show_topbar_notif", False)

        with c3:
            if st.button(" ", key="topbar_cart_btn",
                         help="Cart", type="secondary",
                         use_container_width=True):
                st.session_state["show_topbar_cart"] = \
                    not st.session_state.get("show_topbar_cart", False)

        with c4:
            if st.button(initials, key="topbar_avatar_btn",
                         help=f"Profile — {full_name}", type="secondary",
                         use_container_width=True):
                st.session_state["show_profile_dropdown"] = \
                    not st.session_state.get("show_profile_dropdown", False)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Dropdowns ─────────────────────────────────────────────────────────────
    if st.session_state.get("show_profile_dropdown", False):
        _render_profile_dropdown(full_name, role_label)

    if st.session_state.get("show_topbar_notif", False):
        _render_notif_dropdown(unread)

    if st.session_state.get("show_topbar_cart", False):
        _render_cart_dropdown()

    # ── Divider ──────────────────────────────────────────────────────────────
    st.markdown(
        '<hr style="border:none;border-top:1px solid var(--border,rgba(108,99,255,0.12));margin:0 0 20px;">',
        unsafe_allow_html=True
    )


def _render_profile_dropdown(full_name: str, role_label: str):
    """Profile dropdown with name, My Profile, and Sign Out (red styled)."""
    from auth.session import logout_user
    st.markdown(f"""
<div class="ir-notif-card" style="max-width:240px;margin-left:auto;margin-right:0;">
  <div style="padding:14px 18px 12px;border-bottom:1px solid var(--border,rgba(108,99,255,0.10));">
    <div style="font-size:13.5px;font-weight:700;color:var(--text-primary,#111827);">{full_name}</div>
    <div style="font-size:11.5px;color:var(--text-secondary,#9CA3AF);margin-top:2px;">{role_label}</div>
  </div>
</div>""", unsafe_allow_html=True)

    pd1, pd2 = st.columns([1, 1])
    with pd1:
        if st.button("My Profile", key="pd_profile_btn",
                     use_container_width=True, type="secondary"):
            st.session_state["show_profile_dropdown"] = False
            st.switch_page("pages/06_My_Profile.py")
    with pd2:
        st.markdown("""
<style>
div[data-testid="column"]:last-child div[data-testid="stButton"] > button[kind="secondary"] {
    background: rgba(239,68,68,0.08) !important;
    border: 1px solid rgba(239,68,68,0.2) !important;
    color: #EF4444 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
div[data-testid="column"]:last-child div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background: rgba(239,68,68,0.15) !important;
    border-color: rgba(239,68,68,0.35) !important;
}
</style>""", unsafe_allow_html=True)
        if st.button("Sign Out", key="pd_signout_btn",
                     use_container_width=True, type="secondary"):
            st.session_state["show_profile_dropdown"] = False
            logout_user()
            st.toast("Signed out successfully!", icon="✓")
            st.rerun()


def _render_cart_dropdown():
    """Cart panel with item list and clear/close buttons."""
    try:
        from utils.cart import get_cart_items, get_cart_total, get_cart_count
        items, total, count = get_cart_items(), get_cart_total(), get_cart_count()
    except Exception:
        items, total, count = [], 0.0, 0

    st.markdown(f"""
<div class="ir-notif-card">
  <div style="padding:14px 18px 12px;border-bottom:1px solid var(--border,rgba(108,99,255,0.10));
              display:flex;justify-content:space-between;align-items:center;">
    <span style="font-weight:700;font-size:14px;color:var(--text-primary,#111827);">Your Cart</span>
    <span style="font-size:11px;font-weight:700;padding:2px 10px;border-radius:100px;
                 background:var(--primary-light,#EEF2FF);color:var(--primary,#6C63FF);">{count} items</span>
  </div>""", unsafe_allow_html=True)

    if items:
        for item in items[:5]:
            pid = item.get('product_id', '')
            st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
            padding:10px 18px;border-bottom:1px solid rgba(108,99,255,0.06);">
  <div style="flex:1;min-width:0;">
    <div style="font-size:12.5px;font-weight:600;color:var(--text-primary,#111827);
                overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
      {item.get('title', '')[:40]}
    </div>
    <div style="font-size:11px;color:var(--text-secondary,#9CA3AF);margin-top:2px;">
      ${item.get('price', 0):.2f} &times; {item.get('qty', 1)}
    </div>
  </div>
</div>""", unsafe_allow_html=True)
            if st.button("Remove", key=f"cart_rm_{pid}_drop", type="secondary"):
                try:
                    from utils.cart import remove_from_cart
                    remove_from_cart(pid)
                    st.toast("Removed from cart", icon="✓")
                    st.rerun()
                except Exception:
                    pass

        st.markdown(f"""
<div style="padding:12px 18px;display:flex;justify-content:space-between;align-items:center;
            border-top:1px solid var(--border,rgba(108,99,255,0.10));">
  <span style="font-weight:700;font-size:14px;color:var(--text-primary,#111827);">Total</span>
  <span style="font-weight:700;font-size:16px;color:var(--primary,#6C63FF);">${total:.2f}</span>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="padding:32px;text-align:center;">
  <div style="font-size:13px;color:var(--text-secondary,#9CA3AF);">Your cart is empty</div>
</div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    cart_c1, cart_c2 = st.columns([1, 1])
    with cart_c1:
        if items and st.button("Clear All", key="cart_clear_btn",
                               use_container_width=True, type="secondary"):
            try:
                from utils.cart import clear_cart
                clear_cart()
                st.session_state["show_topbar_cart"] = False
                st.rerun()
            except Exception:
                pass
    with cart_c2:
        if st.button("Close", key="cart_close_btn",
                     use_container_width=True, type="secondary"):
            st.session_state["show_topbar_cart"] = False
            st.rerun()


def _render_notif_dropdown(unread: int):
    """Notification panel."""
    from utils.notifications import time_ago
    recent = get_recent(6)

    type_map = {
        "success":     ("&#10003;",  "#DCFCE7", "#16A34A"),
        "info":        ("i",         "#DBEAFE", "#2563EB"),
        "warning":     ("!",         "#FEF9C3", "#CA8A04"),
        "error":       ("&#10007;",  "#FEE2E2", "#DC2626"),
        "suggestion":  ("&#9654;",   "#EEF2FF", "#6C63FF"),
        "price_alert": ("$",         "#ECFEF7", "#047857"),
        "achievement": ("&#9733;",   "#FFFBEB", "#D97706"),
        "system":      ("&#9881;",   "#F5F3FF", "#7C3AED"),
    }

    badge_label = f"{unread} unread" if unread > 0 else "All read"
    st.markdown(f"""
<div class="ir-notif-card">
  <div style="padding:14px 18px 12px;border-bottom:1px solid var(--border,rgba(108,99,255,0.10));
              display:flex;justify-content:space-between;align-items:center;">
    <span style="font-weight:700;font-size:14px;color:var(--text-primary,#111827);">Notifications</span>
    <span style="font-size:11px;font-weight:700;padding:2px 10px;border-radius:100px;
                 background:var(--primary-light,#EEF2FF);color:var(--primary,#6C63FF);">{badge_label}</span>
  </div>""", unsafe_allow_html=True)

    if recent:
        for n in recent:
            sym, bg, col = type_map.get(n.get("type", "info"), ("i", "#F9FAFB", "#6B7280"))
            opacity = "0.55" if n.get("read") else "1"
            st.markdown(f"""
<div style="display:flex;gap:12px;padding:11px 18px;
            border-bottom:1px solid rgba(108,99,255,0.06);opacity:{opacity};">
  <div style="width:30px;height:30px;border-radius:50%;background:{bg};color:{col};
              display:flex;align-items:center;justify-content:center;
              font-size:13px;font-weight:700;flex-shrink:0;">{sym}</div>
  <div style="flex:1;min-width:0;">
    <div style="font-size:12.5px;font-weight:600;color:var(--text-primary,#111827);line-height:1.3;">
      {n['title']}
    </div>
    <div style="font-size:11.5px;color:var(--text-secondary,#6B7280);margin-top:2px;line-height:1.4;">
      {n['message'][:70]}{'...' if len(n['message']) > 70 else ''}
    </div>
    <div style="font-size:10px;color:var(--text-tertiary,#C4C4C4);margin-top:3px;">{time_ago(n['timestamp'])}</div>
  </div>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="padding:32px;text-align:center;">
  <div style="font-size:13px;font-weight:600;color:var(--text-primary,#111827);margin-bottom:4px;">All caught up</div>
  <div style="font-size:12px;color:var(--text-secondary,#9CA3AF);">No new notifications</div>
</div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    nc1, nc2 = st.columns([1, 1])
    with nc1:
        if unread > 0 and st.button("Mark all read", key="topbar_mark_read",
                                     use_container_width=True, type="secondary"):
            mark_all_read()
            st.session_state["show_topbar_notif"] = False
            st.rerun()
    with nc2:
        if st.button("Close", key="topbar_close_notif",
                     use_container_width=True, type="secondary"):
            st.session_state["show_topbar_notif"] = False
            st.rerun()
