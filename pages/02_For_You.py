import streamlit as st
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.session import check_login
from utils.sidebar import render_sidebar
from utils.topbar import render_topbar
from utils.helpers import render_product_card_html, get_match_score, EXPLANATIONS, normalize_categories, maybe_show_product_dialog
from utils.notifications import add_notification
from utils.explainer import generate_explanation
from utils.model_loader import (
    MODELS_READY, get_hybrid_recommendations,
    get_cf_recommendations, get_cb_recommendations,
    get_similar_products, get_products_df
)
from database.db_operations import add_to_wishlist, remove_from_wishlist, save_feedback

st.set_page_config(page_title="For You | IntelliRec", page_icon="💡", layout="wide", initial_sidebar_state="expanded")
check_login()

# Force reload utils.theme to bust Streamlit cache
import importlib
import sys
if 'utils.theme' in sys.modules:
    importlib.reload(sys.modules['utils.theme'])

from utils.theme import get_palette, inject_global_css
theme = st.session_state.get('theme', 'light')
p = get_palette(theme)
inject_global_css(p)

render_sidebar("for_you")

user_id = st.session_state.get('user_id') or 'guest'


# ── Fallback: sample products from JSON ───────────────────────────────────────
@st.cache_data
def load_sample_products():
    try:
        with open("assets/sample_products.json", "r") as f:
            return json.load(f)
    except Exception:
        return []


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
maybe_show_product_dialog()

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

# ── Model status banner ────────────────────────────────────────────────────────
if MODELS_READY:
    st.markdown(f"""
    <div style="background: {p['accent_soft']};
                border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 12px; padding: 14px 20px; margin-bottom: 24px;
                display: flex; align-items: center; gap: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.02);">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="{p['accent']}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
        </svg>
        <span style="font-size: 14px; color: {p['text_primary']}; font-weight: 400; letter-spacing: 0.2px;">
            <strong style="color: {p['accent']}; font-weight: 600;">AI Engines Active</strong> &nbsp;&bull;&nbsp; Recommendations powered by trained SVD + TF-IDF + VADER
        </span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style="background: rgba(245, 158, 11, 0.08);
                border: 1px solid rgba(245, 158, 11, 0.2); border-radius: 12px; padding: 14px 20px; margin-bottom: 24px;
                display: flex; align-items: center; gap: 12px;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <span style="font-size: 14px; color: {p['text_primary']}; font-weight: 400;">
            <strong style="color: #F59E0B; font-weight: 600;">AI Engine Loading</strong> &nbsp;&bull;&nbsp; Showing curated picks while models initialize. Full personalization activates automatically.
        </span>
    </div>
    """, unsafe_allow_html=True)

# ── Similar Products Section (activated from Home / Explore "Similar" button) ─
# Two-step clear: handle the flag BEFORE reading _sim_pid
if st.session_state.get('_clear_similar_requested'):
    st.session_state.pop('similar_product', None)
    st.session_state.pop('_clear_similar_requested', None)

_sim_pid = st.session_state.get('similar_product')
# Guard: if similar_product was accidentally set to a dict (legacy bug), extract the id
if isinstance(_sim_pid, dict):
    _sim_pid = _sim_pid.get('asin') or _sim_pid.get('product_id') or None
    if _sim_pid:
        st.session_state['similar_product'] = _sim_pid

