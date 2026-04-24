"""
IntelliRec Top Bar Component v6.0 — Glass icon row, no animation.
Button styling is owned by utils/theme.py (avatar circle keyed on
"topbar_avatar_btn"). This module only renders the buttons + dropdowns.
"""

import streamlit as st
from utils.notifications import get_unread_count, get_recent, mark_all_read


def _build_topbar_css(card_bg: str, border: str, shadow: str) -> str:
    """Notification/cart dropdown panel + badge dot styles only."""
    return f"""
<style>
.ir-notif-card {{
    background: {card_bg};
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid {border};
    border-radius: 16px;
    box-shadow: {shadow};
    overflow: hidden;
    margin-bottom: 12px;
}}
.bell-has-unread div[data-testid="column"]:nth-child(2) div[data-testid="stButton"] > button::after {{
    content: '';
    position: absolute; top: -3px; right: -3px;
    background: #EF4444;
    width: 16px; height: 16px; border-radius: 50%;
}}
.cart-has-items div[data-testid="column"]:nth-child(3) div[data-testid="stButton"] > button::after {{
    content: '';
    position: absolute; top: -3px; right: -3px;
    background: #6C63FF;
    width: 16px; height: 16px; border-radius: 50%;
}}
</style>
"""


def render_topbar(page_title: str = "", subtitle: str = ""):
    """
    Renders the shared top bar for every page.
    Far-left: sidebar toggle button (☰/▶)
    Left: page title + subtitle
    Right: 4 items — Wishlist · Bell · Cart · Avatar
    """
    from utils.theme import get_palette
    from utils.sidebar import render_sidebar_toggle
    _theme = st.session_state.get("theme", "light")
    _p = get_palette(_theme)

    st.markdown(_build_topbar_css(
        card_bg=_p['card_bg'],
        border=_p['border'],
        shadow=_p['shadow'],
    ), unsafe_allow_html=True)

    full_name      = (st.session_state.get("full_name") or "Guest User").strip() or "Guest User"
    words          = [w for w in full_name.split() if w]
    initials       = "".join([w[0] for w in words[:2]]).upper() or "GU"
    unread         = get_unread_count()

    # ── Top row: toggle | title | action icons ────────────────────────────────
    toggle_col, left_col, right_col = st.columns([0.4, 3.6, 3])

    with toggle_col:
        render_sidebar_toggle()

    with left_col:
        st.markdown(f"""
<div style="padding:2px 0 14px;">
  <h1 style="color:{_p['text_primary']};font-size:32px;
  font-weight:700;margin:0;">{page_title}</h1>
  <p style="color:{_p['text_secondary']};font-size:16px;
  margin-top:8px;margin-bottom:0;">{subtitle}</p>
</div>""", unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="topbar-clean">', unsafe_allow_html=True)
        _hc1, _hc2, _hc3, _hc4 = st.columns([1, 1, 1, 1])
        with _hc1:
            if st.button("♡", key="topbar_wl_btn", type="secondary",
                         use_container_width=True):
                st.switch_page("pages/06_My_Profile.py")
        with _hc2:
            if st.button("🔔", key="topbar_notif_btn", type="secondary",
                         use_container_width=True):
                st.session_state["show_topbar_notif"] = \
                    not st.session_state.get("show_topbar_notif", False)
        with _hc3:
            if st.button("🛒", key="topbar_cart_btn", type="secondary",
                         use_container_width=True):
                st.session_state["show_topbar_cart"] = \
                    not st.session_state.get("show_topbar_cart", False)
        with _hc4:
            if st.button(initials, key="topbar_avatar_btn", type="secondary",
                         use_container_width=True):
                st.session_state['current_page'] = 'My Profile'
                st.switch_page("pages/06_My_Profile.py")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get("show_topbar_notif", False):
        _render_notif_dropdown(unread)

    if st.session_state.get("show_topbar_cart", False):
        _render_cart_dropdown()

    st.markdown(
        f'<hr style="border:none;border-top:1px solid {_p["border"]};margin:0 0 20px;">',
        unsafe_allow_html=True
    )


def _render_cart_dropdown():
    """Cart panel with item list and clear/close buttons."""
    theme = st.session_state.get('theme', 'light')

    panel_bg      = '#ffffff'  if theme == 'light' else '#1e1e35'
    panel_text    = '#0f0f1a'  if theme == 'light' else '#f1f5f9'
    panel_sub     = '#4b5563'  if theme == 'light' else '#a0aec0'
    panel_border  = '#e5e7eb'  if theme == 'light' else '#2d2d4a'
    panel_shadow  = '0 8px 32px rgba(0,0,0,0.12)' if theme == 'light' \
                    else '0 8px 32px rgba(0,0,0,0.4)'
    empty_icon_bg = '#f3f4f6'  if theme == 'light' else '#2d2d44'

    try:
        from utils.cart import get_cart_items, get_cart_total, get_cart_count
        items, total, count = get_cart_items(), get_cart_total(), get_cart_count()
    except Exception:
        items, total, count = [], 0.0, 0

    st.markdown(f"""
    <div style="
        background: {panel_bg};
        border: 1px solid {panel_border};
        border-radius: 16px;
        padding: 20px 0 0 0;
        box-shadow: {panel_shadow};
        margin-top: 8px;
        margin-bottom: 12px;
        overflow: hidden;
        position: relative;
        z-index: 100;
    ">
        <div style="display:flex; justify-content:space-between;
                    align-items:center; margin-bottom:16px; padding: 0 24px;">
            <span style="color:{panel_text}; font-size:16px; font-weight:700;">Your Cart</span>
            <span style="color:{panel_sub}; font-size:13px; background:{empty_icon_bg};
                         padding: 2px 10px; border-radius: 100px;">{count} items</span>
        </div>
""", unsafe_allow_html=True)

    if items:
        for item in items[:5]:
            pid = item.get('product_id', '')
            st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
            padding:10px 24px;border-bottom:1px solid {panel_border};">
  <div style="flex:1;min-width:0;">
    <div style="font-size:13px;font-weight:600;color:{panel_text};
                overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
      {item.get('title', '')[:40]}
    </div>
    <div style="font-size:12px;color:{panel_sub};margin-top:2px;">
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
<div style="padding:16px 24px;display:flex;justify-content:space-between;align-items:center;
            border-top:1px solid {panel_border};">
  <span style="font-weight:700;font-size:14px;color:{panel_text};">Total</span>
  <span style="font-weight:700;font-size:16px;color:#6C63FF;">${total:.2f}</span>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="text-align:center; padding:32px 0 48px;">
            <div style="background:{empty_icon_bg}; border-radius:50%;
                width:56px; height:56px; margin:0 auto 12px;
                display:flex; align-items:center; justify-content:center; font-size:24px;">
                🛒
            </div>
            <p style="color:{panel_sub}; font-size:14px; margin:0;">Your cart is empty</p>
        </div>
""", unsafe_allow_html=True)

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
    from utils.notifications import time_ago, get_recent, mark_all_read
    recent = get_recent(6)

    theme = st.session_state.get('theme', 'light')

    panel_bg      = '#ffffff'  if theme == 'light' else '#1e1e35'
    panel_text    = '#0f0f1a'  if theme == 'light' else '#f1f5f9'
    panel_sub     = '#4b5563'  if theme == 'light' else '#a0aec0'
    panel_border  = '#e5e7eb'  if theme == 'light' else '#2d2d4a'
    panel_shadow  = '0 8px 32px rgba(0,0,0,0.12)' if theme == 'light' \
                    else '0 8px 32px rgba(0,0,0,0.4)'
    empty_icon_bg = '#f3f4f6'  if theme == 'light' else '#2d2d44'

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
    <div style="
        background: {panel_bg};
        border: 1px solid {panel_border};
        border-radius: 16px;
        padding: 20px 0 0 0;
        box-shadow: {panel_shadow};
        margin-top: 8px;
        margin-bottom: 12px;
        overflow: hidden;
    ">
        <div style="display:flex; justify-content:space-between;
                    align-items:center; margin-bottom:16px; padding: 0 24px;">
            <span style="color:{panel_text}; font-size:16px; font-weight:700;">Notifications</span>
            <span style="color:{panel_sub}; font-size:13px; background:{empty_icon_bg};
                         padding: 2px 10px; border-radius: 100px;">{badge_label}</span>
        </div>
""", unsafe_allow_html=True)

    if recent:
        for n in recent:
            sym, bg, col = type_map.get(n.get("type", "info"), ("i", "#F9FAFB", "#6B7280"))
            opacity = "0.55" if n.get("read") else "1"
            st.markdown(f"""
<div style="display:flex;gap:12px;padding:12px 24px;
            border-bottom:1px solid {panel_border};opacity:{opacity};">
  <div style="width:32px;height:32px;border-radius:50%;background:{bg};color:{col};
              display:flex;align-items:center;justify-content:center;
              font-size:14px;font-weight:700;flex-shrink:0;">{sym}</div>
  <div style="flex:1;min-width:0;">
    <div style="font-size:13px;font-weight:600;color:{panel_text};line-height:1.3;">
      {n['title']}
    </div>
    <div style="font-size:12px;color:{panel_sub};margin-top:4px;line-height:1.4;">
      {n['message'][:70]}{'...' if len(n['message']) > 70 else ''}
    </div>
    <div style="font-size:11px;color:{panel_sub};margin-top:4px;">{time_ago(n['timestamp'])}</div>
  </div>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="text-align:center; padding:32px 0 48px;">
            <div style="background:{empty_icon_bg}; border-radius:50%;
                width:56px; height:56px; margin:0 auto 12px;
                display:flex; align-items:center; justify-content:center; font-size:24px;">
                🔔
            </div>
            <p style="color:{panel_sub}; font-size:14px; margin:0;">No new notifications</p>
        </div>
""", unsafe_allow_html=True)

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
