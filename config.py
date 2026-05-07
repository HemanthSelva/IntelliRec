import os
from dotenv import load_dotenv
load_dotenv()

_PLACEHOLDERS = {
    "add_your_key_here", "add_your_secret_here",
    "your-anon-key", "your-publishable-key",
    "your-google-client-id", "your-google-client-secret",
    "your-grok-api-key", "your-project.supabase.co",
}

def get_secret(key):
    try:
        import streamlit as st
        val = st.secrets.get(key)
        if val and val not in _PLACEHOLDERS:
            return val
    except Exception:
        pass
    return os.getenv(key)

SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_ANON_KEY = get_secret("SUPABASE_ANON_KEY")
SUPABASE_PUBLISHABLE_KEY = get_secret("SUPABASE_PUBLISHABLE_KEY")
GOOGLE_CLIENT_ID = get_secret("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = get_secret("GOOGLE_CLIENT_SECRET")
GROK_API_KEY = get_secret("GROK_API_KEY")
STREAMLIT_URL = get_secret("STREAMLIT_URL") or "http://localhost:8501"


def get_app_url() -> str:
    """Return the current app's base URL, detected from the live request.

    Preference order:
      1. The HTTP Host header from the active Streamlit request
         (always correct: matches the port/domain the user is actually on,
         so OAuth redirects work whether the dev runs on 8501, 8502, or
         the deployed Streamlit Cloud subdomain).
      2. STREAMLIT_URL from secrets / env (fallback for non-request contexts).
      3. http://localhost:8501.

    Returned without a trailing slash so it can be safely concatenated.
    """
    try:
        import streamlit as st
        host = st.context.headers.get("host", "")
        if host:
            scheme = "https" if "streamlit.app" in host else "http"
            return f"{scheme}://{host}".rstrip("/")
    except Exception:
        pass
    return (STREAMLIT_URL or "http://localhost:8501").rstrip("/")

APP_NAME = "IntelliRec"
APP_VERSION = "2.0.0"
APP_TAGLINE = "Discover What You Love, Before You Know You Want It"
