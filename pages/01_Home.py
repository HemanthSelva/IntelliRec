import streamlit as st
import json
import os
import sys
import pandas as pd
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth.session import check_login
from utils.sidebar import render_sidebar
from utils.topbar import render_topbar
from utils.helpers import render_product_card_html, normalize_categories, maybe_show_product_dialog
from utils.notifications import add_notification
from utils.model_loader import MODELS_READY, get_products_df, get_sentiments, get_hybrid_recommendations
from database.db_operations import add_to_wishlist, remove_from_wishlist

st.set_page_config(page_title="Home | IntelliRec", page_icon="💡", layout="wide", initial_sidebar_state="expanded")
check_login()

import importlib
import sys
if 'utils.theme' in sys.modules:
    importlib.reload(sys.modules['utils.theme'])

from utils.theme import get_palette, inject_global_css
theme = st.session_state.get('theme', 'light')
p = get_palette(theme)
inject_global_css(p)

render_sidebar("home")

# ── ANIMATION 1: Floating particles background ──
st.markdown("""
<style>
@keyframes floatUp {
    0%   { transform: translateY(100vh) scale(0); opacity: 0; }
    10%  { opacity: 0.6; }
    90%  { opacity: 0.3; }
    100% { transform: translateY(-10vh) scale(1.2); opacity: 0; }
}
.particle-container {
    position: fixed; top: 0; left: 280px;
    width: calc(100% - 280px); height: 100vh;
    pointer-events: none; overflow: hidden; z-index: 0;
}
.particle {
    position: absolute; border-radius: 50%;
    background: radial-gradient(circle, #6366f1, #8b5cf6);
    animation: floatUp linear infinite;
    opacity: 0;
}
</style>
<div class="particle-container">
  <div class="particle" style="width:8px;height:8px;left:10%;animation-duration:12s;animation-delay:0s;"></div>
  <div class="particle" style="width:5px;height:5px;left:25%;animation-duration:9s;animation-delay:2s;"></div>
  <div class="particle" style="width:10px;height:10px;left:40%;animation-duration:15s;animation-delay:4s;"></div>
  <div class="particle" style="width:6px;height:6px;left:55%;animation-duration:11s;animation-delay:1s;"></div>
  <div class="particle" style="width:8px;height:8px;left:70%;animation-duration:13s;animation-delay:3s;"></div>
  <div class="particle" style="width:4px;height:4px;left:85%;animation-duration:10s;animation-delay:5s;"></div>
  <div class="particle" style="width:7px;height:7px;left:60%;animation-duration:14s;animation-delay:7s;"></div>
</div>
""", unsafe_allow_html=True)

# ── Safe session state ─────────────────────────────────────────────────────────
full_name  = (st.session_state.get("full_name") or "User").strip() or "User"
first_name = full_name.split()[0] if full_name.split() else "User"
user_id    = st.session_state.get("user_id") or "guest"

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_sample_products():
    try:
        with open("assets/sample_products.json", "r") as f:
            return json.load(f)
    except Exception:
        return []


