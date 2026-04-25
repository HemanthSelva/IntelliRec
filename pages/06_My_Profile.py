import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import json
import pandas as pd
import plotly.express as px
import base64
from io import BytesIO
from PIL import Image
from auth.session import check_login
from utils.sidebar import render_sidebar
from utils.topbar import render_topbar
from utils.notifications import add_notification
from database.db_operations import (
    get_wishlist, remove_from_wishlist,
    get_recommendation_history, update_user_preferences
)

st.set_page_config(page_title="My Profile | IntelliRec", page_icon="💡", layout="wide", initial_sidebar_state="expanded")
check_login()

from utils.theme import get_palette, inject_global_css
theme = st.session_state.get('theme', 'light')
p = get_palette(theme)
inject_global_css(p)

try:
    render_sidebar(current_page='my_profile')
except Exception as e:
    st.error(f"Sidebar error: {e}")

# ── Full contrast override for this page ──────────────────────────────────────
st.markdown(f"""
<style>
[data-testid="stMain"] p,
[data-testid="stMain"] span:not(.material-icons):not(.material-symbols-rounded):not(.material-symbols-outlined):not(.ir-gemini-icon),
[data-testid="stMain"] label,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] div {{
    color: {p['text_primary']} !important;
    opacity: 1 !important;
}}
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4 {{
    color: {p['text_primary']} !important;
    opacity: 1 !important;
    font-weight: 700 !important;
}}
</style>
""", unsafe_allow_html=True)

# ── Keep only the shared keyframes needed by other elements ────────────────────
st.markdown("""
<style>
@keyframes avatarRing {
    0%,100% { box-shadow: 0 0 0 3px #6366f1, 0 0 0 6px rgba(99,102,241,0.3); }
    50%     { box-shadow: 0 0 0 3px #8b5cf6, 0 0 0 10px rgba(139,92,246,0.2); }
}
@keyframes statPopIn {
    0%   { opacity: 0; transform: scale(0.8) translateY(15px); }
    70%  { transform: scale(1.05) translateY(-3px); }
    100% { opacity: 1; transform: scale(1) translateY(0); }
}
.avatar-animated { animation: avatarRing 2s ease-in-out infinite; border-radius: 50%; }
.stat-card-animated { animation: statPopIn 0.6s ease-out forwards; }
</style>
""", unsafe_allow_html=True)

full_name    = (st.session_state.get("full_name") or "User").strip() or "User"
username     = st.session_state.get("username") or "user"
user_email   = st.session_state.get("user_email") or ""
user_id      = st.session_state.get("user_id") or "guest"
user         = st.session_state.get("current_user") or {}
member_since = user.get("member_since", "Today") if isinstance(user, dict) else "Today"
words        = [w for w in full_name.split() if w]
initials     = "".join([w[0] for w in words[:2]]).upper() or "U"
is_guest     = user_id == "guest"


def _get_avatar_html(initials: str, size: int = 80) -> str:
    photo_b64 = st.session_state.get("profile_photo_b64")
    if photo_b64:
        return (f'<img src="data:image/png;base64,{photo_b64}" '
                f'style="width:{size}px;height:{size}px;border-radius:50%;'
                f'object-fit:cover;object-position:center top;'
                f'border:3px solid rgba(255,255,255,0.6);display:block;" />')
    return (f'<div style="width:{size}px;height:{size}px;border-radius:50%;'
            f'background:linear-gradient(135deg,#6366f1,#06B6D4);'
            f'display:flex;align-items:center;justify-content:center;'
            f'color:white;font-size:{int(size*0.35)}px;font-weight:700;'
            f'border:3px solid rgba(255,255,255,0.4);"><span style="margin:0;line-height:1">{initials}</span></div>')


render_topbar("My Profile", "Your account, wishlist, and AI preferences")

st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

# ── Profile Header Card — sleek glassmorphism ────────────
st.markdown(f"""
<div style="
    background: {p['glass_bg_strong']};
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1.5px solid {p['glass_border_soft']};
    border-radius: 20px;
    padding: 24px 28px 20px;
    margin-bottom: 0;
    position: relative;
    overflow: hidden;
    box-shadow: {p['glass_shadow_lg']};
">
  <!-- subtle top accent line instead of full gradient bg -->
  <div style="position:absolute;top:0;left:0;right:0;height:3px;
              background:linear-gradient(90deg,#6366f1,#8b5cf6,#06b6d4,#10b981);
              border-radius:20px 20px 0 0;"></div>
  <!-- decorative blur blobs inside card -->
  <div style="position:absolute;top:-30px;right:-30px;width:120px;height:120px;
              border-radius:50%;background:rgba(99,102,241,0.08);filter:blur(20px);"></div>
  <div style="position:absolute;bottom:-40px;right:60px;width:90px;height:90px;
              border-radius:50%;background:rgba(6,182,212,0.06);filter:blur(16px);"></div>
""", unsafe_allow_html=True)

