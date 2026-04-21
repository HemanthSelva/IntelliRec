"""
IntelliRec Cart Utility
Stores cart items in st.session_state.cart as a list of dicts.
No payment processing — UI only.
"""
import streamlit as st


def _ensure_cart():
    """Ensure cart list exists in session state."""
    if "cart" not in st.session_state:
        st.session_state["cart"] = []


def add_to_cart(product_id: str, title: str, price: float, category: str = "") -> bool:
    """Add a product to cart. Returns True if added, False if already in cart."""
    _ensure_cart()
    # Check if already in cart
    for item in st.session_state["cart"]:
        if item.get("product_id") == product_id:
            item["qty"] = item.get("qty", 1) + 1
            return False
    st.session_state["cart"].append({
        "product_id": product_id,
        "title": title,
        "price": price,
        "category": category,
        "qty": 1,
    })
    return True


def remove_from_cart(product_id: str):
    """Remove a product from cart by product_id."""
    _ensure_cart()
    st.session_state["cart"] = [
        item for item in st.session_state["cart"]
        if item.get("product_id") != product_id
    ]


def get_cart_items() -> list:
    """Return all items in the cart."""
    _ensure_cart()
    return st.session_state["cart"]


def get_cart_count() -> int:
    """Return total item count (sum of quantities)."""
    _ensure_cart()
    return sum(item.get("qty", 1) for item in st.session_state["cart"])


def get_cart_total() -> float:
    """Return total price of all cart items."""
    _ensure_cart()
    return sum(item.get("price", 0) * item.get("qty", 1)
               for item in st.session_state["cart"])


def clear_cart():
    """Clear all items from cart."""
    st.session_state["cart"] = []


def is_in_cart(product_id: str) -> bool:
    """Check if a product is already in the cart."""
    _ensure_cart()
    return any(item.get("product_id") == product_id
               for item in st.session_state["cart"])
