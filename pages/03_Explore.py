import streamlit as st
import json
import os
import sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth.session import check_login
from utils.sidebar import render_sidebar
from utils.topbar import render_topbar
from utils.helpers import render_product_card_html, normalize_categories, maybe_show_product_dialog
from utils.notifications import add_notification
from utils.model_loader import MODELS_READY, get_products_df, get_sentiments
from database.db_operations import add_to_wishlist, remove_from_wishlist

st.set_page_config(page_title="Explore | IntelliRec", page_icon="🔍", layout="wide", initial_sidebar_state="expanded")
check_login()

# ── Theme + palette ───────────────────────────────────────────────────────────
from utils.theme import get_palette, inject_global_css
theme = st.session_state.get('theme', 'light')
p = get_palette(theme)
inject_global_css(p)

render_sidebar("explore")

# ── ANIMATION 3: Shimmer loading cards ──
st.markdown("""
<style>
@keyframes shimmerSlide {
    0%   { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}
@keyframes cardEntrance {
    from { opacity: 0; transform: translateY(30px) scale(0.97); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}
.explore-header-bar {
    height: 3px;
    background: linear-gradient(90deg,
        transparent, #6366f1, #8b5cf6, #06b6d4, transparent);
    background-size: 200% 100%;
    animation: shimmerSlide 2s linear infinite;
    border-radius: 2px;
    margin-bottom: 20px;
}
.product-card-wrapper {
    animation: cardEntrance 0.5s ease-out forwards;
}
</style>
<div class="explore-header-bar"></div>
""", unsafe_allow_html=True)

user_id = st.session_state.get('user_id') or 'guest'

@st.cache_data(show_spinner=False)
def load_sample_products():
    try:
        with open("assets/sample_products.json", "r") as f:
            return json.load(f)
    except Exception:
        return []


@st.cache_data(show_spinner=False, ttl=3600)
def load_real_catalogue() -> list:
    """Convert products_df to a list of card-compatible dicts for Explore.
    Limited to top 2000 products by review count for performance."""
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
            if cleaned.lower().startswith("from"):
                cleaned = cleaned[4:].strip()
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0

    df["price_num"] = df["price"].apply(_safe_price)

    # Limit to top 2000 products by review count for performance
    # (iterating 400K rows to build dicts is too slow)
    df = df.nlargest(2000, "rating_number")

    records = []
    for _, row in df.iterrows():
        pid  = str(row["product_id"])
        sent = sentiments.get(pid, {})
        records.append({
            "asin":             pid,
            "product_id":       pid,
            "title":            str(row.get("title") or "Unknown"),
            "price":            float(row["price_num"]),
            "rating":           float(row["average_rating"]),
            "review_count":     int(row["rating_number"]),
            "category":         str(row.get("category") or "Electronics"),
            "store":            str(row.get("store") or ""),
            "description_short": "",
            "sentiment_label":  sent.get("label", "Mixed"),
            "sentiment_score":  sent.get("score", 0.5),
            "is_trending":      float(row["rating_number"]) > 1000,
            "is_bestseller":    float(row["average_rating"]) >= 4.5,
        })
    return records


if MODELS_READY:
    products = load_real_catalogue()
    if not products:
        products = load_sample_products()
else:
    products = load_sample_products()

# ── Wishlist state ─────────────────────────────────────────────────────────────
if 'wishlist_ids' not in st.session_state:
    if user_id == 'guest':
        st.session_state['wishlist_ids'] = {
            p_['product_id'] for p_ in st.session_state.get('guest_wishlist', [])
        }
    else:
        try:
            from database.db_operations import get_wishlist
            wl = get_wishlist(user_id)
            st.session_state['wishlist_ids'] = {p_.get('product_id', '') for p_ in (wl or [])}
        except Exception:
            st.session_state['wishlist_ids'] = set()

# ── Top Bar ───────────────────────────────────────────────────────────────────
render_topbar("Explore Products", "Browse, search and filter our full catalogue")
maybe_show_product_dialog()

# ── Top Filter Panel ────────────────────────────────────────────────────────────
# Initialise defaults on first load or after reset
# FIX 5A: Use user's preferred categories as default (normalized)
_explore_default_cats = normalize_categories(
    st.session_state.get("pref_cats") or
    st.session_state.get("preferred_categories") or
    ["Electronics", "Home & Kitchen",
     "Clothing & Shoes", "Beauty & Personal Care"]
)
if 'ex_cats' not in st.session_state:
    st.session_state['ex_cats'] = _explore_default_cats
if 'ex_price' not in st.session_state:
    st.session_state['ex_price'] = (0, 500)
