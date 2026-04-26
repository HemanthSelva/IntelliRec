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

# ── Global overrides ──────────────────────────────────────────────────────────
st.markdown(f"""
<style>
[data-testid="stMain"] p,
[data-testid="stMain"] span:not(.material-icons),
[data-testid="stMain"] label,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] div {{
    color: {p['text_primary']} !important; opacity:1 !important;
}}
[data-testid="stMain"] h1,[data-testid="stMain"] h2,
[data-testid="stMain"] h3,[data-testid="stMain"] h4 {{
    color: {p['text_primary']} !important; font-weight:700 !important;
}}
@keyframes avatarRing {{
    0%,100% {{ box-shadow: 0 0 0 3px #6366f1, 0 0 0 6px rgba(99,102,241,0.3); }}
    50%     {{ box-shadow: 0 0 0 3px #8b5cf6, 0 0 0 10px rgba(139,92,246,0.2); }}
}}
.avatar-animated {{ animation: avatarRing 2s ease-in-out infinite; border-radius: 50%; overflow: hidden; width: 96px; height: 96px; }}
/* Tab styling */
[data-testid="stTabs"] [data-testid="stTab"] {{
    font-size: 14px !important; font-weight: 600 !important; padding: 10px 20px !important;
}}
/* Hide file uploader "Limit: 200MB" text */
[data-testid="stFileUploaderDropzoneInstructions"] small {{ display: none !important; }}
/* Dark mode textarea (bio field) */
[data-testid="stTextArea"] textarea {{
    background: {p['input_bg']} !important;
    color: {p['text_primary']} !important;
    border-color: {p['border']} !important;
}}
[data-testid="stTextArea"] label p {{
    color: {p['text_secondary']} !important;
}}
/* Dark mode file uploader */
[data-testid="stFileUploaderDropzone"] {{
    background: {p['card_bg']} !important;
    border-color: {p['border']} !important;
}}
[data-testid="stFileUploaderDropzone"] button {{
    background: {p['btn_bg']} !important;
    color: {p['btn_text']} !important;
    border: 1px solid {p['btn_border']} !important;
}}
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] p {{
    color: {p['text_secondary']} !important;
}}
/* Dark mode selectbox (history filter) */
[data-testid="stSelectbox"] [data-baseweb="select"] > div {{
    background: {p['input_bg']} !important;
    border-color: {p['border']} !important;
}}
[data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stSelectbox"] [data-baseweb="select"] div {{
    color: {p['text_primary']} !important;
}}
/* Notification toggle — track and label colors */
.st-key-notif_inapp [role="switch"] {{
    background-color: {p['btn_bg']} !important;
    border-color: {p['border']} !important;
}}
.st-key-notif_inapp [role="switch"][aria-checked="true"] {{
    background-color: {p['accent']} !important;
    border-color: {p['accent']} !important;
}}
.st-key-notif_inapp label p {{
    color: {p['text_primary']} !important;
}}
</style>
""", unsafe_allow_html=True)

# ── User data ─────────────────────────────────────────────────────────────────
full_name    = (st.session_state.get("full_name") or "User").strip() or "User"
username     = st.session_state.get("username") or "user"
user_email   = st.session_state.get("user_email") or ""
user_id      = st.session_state.get("user_id") or "guest"
user         = st.session_state.get("current_user") or {}
member_since = user.get("member_since", "Today") if isinstance(user, dict) else "Today"
words        = [w for w in full_name.split() if w]
initials     = "".join([w[0] for w in words[:2]]).upper() or "U"
is_guest     = user_id == "guest"
user_bio     = (st.session_state.get('user_bio') or '').strip()


def _avatar_html(initials: str, size: int = 80) -> str:
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
            f'border:3px solid rgba(255,255,255,0.4);">'
            f'<span style="margin:0;line-height:1">{initials}</span></div>')


render_topbar("My Profile", "Your account, wishlist, and AI preferences")

# ── Counts (load once) ────────────────────────────────────────────────────────
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

# ═══════════════════════════════════════════════════════════════════════════════
#  HERO SECTION
# ═══════════════════════════════════════════════════════════════════════════════
_cover_bg = "linear-gradient(135deg, #6366f1 0%, #8b5cf6 40%, #06b6d4 100%)"
if theme == 'dark':
    _cover_bg = "linear-gradient(135deg, #0a1a40 0%, #0d2255 50%, #041e3a 100%)"

