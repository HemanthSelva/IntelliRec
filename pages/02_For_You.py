import streamlit as st
import json
from auth.session import check_login
from utils.sidebar import render_sidebar
from utils.topbar import render_topbar
from utils.helpers import render_product_card_html, get_match_score, EXPLANATIONS
from utils.notifications import add_notification
from database.db_operations import add_to_wishlist, remove_from_wishlist, save_feedback

st.set_page_config(page_title="For You | IntelliRec", page_icon="💡", layout="wide")
check_login()

# ── Theme + palette ───────────────────────────────────────────────────────────
from utils.theme import get_palette, inject_global_css
theme = st.session_state.get('theme', 'dark')
p = get_palette(theme)
inject_global_css(p)

render_sidebar("for_you")




user_id = st.session_state.get('user_id') or 'guest'

@st.cache_data
def load_products():
    with open("assets/sample_products.json", "r") as f:
        return json.load(f)

products = load_products()

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
render_topbar("For You", "AI-powered recommendations tuned to your taste")

st.markdown(f"""
<style>
@keyframes ir-gemini-spin {{
    0%   {{ transform: rotate(0deg) scale(1); }}
    25%  {{ transform: rotate(90deg) scale(1.15); }}
    50%  {{ transform: rotate(180deg) scale(1); }}
    75%  {{ transform: rotate(270deg) scale(1.15); }}
    100% {{ transform: rotate(360deg) scale(1); }}
}}
@keyframes ir-gemini-color {{
    0%   {{ color: #6366f1; filter: drop-shadow(0 0 4px #6366f1); }}
    33%  {{ color: #06b6d4; filter: drop-shadow(0 0 4px #06b6d4); }}
    66%  {{ color: #8b5cf6; filter: drop-shadow(0 0 4px #8b5cf6); }}
    100% {{ color: #6366f1; filter: drop-shadow(0 0 4px #6366f1); }}
}}
.ir-foryou-hero {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 4px;
}}
.ir-foryou-hero h2 {{
    font-size: 26px;
    font-weight: 800;
    color: {p['text_primary']};
    margin: 0;
}}
.ir-gemini-icon {{
    font-size: 26px;
    animation: ir-gemini-spin 4s linear infinite,
               ir-gemini-color 3s ease-in-out infinite;
    display: inline-block;
    line-height: 1;
}}
</style>
<div class="ir-foryou-hero">
    <h2>AI Recommendations</h2>
    <span class="ir-gemini-icon">&#10022;</span>
</div>
<p style="color:{p['text_secondary']};font-size:14px;margin:0 0 16px;">
    Personalized picks powered by 3 AI engines
</p>
""", unsafe_allow_html=True)

