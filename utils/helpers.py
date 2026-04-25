"""
IntelliRec Helpers — Product card rendering, SVG icons, category/sentiment data.
SVG strings are kept as single-line (no newlines) to prevent Python-Markdown from
treating indented lines inside the HTML as code blocks.
"""
import streamlit as st

# ── Category Name Normalisation ───────────────────────────────────────────────
# Maps onboarding / UI names → exact dataset category names.
# The dataset contains EXACTLY 4 categories:
#   Electronics, Home & Kitchen, Clothing & Shoes, Beauty & Personal Care
CATEGORY_NAME_MAP = {
    # Direct matches (identity — keeps normalize idempotent)
    "Electronics":              "Electronics",
    "Home & Kitchen":           "Home & Kitchen",
    "Clothing & Shoes":         "Clothing & Shoes",
    "Beauty & Personal Care":   "Beauty & Personal Care",
    # Onboarding UI short names
    "Beauty":                   "Beauty & Personal Care",
    "Fashion":                  "Clothing & Shoes",
    "Clothing":                 "Clothing & Shoes",
    # Best-effort mappings for categories not in dataset
    "Gaming":                   "Electronics",
    "Sports":                   "Electronics",
    "Books":                    "Electronics",
    "Automotive":               "Electronics",
    "Toys & Games":             "Electronics",
    "Health":                   "Beauty & Personal Care",
    "Office":                   "Electronics",
    "Pet Supplies":             "Home & Kitchen",
    # Alternative pkl-name variants (defensive — covers any training-time variation)
    "Beauty_and_Personal_Care":      "Beauty & Personal Care",
    "Beauty and Personal Care":      "Beauty & Personal Care",
    "Clothing_Shoes_and_Jewelry":    "Clothing & Shoes",
    "Clothing, Shoes & Jewelry":     "Clothing & Shoes",
    "Clothing Shoes and Jewelry":    "Clothing & Shoes",
    "Home_and_Kitchen":              "Home & Kitchen",
    "Home and Kitchen":              "Home & Kitchen",
}


def normalize_categories(cats):
    """
    Map onboarding / UI category names to exact dataset category names.
    Deduplicates and preserves order.  Safe to call on already-normalised lists.
    """
    if not cats:
        return []
    seen = set()
    normalized = []
    for cat in cats:
        mapped = CATEGORY_NAME_MAP.get(cat, cat)
        if mapped not in seen:
            seen.add(mapped)
            normalized.append(mapped)
    return normalized


# ── Category SVG Icons — single-line (critical: no newlines!) ─────────────────
_SVG_ELECTRONICS = '<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" fill="none" viewBox="0 0 24 24" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>'

_SVG_HOME_CAT = '<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" fill="none" viewBox="0 0 24 24" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>'

_SVG_BOOK_CAT = '<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" fill="none" viewBox="0 0 24 24" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>'

_SVG_SPORTS_CAT = '<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" fill="none" viewBox="0 0 24 24" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M4.93 4.93l4.24 4.24"/><path d="M14.83 9.17l4.24-4.24"/><path d="M14.83 14.83l4.24 4.24"/><path d="M9.17 14.83l-4.24 4.24"/></svg>'

_SVG_FASHION_CAT = '<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" fill="none" viewBox="0 0 24 24" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20.38 3.46L16 2a4 4 0 0 1-8 0L3.62 3.46a2 2 0 0 0-1.34 2.23l.58 3.57a1 1 0 0 0 .99.84H6v10c0 1.1.9 2 2 2h8a2 2 0 0 0 2-2V10h2.15a1 1 0 0 0 .99-.84l.58-3.57a2 2 0 0 0-1.34-2.23z"/></svg>'

_SVG_BOX_CAT = '<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" fill="none" viewBox="0 0 24 24" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>'

_SVG_BEAUTY_CAT = '<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" fill="none" viewBox="0 0 24 24" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>'

_SVG_TOYS_CAT = '<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" fill="none" viewBox="0 0 24 24" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>'


