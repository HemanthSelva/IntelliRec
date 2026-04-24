import os
from dotenv import load_dotenv
load_dotenv()

def get_secret(key):
    try:
        import streamlit as st
        val = st.secrets.get(key)
        if val:
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

APP_NAME = "IntelliRec"
APP_VERSION = "2.0.0"
APP_TAGLINE = "Discover What You Love, Before You Know You Want It"