if 'ex_rating' not in st.session_state:
    st.session_state['ex_rating'] = 1.0
if 'ex_bestseller' not in st.session_state:
    st.session_state['ex_bestseller'] = False
if 'ex_sort' not in st.session_state:
    st.session_state['ex_sort'] = "Relevance"
if 'ex_search' not in st.session_state:
    st.session_state['ex_search'] = ""

with st.container():
    f_row1, f_row2 = st.columns([2, 1])
    with f_row1:
        search = st.text_input("Search products", placeholder="Search products…",
                               label_visibility="collapsed", key="ex_search")
    with f_row2:
        categories = st.multiselect(
            "Filter categories",
            ["Electronics", "Home & Kitchen",
             "Clothing & Shoes", "Beauty & Personal Care"],
            label_visibility="collapsed", key="ex_cats")

    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    with f_col1:
        price_range = st.slider("Price ($)", 0, 500, value=(0, 500), key="ex_price")
    with f_col2:
        min_rating = st.slider("Min Rating", 1.0, 5.0, step=0.5, key="ex_rating")
    with f_col3:
        # ── Animated pill toggle for Best Sellers ───────────────────────
        _bs_active = st.session_state.get('ex_bestseller', False)
        st.markdown("""
        <style>
        @keyframes bsPulse {
            0%,100% { box-shadow: 0 0 14px rgba(245,158,11,0.45), 0 3px 12px rgba(249,115,22,0.3); }
            50%      { box-shadow: 0 0 26px rgba(245,158,11,0.70), 0 5px 20px rgba(249,115,22,0.5); }
        }
        @keyframes bsStarSpin {
            from { transform: rotate(0deg) scale(1.1); }
            to   { transform: rotate(360deg) scale(1.1); }
        }
        .bs-pill-wrap .stButton > button {
            border-radius: 50px !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            letter-spacing: 0.3px !important;
            padding: 8px 18px !important;
            min-height: 40px !important;
            transition: all 0.28s cubic-bezier(0.4,0,0.2,1) !important;
        }
        /* INACTIVE state — subtle glass pill */
        .bs-pill-wrap .stButton > button[kind="secondary"] {
            background: {p['filter_btn_bg']} !important;
            border: 1.5px solid {p['border']} !important;
            color: {p['filter_btn_text']} !important;
            backdrop-filter: blur(14px) !important;
            box-shadow: 0 2px 8px rgba(99,102,241,0.08) !important;
        }
        .bs-pill-wrap .stButton > button[kind="secondary"]:hover {
            border-color: {p['accent']} !important;
            color: {p['accent']} !important;
            background: {p['card_bg_hover']} !important;
            box-shadow: 0 4px 16px rgba(245,158,11,0.2) !important;
        }
        /* ACTIVE state — golden glow pill */
        .bs-pill-wrap .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%) !important;
            border: 1px solid rgba(255,255,255,0.28) !important;
            color: #ffffff !important;
            animation: bsPulse 2.2s ease-in-out infinite !important;
            animation-name: bsPulse !important;
            box-shadow: 0 0 14px rgba(245,158,11,0.45), 0 3px 12px rgba(249,115,22,0.3) !important;
        }
        .bs-pill-wrap .stButton > button[kind="primary"] p,
        .bs-pill-wrap .stButton > button[kind="primary"] span {
            color: #ffffff !important;
            animation: none !important;
        }
        .bs-pill-wrap .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #d97706 0%, #ea580c 100%) !important;
            box-shadow: 0 0 30px rgba(245,158,11,0.7), 0 6px 20px rgba(249,115,22,0.5) !important;
        }
        </style>
        """, unsafe_allow_html=True)
        st.markdown('<div class="bs-pill-wrap">', unsafe_allow_html=True)
        _bs_label = "⭐ Best Sellers ✓" if _bs_active else "☆ Best Sellers Only"
        if st.button(_bs_label, key="ex_bestseller_btn",
                     type="primary" if _bs_active else "secondary",
                     use_container_width=True):
            st.session_state['ex_bestseller'] = not _bs_active
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        bestseller = _bs_active
    with f_col4:
        sort_by = st.selectbox("Sort by", [
            "Relevance", "Price: Low to High", "Price: High to Low", "Highest Rated"
        ], key="ex_sort", label_visibility="collapsed")

def reset_filters():
    """Reset all filters to their default values."""
    st.session_state['ex_search'] = ""
    st.session_state['ex_cats'] = normalize_categories(
        st.session_state.get("pref_cats") or
        st.session_state.get("preferred_categories") or
        ["Electronics", "Home & Kitchen",
         "Clothing & Shoes", "Beauty & Personal Care"]
    )
    st.session_state['ex_price'] = (0, 500)
    st.session_state['ex_rating'] = 1.0
    st.session_state['ex_bestseller'] = False
    st.session_state['ex_sort'] = "Relevance"
    st.session_state['ex_page'] = 1

