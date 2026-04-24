"""
database/db_operations.py
All Supabase database read/write helpers for IntelliRec.
Guest users are handled in-memory via st.session_state.
"""

import streamlit as st
from database.supabase_client import supabase


# ── Wishlist ──────────────────────────────────────────────────────────────────

def add_to_wishlist(user_id: str, product_id: str,
                    product_title: str, product_price: float,
                    product_category: str) -> bool:
    """Add a product to the user's wishlist. Returns True on success."""
    if user_id == "guest":
        if 'guest_wishlist' not in st.session_state:
            st.session_state.guest_wishlist = []
        # Avoid duplicates
        existing_ids = [p['product_id'] for p in st.session_state.guest_wishlist]
        if product_id not in existing_ids:
            st.session_state.guest_wishlist.append({
                'product_id':       product_id,
                'product_title':    product_title,
                'product_price':    product_price,
                'product_category': product_category
            })
        return True
    try:
        supabase.table('wishlist').upsert({
            'user_id':          user_id,
            'product_id':       product_id,
            'product_title':    product_title,
            'product_price':    float(product_price) if product_price else 0.0,
            'product_category': product_category
        }).execute()
        return True
    except Exception:
        return False


def remove_from_wishlist(user_id: str, product_id: str) -> bool:
    """Remove a product from the wishlist. Returns True on success."""
    if user_id == "guest":
        if 'guest_wishlist' in st.session_state:
            st.session_state.guest_wishlist = [
                p for p in st.session_state.guest_wishlist
                if p['product_id'] != product_id
            ]
        return True
    try:
        supabase.table('wishlist').delete().eq(
            'user_id', user_id).eq('product_id', product_id).execute()
        return True
    except Exception:
        return False


def get_wishlist(user_id: str) -> list:
    """Return list of wishlist items for the user."""
    if user_id == "guest":
        return st.session_state.get('guest_wishlist', [])
    try:
        response = supabase.table('wishlist').select('*').eq(
            'user_id', user_id).order('added_at', desc=True).execute()
        return response.data or []
    except Exception:
        return []


def is_in_wishlist(user_id: str, product_id: str) -> bool:
    """Check if a product is already in the user's wishlist."""
    wishlist = get_wishlist(user_id)
    return any(p['product_id'] == product_id for p in wishlist)


# ── Recommendation History ────────────────────────────────────────────────────

def save_recommendation(user_id: str, product_id: str,
                        product_title: str, match_score: float,
                        engine_used: str, explanation: str) -> bool:
    """Persist a recommendation event. Guest calls are silently skipped."""
    if user_id == "guest":
        return True
    try:
        supabase.table('recommendation_history').insert({
            'user_id':       user_id,
            'product_id':    product_id,
            'product_title': product_title,
            'match_score':   float(match_score),
            'engine_used':   engine_used,
            'explanation':   explanation
        }).execute()
        return True
    except Exception:
        return False


def get_recommendation_history(user_id: str, limit: int = 50) -> list:
    """Return the user's recommendation history, newest first."""
    if user_id == "guest":
        return []
    try:
        response = supabase.table('recommendation_history').select(
            '*').eq('user_id', user_id).order(
            'created_at', desc=True).limit(limit).execute()
        return response.data or []
    except Exception:
        return []


# ── Feedback ──────────────────────────────────────────────────────────────────

def save_feedback(user_id: str, product_id: str, is_positive: bool) -> bool:
    """Save thumbs-up / thumbs-down feedback. Uses upsert to avoid duplicates."""
    if user_id == "guest":
        return True
    try:
        supabase.table('feedback').upsert({
            'user_id':    user_id,
            'product_id': product_id,
            'is_positive': is_positive
        }).execute()
        return True
    except Exception:
        return False


def get_feedback(user_id: str) -> list:
    """Return all feedback rows for the user."""
    if user_id == "guest":
        return []
    try:
        response = supabase.table('feedback').select('*').eq(
            'user_id', user_id).execute()
        return response.data or []
    except Exception:
        return []


# ── User Profile ──────────────────────────────────────────────────────────────

def get_user_profile(user_id: str) -> dict | None:
    """Fetch the profiles row for a user."""
    if user_id == "guest":
        return {
            'full_name':            'Guest User',
            'username':             'guest_user',
            'preferred_categories': ['Electronics', 'Home & Kitchen'],
            'avatar_color':         '#6C63FF'
        }
    try:
        response = supabase.table('profiles').select('*').eq(
            'id', user_id).execute()
        return response.data[0] if response.data else None
    except Exception:
        return None


def update_user_profile(user_id: str, updates: dict) -> bool:
    """Partial update of the profiles row."""
    if user_id == "guest":
        return True
    try:
        supabase.table('profiles').update(updates).eq('id', user_id).execute()
        return True
    except Exception as e:
        st.error(f"Profile update failed: {e}")
        return False


# ── User Preferences ──────────────────────────────────────────────────────────

def get_user_preferences(user_id: str) -> dict:
    """Return user preferences with sensible defaults."""
    defaults = {
        'preferred_categories': [],
        'min_price':            0,
        'max_price':            10000,
        'min_rating':           1.0,
        'diversity_level':      50,
        'preferred_engine':     'hybrid'
    }
    if user_id == "guest":
        return defaults
    try:
        response = supabase.table('user_preferences').select('*').eq(
            'user_id', user_id).execute()
        if response.data:
            return {**defaults, **response.data[0]}
        return defaults
    except Exception:
        return defaults


def update_user_preferences(user_id: str, prefs: dict) -> bool:
    """Upsert user preferences row."""
    if user_id == "guest":
        return True
    try:
        supabase.table('user_preferences').upsert({
            'user_id': user_id,
            **prefs
        }).execute()
        return True
    except Exception as e:
        st.error(f"Preferences update failed: {e}")
        return False
