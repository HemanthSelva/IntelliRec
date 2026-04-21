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
from utils.theme import inject_global_css
inject_global_css()
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
            p['product_id'] for p in st.session_state.get('guest_wishlist', [])
        }
    else:
        try:
            from database.db_operations import get_wishlist
            wl = get_wishlist(user_id)
            st.session_state['wishlist_ids'] = {p.get('product_id', '') for p in (wl or [])}
        except Exception:
            st.session_state['wishlist_ids'] = set()

# ── Top Bar ───────────────────────────────────────────────────────────────────
render_topbar("For You", "AI-powered recommendations tuned to your taste")

# ── Layout: left panel + main grid ───────────────────────────────────────────
left, right = st.columns([1, 3], gap="large")

with left:
    st.markdown("""
<div style="background:var(--bg-card,rgba(255,255,255,0.88));backdrop-filter:blur(20px);
            -webkit-backdrop-filter:blur(20px);
            border:1px solid var(--border-color,rgba(108,99,255,0.12));border-radius:20px;
            padding:20px;box-shadow:0 4px 20px rgba(108,99,255,0.12);">
  <p style="font-size:12px;font-weight:600;color:var(--text-secondary,#9CA3AF);text-transform:uppercase;
            letter-spacing:1px;margin-bottom:12px">Recommendation Engine</p>""",
                unsafe_allow_html=True)

    engine = st.radio("Engine", ["Hybrid", "Collaborative", "Content-Based"],
                      label_visibility="collapsed", key="fy_engine")

    st.markdown("<hr style='margin:14px 0;border-color:rgba(108,99,255,0.12)'>", unsafe_allow_html=True)
    st.markdown("""<p style="font-size:12px;font-weight:600;color:var(--text-secondary,#9CA3AF);
                   text-transform:uppercase;letter-spacing:1px;margin-bottom:10px">
                   Filters</p>""", unsafe_allow_html=True)

    num_recs = st.slider("Results", 5, 20, 12, key="fy_num")
    diversity = st.slider("Diversity (%)", 0, 100, 30, key="fy_diversity")
    categories = st.multiselect("Categories", ["Electronics", "Home & Kitchen"],
                                default=["Electronics", "Home & Kitchen"], key="fy_cats")
    min_rating = st.slider("Min Rating", 1.0, 5.0, 3.0, 0.5, key="fy_rating")
    price_range = st.slider("Price ($)", 0, 500, (0, 500), key="fy_price")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("Refresh Recommendations", use_container_width=True, type="primary",
                 key="fy_refresh"):
        add_notification('info', 'Recommendations Updated',
                         'Fresh picks generated for you.')
        st.toast("Recommendations updated!", icon="↻")

    if st.button("Reset Filters", use_container_width=True, type="secondary", key="fy_reset"):
        for k in ['fy_num', 'fy_diversity', 'fy_cats', 'fy_rating', 'fy_price', 'fy_engine']:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

with right:
    # Engine badge
    st.markdown(f"""
<div style="margin-bottom:16px;display:flex;align-items:center;gap:10px">
  <span style="background:#EEF2FF;color:#6C63FF;padding:5px 14px;border-radius:100px;
               font-size:13px;font-weight:600">{engine} Active</span>
  <span style="font-size:13px;color:#9CA3AF">Diversity: {diversity}%</span>
</div>""", unsafe_allow_html=True)

    # Filter + sort
    filtered = [
        p for p in products
        if p.get('category') in categories
        and p.get('rating', 0) >= min_rating
        and price_range[0] <= p.get('price', 0) <= price_range[1]
    ]

    if not filtered:
        st.markdown("""
<div style="background:rgba(255,255,255,0.78);backdrop-filter:blur(20px);
            border:1px solid rgba(255,255,255,0.6);border-radius:20px;
            padding:40px;text-align:center;margin-top:20px">
  <p style="font-size:16px;font-weight:600;color:#111827;margin-bottom:6px">No results found</p>
  <p style="font-size:14px;color:#6B7280">Try adjusting the filters on the left.</p>
</div>""", unsafe_allow_html=True)
    else:
        display = filtered[:num_recs]
        st.markdown(f"<p style='font-size:13px;color:#9CA3AF;margin-bottom:16px'>"
                    f"Showing {len(display)} of {len(filtered)} recommendations</p>",
                    unsafe_allow_html=True)

        # SVG feedback icons
        _SVG_THUMB_UP = """<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none"
          viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"
          stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z"/>
          <path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg>"""

        _SVG_THUMB_DN = """<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none"
          viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"
          stroke-linecap="round" stroke-linejoin="round">
          <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3H10z"/>
          <path d="M17 2h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"/></svg>"""

        cols = st.columns(3)
        for i, prod in enumerate(display):
            score = get_match_score(prod, i)
            explanation = EXPLANATIONS[i % len(EXPLANATIONS)]
            in_wish = prod['asin'] in st.session_state.get('wishlist_ids', set())
            feedback_key = f"fb_{prod['asin']}"
            current_fb = st.session_state.get(feedback_key)

            with cols[i % 3]:
                st.markdown(render_product_card_html(prod, i), unsafe_allow_html=True)

                # Why this? explanation
                st.markdown(f"""
<div style="background:rgba(108,99,255,0.06);border-left:3px solid #6C63FF;padding:8px 12px;
            border-radius:0 8px 8px 0;font-size:12px;color:#6B7280;
            line-height:1.5;margin-bottom:8px">
  <strong style="color:#111827">Why this?</strong> {explanation}
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
                    save_label = "Saved" if in_wish else "+ Save"
                    if st.button(save_label, key=f"fy_wish_{prod['asin']}_{i}",
                                 use_container_width=True, type="secondary"):
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
