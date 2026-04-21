import streamlit as st
import json
from auth.session import check_login
from utils.sidebar import render_sidebar
from utils.topbar import render_topbar
from utils.helpers import render_product_card_html
from utils.notifications import add_notification
from database.db_operations import add_to_wishlist, remove_from_wishlist

st.set_page_config(page_title="Explore | IntelliRec", page_icon="🔍", layout="wide")
check_login()
from utils.theme import inject_global_css
inject_global_css()
render_sidebar("explore")

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
render_topbar("Explore Products", "Browse, search and filter our full catalogue")

# ── Top Filter Panel ────────────────────────────────────────────────────────────
with st.container():
    f_row1, f_row2 = st.columns([2, 1])
    with f_row1:
        search = st.text_input("Search products", placeholder="Search products…",
                               label_visibility="collapsed", key="ex_search")
    with f_row2:
        categories = st.multiselect("Filter categories",
                                    ["Electronics", "Home & Kitchen"],
                                    default=["Electronics", "Home & Kitchen"],
                                    label_visibility="collapsed", key="ex_cats")

    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    with f_col1:
        price_range = st.slider("Price ($)", 0, 500, (0, 500), key="ex_price")
    with f_col2:
        min_rating = st.slider("Min Rating", 1.0, 5.0, 1.0, 0.5, key="ex_rating")
    with f_col3:
        bestseller = st.toggle("Best Sellers Only", key="ex_bestseller")
    with f_col4:
        sort_by = st.selectbox("Sort by", [
            "Relevance", "Price: Low to High", "Price: High to Low", "Highest Rated"
        ], key="ex_sort", label_visibility="collapsed")

if st.button("Reset Filters", type="secondary", key="ex_reset"):
    for k in ['ex_search', 'ex_cats', 'ex_price', 'ex_rating',
              'ex_bestseller', 'ex_sort', 'ex_page']:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()

# Apply filters
filtered = products.copy()
if search:
    q = search.lower()
    filtered = [p for p in filtered
                if q in p['title'].lower()
                or q in p.get('category', '').lower()
                or q in p.get('description_short', '').lower()]
if categories:
    filtered = [p for p in filtered if p.get('category') in categories]
filtered = [p for p in filtered
            if price_range[0] <= p.get('price', 0) <= price_range[1]
            and p.get('rating', 0) >= min_rating]
if bestseller:
    filtered = [p for p in filtered if p.get('is_bestseller')]

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
  <p style="font-size:13px;color:#9CA3AF;margin:0">
    Showing <strong style="color:#111827">{len(page_prods)}</strong>
    of <strong style="color:#111827">{len(filtered)}</strong> products
  </p>
</div>""", unsafe_allow_html=True)

if not filtered:
    st.markdown("""
<div style="background:rgba(255,255,255,0.78);backdrop-filter:blur(20px);
            -webkit-backdrop-filter:blur(20px);
            border:1px solid rgba(255,255,255,0.6);border-radius:20px;
            padding:40px;text-align:center;box-shadow:0 4px 20px rgba(108,99,255,0.08);">
  <p style="font-size:16px;font-weight:600;color:#111827;margin-bottom:6px">No products found</p>
  <p style="font-size:14px;color:#6B7280">Try broadening your search or adjusting filters.</p>
</div>""", unsafe_allow_html=True)
else:
    cols = st.columns(4)

    for i, prod in enumerate(page_prods):
        in_wish = prod['asin'] in st.session_state.get('wishlist_ids', set())
        save_label = "Saved" if in_wish else "+ Save"
        with cols[i % 4]:
            st.markdown(render_product_card_html(prod, i, show_match=False),
                        unsafe_allow_html=True)
            bc1, bc2 = st.columns([1, 1])
            with bc1:
                if st.button(save_label, key=f"ex_wish_{prod['asin']}_{i}",
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
                            st.toast("Product saved to wishlist!", icon="✓")
                        st.rerun()
                    except Exception:
                        st.toast("Something went wrong")
            with bc2:
                if st.button("Similar", key=f"ex_sim_{prod['asin']}_{i}",
                             use_container_width=True, type="secondary"):
                    st.session_state['similar_product'] = prod['asin']
                    st.switch_page("pages/02_For_You.py")

    # Load more
    if len(page_prods) < len(filtered):
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button(f"Load more ({len(filtered) - len(page_prods)} remaining)",
                     use_container_width=True, key="ex_loadmore"):
            st.session_state['ex_page'] = page + 1
            st.rerun()