st.markdown(f"""
<div style="
    background: {_cover_bg};
    border-radius: 24px;
    padding: 0;
    margin-bottom: 0;
    position: relative;
    overflow: hidden;
    height: 130px;
">
  <div style="position:absolute;top:-40px;left:-40px;width:200px;height:200px;
              border-radius:50%;background:rgba(255,255,255,0.06);"></div>
  <div style="position:absolute;bottom:-60px;right:80px;width:180px;height:180px;
              border-radius:50%;background:rgba(255,255,255,0.04);"></div>
  <div style="position:absolute;top:20px;right:120px;width:60px;height:60px;
              border-radius:50%;background:rgba(255,255,255,0.08);"></div>
</div>
""", unsafe_allow_html=True)

# Avatar overlapping the cover
av_col, info_col, action_col = st.columns([1, 5, 2])
with av_col:
    st.markdown(f"""
<div style="margin-top:-50px;margin-left:20px;width:96px;overflow:visible;
            filter:drop-shadow(0 4px 16px rgba(0,0,0,0.25));">
  <div class="avatar-animated">
    {_avatar_html(initials, 96)}
  </div>
</div>""", unsafe_allow_html=True)

with info_col:
    _bio_html = (f'<p style="font-size:13px;color:{p["text_muted"]};margin:6px 0 0;'
                 f'line-height:1.5;">{user_bio[:120]}</p>') if user_bio else ''
    st.markdown(f"""
<div style="padding-top:8px;">
  <h1 style="font-size:22px;font-weight:800;color:{p['text_primary']};margin:0 0 2px;
             line-height:1.2;">{full_name}</h1>
  <p style="font-size:13px;color:{p['text_secondary']};margin:0 0 8px;">
    @{username} &nbsp;·&nbsp; {user_email or "guest@intellirec.com"}
  </p>
  <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
    <span style="background:{p['accent_soft']};color:{p['accent']};padding:3px 12px;
                 border-radius:100px;font-size:11px;font-weight:700;
                 border:1px solid rgba(99,102,241,0.2);">
      {'Guest' if is_guest else '✦ Member'} since {member_since}
    </span>
    {'<span style="background:rgba(245,158,11,0.15);color:#F59E0B;padding:3px 12px;border-radius:100px;font-size:11px;font-weight:700;">Guest Mode</span>' if is_guest else ''}
  </div>
  {_bio_html}
</div>""", unsafe_allow_html=True)

with action_col:
    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
    if st.button("✏️ Edit Profile", type="secondary", key="edit_profile_btn", use_container_width=True):
        st.session_state["profile_editing"] = True

st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

# ── Edit Profile Panel ────────────────────────────────────────────────────────
if '_temp_name' not in st.session_state:
    st.session_state['_temp_name'] = st.session_state.get('full_name', '')
if '_temp_bio' not in st.session_state:
    st.session_state['_temp_bio'] = st.session_state.get('user_bio', '')
if '_temp_photo' not in st.session_state:
    st.session_state['_temp_photo'] = None

