import streamlit as st
from database.supabase_client import supabase


# ── CSS / Theme helpers ───────────────────────────────────────────────────────

def load_css():
    try:
        with open("assets/style.css", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


def inject_theme():
    dark = st.session_state.get('dark_mode', False)
    if dark:
        st.markdown("""<style>
[data-testid="stAppViewContainer"]>.main{background:#0F0F0F!important;}
section[data-testid="stSidebar"]{background:#1A1A1A!important;border-color:#2D2D2D!important;}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] label{color:#D1D5DB!important;}
[data-testid="stMarkdownContainer"] p{color:#D1D5DB!important;}
h1,h2,h3,h4{color:#F9FAFB!important;}
.product-card{background:#1A1A1A!important;border-color:#2D2D2D!important;box-shadow:0 2px 8px rgba(0,0,0,0.3)!important;}
.product-card h4,.product-card p{color:#E5E7EB!important;}
[data-testid="stMetricValue"]{color:#F9FAFB!important;}
</style>""", unsafe_allow_html=True)


# ── Session initialisation ────────────────────────────────────────────────────

def init_session():
    defaults = {
        'user':         None,
        'logged_in':    False,
        'user_id':      None,
        'username':     None,
        'full_name':    None,
        'user_email':   None,
        'dark_mode':    False,
        'theme':        'light',
        'show_signup':  False,
        'current_user': None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ── Auth operations ───────────────────────────────────────────────────────────

def signup_user(email: str, password: str, full_name: str):
    try:
        username = full_name.strip().lower().replace(" ", "_")
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name,
                    "username": username
                }
            }
        })
        if response.user:
            try:
                supabase.table('profiles').insert({
                    'id': response.user.id,
                    'full_name': full_name,
                    'username': username,
                    'preferred_categories': [],
                    'avatar_color': '#6C63FF'
                }).execute()
                supabase.table('user_preferences').insert({
                    'user_id': response.user.id,
                    'preferred_categories': [],
                    'preferred_engine': 'hybrid'
                }).execute()
            except Exception as db_err:
                print(f"Profile creation pending email verification: {db_err}")
            return True, "success"
        return False, "Signup failed. Please try again."
    except Exception as e:
        error = str(e).lower()
        if "already registered" in error or "already exists" in error:
            return False, "An account with this email already exists. Please sign in instead."
        if "password" in error and "6" in error:
            return False, "Password must be at least 6 characters long."
        if "invalid" in error and "email" in error:
            return False, "Please enter a valid email address."
        return False, f"Signup failed: {str(e)}"


def login_user(email: str, password: str):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if response.user:
            st.session_state.logged_in  = True
            st.session_state.user_id    = response.user.id
            st.session_state.user_email = response.user.email
            st.session_state.user       = response.user
            try:
                profile = supabase.table('profiles').select('*').eq(
                    'id', response.user.id).execute()
                if profile.data:
                    p = profile.data[0]
                    st.session_state.full_name = p.get('full_name', 'User')
                    st.session_state.username  = p.get('username', 'user')
                    st.session_state.preferred_categories = p.get('preferred_categories', [])
                    st.session_state.current_user = {
                        'username':     p.get('username', ''),
                        'name':         p.get('full_name', ''),
                        'email':        response.user.email,
                        'member_since': str(p.get('created_at', ''))[:10]
                    }
                else:
                    full_name = response.user.user_metadata.get('full_name', 'User')
                    username  = full_name.lower().replace(" ", "_")
                    st.session_state.full_name = full_name
                    st.session_state.username  = username
                    st.session_state.current_user = {
                        'username': username, 'name': full_name,
                        'email': response.user.email, 'member_since': ''
                    }
                    try:
                        supabase.table('profiles').insert({
                            'id': response.user.id,
                            'full_name': full_name,
                            'username': username,
                            'preferred_categories': [],
                            'avatar_color': '#6C63FF'
                        }).execute()
                    except Exception:
                        pass
            except Exception as profile_err:
                print(f"Profile fetch error: {profile_err}")
                fallback = response.user.email.split('@')[0]
                st.session_state.full_name    = fallback
                st.session_state.username     = fallback
                st.session_state.current_user = {
                    'username': fallback, 'name': fallback,
                    'email': response.user.email, 'member_since': ''
                }
            from utils.notifications import add_notification
            add_notification('success', 'Logged In Successfully', 'Welcome back to IntelliRec!')
            return True, "Login successful"
        return False, "Incorrect email or password. Please try again."
    except Exception as e:
        error = str(e).lower()
        if "email not confirmed" in error or "not confirmed" in error:
            return False, "EMAIL_NOT_CONFIRMED"
        if "invalid login" in error or "invalid credentials" in error:
            return False, "Incorrect email or password. Please try again."
        if "too many requests" in error:
            return False, "Too many attempts. Please wait a few minutes and try again."
        return False, f"Login failed: {str(e)}"


def login_with_google():
    try:
        response = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": "http://localhost:8501"
            }
        })
        if response.url:
            return response.url
        return None
    except Exception as e:
        print(f"Google OAuth error: {e}")
        return None


def resend_verification_email(email: str):
    try:
        supabase.auth.resend({
            "type": "signup",
            "email": email
        })
        return True, "Verification email sent! Check your inbox."
    except Exception as e:
        return False, f"Could not resend email: {str(e)}"


def logout_user():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    for key in ['user', 'logged_in', 'user_id', 'username', 'full_name',
                'user_email', 'current_user', 'show_signup', 'onboarding_done']:
        if key in st.session_state:
            del st.session_state[key]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _apply_user_session(auth_user):
    st.session_state.user       = auth_user
    st.session_state.logged_in  = True
    st.session_state.user_id    = auth_user.id
    st.session_state.user_email = auth_user.email
    try:
        profile = supabase.table('profiles').select('*').eq(
            'id', auth_user.id).execute()
        if profile.data:
            p = profile.data[0]
            st.session_state.full_name = p.get('full_name', '')
            st.session_state.username  = p.get('username', '')
            st.session_state.current_user = {
                'username':     p.get('username', ''),
                'name':         p.get('full_name', ''),
                'email':        auth_user.email,
                'member_since': str(p.get('created_at', ''))[:10]
            }
    except Exception:
        st.session_state.full_name = ''
        st.session_state.username  = ''
        st.session_state.current_user = {
            'username': '', 'name': '', 'email': auth_user.email,
            'member_since': ''
        }


def get_current_user():
    return st.session_state.get('user', None)


def is_logged_in():
    return st.session_state.get('logged_in', False)


# ── Reusable page elements ───────────────────────────────────────────────────

def check_login():
    load_css()
    # Note: theme injection is handled by utils/theme.inject_global_css() on each page
    if not st.session_state.get('logged_in', False):
        st.switch_page("app.py")


def render_header():
    """Minimal top bar — just greeting + dark toggle."""
    name = st.session_state.get('full_name') or 'User'
    dark = st.session_state.get('dark_mode', False)

    from datetime import datetime
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown(f"**{greeting}, {name}**")
    with col2:
        toggle_icon = "☀️" if dark else "🌙"
        if st.button(toggle_icon, key="theme_toggle_btn", help="Toggle theme"):
            st.session_state['dark_mode'] = not dark
            st.rerun()