# ── SECTION 1: Engine + Filters at TOP (full width, collapsible) ──────────────
with st.expander("⚙️ Recommendation Engine & Filters", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<p style="font-size:12px;font-weight:600;color:{p["text_secondary"]};text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">Engine</p>', unsafe_allow_html=True)
        engine = st.radio("Engine", ["Hybrid", "Collaborative", "Content-Based"],
                          label_visibility="collapsed", key="fy_engine")
    with col2:
        num_recs = st.slider("Results", 5, 20, 12, key="fy_num")
        diversity = st.slider("Diversity (%)", 0, 100, 30, key="fy_diversity")
    with col3:
        categories = st.multiselect("Categories", ["Electronics", "Home & Kitchen"],
                                    default=["Electronics", "Home & Kitchen"], key="fy_cats")
        min_rating = st.slider("Min Rating", 1.0, 5.0, 3.0, 0.5, key="fy_rating")
        price_range = st.slider("Price ($)", 0, 500, (0, 500), key="fy_price")

    fcol1, fcol2 = st.columns(2)
    with fcol1:
        if st.button("🔄 Refresh Recommendations", key="btn_refresh_recs", type="primary"):
            add_notification('info', 'Recommendations Updated',
                             'Fresh picks generated for you.')
            st.toast("Recommendations updated!", icon="↻")
    with fcol2:
        if st.button("Reset Filters", key="btn_reset_filters", type="secondary"):
            for k in ['fy_num', 'fy_diversity', 'fy_cats', 'fy_rating', 'fy_price', 'fy_engine']:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

st.markdown("---")

# ── Engine badge + filter stats ───────────────────────────────────────────────
st.markdown(f"""
<div style="margin-bottom:16px;display:flex;align-items:center;gap:10px" class="foryou-section">
  <span style="background-color:{p['accent_soft']};color:{p['accent']};padding:5px 14px;border-radius:100px;
               font-size:13px;font-weight:600">{engine} Active</span>
  <span style="font-size:13px;color:{p['text_secondary']}">Diversity: {diversity}%</span>
</div>""", unsafe_allow_html=True)

# ── Filter products ────────────────────────────────────────────────────────────
filtered = [
    prod for prod in products
    if prod.get('category') in categories
    and prod.get('rating', 0) >= min_rating
    and price_range[0] <= prod.get('price', 0) <= price_range[1]
]

if not filtered:
    st.markdown(f"""
<div style="background-color:{p['card_bg']};
            border:1px solid {p['border']};border-radius:20px;
            padding:40px;text-align:center;margin-top:20px">
  <p style="font-size:16px;font-weight:600;color:{p['text_primary']};margin-bottom:6px">No results found</p>
  <p style="font-size:14px;color:{p['text_secondary']}">Try adjusting the filters above.</p>
</div>""", unsafe_allow_html=True)
else:
    display = filtered[:num_recs]
    st.markdown(f"<p style='font-size:13px;color:{p['text_secondary']};margin-bottom:16px'>"
                f"Showing {len(display)} of {len(filtered)} recommendations</p>",
                unsafe_allow_html=True)

    # ── SECTION 2: Full-width 4-column grid ──────────────────────────────────
    cols = st.columns(4)
    for i, prod in enumerate(display):
        score = get_match_score(prod, i)
        explanation = EXPLANATIONS[i % len(EXPLANATIONS)]
        in_wish = prod['asin'] in st.session_state.get('wishlist_ids', set())
        feedback_key = f"fb_{prod['asin']}"
        current_fb = st.session_state.get(feedback_key)

        with cols[i % 4]:
            st.markdown(render_product_card_html(prod, i), unsafe_allow_html=True)

            # Why this? explanation
            st.markdown(f"""
<div style="background-color:{p['accent_soft']};border-left:3px solid {p['accent']};padding:8px 12px;
            border-radius:0 8px 8px 0;font-size:12px;color:{p['text_secondary']};
            line-height:1.5;margin-bottom:8px">
  <strong style="color:{p['text_primary']}">Why this?</strong> {explanation}
</div>""", unsafe_allow_html=True)

            # Action row
            fc1, fc2, fc3 = st.columns([1, 1, 2])
            with fc1:
                thumb_up_style = "primary" if current_fb == "up" else "secondary"
                if st.button("▲", key=f"up_{prod['asin']}_{i}",
                             help="More like this", type=thumb_up_style):
                    try:
                        save_feedback(user_id, prod['asin'], True)
                        st.session_state[feedback_key] = "up"
                        st.toast("Thanks for your feedback!", icon="✓")
                        st.rerun()
                    except Exception:
                        st.toast("Could not save feedback")
            with fc2:
                thumb_dn_style = "primary" if current_fb == "down" else "secondary"
                if st.button("▼", key=f"dn_{prod['asin']}_{i}",
                             help="Less like this", type=thumb_dn_style):
                    try:
                        save_feedback(user_id, prod['asin'], False)
                        st.session_state[feedback_key] = "down"
                        st.toast("We'll improve your recommendations!", icon="✓")
                        st.rerun()
                    except Exception:
                        st.toast("Could not save feedback")
            with fc3:
                save_label = "✓ Saved" if in_wish else "+ Save"
                save_bg = p['accent_soft'] if in_wish else p['accent']
                save_txt = p['accent'] if in_wish else '#ffffff'
                if st.button(save_label, key=f"fy_save_{prod['asin']}_{i}", type="secondary"):
                    try:
                        if in_wish:
                            remove_from_wishlist(user_id, prod['asin'])
                            st.session_state['wishlist_ids'].discard(prod['asin'])
                            st.toast("Removed from wishlist", icon="✓")
                        else:
                            add_to_wishlist(user_id, prod['asin'],
                                            prod.get('title', ''),
                                            prod.get('price', 0),
                                            prod.get('category', ''))
                            st.session_state['wishlist_ids'].add(prod['asin'])
                            add_notification('success', 'Wishlist Updated',
                                             f"{prod.get('title', '')[:35]} added")
                            st.toast("Product saved to wishlist!", icon="✓")
                        st.rerun()
                    except Exception:
                        st.toast("Something went wrong")
