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
from utils.theme import inject_global_css
inject_global_css()
render_sidebar("home")

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
            p["product_id"] for p in st.session_state.get("guest_wishlist", [])
        }
    else:
        try:
            from database.db_operations import get_wishlist
            wl = get_wishlist(user_id)
            st.session_state["wishlist_ids"] = {p.get("product_id", "") for p in (wl or [])}
        except Exception:
            st.session_state["wishlist_ids"] = set()

# ── Top Bar ───────────────────────────────────────────────────────────────────
hour = datetime.now().hour
if hour < 12: greeting = "Good morning"
elif hour < 17: greeting = "Good afternoon"
else: greeting = "Good evening"

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
# SVG icons for stats
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
    (s1, _SVG_SHOP, "1.4M+", "Products",           "#6C63FF", "#EEF2FF"),
    (s2, _SVG_AI,   "3",     "AI Engines Active",   "#06B6D4", "#ECFEFF"),
    (s3, _SVG_LIVE, "Live",  "Real-time Updates",   "#10B981", "#DCFCE7"),
]
for col, icon_svg, val, label, accent, bg in stat_data:
    with col:
        st.markdown(f"""
<div style="background:var(--stat-bg,rgba(255,255,255,0.9));backdrop-filter:blur(20px);
            -webkit-backdrop-filter:blur(20px);
            border:var(--stat-border,1px solid rgba(108,99,255,0.12));border-radius:14px;
            padding:16px 20px;display:flex;align-items:center;gap:14px;
            margin-bottom:20px;border-left:3px solid {accent};
            box-shadow:0 2px 8px rgba(108,99,255,0.08);
            transition:box-shadow 0.2s ease,transform 0.2s ease;">
  <div style="width:42px;height:42px;border-radius:10px;background:{bg};
              display:flex;align-items:center;justify-content:center;
              color:{accent};flex-shrink:0;">
    {icon_svg}
  </div>
  <div>
    <div style="font-size:20px;font-weight:700;color:var(--stat-num,#111827);line-height:1;">{val}</div>
    <div style="font-size:12px;color:var(--stat-lbl,#9CA3AF);margin-top:3px;font-weight:500;">{label}</div>
  </div>
</div>""", unsafe_allow_html=True)

# ── Category filter pills ─────────────────────────────────────────────────────
FILTERS = ["All", "Electronics", "Home & Kitchen", "Trending", "Top Rated", "New Arrivals"]
if "home_active_filter" not in st.session_state:
    st.session_state["home_active_filter"] = "All"