av_col, info_col, btn_col = st.columns([1, 5, 2])
with av_col:
    st.markdown(_get_avatar_html(initials, 80), unsafe_allow_html=True)
with info_col:
    st.markdown(f"""
<h1 style="font-size:24px;font-weight:700;color:{p['text_primary']};margin:0 0 4px;">{full_name}</h1>
<p style="font-size:13px;color:{p['text_secondary']};margin:0 0 10px;">
  @{username} &middot; {user_email or "guest@intellirec.com"}
</p>
<span style="background:{p['accent_soft']};color:{p['accent']};padding:4px 12px;
             border-radius:100px;font-size:12px;font-weight:600;
             border:1px solid rgba(99,102,241,0.2);">
  Member since {member_since}
</span>
""", unsafe_allow_html=True)
with btn_col:
    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    if st.button("Edit Profile", type="secondary", key="edit_profile_btn"):
        st.session_state["profile_editing"] = True
    if is_guest:
        st.markdown(f"""
<div style="background:{p['accent_soft']};border-radius:8px;padding:8px 12px;
            margin-top:6px;font-size:11.5px;color:{p['text_secondary']};
            border:1px solid rgba(99,102,241,0.15);">
  <strong style="color:{p['accent']}">Guest Mode</strong> — Sign in for full features
</div>""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ── Edit Profile Modal (full glass card) ─────────────────────────────────────
if '_temp_name' not in st.session_state:
    st.session_state['_temp_name'] = st.session_state.get('full_name', '')
if '_temp_bio' not in st.session_state:
    st.session_state['_temp_bio'] = st.session_state.get('user_bio', '')
if '_temp_photo' not in st.session_state:
    st.session_state['_temp_photo'] = None

if st.session_state.get("profile_editing"):
    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    st.markdown(f"""
<div style="
    background: {p['glass_bg_strong']};
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1.5px solid {p['glass_border_soft']};
    border-radius: 20px;
    padding: 28px;
    box-shadow: {p['glass_shadow_lg']};
    margin-bottom: 8px;
">
  <div style="font-size:16px;font-weight:700;color:{p['text_primary']};margin-bottom:20px;
              display:flex;align-items:center;gap:10px;">
    ✏️ Edit Profile
  </div>
</div>
""", unsafe_allow_html=True)

    ep_col1, ep_col2 = st.columns([1, 1])
    with ep_col1:
        ep_name = st.text_input("Display Name",
                                value=st.session_state['_temp_name'],
                                key="ep_name", placeholder="Your full name")
        st.session_state['_temp_name'] = ep_name
        ep_username = st.text_input("Username", value=username, key="ep_username",
                                    placeholder="@handle", disabled=is_guest,
                                    help="Sign in to change your username")
        ep_bio = st.text_area("Bio",
                              value=st.session_state['_temp_bio'],
                              key="ep_bio", placeholder="Tell us something about yourself…",
                              max_chars=160, height=90)
        st.session_state['_temp_bio'] = ep_bio
    with ep_col2:
        st.markdown(f'<p style="font-size:12px;font-weight:600;color:{p["text_secondary"]};margin-bottom:6px;">Profile Photo</p>',
                    unsafe_allow_html=True)
        # Show current avatar preview
        st.markdown(_get_avatar_html(initials, 72), unsafe_allow_html=True)
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Upload new photo (JPG/PNG, max 10MB)",
            type=["jpg", "jpeg", "png", "webp"],
            key="profile_photo_uploader"
        )
        if (uploaded is not None and
                st.session_state.get('_last_uploaded') != uploaded.name):
            st.session_state['_last_uploaded'] = uploaded.name
            file_size_mb = uploaded.size / (1024 * 1024)
            if file_size_mb > 10:
                st.error(
                    f"File too large ({file_size_mb:.1f}MB). "
                    "Maximum allowed size is 10MB. Please choose a smaller image."
                )
                st.session_state['_temp_photo'] = None
            else:
                try:
                    from PIL import ImageOps
                    img = Image.open(uploaded).convert("RGB")
                    img = ImageOps.fit(img, (256, 256), method=Image.LANCZOS,
                                       centering=(0.5, 0.15))
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    st.session_state['_temp_photo'] = base64.b64encode(
                        buffer.getvalue()).decode()
                    st.session_state['_temp_photo_name'] = uploaded.name
                except Exception as e:
                    st.error(f"Could not process image: {e}")
        if st.session_state.get('_temp_photo'):
            st.image(
                f"data:image/png;base64,{st.session_state['_temp_photo']}",
                width=80, caption="Preview (not saved yet)"
            )
        if st.session_state.get("profile_photo_b64"):
            if st.button("🗑 Remove Photo", key="remove_photo_btn", type="secondary"):
                del st.session_state["profile_photo_b64"]
                st.session_state['_temp_photo'] = None
                st.rerun()

    ep_save, ep_cancel, _ = st.columns([1, 1, 3])
    with ep_save:
        if st.button("💾 Save Changes", key="ep_save_btn", type="primary",
                     use_container_width=True):
            new_name_val = st.session_state.get('_temp_name', '').strip()
            if not new_name_val:
                st.error("Display name cannot be empty.")
            else:
                st.session_state["full_name"] = new_name_val
                st.session_state["user_bio"] = st.session_state.get('_temp_bio', '')
                if st.session_state.get('_temp_photo'):
                    st.session_state["profile_photo_b64"] = st.session_state['_temp_photo']
                    st.session_state['_temp_photo'] = None
                if user_id and user_id != 'guest':
                    try:
                        from database.supabase_client import supabase as sb
                        sb.table('profiles').upsert({
                            'id': user_id,
                            'full_name': new_name_val,
                            'bio': st.session_state["user_bio"],
                        }).execute()
                    except Exception as e:
                        st.warning(f"Saved locally. Sync error: {e}")
                st.session_state["profile_editing"] = False
                for key in ['_temp_name', '_temp_bio', '_temp_photo', '_last_uploaded']:
                    st.session_state.pop(key, None)
                add_notification("success", "Profile Updated",
                                 "Your profile changes have been saved.")
                st.toast("✅ Profile saved!", icon="✅")
                st.rerun()
    with ep_cancel:
        if st.button("✕ Cancel", key="ep_cancel_btn", type="secondary",
                     use_container_width=True):
            for key in ['_temp_name', '_temp_bio', '_temp_photo', '_last_uploaded']:
                st.session_state.pop(key, None)
            st.session_state["profile_editing"] = False
            st.rerun()

st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

# ── Counts ───────────────────────────────────────────────────────────────────
try:
    wishlist_items = get_wishlist(user_id) or []
    wishlist_count = len(wishlist_items)
except Exception:
    wishlist_items = []
    wishlist_count = len(st.session_state.get("wishlist_ids") or set())

try:
    history       = get_recommendation_history(user_id) or []
    history_count = len(history)
except Exception:
    history       = []
    history_count = 0

feedback_count = len([k for k in st.session_state if k.startswith("fb_")])
prefs          = st.session_state.get("current_user") or {}
cat_list       = prefs.get("preferred_categories", []) if isinstance(prefs, dict) else []
cat_count      = len(cat_list)

try:
    from utils.cart import get_cart_count
    cart_count_stat = get_cart_count()
except Exception:
    cart_count_stat = 0

# SVG icons
_SVG_CLIPBOARD = f'<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" fill="none" viewBox="0 0 24 24" stroke="{p["accent"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>'
_SVG_HEART_STAT = '<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" fill="none" viewBox="0 0 24 24" stroke="#EC4899" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>'
_SVG_CHAT = '<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" fill="none" viewBox="0 0 24 24" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>'
_SVG_TAG = '<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" fill="none" viewBox="0 0 24 24" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>'

# ── Stat Cards ────────────────────────────────────────────────────────────────
stat_cols = st.columns(4)
stats = [
    (stat_cols[0], _SVG_CLIPBOARD,  "Recommendations", history_count or 145,  p['accent'],  p['icon_bg_purple']),
    (stat_cols[1], _SVG_HEART_STAT, "Wishlist Items",  wishlist_count,         "#EC4899",    p['icon_bg_pink']),
    (stat_cols[2], _SVG_CHAT,       "Feedback Given",  feedback_count or 21,   "#10B981",    p['icon_bg_green']),
    (stat_cols[3], _SVG_TAG,        "Categories",      cat_count or 3,         p['star_color'], p['icon_bg_amber']),
]
for col, icon_svg, label, val, color, icon_bg in stats:
    with col:
        st.markdown(f"""
<div style="background-color:{p['stat_card_bg']};
            border:1px solid {p['border']};border-radius:20px;
            padding:20px;text-align:center;border-top:3px solid {color};
            box-shadow:{p['shadow']};transition:transform 0.2s ease,box-shadow 0.2s ease;">
  <div style="width:48px;height:48px;border-radius:12px;background-color:{icon_bg};
              display:flex;align-items:center;justify-content:center;margin:0 auto 8px;">
    {icon_svg}
  </div>
  <div style="font-size:28px;font-weight:700;color:{color};margin-bottom:2px;">{val}</div>
  <div style="font-size:12px;color:{p['text_secondary']};font-weight:500;">{label}</div>
</div>""", unsafe_allow_html=True)

st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "History", "Wishlist", "Settings"])

with tab1:
    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
    chart_col, activity_col = st.columns([1, 1])
    with chart_col:
        st.markdown(f'<p style="font-size:15px;font-weight:700;color:{p["text_primary"]};margin-bottom:12px;">Category Preferences</p>',
                    unsafe_allow_html=True)
        # FIX 4A: Dynamic pie chart from user preferences
        _pie_user_cats = (
            st.session_state.get("pref_cats") or
            st.session_state.get("preferred_categories") or
            []
        )
        if _pie_user_cats:
            _pie_weight = round(100 / len(_pie_user_cats))
            _pie_data = {cat: _pie_weight for cat in _pie_user_cats}
            _pie_keys = list(_pie_data.keys())
            _pie_data[_pie_keys[-1]] = 100 - _pie_weight * (len(_pie_user_cats) - 1)
        else:
            _pie_data = {"Electronics": 55, "Home & Kitchen": 25, "Books": 10, "Other": 10}
        cat_data = {"Category": list(_pie_data.keys()), "Views": list(_pie_data.values())}
        _pie_colors = ["#6366f1", "#06B6D4", "#F59E0B", "#E5E7EB", "#EC4899", "#10B981",
                       "#8B5CF6", "#F97316", "#14B8A6", "#A855F7", "#EF4444", "#84CC16"]
        fig = px.pie(cat_data, values="Views", names="Category", hole=0.5,
                     color_discrete_sequence=_pie_colors[:len(cat_data["Category"])])
        fig.update_layout(margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor="rgba(0,0,0,0)",
                          font=dict(family="Inter", color=p['text_primary']), showlegend=True)
        fig.update_traces(textinfo="percent+label", textfont_size=12)
        st.plotly_chart(fig, use_container_width=True)

    with activity_col:
        st.markdown(f'<p style="font-size:15px;font-weight:700;color:{p["text_primary"]};margin-bottom:12px;">Recent Activity</p>',
                    unsafe_allow_html=True)
        # FIX 4B: Dynamic activity feed from real data
        _activities = []
        # Add real wishlist activity
        try:
            if wishlist_items:
                _latest_wl = wishlist_items[0]
                _activities.append({
                    'bg': p['icon_bg_pink'], 'color': '#EC4899', 'sym': '♥',
                    'desc': f"Saved {_latest_wl.get('product_title', 'a product')[:40]} to wishlist",
                    'when': 'Recently'
                })
        except Exception:
            pass
        # Add login activity
        _activities.append({
            'bg': p['icon_bg_green'], 'color': '#10B981', 'sym': '&#10003;',
            'desc': 'Logged in successfully', 'when': 'Just now'
        })
        # Add preference activity if categories set
        _act_pref_cats = st.session_state.get('pref_cats')
        if _act_pref_cats:
            _activities.append({
                'bg': p['icon_bg_purple'], 'color': p['accent'], 'sym': '&#9881;',
                'desc': f"Preferences set: {', '.join(_act_pref_cats[:2])}",
                'when': 'Earlier'
            })
        # Fallback if fewer than 3 activities
        if len(_activities) < 3:
            _activities.extend([
                {'bg': p['icon_bg_amber'], 'color': '#06B6D4', 'sym': '&#128269;',
                 'desc': 'Explored product catalogue', 'when': 'Last session'},
                {'bg': p['icon_bg_green'], 'color': '#8B5CF6', 'sym': '&#9874;',
                 'desc': 'Got AI recommendations', 'when': 'Last session'},
            ])
        _activities = _activities[:5]
        for _act in _activities:
            st.markdown(f"""
<div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:10px;
            padding:12px 16px;background-color:{p['card_bg']};
            border:1px solid {p['border']};border-radius:12px;border-left:3px solid {_act['color']};">
  <div style="width:30px;height:30px;border-radius:50%;background-color:{_act['bg']};
              display:flex;align-items:center;justify-content:center;color:{_act['color']};
              font-size:13px;font-weight:700;flex-shrink:0;">{_act['sym']}</div>
  <div>
    <p style="font-size:13px;color:{p['text_primary']};margin:0;font-weight:500;">{_act['desc']}</p>
    <p style="font-size:11px;color:{p['text_muted']};margin:0;margin-top:2px;">{_act['when']}</p>
  </div>
</div>""", unsafe_allow_html=True)

with tab2:
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:15px;font-weight:700;color:{p["text_primary"]};margin-bottom:12px;">Recommendation History</p>',
                unsafe_allow_html=True)

    # ── Build history: real DB rows first, then session-state recs ──
    _session_recs = st.session_state.get("recommendation_history", [])
    _fy_last_recs = st.session_state.get("fy_last_recs", [])  # from For You page
    _has_real_history = bool(history and len(history) > 0)
    _has_session_recs = bool(_session_recs)
    _has_fy_recs      = bool(_fy_last_recs)

    if _has_real_history:
        # Logged-in user with DB rows
        raw_rows = history
        hist_df = pd.DataFrame(raw_rows)
        # Normalise column names from Supabase schema → display names
        col_map = {
            "created_at": "Date", "product_title": "Product",
            "engine_used": "Engine", "match_score": "Match %"
        }
        hist_df = hist_df.rename(columns=col_map)
        if "Match %" in hist_df.columns:
            hist_df["Match %"] = hist_df["Match %"].apply(
                lambda x: f"{int(float(x))}%" if str(x).replace('.','').isdigit() else str(x))
        if "Date" in hist_df.columns:
            hist_df["Date"] = pd.to_datetime(hist_df["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
        _data_source = "live"
    elif _has_session_recs:
        # Guest who visited For You — session recs available
        rows = []
        import datetime as _dt
        for r in _session_recs:
            rows.append({
                "Date":     _dt.date.today().strftime("%Y-%m-%d"),
                "Product":  r.get("title", r.get("product_title", "—"))[:50],
                "Category": r.get("category", "—"),
                "Engine":   r.get("engine", r.get("engine_used", "Hybrid")),
                "Match %":  f"{r.get('match_score', r.get('predicted_rating', 0))}%",
                "Feedback": "—",
            })
        hist_df = pd.DataFrame(rows)
        _data_source = "session"
    elif _has_fy_recs:
        # Guest who visited For You page — use the products displayed there
        import datetime as _dt
        rows = []
        for r in _fy_last_recs:
            rows.append({
                "Date":     _dt.date.today().strftime("%Y-%m-%d"),
                "Product":  str(r.get("title", r.get("product_title", "—")))[:50],
                "Category": r.get("category", "—"),
                "Engine":   r.get("engine", "Hybrid"),
                "Match %":  f"{r.get('match_score', r.get('average_rating', 0))}%",
                "Feedback": "—",
            })
        hist_df = pd.DataFrame(rows)
        _data_source = "session"
    else:
        # No history at all — show empty state
        hist_df = pd.DataFrame(columns=["Date", "Product", "Category", "Engine", "Match %", "Feedback"])
        _data_source = "empty"

    engine_filter = st.selectbox("Filter by engine", ["All","Hybrid","Collaborative","Content-Based"],
                                 key="hist_engine_filter")
    if engine_filter != "All" and "Engine" in hist_df.columns:
        hist_df = hist_df[hist_df["Engine"].str.contains(engine_filter, case=False, na=False)]

    # Show only the useful columns that exist
    _display_cols = [c for c in ["Date","Product","Category","Engine","Match %","Feedback"]
                     if c in hist_df.columns]
                     
    if hist_df.empty:
        st.markdown(f"""
        <div style="background-color:{p['stat_card_bg']};border:1px solid {p['border']};border-radius:12px;
                    padding:30px;text-align:center;color:{p['text_secondary']};">
          No recommendation history found. Visit the <strong>For You</strong> page to get personalized AI picks!
        </div>""", unsafe_allow_html=True)
    else:
        # Render as HTML to support dark/light theme dynamically and provide horizontal sliding bar
        table_html = hist_df[_display_cols].to_html(index=False, classes="ir-history-table", escape=False)
        st.markdown(f"""
        <style>
        .ir-history-table-wrapper {{
            width: 100%;
            overflow-x: auto;
            border-radius: 10px;
            border: 1px solid {p['border']};
            background: {p['card_bg']};
            margin-bottom: 12px;
        }}
        .ir-history-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13.5px;
            text-align: left;
            color: {p['text_primary']};
        }}
        .ir-history-table th {{
            background: {p['glass_bg_strong']};
            padding: 12px 16px;
            font-weight: 600;
            color: {p['text_secondary']};
            border-bottom: 1px solid {p['border']};
            white-space: nowrap;
        }}
        .ir-history-table td {{
            padding: 12px 16px;
            border-bottom: 1px solid {p['border']};
            white-space: nowrap;
        }}
        .ir-history-table tr:last-child td {{
            border-bottom: none;
        }}
        .ir-history-table tr:hover {{
            background: {p['glass_bg']};
        }}
        </style>
        <div class="ir-history-table-wrapper">
            {table_html}
        </div>
        """, unsafe_allow_html=True)

    if _data_source == "session":
        st.markdown(f"""
