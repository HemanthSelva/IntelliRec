"""
auth/onboarding.py — Post-signup preference selection.
Clean white centered layout, category tile grid, style cards.
Uses st.button only (no HTML div tiles) to prevent duplicate rendering.
"""
import streamlit as st
from database.supabase_client import supabase

CATEGORIES = [
    ("💻", "Electronics"),
    ("🏠", "Home & Kitchen"),
    ("💄", "Beauty & Personal Care"),
    ("👗", "Clothing & Shoes"),
]

STYLES = [
    {"key": "accuracy",  "icon": "🎯", "title": "Accuracy",
     "desc": "Show me products I'll definitely love"},
    {"key": "hybrid",    "icon": "⚖️",  "title": "Balanced",
     "desc": "Mix of familiar and new discoveries"},
    {"key": "diversity", "icon": "🌟", "title": "Discovery",
     "desc": "Surprise me with new products"},
]

_OB_CSS = """
<style>
html,body,[data-testid="stAppViewContainer"],[data-testid="stAppViewContainer"]>.main{
    background:#fff!important;font-family:'Inter',sans-serif!important;
}
section[data-testid="stSidebar"]{display:none!important;}
[data-testid="collapsedControl"]{display:none!important;}
header[data-testid="stHeader"]{display:none!important;}
[data-testid="block-container"]{max-width:680px!important;margin:0 auto!important;padding:2.5rem 1.5rem 4rem!important;}

/* Category buttons — unselected */
div.stButton > button[kind="secondary"] {
    background   : #FFFFFF!important;
    border       : 2px solid #E5E7EB!important;
    border-radius: 12px!important;
    font-weight  : 500!important;
    font-size    : 14px!important;
    color        : #374151!important;
    padding      : 14px 8px!important;
    transition   : all 0.15s!important;
    line-height  : 1.4!important;
}
div.stButton > button[kind="secondary"]:hover {
    border-color : #6C63FF!important;
    color        : #6C63FF!important;
    background   : #F5F3FF!important;
}

/* Category buttons — selected (primary) */
div.stButton > button[kind="primary"] {
    background   : #6C63FF!important;
    color        : #fff!important;
    border       : 2px solid #6C63FF!important;
    border-radius: 12px!important;
    font-weight  : 600!important;
    font-size    : 14px!important;
    padding      : 14px 8px!important;
    box-shadow   : 0 4px 12px rgba(108,99,255,0.3)!important;
    transition   : all 0.15s!important;
    line-height  : 1.4!important;
}
div.stButton > button[kind="primary"]:hover {
    background   : #4F46E5!important;
    border-color : #4F46E5!important;
    transform    : translateY(-1px)!important;
}

/* CTA button */
div[data-testid="stButton"]:has(button[kind="primary"]):last-of-type > button {
    font-size: 16px!important;
}
</style>
"""


def needs_onboarding() -> bool:
    user_id = st.session_state.get('user_id')
    if not user_id or user_id == "guest":
        return False
    if st.session_state.get('onboarding_done'):
        return False
    try:
        resp = supabase.table('user_preferences').select(
            'preferred_categories').eq('user_id', user_id).execute()
        if resp.data:
            cats = resp.data[0].get('preferred_categories', [])
            if cats:
                st.session_state.onboarding_done = True
                return False
    except Exception:
        pass
    return True