# Inject pill button CSS override
st.markdown("""
<style>
div[data-testid="column"] .ir-pill-wrapper div.stButton > button {
    border-radius: 100px !important;
    padding: 6px 14px !important;
    font-size: 12.5px !important;
    font-weight: 500 !important;
    border: var(--pill-border) !important;
    background: var(--pill-bg) !important;
    color: var(--pill-color) !important;
    box-shadow: none !important;
    min-height: unset !important;
    line-height: 1.4 !important;
    transition: all 0.15s ease !important;
}
div[data-testid="column"] .ir-pill-wrapper div.stButton > button:hover {
    border-color: #6C63FF !important;
    color: #6C63FF !important;
    background: rgba(108,99,255,0.1) !important;
    transform: none !important;
    box-shadow: none !important;
}
div[data-testid="column"] .ir-pill-active div.stButton > button {
    background: var(--pill-active-bg) !important;
    color: var(--pill-active-color) !important;
    border: var(--pill-active-border) !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(108,99,255,0.25) !important;
}
div[data-testid="column"] .ir-pill-active div.stButton > button:hover {
    background: #4F46E5 !important;
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

pill_cols = st.columns(len(FILTERS))
for i, f in enumerate(FILTERS):
    with pill_cols[i]:
        is_active = st.session_state["home_active_filter"] == f
        wrapper_class = "ir-pill-active" if is_active else "ir-pill-wrapper"
        st.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)
        if st.button(f, key=f"pill_{f}", use_container_width=True):
            st.session_state["home_active_filter"] = f
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

# ── Filter products ───────────────────────────────────────────────────────────
active   = st.session_state["home_active_filter"]
filtered = products.copy()

if search:
    q = search.lower()
    filtered = [p for p in filtered
                if q in p["title"].lower()
                or q in p.get("category", "").lower()
                or q in p.get("description_short", "").lower()]
    st.markdown(
        f'<p style="font-size:13px;color:#9CA3AF;margin-bottom:12px;">'
        f'Showing {len(filtered)} result(s) for <strong>"{search}"</strong></p>',
        unsafe_allow_html=True
    )

if active == "Electronics":
    filtered = [p for p in filtered if p.get("category") == "Electronics"]
elif active == "Home & Kitchen":
    filtered = [p for p in filtered if p.get("category") == "Home & Kitchen"]
elif active == "Trending":
    filtered = [p for p in filtered if p.get("is_trending")]
elif active == "Top Rated":
    filtered = sorted(filtered, key=lambda x: x.get("rating", 0), reverse=True)
elif active == "New Arrivals":
    filtered = filtered[-12:]


# ── Section icons ─────────────────────────────────────────────────────────────
_SVG_STAR_SEC = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#6C63FF"
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

_SVG_SEARCH_SEC = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none"
  viewBox="0 0 24 24" stroke="#6C63FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="11" cy="11" r="8"/>
  <line x1="21" y1="21" x2="16.65" y2="16.65"/>
</svg>"""

_SVG_EYE_SEC = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none"
  viewBox="0 0 24 24" stroke="#6B7280" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
  <h2 class="section-title" style="margin:0;">{title}</h2>
  <div style="flex:1;height:1px;background:rgba(108,99,255,0.12);margin-left:4px;"></div>
  <span style="font-size:12px;color:#9CA3AF;font-weight:500;">{len(prods[:4])} items</span>
</div>""", unsafe_allow_html=True)

    cols = st.columns(4)
    for i, prod in enumerate(prods[:4]):
        with cols[i]:
            st.markdown(render_product_card_html(prod, i), unsafe_allow_html=True)
            in_wish = prod["asin"] in st.session_state.get("wishlist_ids", set())
            save_label = "Saved" if in_wish else "+ Save"
            bc1, bc2 = st.columns([1, 1])
            with bc1:
                if st.button(save_label,
                             key=f"{section_key}_wish_{prod['asin']}",
                             use_container_width=True, type="secondary"):
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
                if st.button("Similar",
                             key=f"{section_key}_sim_{prod['asin']}",
                             use_container_width=True, type="secondary"):
                    st.session_state["similar_product"] = prod["asin"]
                    st.switch_page("pages/02_For_You.py")

    st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)


# ── Sections ──────────────────────────────────────────────────────────────────
if search or active != "All":
    render_section(f"Results ({len(filtered)})", _SVG_SEARCH_SEC, filtered, "search")
else:
    render_section("Recommended For You", _SVG_STAR_SEC, filtered[:4], "rec")

    trending   = [p for p in products if p.get("is_trending")]
    render_section("Trending Now", _SVG_FIRE_SEC, trending[:4], "trend")

    electronics = sorted(
        [p for p in products if p.get("category") == "Electronics"],
        key=lambda x: x.get("rating", 0), reverse=True
    )
    render_section("Top Rated Electronics", _SVG_AWARD_SEC, electronics[:4], "elec")

    kitchen = [p for p in products if p.get("category") == "Home & Kitchen"]
    render_section("Best in Home & Kitchen", _SVG_HOME_SEC, kitchen[:4], "kit")

    viewed = st.session_state.get("recently_viewed", [])
    if viewed:
        viewed_prods = [p for p in products if p["asin"] in viewed]
        render_section("Recently Viewed", _SVG_EYE_SEC, viewed_prods[:4], "viewed")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:24px 0 8px;
            border-top:1px solid rgba(108,99,255,0.12);margin-top:12px;">
  <p style="font-size:12px;color:#D1D5DB;margin:0;">
    IntelliRec v2.0 &middot; Built with care by Team IntelliRec &middot; Sourcesys Technologies
  </p>
</div>""", unsafe_allow_html=True)
