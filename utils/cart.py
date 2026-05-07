"""
utils/cart.py — IntelliRec cart helpers

Persists to public.cart_items in Supabase for authenticated users; falls
back to st.session_state for guests.  Public function signatures match
the original session-only API so existing callers in utils/topbar.py and
pages/06_My_Profile.py don't change.

session_state["cart"] is kept as the single source of truth for the
current render — Supabase is the durable backing store, and we mirror
writes both ways so reads stay fast.

Run migrations/2026_05_07_cart_items_and_rls.sql in Supabase SQL Editor
before this code is exercised by an authenticated user.
"""
from __future__ import annotations

from typing import Any

import streamlit as st

from database.supabase_client import supabase


# ── Session-state primitives ─────────────────────────────────────────────────

def _ensure_cart() -> None:
    if "cart" not in st.session_state:
        st.session_state["cart"] = []


def _is_guest() -> bool:
    """True for anonymous browsing (no logged-in user)."""
    uid = st.session_state.get("user_id")
    return not uid or uid == "guest"


def _user_id() -> str | None:
    return st.session_state.get("user_id")


# ── Hydration ────────────────────────────────────────────────────────────────

def hydrate_cart_from_db() -> None:
    """Load the user's saved cart from Supabase into session_state.

    Called from auth.session._apply_user_session() right after login.
    Idempotent: clears any guest cart first so we don't merge an
    anonymous browsing session into a logged-in user's saved cart.
    """
    if _is_guest():
        return
    try:
        rows = supabase.table("cart_items").select(
            "product_id, product_title, product_price, product_category, quantity"
        ).eq("user_id", _user_id()).order("added_at", desc=True).execute()

        st.session_state["cart"] = [
            {
                "product_id":  r.get("product_id"),
                "title":       r.get("product_title") or "",
                "price":       float(r.get("product_price") or 0.0),
                "category":    r.get("product_category") or "",
                "qty":         int(r.get("quantity") or 1),
            }
            for r in (rows.data or [])
        ]
    except Exception as e:
        # Don't break login if the table is missing or RLS rejects —
        # surface in logs and fall back to an empty session cart.
        print(f"[cart] hydrate_cart_from_db failed: {e}")
        st.session_state["cart"] = []


# ── Public API (unchanged signatures) ────────────────────────────────────────

def add_to_cart(product_id: str, title: str, price: float,
                category: str = "") -> bool:
    """Add a product to cart. Returns True if newly added, False if it was
    already there (in which case quantity is incremented)."""
    _ensure_cart()
    cart = st.session_state["cart"]

    # Update or insert in session_state
    new_qty = 1
    found = False
    for item in cart:
        if item.get("product_id") == product_id:
            item["qty"] = item.get("qty", 1) + 1
            new_qty = item["qty"]
            found = True
            break
    if not found:
        cart.append({
            "product_id": product_id,
            "title":      title,
            "price":      float(price) if price else 0.0,
            "category":   category,
            "qty":        1,
        })

    # Mirror to Supabase for authenticated users
    if not _is_guest():
        try:
            supabase.table("cart_items").upsert({
                "user_id":          _user_id(),
                "product_id":       product_id,
                "product_title":    title,
                "product_price":    float(price) if price else 0.0,
                "product_category": category,
                "quantity":         new_qty,
            }, on_conflict="user_id,product_id").execute()
        except Exception as e:
            print(f"[cart] add_to_cart upsert failed: {e}")

    return not found


def remove_from_cart(product_id: str) -> None:
    """Remove a product from cart by product_id."""
    _ensure_cart()
    st.session_state["cart"] = [
        item for item in st.session_state["cart"]
        if item.get("product_id") != product_id
    ]
    if not _is_guest():
        try:
            supabase.table("cart_items").delete().eq(
                "user_id", _user_id()).eq("product_id", product_id).execute()
        except Exception as e:
            print(f"[cart] remove_from_cart failed: {e}")


def update_quantity(product_id: str, qty: int) -> None:
    """Set the quantity for a product. qty <= 0 removes the item."""
    if qty <= 0:
        remove_from_cart(product_id)
        return
    _ensure_cart()
    found = False
    for item in st.session_state["cart"]:
        if item.get("product_id") == product_id:
            item["qty"] = int(qty)
            found = True
            break
    if not found:
        return  # nothing to update locally
    if not _is_guest():
        try:
            supabase.table("cart_items").update({
                "quantity": int(qty),
            }).eq("user_id", _user_id()).eq("product_id", product_id).execute()
        except Exception as e:
            print(f"[cart] update_quantity failed: {e}")


def get_cart_items() -> list[dict[str, Any]]:
    """Return all items in the cart."""
    _ensure_cart()
    return st.session_state["cart"]


def get_cart_count() -> int:
    """Total item count (sum of quantities)."""
    _ensure_cart()
    return sum(item.get("qty", 1) for item in st.session_state["cart"])


def get_cart_total() -> float:
    """Total price of all cart items."""
    _ensure_cart()
    return sum(
        float(item.get("price") or 0) * int(item.get("qty", 1))
        for item in st.session_state["cart"]
    )


def clear_cart() -> None:
    """Remove all items from the cart."""
    st.session_state["cart"] = []
    if not _is_guest():
        try:
            supabase.table("cart_items").delete().eq(
                "user_id", _user_id()).execute()
        except Exception as e:
            print(f"[cart] clear_cart failed: {e}")


def is_in_cart(product_id: str) -> bool:
    """Check if a product is already in the cart."""
    _ensure_cart()
    return any(item.get("product_id") == product_id
               for item in st.session_state["cart"])