CATEGORY_MAP = {
    "Electronics":    {
        "svg": _SVG_ELECTRONICS,
        "color1": "#667eea", "color2": "#764ba2",
        "badge_bg": "#6C63FF", "badge_text": "white"
    },
    "Home & Kitchen": {
        "svg": _SVG_HOME_CAT,
        "color1": "#11998e", "color2": "#38ef7d",
        "badge_bg": "#10B981", "badge_text": "white"
    },
    "Books":          {
        "svg": _SVG_BOOK_CAT,
        "color1": "#4facfe", "color2": "#00f2fe",
        "badge_bg": "#0EA5E9", "badge_text": "white"
    },
    "Sports":         {
        "svg": _SVG_SPORTS_CAT,
        "color1": "#43e97b", "color2": "#38f9d7",
        "badge_bg": "#10B981", "badge_text": "white"
    },
    "Clothing":       {
        "svg": _SVG_FASHION_CAT,
        "color1": "#fa709a", "color2": "#fee140",
        "badge_bg": "#F59E0B", "badge_text": "white"
    },
    "Toys":           {
        "svg": _SVG_TOYS_CAT,
        "color1": "#f77062", "color2": "#fe5196",
        "badge_bg": "#EF4444", "badge_text": "white"
    },
    "Beauty":         {
        "svg": _SVG_BEAUTY_CAT,
        "color1": "#ff9a9e", "color2": "#fecfef",
        "badge_bg": "#DB2777", "badge_text": "white"
    },
    "default":        {
        "svg": _SVG_BOX_CAT,
        "color1": "#a18cd1", "color2": "#fbc2eb",
        "badge_bg": "#8B5CF6", "badge_text": "white"
    },
    # Full dataset-name aliases so get_category_info() returns correct styling
    "Beauty & Personal Care": {
        "svg": _SVG_BEAUTY_CAT,
        "color1": "#ff9a9e", "color2": "#fecfef",
        "badge_bg": "#DB2777", "badge_text": "white"
    },
    "Clothing & Shoes": {
        "svg": _SVG_FASHION_CAT,
        "color1": "#fa709a", "color2": "#fee140",
        "badge_bg": "#F59E0B", "badge_text": "white"
    },
}

_SENTIMENT_LIGHT = {
    "Positive": {"bg": "#DCFCE7", "color": "#16A34A"},
    "Mixed":    {"bg": "#FEF9C3", "color": "#CA8A04"},
    "Critical": {"bg": "#FEE2E2", "color": "#DC2626"},
    "Negative": {"bg": "#FEE2E2", "color": "#DC2626"},
}

_SENTIMENT_DARK = {
    "Positive": {"bg": "#064e3b", "color": "#6ee7b7"},
    "Mixed":    {"bg": "#78350f", "color": "#fcd34d"},
    "Critical": {"bg": "#7f1d1d", "color": "#fca5a5"},
    "Negative": {"bg": "#7f1d1d", "color": "#fca5a5"},
}

EXPLANATIONS = [
    "Because users like you loved this product",
    "Trending in your favourite category",
    "Matches your interest in high-quality items",
    "Based on your top-rated purchases",
    "Highly rated by similar shoppers",
    "Popular pick in your price range",
    "Pairs well with your wishlist items",
    "Frequently bought with items you liked",
]


def get_category_info(category: str) -> dict:
    return CATEGORY_MAP.get(category, CATEGORY_MAP["default"])


def get_sentiment_style(label: str) -> dict:
    theme = st.session_state.get("theme", "light")
    styles = _SENTIMENT_DARK if theme == "dark" else _SENTIMENT_LIGHT
    fallback = {"bg": "#1e1e35", "color": "#6b7280"} if theme == "dark" else {"bg": "#F3F4F6", "color": "#6B7280"}
    return styles.get(label, fallback)


def get_match_score(prod: dict, idx: int = 0) -> int:
    base = int(prod.get('rating', 3.5) * 17)
    jitter = abs(hash(prod.get('asin', str(idx)))) % 9
    return min(98, max(62, base + jitter - idx))


def get_product_price(product: dict) -> str:
    """
    Safely extract and format a product price, trying multiple field names
    that Amazon metadata uses. Returns 'Price not listed' instead of '$0.00'
    when no valid price is found.
    """
    for field in ['price', 'Price', 'list_price', 'sale_price', 'buybox_price']:
        val = product.get(field)
        if val and val not in [0, '0', 0.0, '', None]:
            try:
                price_float = float(
                    str(val).replace('$', '').replace(',', '').strip()
                )
                if price_float > 0:
                    return f"${price_float:,.2f}"
            except (ValueError, TypeError):
                pass

    # Check nested details dict (some Amazon export formats)
    details = product.get('details', {})
    if isinstance(details, dict):
        for field in ['price', 'Price', 'list_price']:
            val = details.get(field)
            if val:
                try:
                    price_float = float(
                        str(val).replace('$', '').replace(',', '').strip()
                    )
                    if price_float > 0:
                        return f"${price_float:,.2f}"
                except (ValueError, TypeError):
                    return str(val)  # Return raw string if it can't be parsed

    return "Price not listed"