def show_onboarding():
    st.markdown(
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">',
        unsafe_allow_html=True
    )
    st.markdown(_OB_CSS, unsafe_allow_html=True)

    if 'ob_selected_cats' not in st.session_state:
        st.session_state.ob_selected_cats = set()
    if 'ob_style' not in st.session_state:
        st.session_state.ob_style = "hybrid"

    full_name = st.session_state.get('full_name') or 'there'
    first     = full_name.split()[0]
    selected  = st.session_state.ob_selected_cats
    count     = len(selected)

    # Progress bar
    st.markdown("""
<div style="display:flex;align-items:center;gap:8px;margin-bottom:2rem;">
  <div style="flex:1;height:4px;background:#6C63FF;border-radius:4px;"></div>
  <span style="font-size:12px;color:#9CA3AF;font-weight:500;">Step 1 of 1</span>
</div>
""", unsafe_allow_html=True)

    # Heading
    st.markdown(f"""
<h1 style="font-size:28px;font-weight:700;color:#111827;margin-bottom:6px;">
  Personalise Your Experience
</h1>
<p style="font-size:15px;color:#6B7280;margin-bottom:2rem;">
  Help us understand your shopping preferences, {first}.
</p>
""", unsafe_allow_html=True)

    st.markdown("""
<p style="font-size:13px;font-weight:600;color:#9CA3AF;text-transform:uppercase;
   letter-spacing:1.5px;margin-bottom:12px;">What do you shop for?</p>
""", unsafe_allow_html=True)

    # ── Category grid — 2×2 layout for 4 categories ───────────────────────────
    cols = st.columns(2)
    for idx, (emoji, cat) in enumerate(CATEGORIES):
        is_sel    = cat in selected
        btn_label = f"{emoji}  {cat}" if not is_sel else f"✓  {emoji}  {cat}"
        with cols[idx % 2]:
            if st.button(
                btn_label,
                key=f"ob_cat_{idx}",
                use_container_width=True,
                type="primary" if is_sel else "secondary"
            ):
                if cat in selected:
                    selected.discard(cat)
                else:
                    selected.add(cat)
                st.rerun()

    # Count hint — minimum 1 required
    hint_color = "#6C63FF" if count >= 1 else "#EF4444"
    st.markdown(f"""
<p style="font-size:13px;color:{hint_color};font-weight:500;margin:4px 0 2rem;">
  {'✓ ' if count >= 1 else ''}{count} selected{' — great!' if count >= 1 else ' · pick at least 1 category'}
</p>
""", unsafe_allow_html=True)

    # ── Style selector — buttons only, no HTML divs ────────────────────────────
    st.markdown("""
<p style="font-size:13px;font-weight:600;color:#9CA3AF;text-transform:uppercase;
   letter-spacing:1.5px;margin-bottom:12px;">How should we recommend?</p>
""", unsafe_allow_html=True)

    style_cols = st.columns(3)
    for i, s in enumerate(STYLES):
        is_active = st.session_state.ob_style == s["key"]
        btn_label = f"{s['icon']} {s['title']}\n{s['desc']}"
        with style_cols[i]:
            if st.button(
                btn_label,
                key=f"ob_s_{s['key']}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.ob_style = s["key"]
                st.rerun()

    # ── CTA ────────────────────────────────────────────────────────────────────
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        if count < 1:
            st.markdown(f"""
<div style="background:#F3F4F6;border-radius:10px;padding:13px 20px;
            text-align:center;font-size:14px;color:#9CA3AF;font-weight:500;">
  Personalise My Feed →<br>
  <span style="font-size:12px;">Select at least 1 category to continue</span>
</div>
""", unsafe_allow_html=True)
        else:
            if st.button("Personalise My Feed →", use_container_width=True,
                         type="primary", key="ob_cta"):
                _save_onboarding()

    # Skip
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    col_a, col_b, col_c2 = st.columns([1, 2, 1])
    with col_b:
        if st.button("Skip for now", key="ob_skip",
                     use_container_width=True, type="secondary"):
            st.session_state.onboarding_done = True
            st.rerun()


def _save_onboarding():
    user_id    = st.session_state.get('user_id')
    categories = list(st.session_state.ob_selected_cats)
    style      = st.session_state.get('ob_style', 'hybrid')
    if user_id and user_id != "guest":
        try:
            supabase.table('user_preferences').upsert({
                'user_id':              user_id,
                'preferred_categories': categories,
                'preferred_engine':     style
            }).execute()
            supabase.table('profiles').update({
                'preferred_categories': categories
            }).eq('id', user_id).execute()
        except Exception as e:
            st.warning(f"Could not save preferences: {e}")
    st.session_state.onboarding_done = True
    if 'current_user' in st.session_state and st.session_state.current_user:
        st.session_state.current_user['preferred_categories'] = categories
        st.session_state.current_user['preferred_engine'] = style
    # Sync to the key the recommendation engine actually reads
    st.session_state["pref_cats"] = categories
    st.session_state["preferred_categories"] = categories
    st.session_state["preferred_engine"] = style
    st.rerun()