if _sim_pid:
    # Look up the source product name — works whether models are live or in fallback mode
    _products_df = get_products_df()
    _has_live_models = MODELS_READY and not (_products_df is None or _products_df.empty or 'product_id' not in _products_df.columns)
    if True:  # always enter to show similar results (fallback is handled inside get_similar_products)
        # Resolve source product name from live DF or session state fallback
        _src_name = _sim_pid
        if _has_live_models and not _products_df.empty:
            _src_rows = _products_df[_products_df['product_id'] == _sim_pid]
            if not _src_rows.empty:
                _src_name = str(_src_rows.iloc[0].get('title', _sim_pid))[:60]
        # Also check if the product title was stored when user clicked Similar
        if _src_name == _sim_pid:
            _src_name = st.session_state.get('similar_product_title', _sim_pid)[:60]

        _engine_label = "TF-IDF cosine similarity" if _has_live_models else "curated picks (AI engine loading)"
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,{p['accent_soft']},{p['glass_bg']});
                    border:1px solid {p['accent']}20;border-radius:16px;
                    padding:18px 24px;margin-bottom:20px;
                    display:flex;align-items:center;justify-content:space-between;gap:12px;">
            <div>
                <span style="font-size:15px;font-weight:700;color:{p['text_primary']}">
                    🔍 Similar to: {_src_name}
                </span><br/>
                <span style="font-size:12px;color:{p['text_secondary']}">
                    Products found via {_engine_label}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Clear button — sets a flag then reruns (reliable two-step pattern for Streamlit)
        if st.button("✕ Clear & show regular recommendations", key="btn_clear_similar_v2", type="secondary"):
            st.session_state['_clear_similar_requested'] = True
            st.rerun()

        with st.spinner("Finding similar products…"):
            _sim_results = get_similar_products(_sim_pid, n=12)

        if _sim_results:
            st.markdown(f"<p style='font-size:13px;color:{p['text_secondary']};margin-bottom:16px'>"
                        f"Showing {len(_sim_results)} similar products</p>",
                        unsafe_allow_html=True)
            _sim_cols = st.columns(4)
            for _si, _sr in enumerate(_sim_results):
                with _sim_cols[_si % 4]:
                    st.markdown(render_product_card_html(_sr, _si), unsafe_allow_html=True)

                    # Save button
                    _sr_pid = _sr['product_id']
                    _sr_in_wish = _sr_pid in st.session_state.get('wishlist_ids', set())
                    _sr_label = "✓ Saved" if _sr_in_wish else "+ Save"
                    bc1, bc2 = st.columns([1, 1])
                    with bc1:
                        if st.button(_sr_label, key=f"sim_save_{_sr_pid}_{_si}", type="secondary", use_container_width=True):
                            if not isinstance(st.session_state.get('wishlist_ids'), set):
                                st.session_state['wishlist_ids'] = set()
                            try:
                                if _sr_in_wish:
                                    remove_from_wishlist(user_id, _sr_pid)
                                    st.session_state['wishlist_ids'].discard(_sr_pid)
                                    st.toast("Removed from wishlist", icon="✅")
                                else:
                                    success = add_to_wishlist(user_id, _sr_pid,
                                        _sr.get('title', ''), _sr.get('price', 0), _sr.get('category', ''))
                                    if success:
                                        st.session_state['wishlist_ids'].add(_sr_pid)
                                        _cat = _sr.get('category', '')
                                        if _cat:
                                            st.session_state.setdefault('saved_cats', []).append(_cat)
                                        st.toast("✅ Saved to wishlist!", icon="💾")
                                    else:
                                        st.toast("Could not save", icon="❌")
                                st.rerun()
                            except Exception as _e:
                                st.toast(f"Error: {_e}", icon="❌")
                    with bc2:
                        if st.button("Similar", key=f"sim_sim_{_sr_pid}_{_si}", type="secondary", use_container_width=True):
                            st.session_state['similar_product'] = _sr_pid
                            st.rerun()
        else:
            st.info("No similar products found for this item.")

        st.markdown("---")


if 'show_filters' not in st.session_state:
    st.session_state['show_filters'] = False