def get_stars(rating: float) -> str:
    full = int(rating)
    empty = 5 - full
    return "★" * full + "☆" * empty


def render_product_card_html(prod: dict, idx: int = 0, show_match: bool = True) -> str:
    """
    Returns a single-line HTML string for a glassmorphism product card.
    IMPORTANT: The output must be a flat string with NO newlines to prevent
    Streamlit's Python-Markdown from misinterpreting indented HTML as code blocks.
    """
    from utils.theme import get_palette
    _theme = st.session_state.get('theme', 'light')
    _p = get_palette(_theme)
    card_bg   = _p['card_bg']
    text_col  = _p['text_primary']
    sub_col   = _p['text_secondary']
    muted_col = _p['text_muted']
    price_col = _p['price_color']
    border_col = _p['border']

    cat              = get_category_info(prod.get('category', ''))
    sent             = get_sentiment_style(prod.get('sentiment_label', ''))
    score            = get_match_score(prod, idx)
    title            = prod.get('title', 'Product')
    price_display    = get_product_price(prod)   # safe multi-field lookup
    rating           = int(prod.get('rating', 0))
    reviews          = int(prod.get('review_count', 0))
    category         = prod.get('category', '')
    sentiment_label  = prod.get('sentiment_label', '')

    stars    = '★' * rating + '☆' * (5 - rating)
    svg      = cat["svg"]  # already single-line

    match_html = ""
    if show_match:
        match_html = (
            f'<div style="margin:8px 0 4px">'
            f'<div style="background:rgba(108,99,255,0.12);border-radius:4px;height:4px">'
            f'<div style="background:linear-gradient(90deg,#6C63FF,#06B6D4);height:4px;border-radius:4px;width:{score}%"></div>'
            f'</div>'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-top:4px">'
            f'<span style="font-size:11px;color:var(--text-tertiary,#9090A8);font-weight:500">{score}% match</span>'
            f'<span style="font-size:10px;font-weight:600;padding:2px 8px;border-radius:20px;background:{sent["bg"]};color:{sent["color"]}">{sentiment_label}</span>'
            f'</div></div>'
        )

    # One continuous string — no newlines!
    return (
        f'<div style="background:{card_bg};backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid {border_col};border-radius:20px;box-shadow:0 4px 20px rgba(108,99,255,0.12);overflow:hidden;margin-bottom:4px">'
        f'<div style="background:linear-gradient(135deg,{cat["color1"]},{cat["color2"]});height:140px;display:flex;align-items:center;justify-content:center;position:relative;flex-direction:column">'
        f'{svg}'
        f'<span style="position:absolute;top:8px;left:8px;background:{cat["badge_bg"]};color:{cat["badge_text"]};font-size:10px;font-weight:600;padding:3px 9px;border-radius:100px">{category}</span>'
        '</div>'
        f'<div style="padding:14px 16px 12px;background-color:{card_bg};border-radius:0 0 20px 20px">'
        f'<div style="font-size:14px;font-weight:700;color:{text_col};line-height:1.4;height:2.8em;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;margin-bottom:6px">{title}</div>'
        f'<div style="font-size:18px;font-weight:700;color:{price_col};margin-bottom:4px">{price_display}</div>'
        f'<div style="font-size:12px;color:#F59E0B;margin-bottom:2px">{stars}<span style="color:{muted_col};font-weight:400;font-size:11px"> ({reviews:,})</span></div>'
        f'{match_html}'
        '</div>'
        '</div>'
    )


# Apply @st.dialog lazily so helpers.py can be safely imported by non-page
# modules (e.g. chatbot_engine.py → model_loader.py → helpers.py).
# If st.dialog is not available in the current context, fall back to a no-op
# so the import chain never crashes at module load time.
try:
    _dialog_decorator = st.dialog("Product Details", width="large")
except Exception:
    # Fallback: identity decorator (dialog won't open, but nothing crashes)
    def _dialog_decorator(fn):
        return fn