if st.session_state.get("profile_editing"):
    st.markdown(f"""
<div style="background:{p['card_bg']};border:1.5px solid {p['border']};border-radius:20px;
            padding:28px 32px;margin:8px 0;box-shadow:{p['shadow']};
            border-top:3px solid {p['accent']};">
  <p style="font-size:16px;font-weight:700;color:{p['text_primary']};margin:0 0 4px;">
    ✏️ Edit Profile
  </p>
  <p style="font-size:13px;color:{p['text_muted']};margin:0 0 20px;">
    Update your name, bio, and photo
  </p>
</div>
""", unsafe_allow_html=True)

    ep_col1, ep_col2 = st.columns([1.4, 1])
    with ep_col1:
        ep_name = st.text_input("Display Name",
                                value=st.session_state['_temp_name'],
                                key="ep_name", placeholder="Your full name")
        st.session_state['_temp_name'] = ep_name
        st.text_input("Username", value=username, key="ep_username",
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
        st.markdown(_avatar_html(initials, 72), unsafe_allow_html=True)
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload new photo (JPG/PNG, max 10MB)",
                                    type=["jpg","jpeg","png","webp"],
                                    key="profile_photo_uploader")
        if uploaded is not None and st.session_state.get('_last_uploaded') != uploaded.name:
            st.session_state['_last_uploaded'] = uploaded.name
            if uploaded.size / (1024*1024) > 10:
                st.error("File too large (max 10MB).")
                st.session_state['_temp_photo'] = None
            else:
                try:
                    from PIL import ImageOps
                    img = Image.open(uploaded).convert("RGB")
                    img = ImageOps.fit(img, (256,256), method=Image.LANCZOS, centering=(0.5,0.15))
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                    st.session_state['_temp_photo'] = base64.b64encode(buf.getvalue()).decode()
                    st.session_state['_temp_photo_name'] = uploaded.name
                except Exception as e:
                    st.error(f"Could not process image: {e}")
        if st.session_state.get('_temp_photo'):
            st.image(f"data:image/png;base64,{st.session_state['_temp_photo']}",
                     width=80, caption="Preview")
        if st.session_state.get("profile_photo_b64"):
            if st.button("🗑 Remove Photo", key="remove_photo_btn", type="secondary"):
                del st.session_state["profile_photo_b64"]
                st.session_state['_temp_photo'] = None
                st.rerun()

    ep_save, ep_cancel, _ = st.columns([1, 1, 3])
    with ep_save:
        if st.button("💾 Save Changes", key="ep_save_btn", type="primary", use_container_width=True):
            new_name_val = st.session_state.get('_temp_name', '').strip()
            if not new_name_val:
                st.error("Display name cannot be empty.")
            else:
                st.session_state["full_name"] = new_name_val
                st.session_state["user_bio"]  = st.session_state.get('_temp_bio', '')
                if st.session_state.get('_temp_photo'):
                    st.session_state["profile_photo_b64"] = st.session_state['_temp_photo']
                    st.session_state['_temp_photo'] = None
                if user_id and user_id != 'guest':
                    try:
                        from database.supabase_client import supabase as sb
                        sb.table('profiles').upsert({
                            'id': user_id, 'full_name': new_name_val,
                            'bio': st.session_state["user_bio"],
                        }).execute()
                    except Exception as e:
                        st.warning(f"Saved locally. Sync error: {e}")
                st.session_state["profile_editing"] = False
                for key in ['_temp_name','_temp_bio','_temp_photo','_last_uploaded']:
                    st.session_state.pop(key, None)
                add_notification("success", "Profile Updated", "Your profile changes have been saved.")
                st.toast("Profile saved!", icon="✅")
                st.rerun()
    with ep_cancel:
        if st.button("✕ Cancel", key="ep_cancel_btn", type="secondary", use_container_width=True):
            for key in ['_temp_name','_temp_bio','_temp_photo','_last_uploaded']:
                st.session_state.pop(key, None)
            st.session_state["profile_editing"] = False
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
#  STAT METRICS ROW
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

_stats = [
    {"icon":"📋", "label":"Recommendations", "value": history_count or 145,
     "color":"#6366f1", "sub": "AI picks generated"},
    {"icon":"♥",  "label":"Wishlist Items",  "value": wishlist_count,
     "color":"#EC4899", "sub": "Products saved"},
    {"icon":"💬", "label":"Feedback Given",  "value": feedback_count or 21,
     "color":"#10B981", "sub": "Votes cast"},
    {"icon":"🏷️", "label":"Categories",     "value": cat_count or 3,
     "color":"#F59E0B", "sub": "Interests tracked"},
]