# Inject custom CSS for the toggle buttons and card action rows
st.markdown(f"""
<style>
/* Beautiful SaaS Toggle Buttons via adjacent sibling selector */
.ir-toggles-marker + div[data-testid="stHorizontalBlock"] div[data-testid="column"] div[data-testid="stButton"] > button {{
    border-radius: 100px !important;
    padding: 8px 24px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    min-height: 42px !important;
    border: 1px solid {p['border']} !important;
    background: {p['card_bg']} !important;
    color: {p['text_primary']} !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}}
.ir-toggles-marker + div[data-testid="stHorizontalBlock"] div[data-testid="column"] div[data-testid="stButton"] > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(99,102,241,0.2) !important;
    border-color: {p['accent']} !important;
}}
.ir-toggles-marker + div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(1) div[data-testid="stButton"] > button {{
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.3) !important;
}}
.ir-toggles-marker + div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(1) div[data-testid="stButton"] > button:hover {{
    box-shadow: 0 8px 25px rgba(99,102,241,0.5) !important;
}}
.ir-toggles-marker + div[data-testid="stHorizontalBlock"] div[data-testid="column"] div[data-testid="stButton"] > button p {{
    color: inherit !important;
}}

/* ── "Why this?" native HTML details/summary ── */
.ir-why-details {{
    border: 1px solid {p['border']};
    border-radius: 8px;
    background: {p['glass_bg']};
    margin: 4px 0 6px;
    overflow: hidden;
}}
.ir-why-details summary {{
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 600;
    color: {p['accent']};
    cursor: pointer;
    list-style: none;
    display: flex;
    align-items: center;
    gap: 6px;
    user-select: none;
}}
.ir-why-details summary::-webkit-details-marker {{ display: none; }}
.ir-why-details summary::before {{
    content: '▶';
    font-size: 9px;
    transition: transform 0.2s ease;
}}
.ir-why-details[open] summary::before {{
    transform: rotate(90deg);
}}
.ir-why-details summary:hover {{
    background: {p['accent_soft']};
}}
.ir-why-details .ir-why-body {{
    padding: 6px 12px 10px;
    font-size: 12px;
    line-height: 1.6;
    color: {p['text_secondary']};
    border-top: 1px solid {p['border']};
}}

/* ── Card feedback action row uniform sizing ── */
.ir-card-actions [data-testid="stHorizontalBlock"] [data-testid="column"] .stButton > button {{
    width: 100% !important;
    min-height: 34px !important;
    padding: 6px 8px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    text-align: center !important;
    justify-content: center !important;
    white-space: nowrap !important;
}}
</style>
<div class="ir-toggles-marker"></div>
""", unsafe_allow_html=True)

# Layout for the toggle button
btn_col1, _ = st.columns([1.5, 8.5])
with btn_col1:
    btn_label_1 = "Close Filters" if st.session_state['show_filters'] else "Configure Engine"
    if st.button(btn_label_1, use_container_width=True, key="btn_tune_ai"):
        st.session_state['show_filters'] = not st.session_state['show_filters']
        st.rerun()



