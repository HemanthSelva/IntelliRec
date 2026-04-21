"""
IntelliRec Notification System v2
Supports in-app smart suggestions, price alerts, achievements, and system messages.
Future-ready: notification_channel field for Supabase email/SMS integration.
"""

import streamlit as st
from datetime import datetime, timedelta
import random


# ── Notification type registry ─────────────────────────────────────────────────
TYPES = {"success", "info", "warning", "error",
         "suggestion", "price_alert", "achievement", "system"}


def _init():
    if "notifications" not in st.session_state:
        st.session_state["notifications"] = []
    if "_notif_suggestions_sent" not in st.session_state:
        st.session_state["_notif_suggestions_sent"] = False


def add_notification(type_: str, title: str, message: str,
                     channel: str = "in_app"):
    """
    Add a notification.
    channel: 'in_app' | 'email' | 'sms'  (email/sms reserved for Supabase integration)
    """
    _init()
    nid = len(st.session_state["notifications"])
    st.session_state["notifications"].append({
        "id":        nid,
        "type":      type_ if type_ in TYPES else "info",
        "title":     title,
        "message":   message,
        "timestamp": datetime.now(),
        "read":      False,
        "channel":   channel,
    })


def get_unread_count() -> int:
    _init()
    return sum(1 for n in st.session_state["notifications"] if not n["read"])


def mark_all_read():
    _init()
    for n in st.session_state["notifications"]:
        n["read"] = True


def mark_read(nid: int):
    _init()
    for n in st.session_state["notifications"]:
        if n["id"] == nid:
            n["read"] = True


def delete_notification(nid: int):
    _init()
    st.session_state["notifications"] = [
        n for n in st.session_state["notifications"] if n["id"] != nid
    ]


def clear_all():
    _init()
    st.session_state["notifications"] = []


def get_recent(n: int = 5) -> list:
    _init()
    return sorted(
        st.session_state["notifications"],
        key=lambda x: x["timestamp"],
        reverse=True,
    )[:n]


def get_all() -> list:
    _init()
    return sorted(
        st.session_state["notifications"],
        key=lambda x: x["timestamp"],
        reverse=True,
    )


# ── Smart Suggestion Engine ────────────────────────────────────────────────────

_SUGGESTION_POOL = [
    # Wishlist-based
    ("suggestion", "Trending in Your Wishlist",
     "Products you saved are climbing in popularity — check what's hot!"),
    ("suggestion", "Similar to Your Saved Items",
     "We found 8 products matching your wishlist interests."),
    # Category suggestions
    ("suggestion", "New in Electronics",
     "14 new top-rated products dropped in Electronics this week."),
    ("suggestion", "Home & Kitchen Deals",
     "Your most browsed category has items on sale this week."),
    # Engine tips
    ("system", "Try the Hybrid Engine",
     "Switch to Hybrid mode in For You to get 23% better match scores."),
    ("system", "AI Model Improved",
     "Your recommendation engine just improved based on your recent feedback."),
    # Achievements
    ("achievement", "🏆 First Recommendation!",
     "You've received your first AI recommendation. Keep exploring!"),
    ("achievement", "❤️ Wishlist Growing",
     "You saved 5+ products! Your AI profile is getting more accurate."),
    # Price alerts (simulated)
    ("price_alert", "Price Drop Alert",
     "Sony WH-1000XM5 dropped from $349 → $279. Your saved item!"),
    ("price_alert", "Limited Time Deal",
     "Instant Pot Duo is 30% off for the next 24 hours."),
    # Weekly digest
    ("info", "📈 Your Weekly Digest",
     "This week: 12 recommendations, 3 wishlisted, 2 ratings given."),
    ("info", "🎯 Personalization Update",
     "Your AI profile was updated based on your browsing patterns."),
]

_WELCOME_TIPS = [
    ("info", "👋 Welcome to IntelliRec",
     "Tip: Use the For You page to get AI-powered recommendations tailored to you."),
    ("system", "🔍 Explore the Catalogue",
     "Over 1.4M products across 6 categories. Use Explore to browse."),
    ("suggestion", "⭐ Rate Products You See",
     "Giving thumbs up/down trains your personal AI model for better picks."),
]


def generate_smart_suggestions():
    """
    Generates contextual smart notifications once per session.
    Called on every sidebar render; only fires once per login session.
    """
    _init()
    if st.session_state.get("_notif_suggestions_sent"):
        return

    # Welcome tip (always first)
    tip = random.choice(_WELCOME_TIPS)
    add_notification(*tip)

    # 2 random suggestions
    picks = random.sample(_SUGGESTION_POOL, min(2, len(_SUGGESTION_POOL)))
    for p in picks:
        add_notification(*p)

    st.session_state["_notif_suggestions_sent"] = True


# ── Time Formatter ─────────────────────────────────────────────────────────────

def time_ago(dt) -> str:
    """Return human-readable time-ago string."""
    if not isinstance(dt, datetime):
        return "Just now"
    delta = datetime.now() - dt
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        mins = seconds // 60
        return f"{mins}m ago"
    elif seconds < 86400:
        hrs = seconds // 3600
        return f"{hrs}h ago"
    elif seconds < 172800:
        return "Yesterday"
    else:
        days = seconds // 86400
        return f"{days}d ago"
