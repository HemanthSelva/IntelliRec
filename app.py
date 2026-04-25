import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# NumPy compatibility shim for Streamlit Cloud
try:
    import numpy as np
    # Fix for numpy 1.x models loaded in numpy 2.x environment
    if not hasattr(np, 'bool'):
        np.bool = bool
    if not hasattr(np, 'int'):
        np.int = int
    if not hasattr(np, 'float'):
        np.float = float
    if not hasattr(np, 'complex'):
        np.complex = complex
    if not hasattr(np, 'object'):
        np.object = object
    if not hasattr(np, 'str'):
        np.str = str
except Exception:
    pass

import streamlit as st
from database.supabase_client import supabase
from auth.session import init_session, is_logged_in

st.set_page_config(
    page_title="IntelliRec — AI Recommendations",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Email confirmation / OAuth callback handler ───────────────────────────────
_token_hash = st.query_params.get('token_hash')
_type       = st.query_params.get('type')
_code       = st.query_params.get('code')

if _token_hash and _type:
    try:
        supabase.auth.verify_otp({'token_hash': _token_hash, 'type': _type})
        st.query_params.clear()
        st.session_state.show_email_confirmed = True
    except Exception:
        st.markdown("""
<div style="background:#FEE2E2;color:#DC2626;border-left:4px solid #DC2626;
            border-radius:8px;padding:14px 18px;margin:16px 0;font-size:14px;">
  <strong>Confirmation link expired.</strong> Request a new one by signing in and clicking
  "Resend Verification Email".
</div>
""", unsafe_allow_html=True)
elif _code:
    try:
        resp = supabase.auth.exchange_code_for_session(
            {"auth_code": _code}
        )
        st.query_params.clear()
        if resp and resp.user:
            from auth.session import _apply_user_session
            _apply_user_session(resp.user)
            # Create profile for Google users if missing
            try:
                existing = supabase.table('profiles').select(
                    'id').eq('id', resp.user.id).execute()
                if not existing.data:
                    meta = resp.user.user_metadata or {}
                    full_name = (
                        meta.get('full_name') or
                        meta.get('name') or
                        resp.user.email.split('@')[0]
                    )
                    username = full_name.lower().replace(
                        ' ', '_')
                    supabase.table('profiles').insert({
                        'id': resp.user.id,
                        'full_name': full_name,
                        'username': username,
                        'preferred_categories': [],
                        'avatar_color': '#6C63FF'
                    }).execute()
                    supabase.table(
                        'user_preferences').insert({
                        'user_id': resp.user.id,
                        'preferred_categories': [],
                        'preferred_engine': 'hybrid'
                    }).execute()
            except Exception as profile_err:
                print(f"Google profile creation: {profile_err}")
    except Exception as e:
        print(f"OAuth code exchange error: {e}")
        st.session_state.oauth_error = str(e)

# ── Session init ──────────────────────────────────────────────────────────────
init_session()

# ── Sidebar collapse state (used by CSS-based toggle in sidebar.py) ───────────
if 'sidebar_collapsed' not in st.session_state:
    st.session_state['sidebar_collapsed'] = False

# ── Auth routing ──────────────────────────────────────────────────────────────
if not is_logged_in():
    if st.session_state.get('show_signup', False):
        from auth.signup import render_signup
        render_signup()
    else:
        from auth.login import render_login
        render_login()
    st.stop()

# ── Onboarding check ──────────────────────────────────────────────────────────
from auth.onboarding import needs_onboarding, show_onboarding
if needs_onboarding():
    show_onboarding()
    st.stop()

# ── Welcome notification on first login ───────────────────────────────────────
from utils.notifications import add_notification
if not st.session_state.get('welcome_sent'):
    first_name = (st.session_state.get('full_name') or 'there').split()[0]
    add_notification('success', f'Welcome back, {first_name}!',
                     'Your AI-powered recommendations are ready.')
    st.session_state['welcome_sent'] = True


# ── Redirect authenticated users to Home ─────────────────────────────────────
st.switch_page("pages/01_Home.py")