@_dialog_decorator
def _show_product_detail_dialog(product: dict):
    """Modal product detail view — Flipkart-style."""
    from utils.theme import get_palette
    _theme = st.session_state.get('theme', 'light')
    _p = get_palette(_theme)

    cat   = get_category_info(product.get('category', ''))
    sent  = get_sentiment_style(product.get('sentiment_label', ''))
    score = get_match_score(product)

    title    = product.get('title', 'Product')
    price    = get_product_price(product)
    rating   = float(product.get('rating', 0))
    reviews  = int(product.get('review_count', 0))
    category = product.get('category', '')
    sentiment_label = product.get('sentiment_label', '')
    description = product.get('description', product.get('features', ''))
    asin     = product.get('asin', product.get('product_id', ''))

    stars_full = get_stars(rating)

    # Header gradient banner
    st.markdown(
        f'<div style="background:linear-gradient(135deg,{cat["color1"]},{cat["color2"]});'
        f'border-radius:16px;padding:28px;display:flex;align-items:center;'
        f'justify-content:center;margin-bottom:20px;">'
        f'{cat["svg"]}</div>',
        unsafe_allow_html=True
    )

    # Title + price row
    st.markdown(
        f'<h2 style="font-size:18px;font-weight:700;color:{_p["text_primary"]};'
        f'margin:0 0 8px;line-height:1.4;">{title}</h2>',
        unsafe_allow_html=True
    )

    meta_c1, meta_c2, meta_c3 = st.columns([1.2, 1, 1])
    with meta_c1:
        st.markdown(
            f'<div style="font-size:22px;font-weight:800;color:{_p["price_color"]};">{price}</div>',
            unsafe_allow_html=True
        )
    with meta_c2:
        st.markdown(
            f'<div style="font-size:14px;color:#F59E0B;font-weight:600;">{stars_full}'
            f'<span style="font-size:12px;color:{_p["text_muted"]};font-weight:400;"> {rating:.1f} ({reviews:,})</span></div>',
            unsafe_allow_html=True
        )
    with meta_c3:
        badge_row = ''
        if category:
            badge_row += (
                f'<span style="background:{cat["badge_bg"]};color:{cat["badge_text"]};'
                f'font-size:11px;font-weight:600;padding:3px 10px;border-radius:100px;'
                f'margin-right:6px;">{category}</span>'
            )
        if sentiment_label:
            badge_row += (
                f'<span style="background:{sent["bg"]};color:{sent["color"]};'
                f'font-size:11px;font-weight:600;padding:3px 10px;border-radius:100px;">{sentiment_label}</span>'
            )
        st.markdown(f'<div style="padding-top:4px;">{badge_row}</div>', unsafe_allow_html=True)

    # Match score bar
    st.markdown(
        f'<div style="margin:12px 0;">'
        f'<div style="display:flex;justify-content:space-between;margin-bottom:4px;">'
        f'<span style="font-size:12px;color:{_p["text_secondary"]};font-weight:500;">AI Match Score</span>'
        f'<span style="font-size:12px;font-weight:700;color:#6366f1;">{score}%</span></div>'
        f'<div style="background:{_p["border"]};border-radius:4px;height:6px;">'
        f'<div style="background:linear-gradient(90deg,#6366f1,#8b5cf6);height:6px;'
        f'border-radius:4px;width:{score}%;"></div></div></div>',
        unsafe_allow_html=True
    )

    # Description / features
    if description:
        st.markdown(
            f'<p style="font-size:14px;color:{_p["text_secondary"]};'
            f'line-height:1.6;margin:8px 0 16px;">'
            f'{str(description)[:300]}{"..." if len(str(description)) > 300 else ""}</p>',
            unsafe_allow_html=True
        )

    st.markdown(f'<hr style="border:none;border-top:1px solid {_p["border"]};margin:12px 0;">', unsafe_allow_html=True)

    # Action buttons
    btn_c1, btn_c2, btn_c3 = st.columns(3)
    with btn_c1:
        _in_wl = asin in (st.session_state.get("wishlist_ids") or set())
        if st.button("♡ Wishlist" if not _in_wl else "♥ Saved", key="dlg_wl_btn",
                     type="primary" if not _in_wl else "secondary", use_container_width=True):
            if not _in_wl:
                try:
                    from database.db_operations import add_to_wishlist
                    add_to_wishlist(st.session_state.get("user_id"), asin, title, category)
                    _wl = st.session_state.get("wishlist_ids") or set()
                    _wl.add(asin)
                    st.session_state["wishlist_ids"] = _wl
                    st.toast("Added to wishlist!", icon="♥")
                except Exception:
                    pass
            st.rerun()
    with btn_c2:
        if st.button("Find Similar", key="dlg_sim_btn", type="secondary", use_container_width=True):
            st.session_state["similar_product"] = {"asin": asin, "title": title, "category": category}
            st.session_state.pop("view_product", None)
            st.switch_page("pages/02_For_You.py")
    with btn_c3:
        if st.button("Close", key="dlg_close_btn", type="secondary", use_container_width=True):
            st.session_state.pop("view_product", None)
            st.rerun()


def maybe_show_product_dialog():
    """Call at the top of any page to trigger the product detail modal when set."""
    prod = st.session_state.get("view_product")
    if prod:
        _show_product_detail_dialog(prod)