if st.session_state['show_filters']:
    st.markdown(f'<div style="background:{p["card_bg"]}; border:1px solid {p["border"]}; border-radius:16px; padding:24px; margin-bottom:24px; box-shadow:0 8px 32px rgba(0,0,0,0.06);">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<p style="font-size:12px;font-weight:600;color:{p["text_secondary"]};text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">Engine</p>', unsafe_allow_html=True)
        engine = st.radio("Engine", ["Hybrid", "Collaborative", "Content-Based"],
                          label_visibility="collapsed", key="fy_engine")
    with col2:
        num_recs  = st.slider("Results", 5, 20, 12, key="fy_num")
        diversity = st.slider("Diversity (%)", 0, 100, 30, key="fy_diversity")
    with col3:
        # All possible category names (onboarding UI names + dataset names)
        _FY_ALL_OPTIONS = [
            "Electronics", "Home & Kitchen", "Clothing & Shoes", "Beauty & Personal Care",
            "Fashion", "Clothing", "Beauty", "Sports", "Books", "Gaming",
            "Health", "Fitness", "Toys", "Automotive", "Office",
            "Pet Supplies", "Garden", "Toys & Games",
        ]
        _fy_raw_default = (
            st.session_state.get("pref_cats") or
            st.session_state.get("preferred_categories") or
            ["Electronics", "Home & Kitchen", "Clothing & Shoes", "Beauty & Personal Care"]
        )
        # Filter to only options present in the list (prevents crash on unknown values)
        _fy_default_cats = [c for c in _fy_raw_default if c in _FY_ALL_OPTIONS]
        if not _fy_default_cats:
            _fy_default_cats = ["Electronics", "Home & Kitchen", "Clothing & Shoes", "Beauty & Personal Care"]

        # Also sanitize any previously stored fy_cats value
        if 'fy_cats' in st.session_state:
            _stored = [c for c in st.session_state['fy_cats'] if c in _FY_ALL_OPTIONS]
            if not _stored:
                del st.session_state['fy_cats']

        categories = st.multiselect(
            "Categories",
            _FY_ALL_OPTIONS,
            default=_fy_default_cats if 'fy_cats' not in st.session_state else st.session_state['fy_cats'],
            key="fy_cats")
        min_rating  = st.slider("Min Rating", 1.0, 5.0, 1.0, 0.5, key="fy_rating")
        price_range = st.slider("Price ($)", 0, 99999, (0, 99999), key="fy_price")

    fcol1, fcol2 = st.columns(2)
    with fcol1:
        if st.button("🔄 Refresh Recommendations", key="btn_refresh_recs", type="primary"):
            add_notification('info', 'Recommendations Updated', 'Fresh picks generated for you.')
            st.toast("Recommendations updated!", icon="🔄")
    with fcol2:
        if st.button("Reset Filters", key="btn_reset_filters", type="secondary"):
            for k in ['fy_num', 'fy_diversity', 'fy_cats', 'fy_rating', 'fy_price', 'fy_engine', 'show_filters']:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)
else:
    # Read values from session state if hidden, otherwise use defaults
    engine     = st.session_state.get('fy_engine', 'Hybrid')
    num_recs   = st.session_state.get('fy_num', 12)
    diversity  = st.session_state.get('fy_diversity', 30)
    _fy_fallback_cats = (
        st.session_state.get("pref_cats") or
        st.session_state.get("preferred_categories") or
        ["Electronics", "Home & Kitchen", "Clothing & Shoes", "Beauty & Personal Care"]
    )
    categories = st.session_state.get('fy_cats', _fy_fallback_cats)
    min_rating  = st.session_state.get('fy_rating', 1.0)
    price_range = st.session_state.get('fy_price', (0, 99999))

st.markdown("---")

# Engine badge
st.markdown(f"""
<div style="margin-bottom:16px;display:flex;align-items:center;gap:10px">
  <span style="background-color:{p['accent_soft']};color:{p['accent']};padding:5px 14px;border-radius:100px;
               font-size:13px;font-weight:600">{engine} Active</span>
  <span style="font-size:13px;color:{p['text_secondary']}">Diversity: {diversity}%</span>
</div>""", unsafe_allow_html=True)