sc1, sc2, sc3, sc4 = st.columns(4)
for col, s in zip([sc1, sc2, sc3, sc4], _stats):
    with col:
        st.markdown(f"""
<div style="
    background: {p['card_bg']};
    border: 1px solid {p['border']};
    border-radius: 18px;
    padding: 20px 18px 18px;
    position: relative;
    overflow: hidden;
    box-shadow: {p['shadow']};
">
  <div style="position:absolute;top:0;left:0;right:0;height:3px;
              background:{s['color']};border-radius:18px 18px 0 0;"></div>
  <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:12px;">
    <div style="font-size:28px;line-height:1;">{s['icon']}</div>
    <div style="font-size:30px;font-weight:800;color:{s['color']};line-height:1;">{s['value']}</div>
  </div>
  <div style="font-size:13px;font-weight:700;color:{p['text_primary']};margin-bottom:2px;">{s['label']}</div>
  <div style="font-size:11px;color:{p['text_muted']};">{s['sub']}</div>
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN TABS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)

@st.dialog("Confirm Account Deletion")
def _delete_account_dialog(uid: str, email: str):
    st.markdown(f"**This action is permanent and cannot be undone.**")
    st.markdown(f"All data for **{email}** will be erased from IntelliRec.")
    st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
    dc1, dc2 = st.columns(2)
    with dc1:
        if st.button("Delete Forever", key="btn_confirm_delete",
                     type="primary", use_container_width=True):
            try:
                from database.supabase_client import supabase as _dsb
                from auth.session import logout_user as _logout
                for _tbl, _col in [
                    ('feedback', 'user_id'),
                    ('recommendation_history', 'user_id'),
                    ('wishlist', 'user_id'),
                    ('user_preferences', 'user_id'),
                    ('profiles', 'id'),
                ]:
                    try:
                        _dsb.table(_tbl).delete().eq(_col, uid).execute()
                    except Exception:
                        pass
                try:
                    from config import get_secret, SUPABASE_URL
                    _srk = get_secret("SUPABASE_SERVICE_ROLE_KEY")
                    if _srk:
                        from supabase import create_client
                        _admin = create_client(SUPABASE_URL, _srk)
                        _admin.auth.admin.delete_user(uid)
                except Exception:
                    pass
                _logout()
                st.toast("Account deleted.", icon="✅")
                st.switch_page("app.py")
            except Exception as _de:
                st.error(f"Deletion failed: {_de}")
    with dc2:
        if st.button("Cancel", key="btn_cancel_delete",
                     type="secondary", use_container_width=True):
            st.session_state['_confirm_delete_account'] = False
            st.rerun()


tab1, tab2, tab3, tab4 = st.tabs(["📊  Overview", "🕒  History", "♥  Wishlist", "⚙️  Settings"])

# ────────────────────────────────────────────────────────────────────────────
# TAB 1 — OVERVIEW
# ────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
    chart_col, activity_col = st.columns([1.1, 0.9])

    with chart_col:
        st.markdown(f"""
<div style="background:{p['card_bg']};border:1px solid {p['border']};border-radius:16px;
            padding:20px 20px 8px;box-shadow:{p['shadow']};">
  <p style="font-size:15px;font-weight:700;color:{p['text_primary']};margin:0 0 4px;">
    Category Preferences
  </p>
  <p style="font-size:12px;color:{p['text_muted']};margin:0 0 12px;">
    Distribution of your saved interests
  </p>
</div>""", unsafe_allow_html=True)

        _pie_user_cats = (st.session_state.get("pref_cats") or
                          st.session_state.get("preferred_categories") or [])
        if _pie_user_cats:
            _w = round(100 / len(_pie_user_cats))
            _pie_data = {cat: _w for cat in _pie_user_cats}
            _last_key = list(_pie_data)[-1]
            _pie_data[_last_key] = 100 - _w * (len(_pie_user_cats) - 1)
        else:
            _pie_data = {"Electronics": 40, "Home & Kitchen": 30,
                         "Clothing & Shoes": 20, "Beauty & Personal Care": 10}

        fig = px.pie(
            {"Category": list(_pie_data.keys()), "Views": list(_pie_data.values())},
            values="Views", names="Category", hole=0.55,
            color_discrete_sequence=["#6366f1","#06B6D4","#F59E0B","#EC4899","#10B981","#8B5CF6"]
        )
        fig.update_layout(
            margin=dict(t=10,b=10,l=0,r=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", color=p['text_primary']),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
        )
        fig.update_traces(textinfo="percent", textfont_size=12)
        st.plotly_chart(fig, use_container_width=True)

    with activity_col:
        st.markdown(f"""
<div style="background:{p['card_bg']};border:1px solid {p['border']};border-radius:16px;
            padding:20px;box-shadow:{p['shadow']};">
  <p style="font-size:15px;font-weight:700;color:{p['text_primary']};margin:0 0 4px;">
    Recent Activity
  </p>
  <p style="font-size:12px;color:{p['text_muted']};margin:0 0 16px;">
    Your latest interactions
  </p>
</div>""", unsafe_allow_html=True)

        _activities = []
        try:
            if wishlist_items:
                _wl0 = wishlist_items[0]
                _activities.append({
                    'bg': '#fdf2f8', 'color': '#EC4899', 'sym': '♥',
                    'desc': f"Saved {_wl0.get('product_title','a product')[:38]} to wishlist",
                    'when': 'Recently'
                })
        except Exception:
            pass
        _activities.append({'bg': '#dcfce7', 'color': '#10B981', 'sym': '✓',
                             'desc': 'Logged in successfully', 'when': 'Just now'})
        if st.session_state.get('pref_cats'):
            _activities.append({'bg': '#eef2ff', 'color': '#6366f1', 'sym': '⚙',
                                 'desc': f"AI engine tuned to {', '.join(st.session_state['pref_cats'][:2])}",
                                 'when': 'Earlier'})
        _fallback_acts = [
            {'bg': '#ecfeff', 'color': '#06B6D4', 'sym': '🔍',
             'desc': 'Explored product catalogue', 'when': 'Last session'},
            {'bg': '#fffbeb', 'color': '#F59E0B', 'sym': '★',
             'desc': 'Got AI-powered recommendations', 'when': 'Last session'},
        ]
        while len(_activities) < 4:
            _activities.append(_fallback_acts[len(_activities) % 2])

        for _act in _activities[:5]:
            _bg  = _act['bg']  if theme == 'light' else p['icon_bg_purple']
            st.markdown(f"""
<div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:8px;
            padding:12px 14px;background:{p['glass_bg']};
            border:1px solid {p['border']};border-radius:12px;
            border-left:3px solid {_act['color']};">
  <div style="width:30px;height:30px;border-radius:50%;background:{_bg};
              display:flex;align-items:center;justify-content:center;
              color:{_act['color']};font-size:13px;font-weight:700;
              flex-shrink:0;">{_act['sym']}</div>
  <div style="flex:1;min-width:0;">
    <p style="font-size:12.5px;color:{p['text_primary']};margin:0;
              font-weight:500;line-height:1.4;">{_act['desc']}</p>
    <p style="font-size:11px;color:{p['text_muted']};margin:2px 0 0;">{_act['when']}</p>
  </div>
</div>""", unsafe_allow_html=True)

    # ── Quick stats row ────────────────────────────────────────────────────
    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    st.markdown(f"""
<div style="background:{p['card_bg']};border:1px solid {p['border']};border-radius:16px;
            padding:20px 24px;box-shadow:{p['shadow']};">
  <p style="font-size:14px;font-weight:700;color:{p['text_primary']};margin:0 0 16px;">
    AI Engine Performance
  </p>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;">
    <div style="text-align:center;padding:14px;background:{p['glass_bg']};
                border-radius:12px;border:1px solid {p['border']};">
      <div style="font-size:22px;font-weight:800;color:#6366f1;">87%</div>
      <div style="font-size:11px;color:{p['text_muted']};margin-top:2px;">Avg Match Score</div>
    </div>
    <div style="text-align:center;padding:14px;background:{p['glass_bg']};
                border-radius:12px;border:1px solid {p['border']};">
      <div style="font-size:22px;font-weight:800;color:#10B981;">{history_count or 145}</div>
      <div style="font-size:11px;color:{p['text_muted']};margin-top:2px;">Products Shown</div>
    </div>
    <div style="text-align:center;padding:14px;background:{p['glass_bg']};
                border-radius:12px;border:1px solid {p['border']};">
      <div style="font-size:22px;font-weight:800;color:#F59E0B;">{wishlist_count}</div>
      <div style="font-size:11px;color:{p['text_muted']};margin-top:2px;">Items Saved</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# TAB 2 — HISTORY
# ────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    _session_recs = st.session_state.get("recommendation_history", [])
    _fy_last_recs = st.session_state.get("fy_last_recs", [])

    if history and len(history) > 0:
        hist_df = pd.DataFrame(history)
        col_map = {"created_at":"Date","product_title":"Product",
                   "engine_used":"Engine","match_score":"Match %"}
        hist_df = hist_df.rename(columns=col_map)
        if "Match %" in hist_df.columns:
            hist_df["Match %"] = hist_df["Match %"].apply(
                lambda x: f"{int(float(x))}%" if str(x).replace('.','').isdigit() else str(x))
        if "Date" in hist_df.columns:
            hist_df["Date"] = pd.to_datetime(hist_df["Date"], errors="coerce").dt.strftime("%b %d, %Y")
        _data_source = "live"
    elif _session_recs or _fy_last_recs:
        import datetime as _dt
        _src = _session_recs or _fy_last_recs
        rows = []
        for r in _src:
            rows.append({
                "Date":     _dt.date.today().strftime("%b %d, %Y"),
                "Product":  str(r.get("title", r.get("product_title","—")))[:50],
                "Category": r.get("category","—"),
                "Engine":   r.get("engine", r.get("engine_used","Hybrid")),
                "Match %":  f"{r.get('match_score', r.get('predicted_rating',0))}%",
            })
        hist_df = pd.DataFrame(rows)
        _data_source = "session"
    else:
        hist_df = pd.DataFrame(columns=["Date","Product","Category","Engine","Match %"])
        _data_source = "empty"

    filt_c1, filt_c2 = st.columns([1, 3])
    with filt_c1:
        engine_filter = st.selectbox("Filter by engine",
                                     ["All","Hybrid","Collaborative","Content-Based"],
                                     key="hist_engine_filter")
    if engine_filter != "All" and "Engine" in hist_df.columns:
        hist_df = hist_df[hist_df["Engine"].str.contains(engine_filter, case=False, na=False)]

    _display_cols = [c for c in ["Date","Product","Category","Engine","Match %"] if c in hist_df.columns]

    if hist_df.empty:
        st.markdown(f"""
<div style="background:{p['card_bg']};border:1px solid {p['border']};border-radius:16px;
            padding:48px;text-align:center;box-shadow:{p['shadow']};">
  <div style="font-size:48px;margin-bottom:12px;">📋</div>
  <p style="font-size:16px;font-weight:700;color:{p['text_primary']};margin:0 0 6px;">
    No recommendation history yet
  </p>
  <p style="font-size:13px;color:{p['text_secondary']};margin:0;">
    Visit the <strong>For You</strong> page to get AI-powered picks!
  </p>
</div>""", unsafe_allow_html=True)
    else:
        table_html = hist_df[_display_cols].to_html(index=False, classes="ir-hist-tbl", escape=False)
        st.markdown(f"""
<style>
.ir-hist-wrapper {{ width:100%;overflow-x:auto;border-radius:14px;
                    border:1px solid {p['border']};background:{p['card_bg']};margin-bottom:12px;
                    box-shadow:{p['shadow']}; }}
.ir-hist-tbl {{ width:100%;border-collapse:collapse;font-size:13.5px;
                text-align:left;color:{p['text_primary']}; }}
.ir-hist-tbl th {{ background:{p['glass_bg_strong']};padding:12px 18px;font-weight:600;
                   color:{p['text_secondary']};border-bottom:1px solid {p['border']};white-space:nowrap; }}
.ir-hist-tbl td {{ padding:12px 18px;border-bottom:1px solid {p['border']};white-space:nowrap; }}
.ir-hist-tbl tr:last-child td {{ border-bottom:none; }}
.ir-hist-tbl tr:hover {{ background:{p['glass_bg']}; }}
</style>
<div class="ir-hist-wrapper">{table_html}</div>
""", unsafe_allow_html=True)

        if _data_source == "session":
            st.markdown(f"""
<div style="background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.2);
            border-left:3px solid #10b981;border-radius:10px;
            padding:11px 16px;font-size:13px;color:{p['text_secondary']};">
  <strong style="color:#10b981">Session data</strong> —
  Showing recommendations from your current session. Sign in to save history permanently.
</div>""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
# TAB 3 — WISHLIST
# ────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
    session_wl_ids = st.session_state.get("wishlist_ids") or set()

    @st.cache_data
    def _load_products():
        with open("assets/sample_products.json", "r") as f:
            return json.load(f)

    all_products = _load_products()
    display_wl = []
    if wishlist_items:
        for item in wishlist_items:
            pid = item.get("product_id","")
            prod_data = next((pr for pr in all_products if pr.get("asin")==pid), None)
            if prod_data:
                display_wl.append(prod_data)
            else:
                display_wl.append({"asin":pid,"title":item.get("product_title","Product"),
                                   "price":item.get("product_price",0),
                                   "category":item.get("product_category",""),
                                   "rating":0,"review_count":0,"sentiment_label":""})
    elif session_wl_ids:
        display_wl = [pr for pr in all_products if pr.get("asin") in session_wl_ids]

    if display_wl:
        wl_head_c1, wl_head_c2 = st.columns([3, 1])
        with wl_head_c1:
            st.markdown(f"""
<p style="font-size:15px;font-weight:700;color:{p['text_primary']};margin:0;">
  {len(display_wl)} Saved {'Item' if len(display_wl)==1 else 'Items'}
</p>""", unsafe_allow_html=True)
        with wl_head_c2:
            if st.button("🗑️ Clear All", key="wl_clear_top_btn", type="secondary",
                         use_container_width=True):
                st.session_state["wishlist_ids"] = set()
                if user_id and user_id != 'guest':
                    try:
                        from database.supabase_client import supabase as _sb
                        _sb.table('wishlist').delete().eq('user_id', user_id).execute()
                    except Exception:
                        pass
                st.toast("Wishlist cleared.", icon="🗑️")
                st.rerun()

        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        from utils.helpers import render_product_card_html
        from utils.cart import add_to_cart as _add_to_cart, is_in_cart as _is_in_cart
        wl_cols = st.columns(3)
        for j, prod in enumerate(display_wl):
            pid = prod.get("asin", prod.get("product_id",""))
            with wl_cols[j % 3]:
                st.markdown(render_product_card_html(prod, j, show_match=False), unsafe_allow_html=True)
                wc1, wc2 = st.columns([1,1])
                with wc1:
                    _in_cart = _is_in_cart(pid)
                    _cart_lbl = "✓ In Cart" if _in_cart else "🛒 Add to Cart"
                    if st.button(_cart_lbl, key=f"wl_cart_{pid}_{j}",
                                 use_container_width=True, type="primary"):
                        if not _in_cart:
                            _add_to_cart(pid, prod.get("title",""),
                                         float(prod.get("price", 0)),
                                         prod.get("category",""))
                            st.toast("Added to cart!", icon="🛒")
                            st.rerun()
                with wc2:
                    if st.button("Remove", key=f"wl_rm_{pid}_{j}",
                                 use_container_width=True, type="secondary"):
                        try:
                            remove_from_wishlist(user_id, pid)
                            if "wishlist_ids" in st.session_state:
                                st.session_state["wishlist_ids"].discard(pid)
                            st.toast("Removed from wishlist", icon="✅")
                            st.rerun()
                        except Exception:
                            st.toast("Could not remove item")
    else:
        st.markdown(f"""
<div style="background:{p['card_bg']};border:1px solid {p['border']};border-radius:20px;
            padding:56px;text-align:center;box-shadow:{p['shadow']};">
  <div style="font-size:52px;margin-bottom:12px;">🤍</div>
  <p style="font-size:17px;font-weight:700;color:{p['text_primary']};margin:0 0 6px;">
    Your wishlist is empty
  </p>
  <p style="font-size:13px;color:{p['text_secondary']};margin:0 0 20px;">
    Save products you love while browsing recommendations
  </p>
</div>""", unsafe_allow_html=True)
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        if st.button("✦ Explore Products", key="wl_explore_btn", type="primary"):
            st.switch_page("pages/03_Explore.py")


# ────────────────────────────────────────────────────────────────────────────
# TAB 4 — SETTINGS
# ────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    # ── AI Preferences ────────────────────────────────────────────────────────
    st.markdown(f"""
<div style="background:{p['card_bg']};border:1px solid {p['border']};border-radius:16px;
            padding:20px 24px;margin-bottom:16px;box-shadow:{p['shadow']};
            border-top:3px solid {p['accent']};">
  <p style="font-size:15px;font-weight:700;color:{p['text_primary']};margin:0 0 4px;">
    AI Preferences
  </p>
  <p style="font-size:12px;color:{p['text_muted']};margin:0 0 16px;">
    Tune your recommendation engine
  </p>
</div>""", unsafe_allow_html=True)

    pref_col1, pref_col2 = st.columns([1, 1])
    with pref_col1:
        # Only the 4 real dataset categories
        _ALL_PREF_OPTIONS = [
            "Electronics", "Home & Kitchen", "Clothing & Shoes", "Beauty & Personal Care"
        ]
        _safe_defaults = [c for c in (cat_list or []) if c in _ALL_PREF_OPTIONS]
        if not _safe_defaults:
            _safe_defaults = ["Electronics", "Home & Kitchen"]
        pref_cats = st.multiselect("Favourite Categories",
                                   _ALL_PREF_OPTIONS,
                                   default=_safe_defaults,
                                   key="profile_pref_cats_widget")
        pref_engine = st.radio("Preferred AI Engine",
                               ["Hybrid","Collaborative Filtering","Content-Based"],
                               horizontal=True, key="pref_engine")
    with pref_col2:
        pref_diversity = st.slider("Recommendation Diversity (%)", 0, 100, 30,
                                   key="pref_diversity")
        st.markdown(f"""
<div style="background:{p['glass_bg']};border:1px solid {p['border']};border-radius:12px;
            padding:14px 16px;margin-top:8px;">
  <p style="font-size:12px;font-weight:600;color:{p['text_secondary']};margin:0 0 8px;">Theme</p>
</div>""", unsafe_allow_html=True)
        from utils.theme import inject_theme_toggle
        inject_theme_toggle(key_prefix="tab")

    st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
    save_c, _ = st.columns([1, 3])
    with save_c:
        if st.button("💾 Save Preferences", type="primary", key="pref_save",
                     use_container_width=True):
            if is_guest:
                st.warning("Guest account — preferences not saved. Sign up to persist settings.")
            else:
                try:
                    update_user_preferences(user_id, {
                        "preferred_categories": pref_cats,
                        "preferred_engine": pref_engine.lower().replace(" ","_"),
                        "diversity_level": pref_diversity,
                    })
                    st.session_state["pref_cats"] = pref_cats
                    st.session_state["preferred_categories"] = pref_cats
                    if isinstance(st.session_state.get("current_user"), dict):
                        st.session_state["current_user"]["preferred_categories"] = pref_cats
                    add_notification("success", "Settings Saved", "Preferences updated.")
                    st.toast("Preferences saved!", icon="✅")
                except Exception as _pref_err:
                    st.error(f"Could not save preferences. {_pref_err}")

    # ── Notifications ─────────────────────────────────────────────────────────
    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    st.markdown(f"""
<div style="background:{p['card_bg']};border:1px solid {p['border']};border-radius:16px;
            padding:20px 24px;box-shadow:{p['shadow']};
            border-top:3px solid #10B981;">
  <p style="font-size:15px;font-weight:700;color:{p['text_primary']};margin:0 0 16px;">
    Notifications
  </p>
  <div style="display:flex;flex-direction:column;gap:0;">
</div>""", unsafe_allow_html=True)

    notif_col, _ = st.columns([1, 2])
    with notif_col:
        st.toggle("In-App Notifications", value=True, key="notif_inapp")

    st.markdown(f"""
<div style="margin-top:8px;">
  <div style="display:flex;align-items:center;justify-content:space-between;
              padding:12px 0;border-top:1px solid {p['border']};">
    <div>
      <p style="font-size:14px;font-weight:500;color:{p['text_primary']};margin:0;">Email Digest</p>
      <p style="font-size:11px;color:{p['text_muted']};margin:2px 0 0;">Weekly summary of top picks</p>
    </div>
    <span style="font-size:11px;font-weight:600;background:{p['accent_soft']};
                 color:{p['accent']};padding:3px 12px;border-radius:100px;">Coming Soon</span>
  </div>
  <div style="display:flex;align-items:center;justify-content:space-between;
              padding:12px 0;border-top:1px solid {p['border']};">
    <div>
      <p style="font-size:14px;font-weight:500;color:{p['text_primary']};margin:0;">Price Drop Alerts</p>
      <p style="font-size:11px;color:{p['text_muted']};margin:2px 0 0;">SMS when wishlist items go on sale</p>
    </div>
    <span style="font-size:11px;font-weight:600;background:{p['accent_soft']};
                 color:{p['accent']};padding:3px 12px;border-radius:100px;">Coming Soon</span>
  </div>
  <div style="display:flex;align-items:center;justify-content:space-between;
              padding:12px 0;border-top:1px solid {p['border']};">
    <div>
      <p style="font-size:14px;font-weight:500;color:{p['text_primary']};margin:0;">Browser Push</p>
      <p style="font-size:11px;color:{p['text_muted']};margin:2px 0 0;">Real-time recommendation alerts</p>
    </div>
    <span style="font-size:11px;font-weight:600;background:{p['accent_soft']};
                 color:{p['accent']};padding:3px 12px;border-radius:100px;">Coming Soon</span>
  </div>
</div>""", unsafe_allow_html=True)

    # ── WARNING / Danger Zone ─────────────────────────────────────────────────
    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    st.markdown(f"""
<div style="display:flex;align-items:center;gap:12px;
            padding:14px 20px;background:{p['danger_bg']};
            border:1px solid {p['danger_border']};border-radius:14px;
            margin-bottom:14px;">
  <span style="font-size:20px;flex-shrink:0;">⚠️</span>
  <div>
    <p style="font-size:14px;font-weight:700;color:{p['danger_text']};margin:0;">WARNING!</p>
    <p style="font-size:11px;color:{p['danger_text']};opacity:0.75;margin:0;">
      Irreversible actions — proceed with caution
    </p>
  </div>
</div>""", unsafe_allow_html=True)

    dz_act1, dz_act2, _ = st.columns([1, 1, 2])
    with dz_act1:
        if st.button("🗑️ Clear Wishlist", key="clear_wl_btn", type="secondary",
                     use_container_width=True):
            st.session_state["wishlist_ids"] = set()
            if user_id and user_id != 'guest':
                try:
                    from database.supabase_client import supabase as _sb
                    _sb.table('wishlist').delete().eq('user_id', user_id).execute()
                except Exception:
                    pass
            st.toast("Wishlist cleared.", icon="🗑️")
            st.rerun()

    with dz_act2:
        if is_guest:
            st.markdown(f"""
<div style="background:{p['accent_soft']};border:1px solid rgba(99,102,241,0.2);
            border-radius:10px;padding:10px 14px;font-size:12px;color:{p['text_secondary']};">
  🔒 Sign in to delete account.
</div>""", unsafe_allow_html=True)
        else:
            if st.button("🗑️ Delete Account", key="btn_request_delete",
                         type="secondary", use_container_width=True):
                st.session_state['_confirm_delete_account'] = True
                st.rerun()

    if st.session_state.get('_confirm_delete_account') and not is_guest:
        _delete_account_dialog(user_id, user_email or "your account")