@st.cache_data(show_spinner=False, ttl=3600)
def _get_real_products_as_list(n=40):
    """
    Convert the top-N real products to a list of card dicts
    compatible with the existing render_section() / render_product_card_html() helpers.
    The helpers expect: asin, title, price, rating, category, etc.
    """
    df = get_products_df()
    sentiments = get_sentiments()
    if df.empty:
        return []

    df = df.copy()
    df["average_rating"] = pd.to_numeric(df["average_rating"], errors="coerce").fillna(0)
    df["rating_number"]  = pd.to_numeric(df["rating_number"],  errors="coerce").fillna(0)
    def _safe_price(x):
        if x is None:
            return 0.0
        try:
            cleaned = str(x).replace("$", "").replace(",", "").strip()
            # Handle 'from X.XX' patterns
            if cleaned.lower().startswith("from"):
                cleaned = cleaned[4:].strip()
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0

    df["price_num"] = df["price"].apply(_safe_price)

    # Always load from all 4 canonical categories so every section has data.
    # User preferences influence recommendation ordering, not product availability.
    user_cats = ["Electronics", "Home & Kitchen", "Beauty & Personal Care", "Clothing & Shoes"]

    n_per_cat = max(2, n // len(user_cats))
    cat_frames = []
    for cat in user_cats:
        cat_df = df[df["category"] == cat].nlargest(n_per_cat, "average_rating")
        print(f"[HOME]   '{cat}' -> {len(cat_df)} products")
        cat_frames.append(cat_df)

    top = pd.concat(cat_frames, ignore_index=True) if cat_frames else df.nlargest(n, "average_rating")

    records = []
    for _, row in top.iterrows():
        pid  = str(row["product_id"])
        sent = sentiments.get(pid, {})
        records.append({
            "asin":           pid,
            "product_id":     pid,
            "title":          str(row.get("title") or "Unknown"),
            "price":          float(row["price_num"]),
            "rating":         float(row["average_rating"]),
            "review_count":   int(row["rating_number"]),
            "category":       str(row.get("category") or "Electronics"),
            "store":          str(row.get("store") or ""),
            "sentiment_label": sent.get("label", "Mixed"),
            "sentiment_score": sent.get("score", 0.5),
            "is_trending":    float(row["rating_number"]) > 1000,
            "is_bestseller":  float(row["average_rating"]) >= 4.5,
            "description_short": "",
            "match_score":    min(99, int(round(float(row["average_rating"]) / 5.0 * 100))),
        })
    return records


if MODELS_READY:
    products = _get_real_products_as_list(n=40)
    if not products:
        products = load_sample_products()
else:
    products = load_sample_products()

# ── Wishlist state ────────────────────────────────────────────────────────────
if "wishlist_ids" not in st.session_state:
    if user_id == "guest":
        st.session_state["wishlist_ids"] = {
            p_["product_id"] for p_ in st.session_state.get("guest_wishlist", [])
        }
    else:
        try:
            from database.db_operations import get_wishlist
            wl = get_wishlist(user_id)
            st.session_state["wishlist_ids"] = {p_.get("product_id", "") for p_ in (wl or [])}
        except Exception:
            st.session_state["wishlist_ids"] = set()

# ── Top Bar ───────────────────────────────────────────────────────────────────
hour = datetime.now().hour
if hour < 12:   greeting = "Good morning"
elif hour < 17: greeting = "Good afternoon"
else:           greeting = "Good evening"

name = st.session_state.get('full_name', 'there')
first_name = name.split()[0] if name else 'there'
display = f"{greeting}, {first_name}"

render_topbar(
    page_title=display,
    subtitle="Here are today's picks curated by your AI engines"
)

maybe_show_product_dialog()

# ── Search ────────────────────────────────────────────────────────────────────
search = st.text_input("Search products",
                       placeholder="Search products, brands, categories…",
                       label_visibility="collapsed",
                       key="home_search_input")

st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

# ── Stats bar ─────────────────────────────────────────────────────────────────
_SVG_SHOP = """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="none"
  viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"
  stroke-linecap="round" stroke-linejoin="round">
  <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
  <line x1="3" y1="6" x2="21" y2="6"/>
  <path d="M16 10a4 4 0 0 1-8 0"/></svg>"""

_SVG_AI = """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="none"
  viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"
  stroke-linecap="round" stroke-linejoin="round">
  <rect x="2" y="3" width="20" height="14" rx="2"/>
  <line x1="8" y1="21" x2="16" y2="21"/>
  <line x1="12" y1="17" x2="12" y2="21"/></svg>"""

_SVG_LIVE = """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="none"
  viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"
  stroke-linecap="round" stroke-linejoin="round">
  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>"""

s1, s2, s3 = st.columns(3)
stat_data = [
    (s1, _SVG_SHOP, "1.4M+", "Products",           "#6366f1", p['icon_bg_purple']),
    (s2, _SVG_AI,   "3",     "AI Engines Active",   "#06b6d4", p['icon_bg_cyan']),
    (s3, _SVG_LIVE, "Live",  "Real-time Updates",   "#10b981", p['icon_bg_green']),
]
for col, icon_svg, val, label, accent, icon_bg in stat_data:
    with col:
        st.markdown(f"""
<div style="background-color:{p['stat_card_bg']};
            border:1px solid {p['border']};border-left:3px solid {accent};
            border-radius:14px;padding:16px 20px;
            display:flex;align-items:center;gap:14px;margin-bottom:20px;
            box-shadow:{p['shadow']};transition:box-shadow 0.2s ease,transform 0.2s ease;">
  <div style="width:42px;height:42px;border-radius:10px;background-color:{icon_bg};
              display:flex;align-items:center;justify-content:center;
              color:{accent};flex-shrink:0;">
    {icon_svg}
  </div>
  <div>
    <div style="font-size:20px;font-weight:700;color:{p['text_primary']};line-height:1;">{val}</div>
    <div style="font-size:12px;color:{p['text_secondary']};margin-top:3px;font-weight:500;">{label}</div>
  </div>
</div>""", unsafe_allow_html=True)

# ── Category filter pills ─────────────────────────────────────────────────────
FILTERS = ["All", "Electronics", "Home & Kitchen", "Beauty & Personal Care", "Clothing & Shoes", "Trending", "Top Rated", "New Arrivals"]
if "home_active_filter" not in st.session_state:
    st.session_state["home_active_filter"] = "All"

# Pill-button CSS — scoped to the filter row only
st.markdown(f"""<style>
.ir-filter-marker + div[data-testid="stHorizontalBlock"] .stButton > button {{
    border-radius: 100px !important;
    padding: 6px 16px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    min-height: 36px !important;
    white-space: nowrap !important;
    border: 1.5px solid {p['border']} !important;
    background: {p['filter_btn_bg']} !important;
    color: {p['filter_btn_text']} !important;
    transition: all 0.15s ease !important;
}}
.ir-filter-marker + div[data-testid="stHorizontalBlock"] .stButton > button:hover {{
    border-color: {p['accent']} !important;
    color: {p['accent']} !important;
}}
.ir-filter-marker + div[data-testid="stHorizontalBlock"] .stButton > button[kind="primary"] {{
    background: {p['accent']} !important;
    color: #ffffff !important;
    border-color: {p['accent']} !important;
    font-weight: 700 !important;
}}
.ir-filter-marker + div[data-testid="stHorizontalBlock"] .stButton > button p {{
    color: inherit !important;
}}
</style>
<div class="ir-filter-marker"></div>""", unsafe_allow_html=True)

# Clickable filter pill buttons — weighted columns so long labels don't truncate
_pill_cols = st.columns([0.5, 1, 1.2, 1.8, 1.4, 0.8, 0.8, 1])
for _pi, _pf in enumerate(FILTERS):
    with _pill_cols[_pi]:
        _is_active = (_pf == st.session_state["home_active_filter"])
        if st.button(_pf, key=f"filter_pill_{_pf}",
                     type="primary" if _is_active else "secondary",
                     use_container_width=True):
            st.session_state["home_active_filter"] = _pf
            st.rerun()

st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

# ── Build product pool based on active filter ─────────────────────────────────
active = st.session_state.get("home_active_filter", "All")
_DATASET_CATS = ["Electronics", "Home & Kitchen", "Beauty & Personal Care", "Clothing & Shoes"]

if active == "All":
    pool = products
elif active in _DATASET_CATS:
    pool = [pr for pr in products if pr.get("category") == active]
elif active == "Trending":
    pool = sorted(products, key=lambda x: x.get("review_count", 0), reverse=True)
elif active == "Top Rated":
    pool = sorted(products, key=lambda x: x.get("rating", 0), reverse=True)
elif active == "New Arrivals":
    pool = products[-20:] if len(products) > 20 else list(products)
else:
    pool = products

# Apply search filter on top of pool
if search:
    q = search.lower()
    pool = [pr for pr in pool
            if q in pr["title"].lower()
            or q in pr.get("category", "").lower()
            or q in pr.get("description_short", "").lower()]
    st.markdown(
        f'<p style="font-size:13px;color:{p["text_secondary"]};margin-bottom:12px;">'
        f'Showing {len(pool)} result(s) for <strong>"{search}"</strong></p>',
        unsafe_allow_html=True
    )

# ── Section icons ─────────────────────────────────────────────────────────────
_SVG_STAR_SEC = f"""<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="{p['accent']}"
  viewBox="0 0 24 24"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02
  12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>"""

_SVG_FIRE_SEC = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none"
  viewBox="0 0 24 24" stroke="#EF4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M12 2c0 6-6 8-6 14a6 6 0 0 0 12 0c0-4-2-7-2-9
           1 3 3 5 3 8a4 4 0 0 1-8 0c0-3 2-5 3-8"/>
</svg>"""

_SVG_AWARD_SEC = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none"
  viewBox="0 0 24 24" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="8" r="6"/>
  <path d="M15.477 12.89L17 22l-5-3-5 3 1.523-9.11"/>
</svg>"""

_SVG_HOME_SEC = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none"
  viewBox="0 0 24 24" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
  <polyline points="9 22 9 12 15 12 15 22"/>
</svg>"""

_SVG_SEARCH_SEC = f"""<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none"
  viewBox="0 0 24 24" stroke="{p['accent']}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="11" cy="11" r="8"/>
  <line x1="21" y1="21" x2="16.65" y2="16.65"/>
</svg>"""

_SVG_EYE_SEC = f"""<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none"
  viewBox="0 0 24 24" stroke="{p['text_secondary']}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
  <circle cx="12" cy="12" r="3"/>
</svg>"""


# ── Product section renderer ──────────────────────────────────────────────────
def render_section(title: str, icon_svg: str, prods: list, section_key: str):
    if not prods:
        return
    st.markdown(f"""
<div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;margin-top:4px;">
  {icon_svg}
  <h2 class="section-title" style="margin:0;color:{p['text_primary']};">{title}</h2>
  <div style="flex:1;height:1px;background-color:{p['border']};margin-left:4px;"></div>
  <span style="font-size:12px;color:{p['text_muted']};font-weight:500;">{len(prods[:4])} items</span>
</div>""", unsafe_allow_html=True)

    cols = st.columns(4)
    for i, prod in enumerate(prods[:4]):
        with cols[i]:
            st.markdown(render_product_card_html(prod, i), unsafe_allow_html=True)
            in_wish = prod["asin"] in st.session_state.get("wishlist_ids", set())
            save_label = "✓ Saved" if in_wish else "+ Save"

            bc1, bc2, bc3 = st.columns(3)
            with bc1:
                if st.button(save_label, key=f"{section_key}_save_{prod['asin']}", type="secondary", use_container_width=True):
                    if not isinstance(st.session_state.get("wishlist_ids"), set):
                        st.session_state["wishlist_ids"] = set()
                    try:
                        if in_wish:
                            remove_from_wishlist(user_id, prod["asin"])
                            st.session_state["wishlist_ids"].discard(prod["asin"])
                            st.toast("Removed from wishlist", icon="✅")
                        else:
                            success = add_to_wishlist(user_id, prod["asin"],
                                            prod.get("title", ""),
                                            prod.get("price", 0),
                                            prod.get("category", ""))
                            if success:
                                st.session_state["wishlist_ids"].add(prod["asin"])
                                try:
                                    add_notification("success", "Saved to Wishlist",
                                                     f"{prod.get('title','')[:35]} added to your wishlist")
                                except Exception:
                                    pass
                                st.toast("✅ Product saved to wishlist!", icon="💾")
                            else:
                                st.toast("Could not save. Try again.", icon="❌")
                        st.rerun()
                    except Exception as _save_err:
                        st.toast(f"Error: {_save_err}", icon="❌")
            with bc2:
                if st.button("Details", key=f"{section_key}_det_{prod['asin']}", type="secondary", use_container_width=True):
                    st.session_state["view_product"] = prod
                    st.rerun()
            with bc3:
                if st.button("Similar", key=f"{section_key}_sim_{prod['asin']}", type="secondary", use_container_width=True):
                    st.session_state["similar_product"] = prod["asin"]
                    st.session_state["similar_seed_category"] = prod.get("category", prod.get("main_category", ""))
                    st.switch_page("pages/02_For_You.py")

    st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)


# ── Section rendering ─────────────────────────────────────────────────────────
# SECTION 1: Recommended / main picks
if active == "All":
    _raw_pref = (
        st.session_state.get("pref_cats")
        or st.session_state.get("preferred_categories")
        or []
    )
    _norm_pref = normalize_categories(_raw_pref) if _raw_pref else []
    _pref_engine = st.session_state.get("preferred_engine", "hybrid")

    # Use ML engine if models are ready and user is logged in
    _rec_from_engine = []
    if MODELS_READY and user_id != "guest":
        try:
            _cats_for_rec = _norm_pref if _norm_pref else None
            if _pref_engine == "accuracy":
                from utils.model_loader import get_cf_recommendations
                _raw_recs = get_cf_recommendations(user_id, n=12, categories=_cats_for_rec)
            elif _pref_engine == "diversity":
                from utils.model_loader import get_cb_recommendations
                _raw_recs = get_cb_recommendations(categories=_cats_for_rec, n=12)
            else:
                _raw_recs = get_hybrid_recommendations(user_id, n=12, categories=_cats_for_rec, diversity=0.3)
            _rec_from_engine = _raw_recs[:8] if _raw_recs else []
        except Exception:
            _rec_from_engine = []

    if _rec_from_engine:
        render_section("Recommended For You", _SVG_STAR_SEC, _rec_from_engine, "rec")
    elif _norm_pref:
        rec_products = [pr for pr in products if pr.get("category") in _norm_pref]
        if not rec_products:
            rec_products = pool[:8]
        render_section("Recommended For You", _SVG_STAR_SEC, rec_products[:8], "rec")
    else:
        render_section("Recommended For You", _SVG_STAR_SEC, pool[:8], "rec")

    if _norm_pref:
        st.caption("Based on your interests: " + ", ".join(_norm_pref))
elif active in _DATASET_CATS:
    render_section(f"Recommended {active}", _SVG_STAR_SEC, pool[:8], "rec")
elif active == "Trending":
    render_section("Trending Products", _SVG_FIRE_SEC, pool[:8], "rec")
elif active == "Top Rated":
    render_section("Highest Rated Products", _SVG_AWARD_SEC, pool[:8], "rec")
elif active == "New Arrivals":
    render_section("New Arrivals", _SVG_STAR_SEC, pool[:8], "rec")
else:
    render_section("Products", _SVG_STAR_SEC, pool[:8], "rec")

# SECTION 2: Top Rated from pool
top_rated_pool = sorted(pool, key=lambda x: x.get("rating", 0), reverse=True)
if active == "All":
    _s2_title = "Top Rated Products"
elif active in _DATASET_CATS:
    _s2_title = f"Top Rated {active}"
else:
    _s2_title = "Top Rated — All Categories"
render_section(_s2_title, _SVG_AWARD_SEC, top_rated_pool[:4], "toprated")

# SECTION 3: Trending from pool
trending_pool = sorted(pool, key=lambda x: x.get("review_count", 0), reverse=True)
if active == "All":
    _s3_title = "Trending Now"
elif active in _DATASET_CATS:
    _s3_title = f"Trending {active}"
else:
    _s3_title = "Trending Now"
render_section(_s3_title, _SVG_FIRE_SEC, trending_pool[:4], "trend")

# SECTION 4+: Category-specific breakdown
_section_icons = [_SVG_HOME_SEC, _SVG_STAR_SEC, _SVG_FIRE_SEC, _SVG_AWARD_SEC]

if active == "All":
    # Per-user-preference category sections
    _raw_pref2 = (
        st.session_state.get("pref_cats")
        or st.session_state.get("preferred_categories")
        or []
    )
    _user_section_cats = _DATASET_CATS  # Always show all 4 categories
    for _ci, _cat in enumerate(_user_section_cats):
        _cat_prods = sorted(
            [pr for pr in products if pr.get("category") == _cat],
            key=lambda x: x.get("rating", 0), reverse=True
        )
        if _cat_prods:
            _icon = _section_icons[_ci % len(_section_icons)]
            render_section(f"Top in {_cat}", _icon, _cat_prods[:4], f"cat_{_ci}")

elif active in ["Trending", "Top Rated", "New Arrivals"]:
    # Per-category breakdown for special filters
    for _ci, _cat in enumerate(_DATASET_CATS):
        if active == "Trending":
            _cat_prods = sorted(
                [pr for pr in products if pr.get("category") == _cat],
                key=lambda x: x.get("review_count", 0), reverse=True
            )
            _sec_title = f"Trending {_cat}"
        elif active == "Top Rated":
            _cat_prods = sorted(
                [pr for pr in products if pr.get("category") == _cat],
                key=lambda x: x.get("rating", 0), reverse=True
            )
            _sec_title = f"Top Rated {_cat}"
        else:
            _all_cat = [pr for pr in products if pr.get("category") == _cat]
            _cat_prods = _all_cat[-4:] if _all_cat else []
            _sec_title = f"New {_cat}"
        if _cat_prods:
            _icon = _section_icons[_ci % len(_section_icons)]
            render_section(_sec_title, _icon, _cat_prods[:4], f"filter_{_ci}")

else:
    # Single category active — show best value section
    best_value = sorted(
        pool,
        key=lambda x: (x.get("rating", 0) / max(x.get("price", 1), 0.01)),
        reverse=True
    )
    render_section(f"Best Value {active}", _SVG_HOME_SEC, best_value[:4], "bestval")

# Recently viewed — always show if data exists
viewed = st.session_state.get("recently_viewed", [])
if viewed:
    viewed_prods = [pr for pr in products if pr.get("asin") in viewed]
    render_section("Recently Viewed", _SVG_EYE_SEC, viewed_prods[:4], "viewed")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;padding:24px 0 8px;
            border-top:1px solid {p['border']};margin-top:12px;">
  <p style="font-size:12px;color:{p['text_muted']};margin:0;">
    IntelliRec v2.0 &middot; Built with care by Team IntelliRec &middot; Sourcesys Technologies
  </p>
</div>""", unsafe_allow_html=True)
