import streamlit as st
import json
from datetime import datetime
from auth.session import check_login
from utils.sidebar import render_sidebar
from utils.topbar import render_topbar
from utils.helpers import render_product_card_html
from utils.notifications import add_notification
from database.db_operations import add_to_wishlist, remove_from_wishlist

st.set_page_config(page_title="Home | IntelliRec", page_icon="💡", layout="wide")
check_login()

# ── Theme + palette ───────────────────────────────────────────────────────────
from utils.theme import get_palette, inject_global_css
theme = st.session_state.get('theme', 'dark')
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
def load_products():
    with open("assets/sample_products.json", "r") as f:
        return json.load(f)

products = load_products()

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
FILTERS = ["All", "Electronics", "Home & Kitchen", "Trending", "Top Rated", "New Arrivals"]
if "home_active_filter" not in st.session_state:
    st.session_state["home_active_filter"] = "All"


def render_filter_pills(categories, active, palette):
    """Render category filter pills as HTML spans (bypasses Streamlit button styling issues)."""
    html = '<div style="display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 16px;">'
    for cat in categories:
        is_active = (cat == active)
        bg = palette['accent'] if is_active else palette['filter_btn_bg']
        color = '#ffffff' if is_active else palette['filter_btn_text']
        border = palette['accent'] if is_active else palette['border']
        fw = '700' if is_active else '500'
        html += (
            f'<span style="background-color:{bg};color:{color};border:1.5px solid {border};'
            f'border-radius:20px;padding:7px 18px;font-size:13px;font-weight:{fw};'
            f'display:inline-block;white-space:nowrap;">{cat}</span>'
        )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# ── Category filter pills (HTML-rendered for reliable cross-theme styling) ──
render_filter_pills(FILTERS, st.session_state["home_active_filter"], p)

# Allow changing filter via a compact selectbox below pills
_sel = st.selectbox(
    "Change category",
    FILTERS,
    index=FILTERS.index(st.session_state["home_active_filter"]),
    label_visibility="collapsed",
    key="home_filter_select"
)
if _sel != st.session_state["home_active_filter"]:
    st.session_state["home_active_filter"] = _sel
    st.rerun()

# ── Filter products ───────────────────────────────────────────────────────────
active   = st.session_state["home_active_filter"]
filtered = products.copy()

if search:
    q = search.lower()
    filtered = [prod for prod in filtered
                if q in prod["title"].lower()
                or q in prod.get("category", "").lower()
                or q in prod.get("description_short", "").lower()]
    st.markdown(
        f'<p style="font-size:13px;color:{p["text_secondary"]};margin-bottom:12px;">'
        f'Showing {len(filtered)} result(s) for <strong>"{search}"</strong></p>',
        unsafe_allow_html=True
    )

if active == "Electronics":
    filtered = [prod for prod in filtered if prod.get("category") == "Electronics"]
elif active == "Home & Kitchen":
    filtered = [prod for prod in filtered if prod.get("category") == "Home & Kitchen"]
elif active == "Trending":
    filtered = [prod for prod in filtered if prod.get("is_trending")]
elif active == "Top Rated":
    filtered = sorted(filtered, key=lambda x: x.get("rating", 0), reverse=True)
elif active == "New Arrivals":
    filtered = filtered[-12:]


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
            save_bg  = p['accent_soft'] if in_wish else p['accent']
            save_txt = p['accent'] if in_wish else '#ffffff'
            sim_bg   = p['secondary_btn_bg']
            sim_txt  = p['secondary_btn_text']
            bdr      = p['border']

            bc1, bc2 = st.columns([1, 1])
            with bc1:
                if st.button(save_label, key=f"{section_key}_save_{prod['asin']}", type="secondary"):
                    try:
                        if in_wish:
                            remove_from_wishlist(user_id, prod["asin"])
                            st.session_state["wishlist_ids"].discard(prod["asin"])
                            st.toast("Removed from wishlist", icon="✓")
                        else:
                            add_to_wishlist(user_id, prod["asin"],
                                            prod.get("title", ""),
                                            prod.get("price", 0),
                                            prod.get("category", ""))
                            st.session_state["wishlist_ids"].add(prod["asin"])
                            add_notification("success", "Saved to Wishlist",
                                             f"{prod.get('title','')[:35]} added to your wishlist")
                            st.toast("Product saved to wishlist!", icon="✓")
                        st.rerun()
                    except Exception:
                        st.toast("Something went wrong. Try again.")
            with bc2:
                if st.button("Similar", key=f"{section_key}_sim_{prod['asin']}", type="secondary"):
                    st.session_state["similar_product"] = prod["asin"]
                    st.switch_page("pages/02_For_You.py")

    st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)


# ── Sections ──────────────────────────────────────────────────────────────────
if search or active != "All":
    render_section(f"Results ({len(filtered)})", _SVG_SEARCH_SEC, filtered, "search")
else:
    render_section("Recommended For You", _SVG_STAR_SEC, filtered[:4], "rec")

    trending   = [prod for prod in products if prod.get("is_trending")]
    render_section("Trending Now", _SVG_FIRE_SEC, trending[:4], "trend")

    electronics = sorted(
        [prod for prod in products if prod.get("category") == "Electronics"],
        key=lambda x: x.get("rating", 0), reverse=True
    )
    render_section("Top Rated Electronics", _SVG_AWARD_SEC, electronics[:4], "elec")

    kitchen = [prod for prod in products if prod.get("category") == "Home & Kitchen"]
    render_section("Best in Home & Kitchen", _SVG_HOME_SEC, kitchen[:4], "kit")

    viewed = st.session_state.get("recently_viewed", [])
    if viewed:
        viewed_prods = [prod for prod in products if prod["asin"] in viewed]
        render_section("Recently Viewed", _SVG_EYE_SEC, viewed_prods[:4], "viewed")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;padding:24px 0 8px;
            border-top:1px solid {p['border']};margin-top:12px;">
  <p style="font-size:12px;color:{p['text_muted']};margin:0;">
    IntelliRec v2.0 &middot; Built with care by Team IntelliRec &middot; Sourcesys Technologies
  </p>
</div>""", unsafe_allow_html=True)