st.button("Reset Filters", type="secondary", key="ex_reset", on_click=reset_filters)

# Apply filters
filtered = products.copy()
if search:
    q = search.lower()
    filtered = [prod for prod in filtered
                if q in prod['title'].lower()
                or q in prod.get('category', '').lower()
                or q in prod.get('description_short', '').lower()]
if categories:
    filtered = [prod for prod in filtered if prod.get('category') in categories]
filtered = [prod for prod in filtered
            if price_range[0] <= prod.get('price', 0) <= price_range[1]
            and prod.get('rating', 0) >= min_rating]
if bestseller:
    filtered = [prod for prod in filtered if prod.get('is_bestseller')]

if sort_by == "Price: Low to High":
    filtered.sort(key=lambda x: x.get('price', 0))
elif sort_by == "Price: High to Low":
    filtered.sort(key=lambda x: x.get('price', 0), reverse=True)
elif sort_by == "Highest Rated":
    filtered.sort(key=lambda x: x.get('rating', 0), reverse=True)

# Pagination
PAGE_SIZE = 20
if 'ex_page' not in st.session_state:
    st.session_state['ex_page'] = 1
page = st.session_state['ex_page']
page_prods = filtered[: page * PAGE_SIZE]

st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
  <p style="font-size:13px;color:{p['text_secondary']};margin:0">
    Showing <strong style="color:{p['text_primary']}">{len(page_prods)}</strong>
    of <strong style="color:{p['text_primary']}">{len(filtered)}</strong> products
  </p>
</div>""", unsafe_allow_html=True)

if not filtered:
    st.markdown(f"""
<div style="background-color:{p['card_bg']};
            border:1px solid {p['border']};border-radius:20px;
            padding:40px;text-align:center;box-shadow:{p['shadow']};">
  <p style="font-size:16px;font-weight:600;color:{p['text_primary']};margin-bottom:6px">No products found</p>
  <p style="font-size:14px;color:{p['text_secondary']}">Try broadening your search or adjusting filters.</p>
</div>""", unsafe_allow_html=True)
else:
    cols = st.columns(4)

    for i, prod in enumerate(page_prods):
        in_wish = prod['asin'] in st.session_state.get('wishlist_ids', set())
        save_label = "✓ Saved" if in_wish else "+ Save"
        with cols[i % 4]:
            st.markdown(render_product_card_html(prod, i, show_match=False),
                        unsafe_allow_html=True)
            bc1, bc2, bc3 = st.columns(3)
            with bc1:
                if st.button(save_label, key=f"ex_save_{prod['asin']}_{i}", type="secondary", use_container_width=True):
                    if not isinstance(st.session_state.get('wishlist_ids'), set):
                        st.session_state['wishlist_ids'] = set()
                    try:
                        if in_wish:
                            remove_from_wishlist(user_id, prod['asin'])
                            st.session_state['wishlist_ids'].discard(prod['asin'])
                            st.toast("Removed from wishlist", icon="✅")
                        else:
                            success = add_to_wishlist(user_id, prod['asin'],
                                            prod.get('title', ''),
                                            prod.get('price', 0),
                                            prod.get('category', ''))
                            if success:
                                st.session_state['wishlist_ids'].add(prod['asin'])
                                st.toast("✅ Product saved to wishlist!", icon="💾")
                            else:
                                st.toast("Could not save. Try again.", icon="❌")
                        st.rerun()
                    except Exception as _save_err:
                        st.toast(f"Error: {_save_err}", icon="❌")
            with bc2:
                if st.button("Details", key=f"ex_det_{prod['asin']}_{i}", type="secondary", use_container_width=True):
                    st.session_state["view_product"] = prod
                    st.rerun()
            with bc3:
                if st.button("Similar", key=f"ex_sim_{prod['asin']}_{i}", type="secondary", use_container_width=True):
                    st.session_state['similar_product'] = prod['asin']
                    st.session_state["similar_seed_category"] = prod.get("category", prod.get("main_category", ""))
                    st.switch_page("pages/02_For_You.py")

    # Load more
    if len(page_prods) < len(filtered):
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        _remaining = len(filtered) - len(page_prods)
        _lbl = f"Load more ({_remaining} remaining)"
        if st.button(_lbl, key="ex_loadmore"):
            st.session_state['ex_page'] = page + 1
            st.rerun()