<div style="background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.2);
            border-left:3px solid #10b981;border-radius:10px;
            padding:12px 16px;margin-top:10px;font-size:13px;color:{p['text_secondary']};">
  <strong style="color:#10b981">✅ Session data</strong> —
  Showing recommendations from your current session.
  Sign in to save history permanently.
</div>""", unsafe_allow_html=True)

with tab3:
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:15px;font-weight:700;color:{p["text_primary"]};margin-bottom:12px;">My Wishlist</p>',
                unsafe_allow_html=True)
    session_wl_ids = st.session_state.get("wishlist_ids") or set()

    @st.cache_data
    def _load_products():
        with open("assets/sample_products.json", "r") as f:
            return json.load(f)

    all_products = _load_products()
    display_wl = []
    if wishlist_items:
        for item in wishlist_items:
            pid = item.get("product_id", "")
            prod_data = next((pr for pr in all_products if pr.get("asin") == pid), None)
            if prod_data:
                display_wl.append(prod_data)
            else:
                display_wl.append({"asin": pid, "title": item.get("product_title","Product"),
                                   "price": item.get("product_price",0),
                                   "category": item.get("product_category",""),
                                   "rating": 0, "review_count": 0, "sentiment_label": ""})
    elif session_wl_ids:
        display_wl = [pr for pr in all_products if pr.get("asin") in session_wl_ids]

    if display_wl:
        from utils.helpers import render_product_card_html
        wl_cols = st.columns(3)
        for j, prod in enumerate(display_wl):
            pid = prod.get("asin", prod.get("product_id", ""))
            with wl_cols[j % 3]:
                st.markdown(render_product_card_html(prod, j, show_match=False), unsafe_allow_html=True)
                wc1, wc2 = st.columns([1, 1])
                with wc1:
                    if st.button("Find Similar", key=f"wl_sim_{pid}_{j}",
                                 use_container_width=True, type="primary"):
                        st.session_state["similar_product"] = pid  # must be string product_id
                        st.session_state["similar_product_title"] = prod.get("title", "")
                        st.switch_page("pages/02_For_You.py")
                with wc2:
                    if st.button("Remove", key=f"wl_rm_{pid}_{j}", use_container_width=True, type="secondary"):
                        try:
                            remove_from_wishlist(user_id, pid)
                            if "wishlist_ids" in st.session_state:
                                st.session_state["wishlist_ids"].discard(pid)
                            st.toast("Removed from wishlist", icon="✅")
                            st.rerun()
                        except Exception:
                            st.toast("Could not remove item")
    else:
        _SVG_EMPTY_HEART = f'<svg xmlns="http://www.w3.org/2000/svg" width="52" height="52" fill="none" viewBox="0 0 24 24" stroke="{p["border"]}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>'
        st.markdown(f"""
