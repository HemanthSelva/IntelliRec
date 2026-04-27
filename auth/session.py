import streamlit as st
from database.supabase_client import supabase

_OAUTH_VERIFIERS = {}


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
[data-testid="stAppViewContainer"]>.main{background:#050d1a!important;}
section[data-testid="stSidebar"]{background:#070f1e!important;border-color:rgba(0,180,255,0.14)!important;}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] label{color:#cce8ff!important;}
[data-testid="stMarkdownContainer"] p{color:#e2eeff!important;}
h1,h2,h3,h4{color:#e2eeff!important;}
.product-card{background:#0d1e35!important;border-color:rgba(0,180,255,0.14)!important;
  box-shadow:0 2px 12px rgba(0,0,0,0.5),0 0 8px rgba(0,180,255,0.06)!important;}
.product-card h4,.product-card p{color:#e2eeff!important;}
[data-testid="stMetricValue"]{color:#e2eeff!important;}
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
    # NOTE: Do NOT call supabase.auth.get_user() here.
    # The Supabase Python client is a module-level singleton shared across ALL
    # concurrent users on Streamlit Cloud. Calling get_user() returns whoever
    # logged in last on the server, not the current browser user, causing
    # one user to land directly in another user's session.
    # Authentication is established only via explicit login actions below.


# ── Auth operations ───────────────────────────────────────────────────────────

def signup_user(email: str, password: str, full_name: str):
    try:
        username = full_name.strip().lower().replace(" ", "_")
        # Layer 1: pre-check profiles table before hitting Supabase sign_up
        try:
            existing = supabase.table('profiles').select('id').eq('email', email.strip()).execute()
            if existing.data:
                return False, "An account with this email already exists. Please sign in instead."
        except Exception:
            pass  # If check fails, let Supabase handle it
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
            # Layer 2: Supabase returns empty identities for already-confirmed accounts
            # instead of throwing an error — catch that here
            if not response.user.identities:
                return False, "An account with this email already exists. Please sign in instead."
            try:
                supabase.table('profiles').insert({
                    'id': response.user.id,
                    'full_name': full_name,
                    'username': username,
                    'email': email,
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
                    st.session_state["pref_cats"] = p.get('preferred_categories', [])
                    st.session_state.current_user = {
                        'username':     p.get('username', ''),
                        'name':         p.get('full_name', ''),
                        'email':        response.user.email,
                        'member_since': str(p.get('created_at', ''))[:10],
                        'preferred_categories': p.get('preferred_categories', []),
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
                            'email': response.user.email,
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
            try:
                chk = supabase.table('profiles').select('id').ilike('email', email.strip()).execute()
                if not chk.data:
                    return False, "NO_ACCOUNT"
                # Account exists but password is wrong (could be a Google-only account)
                return False, "WRONG_PASSWORD"
            except Exception:
                pass
            return False, "Incorrect email or password. Please try again."
        if "too many requests" in error:
            return False, "Too many attempts. Please wait a few minutes and try again."
        return False, f"Login failed: {str(e)}"


def login_with_google():
    # Cache the OAuth URL in session_state so sign_in_with_oauth() is called
    # exactly ONCE per login attempt.  Every call to sign_in_with_oauth()
    # generates a new PKCE code_verifier and overwrites the one stored in the
    # Supabase singleton.  Streamlit rerenders the page many times between the
    # initial redirect and the OAuth callback, so without caching each rerender
    # generates a new verifier, making the final exchange fail with
    # "code challenge does not match previously saved code verifier".
    if st.session_state.get('_google_oauth_url'):
        return st.session_state['_google_oauth_url']
    try:
        from config import STREAMLIT_URL
        base_url = (STREAMLIT_URL or "http://localhost:8501").rstrip("/")
        redirect_url = base_url + "/"
        response = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": redirect_url
            }
        })
        if response.url:
            st.session_state['_google_oauth_url'] = response.url
            # Bridge the PKCE verifier into session_state so it survives the
            # OAuth redirect.  The supabase singleton's SyncMemoryStorage is
            # in-process memory; if the callback lands on a different Streamlit
            # session or Cloud worker the storage dict is empty.  Storing it
            # here lets app.py pass it explicitly to exchange_code_for_session()
            # which accepts params.get("code_verifier") before falling back to
            # storage (supabase_auth/_sync/gotrue_client.py line 1184).
            try:
                verifier = supabase.auth._storage.get_item(
                    f"{supabase.auth._storage_key}-code-verifier"
                )
                if verifier:
                    st.session_state['_pkce_verifier'] = verifier
                    import urllib.parse
                    parsed = urllib.parse.urlparse(response.url)
                    qs = urllib.parse.parse_qs(parsed.query)
                    state = qs.get("state", [None])[0]
                    if state:
                        _OAUTH_VERIFIERS[state] = verifier
            except Exception:
                pass
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


def send_password_reset(email: str):
    try:
        from config import STREAMLIT_URL
        redirect_url = STREAMLIT_URL or "http://localhost:8501"
        if "?" in redirect_url:
            redirect_url += "&reset=1"
        else:
            redirect_url += "?reset=1"

        supabase.auth.reset_password_for_email(
            email,
            options={"redirect_to": redirect_url}
        )
        return True, "Reset link sent! Check your inbox."
    except Exception as e:
        error = str(e).lower()
        if "user not found" in error or "unable to find" in error:
            return False, "No account found with this email."
        return False, f"Could not send reset email: {str(e)}"


def logout_user():
    try:
        supabase.auth.sign_out()
    except Exception as e:
        print(f"Sign out error: {e}")

    # Clear ALL user-related session keys
    keys_to_clear = [
        'logged_in', 'user_id', 'user_email', 'user',
        'full_name', 'username', 'current_user',
        'preferred_categories', 'pref_cats', 'onboarding_done',
        'show_signup', 'welcome_sent', 'is_guest',
        'dark_mode', 'ob_selected_cats', 'ob_style',
        'guest_wishlist', 'profile_photo_b64',
        '_confirm_signout', 'show_email_confirmed',
        'cart', 'notifications', 'selected_engine',
        'selected_categories', 'oauth_error',
        'signup_success_email', 'li_resend_email',
        'current_page',
        'user_bio', '_temp_bio', '_temp_name', '_temp_photo', '_last_uploaded',
        '_google_oauth_url', '_pkce_verifier',
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _apply_user_session(user):
    if not user:
        return
    st.session_state.logged_in  = True
    st.session_state.user_id    = user.id
    st.session_state.user_email = user.email
    st.session_state.user       = user

    try:
        profile = supabase.table('profiles').select(
            '*').eq('id', user.id).execute()

        if profile.data:
            p = profile.data[0]
            st.session_state.full_name = p.get(
                'full_name', 'User')
            st.session_state.username = p.get(
                'username', 'user')
            st.session_state.preferred_categories = p.get(
                'preferred_categories', [])
            st.session_state["pref_cats"] = p.get(
                'preferred_categories', [])
            st.session_state.current_user = {
                'id': user.id,
                'name': p.get('full_name', 'User'),
                'username': p.get('username', 'user'),
                'email': user.email,
                'preferred_categories': p.get(
                    'preferred_categories', []),
                'member_since': str(
                    p.get('created_at', ''))[:10]
            }
        else:
            # Profile missing — create from metadata
            meta = user.user_metadata or {}
            full_name = (
                meta.get('full_name') or
                meta.get('name') or
                user.email.split('@')[0]
            )
            username = full_name.lower().replace(' ', '_')
            st.session_state.full_name = full_name
            st.session_state.username = username
            st.session_state.preferred_categories = []
            st.session_state.current_user = {
                'id': user.id,
                'name': full_name,
                'username': username,
                'email': user.email,
                'preferred_categories': [],
                'member_since': 'Today'
            }
            # Try to create profile
            try:
                supabase.table('profiles').insert({
                    'id': user.id,
                    'full_name': full_name,
                    'username': username,
                    'email': user.email,
                    'preferred_categories': [],
                    'avatar_color': '#6C63FF'
                }).execute()
                supabase.table(
                    'user_preferences').insert({
                    'user_id': user.id,
                    'preferred_categories': [],
                    'preferred_engine': 'hybrid'
                }).execute()
            except Exception as create_err:
                print(f"Profile create error: {create_err}")
    except Exception as fetch_err:
        print(f"Profile fetch error: {fetch_err}")
        meta = user.user_metadata or {}
        st.session_state.full_name = (
            meta.get('full_name') or
            user.email.split('@')[0]
        )
        st.session_state.username = (
            st.session_state.full_name.lower().replace(
                ' ', '_'))


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
