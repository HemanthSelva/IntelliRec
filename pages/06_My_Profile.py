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

st.set_page_config(page_title="My Profile | IntelliRec", page_icon="💡", layout="wide")
check_login()

from utils.theme import get_palette, inject_global_css
theme = st.session_state.get('theme', 'dark')
p = get_palette(theme)
inject_global_css(p)

render_sidebar("my_profile")

# ── Full contrast override for this page ──────────────────────────────────────
st.markdown(f"""
<style>
[data-testid="stMain"] p,
[data-testid="stMain"] span:not(.material-icons):not(.ir-gemini-icon),
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

# ── ANIMATION 6: Gradient banner + avatar ring ──
st.markdown("""
<style>
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes avatarRing {
    0%,100% { box-shadow: 0 0 0 3px #6366f1, 0 0 0 6px rgba(99,102,241,0.3); }
    50%     { box-shadow: 0 0 0 3px #8b5cf6, 0 0 0 10px rgba(139,92,246,0.2); }
}
@keyframes statPopIn {
    0%   { opacity: 0; transform: scale(0.8) translateY(15px); }
    70%  { transform: scale(1.05) translateY(-3px); }
    100% { opacity: 1; transform: scale(1) translateY(0); }
}
.profile-banner-animated {
    background: linear-gradient(270deg, #6366f1, #8b5cf6, #06b6d4, #10b981, #6366f1);
    background-size: 400% 400%;
    animation: gradientShift 6s ease infinite;
    height: 6px; border-radius: 3px; margin-bottom: 0;
}
.avatar-animated {
    animation: avatarRing 2s ease-in-out infinite;
    border-radius: 50%;
}
.stat-card-animated {
    animation: statPopIn 0.6s ease-out forwards;
}
</style>
<div class="profile-banner-animated"></div>
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
                f'object-fit:cover;border:3px solid rgba(255,255,255,0.6);display:block;" />')
    return (f'<div style="width:{size}px;height:{size}px;border-radius:50%;'
            f'background:linear-gradient(135deg,#6366f1,#06B6D4);'
            f'display:flex;align-items:center;justify-content:center;'
            f'color:white;font-size:{int(size*0.35)}px;font-weight:700;'
            f'border:3px solid rgba(255,255,255,0.4);">{initials}</div>')


render_topbar("My Profile", "Your account, wishlist, and AI preferences")

# ── Profile Header Card ───────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#6366f1 0%,#06B6D4 100%);
            border-radius:20px;padding:28px 28px 0;margin-bottom:0;
            position:relative;overflow:hidden;
            box-shadow:0 8px 40px rgba(99,102,241,0.3);">
  <div style="position:absolute;top:-40px;right:-40px;width:200px;height:200px;
              border-radius:50%;background:rgba(255,255,255,0.06);"></div>
  <div style="position:absolute;bottom:-60px;right:80px;width:150px;height:150px;
              border-radius:50%;background:rgba(255,255,255,0.04);"></div>
""", unsafe_allow_html=True)

av_col, info_col, btn_col = st.columns([1, 5, 2])
with av_col:
    st.markdown(_get_avatar_html(initials, 80), unsafe_allow_html=True)
with info_col:
    st.markdown(f"""
<h1 style="font-size:24px;font-weight:700;color:white;margin:0 0 4px;">{full_name}</h1>
<p style="font-size:13px;color:rgba(255,255,255,0.75);margin:0 0 10px;">
  @{username} &middot; {user_email or "guest@intellirec.com"}
</p>
<span style="background:rgba(255,255,255,0.2);color:white;padding:4px 12px;
             border-radius:100px;font-size:12px;font-weight:600;
             backdrop-filter:blur(4px);">
  Member since {member_since}
</span>
""", unsafe_allow_html=True)
with btn_col:
    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    if st.button("Edit Profile", type="secondary", key="edit_profile_btn"):
        st.session_state["profile_editing"] = True
    if is_guest:
        st.markdown("""
<div style="background:rgba(255,255,255,0.15);border-radius:8px;padding:8px 12px;
            margin-top:6px;font-size:11.5px;color:rgba(255,255,255,0.85);">
  <strong>Guest Mode</strong> — Sign in for full features
</div>""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ── Profile Photo Upload ──────────────────────────────────────────────────────
if st.session_state.get("profile_editing"):
    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
    with st.expander("Upload Profile Photo", expanded=True):
        uploaded = st.file_uploader("Choose a photo", type=["jpg","jpeg","png","webp"],
                                    key="profile_photo_upload", help="Square images work best. Max 5MB.")
        if uploaded:
            try:
                img = Image.open(uploaded).convert("RGB")
                img = img.resize((256, 256), Image.LANCZOS)
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                b64 = base64.b64encode(buffer.getvalue()).decode()
                st.session_state["profile_photo_b64"] = b64
                st.toast("Photo uploaded! It will appear in the sidebar and header.", icon="✓")
                st.rerun()
            except Exception as e:
                st.error(f"Could not process image: {e}")
        col_prev, col_rm = st.columns([1, 1])
        with col_prev:
            if st.session_state.get("profile_photo_b64"):
                st.markdown(f'<img src="data:image/png;base64,{st.session_state["profile_photo_b64"]}" '
                            f'style="width:80px;height:80px;border-radius:50%;object-fit:cover;'
                            f'border:2px solid {p["accent"]};" />', unsafe_allow_html=True)
        with col_rm:
            if st.session_state.get("profile_photo_b64"):
                if st.button("Remove Photo", key="remove_photo_btn", type="secondary"):
                    del st.session_state["profile_photo_b64"]
                    st.toast("Profile photo removed")
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
        cat_data = {"Category": ["Electronics", "Home & Kitchen", "Books", "Other"], "Views": [55, 25, 10, 10]}
        fig = px.pie(cat_data, values="Views", names="Category", hole=0.5,
                     color_discrete_sequence=["#6366f1", "#06B6D4", "#F59E0B", "#E5E7EB"])
        fig.update_layout(margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor="rgba(0,0,0,0)",
                          font=dict(family="Inter", color=p['text_primary']), showlegend=True)
        fig.update_traces(textinfo="percent+label", textfont_size=12)
        st.plotly_chart(fig, use_container_width=True)

    with activity_col:
        st.markdown(f'<p style="font-size:15px;font-weight:700;color:{p["text_primary"]};margin-bottom:12px;">Recent Activity</p>',
                    unsafe_allow_html=True)
        activities = [
            (p['icon_bg_green'],  "#16A34A", "&#10003;", "Logged in successfully",            "Just now"),
            (p['icon_bg_pink'],   "#EC4899", "♥",        "Saved Sony Headphones to wishlist", "Yesterday"),
            (p['icon_bg_amber'],  "#F59E0B", "★",        "Rated Instant Pot Duo 5 stars",     "2 days ago"),
            (p['icon_bg_purple'], p['accent'], "&#9679;", "Explored Electronics category",    "Last week"),
            (p['icon_bg_green'],  "#10B981", "&#9874;",  "Got 12 AI recommendations",         "Last week"),
        ]
        for bg, color, sym, desc, when in activities:
            st.markdown(f"""
<div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:10px;
            padding:12px 16px;background-color:{p['card_bg']};
            border:1px solid {p['border']};border-radius:12px;border-left:3px solid {color};">
  <div style="width:30px;height:30px;border-radius:50%;background-color:{bg};
              display:flex;align-items:center;justify-content:center;color:{color};
              font-size:13px;font-weight:700;flex-shrink:0;">{sym}</div>
  <div>
    <p style="font-size:13px;color:{p['text_primary']};margin:0;font-weight:500;">{desc}</p>
    <p style="font-size:11px;color:{p['text_muted']};margin:0;margin-top:2px;">{when}</p>
  </div>
</div>""", unsafe_allow_html=True)

with tab2:
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:15px;font-weight:700;color:{p["text_primary"]};margin-bottom:12px;">Recommendation History</p>',
                unsafe_allow_html=True)
    hist_df = pd.DataFrame({
        "Date":     ["2024-01-05","2024-01-04","2024-01-03","2024-01-01"],
        "Product":  ["Sony Headphones","Instant Pot Duo","Kindle Paperwhite","Air Fryer"],
        "Category": ["Electronics","Home & Kitchen","Electronics","Home & Kitchen"],
        "Engine":   ["Hybrid","Collaborative","Hybrid","Content-Based"],
        "Match %":  ["94%","82%","91%","75%"],
        "Feedback": ["Up","—","Down","Up"],
    })
    if history and len(history) > 0:
        hist_df = pd.DataFrame(history)
    engine_filter = st.selectbox("Filter by engine", ["All","Hybrid","Collaborative","Content-Based"],
                                 key="hist_engine_filter")
    if engine_filter != "All":
        col_name = "Engine" if "Engine" in hist_df.columns else "engine_used"
        if col_name in hist_df.columns:
            hist_df = hist_df[hist_df[col_name] == engine_filter]
    st.dataframe(hist_df, use_container_width=True, hide_index=True)
    if not (history and len(history) > 0):
        st.info("This is demo data. Real history appears once you use recommendations.")

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
                    if st.button("+ Cart", key=f"wl_cart_{pid}_{j}", use_container_width=True, type="primary"):
                        try:
                            from utils.cart import add_to_cart, is_in_cart
                            if not is_in_cart(pid):
                                add_to_cart(pid, prod.get("title",""), prod.get("price",0), prod.get("category",""))
                                st.toast("Added to cart!", icon="✓")
                            else:
                                st.toast("Already in cart")
                            st.rerun()
                        except Exception:
                            st.toast("Could not add to cart")
                with wc2:
                    if st.button("Remove", key=f"wl_rm_{pid}_{j}", use_container_width=True, type="secondary"):
                        try:
                            remove_from_wishlist(user_id, pid)
                            if "wishlist_ids" in st.session_state:
                                st.session_state["wishlist_ids"].discard(pid)
                            st.toast("Removed from wishlist", icon="✓")
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
        display_name = st.text_input("Display Name", value=full_name, key="pref_name")
        pref_cats = st.multiselect("Favourite Categories",
                                   ["Electronics","Home & Kitchen","Books","Sports","Clothing","Beauty"],
                                   default=cat_list or ["Electronics","Home & Kitchen"], key="pref_cats")
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
        st.toggle("Email Digest (coming soon)", value=False, key="notif_email", disabled=True)
        st.toggle("SMS Alerts (coming soon)", value=False, key="notif_sms", disabled=True)
        st.markdown(f"""
<div style="background-color:{p['accent_soft']};border-radius:10px;padding:12px 16px;
            margin-top:8px;font-size:12.5px;color:{p['text_secondary']};line-height:1.6;">
  <strong style="color:{p['accent']};">Coming soon via Supabase:</strong><br/>
  Email weekly digests &middot; SMS price drop alerts &middot; Browser push notifications
</div>""", unsafe_allow_html=True)
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    st.markdown("---")
    save_col, _ = st.columns([1, 2])
    with save_col:
        if st.button("Save Preferences", type="primary", key="pref_save", use_container_width=True):
            try:
                update_user_preferences(user_id, {
                    "preferred_categories": pref_cats,
                    "preferred_engine": pref_engine.lower().replace(" ", "_"),
                    "diversity_level": pref_diversity,
                })
                if display_name and display_name != full_name:
                    st.session_state["full_name"] = display_name
                add_notification("success", "Settings Saved", "Your preferences have been updated successfully.")
                st.toast("Profile saved successfully!", icon="✓")
            except Exception:
                st.toast("Could not save preferences. Try again.")

    st.markdown("---")
    st.markdown(f'<p style="font-size:14px;font-weight:700;color:{p["danger_text"]};margin-bottom:10px;">Danger Zone</p>',
                unsafe_allow_html=True)
    st.markdown(f"""
<div style="background-color:{p['danger_bg']};border:1px solid {p['danger_border']};
            border-radius:10px;padding:14px 18px;margin-bottom:12px;
            font-size:13px;color:{p['danger_text']};">
  Deleting your account is permanent and cannot be undone.
  All recommendations, wishlist items, and preferences will be removed.
</div>""", unsafe_allow_html=True)
    danger_col, _ = st.columns([1, 3])
    with danger_col:
        if st.button("Clear Wishlist", key="clear_wl_btn", type="secondary", use_container_width=True):
            try:
                st.session_state["wishlist_ids"] = set()
                st.toast("Wishlist cleared")
                st.rerun()
            except Exception:
                st.toast("Could not clear wishlist")
    st.button("Delete Account", type="secondary", key="prof_del", help="Contact support to delete your account")