# ── Fetch recommendations ─────────────────────────────────────────────────────
if MODELS_READY:
    with st.spinner("Generating personalized recommendations…"):
        # Normalize categories to match dataset names
        _cats_to_use = normalize_categories(
            categories or ["Electronics", "Home & Kitchen",
                           "Clothing & Shoes", "Beauty & Personal Care"]
        )
        print(f"[FOR_YOU] Categories passed to engine: {_cats_to_use}")
        try:
            _is_guest = (user_id == 'guest')
            if engine == "Collaborative" and not _is_guest:
                recs = get_cf_recommendations(user_id, n=num_recs * 2, categories=_cats_to_use)
            elif engine == "Content-Based" or (engine == "Collaborative" and _is_guest):
                # Guest users can't use collaborative filtering (no user history)
                recs = get_cb_recommendations(categories=_cats_to_use, n=num_recs * 2)
            else:
                recs = get_hybrid_recommendations(
                    user_id, n=num_recs * 2,
                    categories=_cats_to_use,
                    diversity=diversity / 100.0
                )
        except Exception as e:
            st.warning(f"Recommendation engine note: {e}")
            recs = []

    # Apply price + rating post-filters
    filtered = [
        r for r in recs
        if r.get('rating', 0) >= min_rating
        and price_range[0] <= float(r.get('price') or 0) <= price_range[1]
    ]

    # Fallback 1: relax price/rating filters — keep all recs as-is
    if not filtered and recs:
        filtered = recs[:num_recs]

    # Fallback 2: categories may not have matched — retry without category filter
    if not filtered:
        try:
            _fallback = get_cb_recommendations(categories=None, n=num_recs * 2)
            filtered = _fallback[:num_recs]
        except Exception:
            filtered = []

    # Fallback 3: if all ML engines fail, use sample products
    if not filtered:
        _sp = load_sample_products()
        filtered = _sp[:num_recs] if _sp else []

    if not filtered:
        st.markdown(f"""
<div style="background-color:{p['card_bg']};border:1px solid {p['border']};border-radius:20px;
            padding:40px;text-align:center;margin-top:20px">
  <p style="font-size:16px;font-weight:600;color:{p['text_primary']};margin-bottom:6px">No results found</p>
  <p style="font-size:14px;color:{p['text_secondary']}">Try adjusting the filters above.</p>
</div>""", unsafe_allow_html=True)
    else:
        display = filtered[:num_recs]
        # ── Store displayed recs for Profile > History tab ──────────────────────
        st.session_state['fy_last_recs'] = display
        st.markdown(
            f"<p style='font-size:13px;color:{p['text_secondary']};margin-bottom:16px'>"
            f"Showing {len(display)} of {len(filtered)} AI-powered recommendations</p>",
            unsafe_allow_html=True
        )

        cols = st.columns(4)
        for i, rec in enumerate(display):
            pid          = rec['product_id']
            in_wish      = pid in st.session_state.get('wishlist_ids', set())
            feedback_key = f"fb_{pid}"
            current_fb   = st.session_state.get(feedback_key)
            score        = rec.get('match_score', 50)

            with cols[i % 4]:
                st.markdown(render_product_card_html(rec, i), unsafe_allow_html=True)

                # Why this? — native HTML details (no Streamlit icon dependencies)
                _user_prefs = st.session_state.get('pref_cats') or []
                _expl = generate_explanation(rec, _user_prefs, i) if rec.get('engine') \
                        else (rec.get('explanation') or EXPLANATIONS[i % len(EXPLANATIONS)])

                st.markdown(f"""
                <details class="ir-why-details">
                    <summary>Why this?</summary>
                    <div class="ir-why-body">
                        <strong style="color:{p['text_primary']}">AI Insight</strong><br/>
                        {_expl}
                    </div>
                </details>
                """, unsafe_allow_html=True)

                # Actions — feedback + details + save row
                st.markdown('<div class="ir-card-actions">', unsafe_allow_html=True)
                fc1, fc2, fc3, fc4 = st.columns([1, 1, 2, 2])
                with fc1:
                    style_up = "primary" if current_fb == "up" else "secondary"
                    if st.button("▲", key=f"up_{pid}_{i}", help="More like this", type=style_up, use_container_width=True):
                        try:
                            save_feedback(user_id, pid, True)
                            st.session_state[feedback_key] = "up"
                            # Track liked product + category for recommendation boosting
                            st.session_state.setdefault('liked_pids', set()).add(pid)
                            st.session_state.setdefault('disliked_pids', set()).discard(pid)
                            _cat = rec.get('category', '')
                            if _cat:
                                st.session_state.setdefault('liked_cats_feedback', []).append(_cat)
                            st.toast(f"Got it! We'll show more {_cat or 'similar'} picks.", icon="✅")
                            st.rerun()
                        except Exception:
                            st.toast("Could not save feedback")
                with fc2:
                    style_dn = "primary" if current_fb == "down" else "secondary"
                    if st.button("▼", key=f"dn_{pid}_{i}", help="Less like this", type=style_dn, use_container_width=True):
                        try:
                            save_feedback(user_id, pid, False)
                            st.session_state[feedback_key] = "down"
                            # Track disliked product + category for recommendation penalizing
                            st.session_state.setdefault('disliked_pids', set()).add(pid)
                            st.session_state.setdefault('liked_pids', set()).discard(pid)
                            _cat = rec.get('category', '')
                            if _cat:
                                st.session_state.setdefault('disliked_cats_feedback', []).append(_cat)
                            st.toast(f"Got it! We'll show fewer {_cat or 'similar'} picks.", icon="✅")
                            st.rerun()
                        except Exception:
                            st.toast("Could not save feedback")
                with fc3:
                    if st.button("Details", key=f"fy_det_{pid}_{i}", type="secondary", use_container_width=True):
                        st.session_state["view_product"] = rec
                        st.rerun()
                with fc4:
                    save_label = "✓ Saved" if in_wish else "+ Save"
                    if st.button(save_label, key=f"fy_save_{pid}_{i}", type="secondary", use_container_width=True):
                        # Ensure wishlist_ids is always a set before any operation
                        if not isinstance(st.session_state.get('wishlist_ids'), set):
                            st.session_state['wishlist_ids'] = set()
                        try:
                            if in_wish:
                                remove_from_wishlist(user_id, pid)
                                st.session_state['wishlist_ids'].discard(pid)
                                st.toast("Removed from wishlist", icon="✅")
                            else:
                                success = add_to_wishlist(user_id, pid,
                                                rec.get('title', ''),
                                                rec.get('price', 0),
                                                rec.get('category', ''))
                                if success:
                                    st.session_state['wishlist_ids'].add(pid)
                                    # Track saved category for recommendation boosting
                                    _cat = rec.get('category', '')
                                    if _cat:
                                        st.session_state.setdefault('saved_cats', []).append(_cat)
                                    try:
                                        add_notification('success', 'Wishlist Updated',
                                                         f"{rec.get('title','')[:35]} added")
                                    except Exception:
                                        pass
                                    st.toast("✅ Product saved to wishlist!", icon="💾")
                                else:
                                    st.toast("Could not save. Try again.", icon="❌")
                            st.rerun()
                        except Exception as _save_err:
                            st.toast(f"Error: {_save_err}", icon="❌")
                st.markdown('</div>', unsafe_allow_html=True)