<div style="background-color:{p['stat_card_bg']};border:1px solid {p['border']};border-radius:20px;
            padding:56px;text-align:center;box-shadow:{p['shadow']};">
  <div style="display:flex;justify-content:center;margin-bottom:14px;">{_SVG_EMPTY_HEART}</div>
  <p style="font-size:17px;font-weight:700;color:{p['text_primary']};margin-bottom:6px;">Your wishlist is empty</p>
  <p style="font-size:14px;color:{p['text_secondary']};margin:0;">Save products you love while browsing recommendations</p>
</div>""", unsafe_allow_html=True)
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        if st.button("Explore Products", key="wl_explore_btn", type="primary"):
            st.switch_page("pages/03_Explore.py")

with tab4:
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown(f'<p style="font-size:15px;font-weight:700;color:{p["text_primary"]};margin-bottom:16px;">Account Preferences</p>',
                    unsafe_allow_html=True)
        # Display Name removed — edit it via Edit Profile button above
        # ── Settings: expanded category options (covers all onboarding + dataset categories) ──
        _ALL_PREF_OPTIONS = [
            "Electronics", "Home & Kitchen", "Books", "Sports",
            "Clothing", "Beauty", "Health", "Fitness", "Toys",
            "Automotive", "Office", "Garden", "Pet Supplies",
            "Clothing & Shoes", "Beauty & Personal Care"
        ]
        # Filter cat_list to only include values in options (prevents crash)
        _safe_defaults = [c for c in (cat_list or []) if c in _ALL_PREF_OPTIONS]
        if not _safe_defaults:
            _safe_defaults = ["Electronics", "Home & Kitchen"]
        pref_cats = st.multiselect("Favourite Categories",
                                   _ALL_PREF_OPTIONS,
                                   default=_safe_defaults, key="profile_pref_cats_widget")
        pref_engine = st.radio("Preferred AI Engine",
                               ["Hybrid","Collaborative Filtering","Content-Based"],
                               horizontal=True, key="pref_engine")
        pref_diversity = st.slider("Recommendation Diversity (%)", 0, 100, 30, key="pref_diversity")
        st.markdown(f'<p style="font-size:12px;font-weight:600;color:{p["text_muted"]}; text-transform:uppercase;letter-spacing:0.4px;margin-bottom:8px;margin-top:16px;">Theme</p>',
                    unsafe_allow_html=True)
        from utils.theme import inject_theme_toggle
        inject_theme_toggle(key_prefix="tab")

    with col_b:
        st.markdown(f'<p style="font-size:15px;font-weight:700;color:{p["text_primary"]};margin-bottom:16px;">Notifications</p>',
                    unsafe_allow_html=True)
        st.toggle("In-App Notifications", value=True, key="notif_inapp")
        st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
            padding:10px 0;border-bottom:1px solid {p['border']};">
  <span style="font-size:14px;color:{p['text_secondary']};">Email Digest</span>
  <span style="font-size:11px;font-weight:600;background:{p['accent_soft']};
               color:{p['accent']};padding:3px 10px;border-radius:100px;">Coming Soon</span>
</div>
<div style="display:flex;align-items:center;justify-content:space-between;
            padding:10px 0;border-bottom:1px solid {p['border']};">
  <span style="font-size:14px;color:{p['text_secondary']};">SMS Alerts</span>
  <span style="font-size:11px;font-weight:600;background:{p['accent_soft']};
               color:{p['accent']};padding:3px 10px;border-radius:100px;">Coming Soon</span>
</div>
<div style="background-color:{p['accent_soft']};border-radius:10px;padding:12px 16px;
            margin-top:12px;font-size:12.5px;color:{p['text_secondary']};line-height:1.6;">
  <strong style="color:{p['accent']};">Coming soon:</strong><br/>
  Email weekly digests &middot; SMS price drop alerts &middot; Browser push notifications
</div>""", unsafe_allow_html=True)
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    st.markdown("---")
    save_col, _ = st.columns([1, 2])
    with save_col:
        if st.button("Save Preferences", type="primary", key="pref_save", use_container_width=True):
            if is_guest:
                st.markdown(f"""
<div style="background:{p['dataset_bg']};border:1px solid {p['dataset_border']};
            border-left:4px solid {p['star_color']};border-radius:10px;
            padding:14px 18px;margin-top:12px;font-size:13.5px;
            color:{p['dataset_text']};line-height:1.6;">
  <strong>Guest account — preferences not saved.</strong><br/>
  Create a free account to persist your preferences. Guest settings are lost when you close the app.
</div>""", unsafe_allow_html=True)
                st.markdown(f"""
<div style="background:{p['accent_soft']};border:1px solid rgba(99,102,241,0.25);
            border-left:4px solid {p['accent']};border-radius:10px;
            padding:14px 18px;margin-top:8px;font-size:13.5px;
            color:{p['text_secondary']};line-height:1.6;">
  <strong style="color:{p['accent']};">Sign up to unlock:</strong><br/>
  Saved preferences &middot; Wishlist sync &middot; Recommendation history &middot; Full personalization
</div>""", unsafe_allow_html=True)
            else:
                try:
                    update_user_preferences(user_id, {
                        "preferred_categories": pref_cats,
                        "preferred_engine": pref_engine.lower().replace(" ", "_"),
                        "diversity_level": pref_diversity,
                    })
                    # Sync to session keys the recommendation engine reads
                    st.session_state["pref_cats"] = pref_cats
                    st.session_state["preferred_categories"] = pref_cats
                    if isinstance(st.session_state.get("current_user"), dict):
                        st.session_state["current_user"]["preferred_categories"] = pref_cats
                    add_notification("success", "Settings Saved", "Your preferences have been updated successfully.")
                    st.markdown(f"""
<div style="background:{p['badge_positive_bg']};border:1px solid rgba(16,185,129,0.3);
            border-left:4px solid #10b981;border-radius:10px;
            padding:14px 18px;margin-top:12px;font-size:13.5px;
            color:{p['badge_positive_text']};line-height:1.6;">
  <strong>Preferences saved successfully.</strong><br/>
  Your recommendation engine will use the updated settings from your next visit.
</div>""", unsafe_allow_html=True)
                    st.toast("Preferences saved.")
                except Exception as _pref_err:
                    st.markdown(f"""
<div style="background:{p['danger_bg']};border:1px solid {p['danger_border']};
            border-left:4px solid {p['danger_text']};border-radius:10px;
            padding:14px 18px;margin-top:12px;font-size:13.5px;
            color:{p['danger_text']};line-height:1.6;">
  <strong>Could not save preferences.</strong> Please try again.<br/>
  <span style="font-size:12px;opacity:0.7;">{_pref_err}</span>
</div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f'<p style="font-size:14px;font-weight:700;color:{p["danger_text"]};margin-bottom:10px;">⚠️ Danger Zone</p>',
                unsafe_allow_html=True)

    if st.button("🗑️ Clear Wishlist", key="clear_wl_btn", type="secondary"):
        st.session_state["wishlist_ids"] = set()
        if user_id and user_id != 'guest':
            try:
                from database.supabase_client import supabase as _sb
                _sb.table('wishlist').delete().eq('user_id', user_id).execute()
            except Exception:
                pass
        st.toast("Wishlist cleared.", icon="🗑️")
        st.rerun()

    st.markdown("---")

    if is_guest:
        st.markdown(f"""
<div style="background:{p['accent_soft']};border:1px solid rgba(99,102,241,0.2);
            border-radius:12px;padding:14px 18px;color:{p['text_secondary']};font-size:14px;">
    🔒 <strong>Account deletion</strong> is only available for registered users.
    <a href="#" style="color:{p['accent']};">Sign up</a> to access this feature.
</div>""", unsafe_allow_html=True)
    else:
        if not st.session_state.get('_confirm_delete_account'):
            st.markdown(f"""
<div style="background:{p['danger_bg']};border:1px solid {p['danger_border']};
            border-radius:12px;padding:14px 18px;color:{p['danger_text']};
            font-size:14px;margin-bottom:12px;">
    ⚠️ <strong>Permanent action.</strong> Deleting your account will remove all your
    recommendations, wishlist items, and preferences. This cannot be undone.
</div>""", unsafe_allow_html=True)
            if st.button("🗑️ Delete My Account", key="btn_request_delete", type="secondary"):
                st.session_state['_confirm_delete_account'] = True
                st.rerun()
        else:
            st.error(
                "🚨 Are you absolutely sure? This will permanently delete your account "
                "and all associated data."
            )
            col_confirm, col_back = st.columns(2)
            with col_confirm:
                if st.button("Yes, Delete Forever", key="btn_confirm_delete", type="primary"):
                    try:
                        from database.supabase_client import supabase as sb
                        from auth.session import logout_user
                        # Cascade delete in dependency order (children first)
                        for _tbl, _col in [
                            ('feedback',                 'user_id'),
                            ('recommendation_history',   'user_id'),
                            ('wishlist',                 'user_id'),
                            ('user_preferences',         'user_id'),
                            ('profiles',                 'id'),
                        ]:
                            try:
                                sb.table(_tbl).delete().eq(_col, user_id).execute()
                            except Exception:
                                pass
                        # Also delete the Supabase auth user if service role key is available
                        try:
                            from config import get_secret
                            _srk = get_secret("SUPABASE_SERVICE_ROLE_KEY")
                            if _srk:
                                from supabase import create_client
                                from config import SUPABASE_URL
                                _admin = create_client(SUPABASE_URL, _srk)
                                _admin.auth.admin.delete_user(user_id)
                        except Exception:
                            pass
                        logout_user()
                        st.toast("Account deleted.", icon="✅")
                        st.switch_page("app.py")
                    except Exception as e:
                        st.error(f"Deletion failed: {e}")
            with col_back:
                if st.button("Cancel", key="btn_cancel_delete"):
                    st.session_state['_confirm_delete_account'] = False
                    st.rerun()