else:
    # ── DEMO MODE — show sample products without heavy filtering ──────────────
    _demo_all = load_sample_products()
    _pref_cats_demo = normalize_categories(
        st.session_state.get("pref_cats") or
        st.session_state.get("preferred_categories") or []
    )
    _nr = num_recs if 'num_recs' in dir() else 12
    _mr = min_rating if 'min_rating' in dir() else 1.0
    _pr = price_range if 'price_range' in dir() else (0, 99999)

    # Apply a loose filter: preferred cats first, then all categories
    if _pref_cats_demo:
        filtered = [p for p in _demo_all if p.get("category") in _pref_cats_demo and p.get("rating", 0) >= _mr]
        if not filtered:
            filtered = _demo_all  # fallback: show everything
    else:
        filtered = _demo_all

    num_recs_fb = _nr

    if not filtered:
        st.markdown(f"""
<div style="background-color:{p['card_bg']};border:1px solid {p['border']};border-radius:20px;
            padding:40px;text-align:center;margin-top:20px">
  <p style="font-size:16px;font-weight:600;color:{p['text_primary']};margin-bottom:6px">No results found</p>
  <p style="font-size:14px;color:{p['text_secondary']}">Try adjusting the filters above.</p>
</div>""", unsafe_allow_html=True)
    else:
        display = filtered[:num_recs_fb]
        # ── Store displayed recs for Profile > History tab ──────────────────────
        st.session_state['fy_last_recs'] = display
        st.markdown(f"<p style='font-size:13px;color:{p['text_secondary']};margin-bottom:16px'>"
                    f"Showing {len(display)} of {len(filtered)} recommendations</p>",
                    unsafe_allow_html=True)
        cols = st.columns(4)
        for i, prod in enumerate(display):
            score        = get_match_score(prod, i)
            explanation  = EXPLANATIONS[i % len(EXPLANATIONS)]
            in_wish      = prod['asin'] in st.session_state.get('wishlist_ids', set())
            feedback_key = f"fb_{prod['asin']}"
            current_fb   = st.session_state.get(feedback_key)

            with cols[i % 4]:
                st.markdown(render_product_card_html(prod, i), unsafe_allow_html=True)

                st.markdown(f"""
                <details class="ir-why-details">
                    <summary>Why this?</summary>
                    <div class="ir-why-body">
                        <strong style="color:{p['text_primary']}">AI Insight</strong><br/>
                        {explanation}
                    </div>
                </details>
                """, unsafe_allow_html=True)

                st.markdown('<div class="ir-card-actions">', unsafe_allow_html=True)
                fc1, fc2, fc3, fc4 = st.columns([1, 1, 2, 2])
                with fc1:
                    style_up = "primary" if current_fb == "up" else "secondary"
                    if st.button("▲", key=f"up_{prod['asin']}_{i}", help="More like this", type=style_up, use_container_width=True):
                        try:
                            save_feedback(user_id, prod['asin'], True)
                            st.session_state[feedback_key] = "up"
                            st.session_state.setdefault('liked_pids', set()).add(prod['asin'])
                            st.session_state.setdefault('disliked_pids', set()).discard(prod['asin'])
                            _cat = prod.get('category', '')
                            if _cat:
                                st.session_state.setdefault('liked_cats_feedback', []).append(_cat)
                            st.toast(f"Got it! We'll show more {_cat or 'similar'} picks.", icon="✅")
                            st.rerun()
                        except Exception:
                            st.toast("Could not save feedback")
                with fc2:
                    style_dn = "primary" if current_fb == "down" else "secondary"
                    if st.button("▼", key=f"dn_{prod['asin']}_{i}", help="Less like this", type=style_dn, use_container_width=True):
                        try:
                            save_feedback(user_id, prod['asin'], False)
                            st.session_state[feedback_key] = "down"
                            st.session_state.setdefault('disliked_pids', set()).add(prod['asin'])
                            st.session_state.setdefault('liked_pids', set()).discard(prod['asin'])
                            _cat = prod.get('category', '')
                            if _cat:
                                st.session_state.setdefault('disliked_cats_feedback', []).append(_cat)
                            st.toast(f"Got it! We'll show fewer {_cat or 'similar'} picks.", icon="✅")
                            st.rerun()
                        except Exception:
                            st.toast("Could not save feedback")
                with fc3:
                    if st.button("Details", key=f"fy_det_{prod['asin']}_{i}", type="secondary", use_container_width=True):
                        st.session_state["view_product"] = prod
                        st.rerun()
                with fc4:
                    save_label = "✓ Saved" if in_wish else "+ Save"
                    if st.button(save_label, key=f"fy_save_{prod['asin']}_{i}", type="secondary", use_container_width=True):
                        # Ensure wishlist_ids is always a set before any operation
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
                                    # Track saved category for recommendation boosting
                                    _cat = prod.get('category', '')
                                    if _cat:
                                        st.session_state.setdefault('saved_cats', []).append(_cat)
                                    try:
                                        add_notification('success', 'Wishlist Updated',
                                                         f"{prod.get('title','')[:35]} added")
                                    except Exception:
                                        pass
                                    st.toast("✅ Product saved to wishlist!", icon="💾")
                                else:
                                    st.toast("Could not save. Try again.", icon="❌")
                            st.rerun()
                        except Exception as _save_err:
                            st.toast(f"Error: {_save_err}", icon="❌")
                st.markdown('</div>', unsafe_allow_html=True)
