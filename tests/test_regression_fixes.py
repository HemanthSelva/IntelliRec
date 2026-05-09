"""
tests/test_regression_fixes.py — protects every fix that landed in this
mission cycle. If one of these starts failing, a previous regression has
re-emerged.
"""
from __future__ import annotations

import builtins
import importlib
import sys


# ── 1. SVD: models.mf_gpu must import without torch on cloud ─────────────────

def test_mf_gpu_imports_without_torch(monkeypatch):
    """Step 2b: regression for `name 'nn' is not defined` on Streamlit Cloud.

    The cloud has scikit-surprise installed but not torch. The pickle
    `models.mf_gpu.SurpriseCompatibleMF` must still resolve, which means
    the module must import even when `import torch` raises ImportError.
    """
    real_import = builtins.__import__

    def block_torch(name, *a, **k):
        if name == "torch" or name.startswith("torch."):
            raise ImportError("torch deliberately blocked for test")
        return real_import(name, *a, **k)

    # Force a fresh import of mf_gpu under the no-torch shim
    for mod in list(sys.modules):
        if mod.startswith("models"):
            sys.modules.pop(mod, None)

    monkeypatch.setattr(builtins, "__import__", block_torch)
    m = importlib.import_module("models.mf_gpu")

    assert m.TORCH_AVAILABLE is False
    assert m.SurpriseCompatibleMF is not None
    # The class definition itself must succeed (class body would run nn.Module
    # before the stub fix and raise NameError).
    assert hasattr(m, "_NeuralMF")


# ── 2. config: get_app_url() drops trailing slash + falls back cleanly ───────

def test_get_app_url_no_trailing_slash():
    """Step 3: regression for the trailing-slash 403 on Supabase allowlist."""
    from config import get_app_url
    url = get_app_url()
    assert isinstance(url, str)
    assert not url.endswith("/"), f"redirect URL must not end with '/': got {url!r}"


# ── 3. cart.py: public API surface must remain stable ────────────────────────

def test_cart_public_api():
    """Step 4: utils/topbar.py and pages/06_My_Profile.py call these by name.

    Renaming or removing one would crash the page silently — guard the surface
    so refactors can't drop a function without a test failure.
    """
    from utils import cart
    expected = {
        "add_to_cart", "remove_from_cart", "update_quantity",
        "get_cart_items", "get_cart_count", "get_cart_total",
        "clear_cart", "is_in_cart", "hydrate_cart_from_db",
    }
    actual = {n for n in dir(cart) if not n.startswith("_")}
    missing = expected - actual
    assert not missing, f"cart.py missing public functions: {missing}"


# ── 4. cart.py: guest path must not touch Supabase ───────────────────────────

def test_cart_add_guest_only_writes_session(fake_st, session_state, monkeypatch):
    """Step 4: guest users have no DB row, code must short-circuit before any
    supabase.table(...) call to avoid PGRST errors on every add."""
    session_state["user_id"] = "guest"
    from utils import cart

    # Booby-trap: any access to supabase.table() raises and fails the test.
    boom = lambda *a, **k: (_ for _ in ()).throw(
        AssertionError("guest path must NOT hit Supabase"))
    monkeypatch.setattr(cart, "supabase", type("S", (), {"table": boom})())

    added = cart.add_to_cart("p1", "Widget", 9.99, "Electronics")
    assert added is True
    assert cart.is_in_cart("p1") is True
    assert cart.get_cart_count() == 1
    assert cart.get_cart_total() == 9.99


# ── 5. cart.py: authenticated add upserts the right row shape ────────────────

def test_cart_add_authenticated_upserts(fake_st, session_state, fake_supabase,
                                         monkeypatch):
    """Step 4: the upsert payload must include user_id + product_id +
    quantity + on_conflict so RLS + the unique constraint work."""
    session_state["user_id"] = "user-uuid-123"
    client, recorder = fake_supabase
    from utils import cart
    monkeypatch.setattr(cart, "supabase", client)

    cart.add_to_cart("p42", "Gizmo", 19.95, "Home & Kitchen")

    upserts = [r for r in recorder if r[0] == "upsert" and r[1] == "cart_items"]
    assert len(upserts) == 1, f"expected 1 cart_items upsert, got {recorder}"
    _op, _tbl, payload, kwargs = upserts[0]
    assert payload["user_id"] == "user-uuid-123"
    assert payload["product_id"] == "p42"
    assert payload["quantity"] == 1
    assert payload["product_price"] == 19.95
    assert kwargs.get("on_conflict") == "user_id,product_id"


# ── 6. cart.hydrate_cart_from_db: degrades silently if table missing ─────────

def test_cart_hydrate_handles_missing_table(fake_st, session_state, monkeypatch):
    """Step 4: hydrate must NEVER raise — we wrap login in a try/except, but
    the inner function should also be defensive so a misbehaving Supabase
    response doesn't take down the auth flow."""
    session_state["user_id"] = "user-uuid-999"

    class _ExplodingClient:
        def __init__(self):
            self.auth = None
        def table(self, name):
            raise RuntimeError("table missing / network down")

    from utils import cart
    monkeypatch.setattr(cart, "supabase", _ExplodingClient())

    cart.hydrate_cart_from_db()  # must NOT raise
    assert session_state.get("cart") == []


# ── 7. cart.update_quantity: 0 or negative qty deletes the item ──────────────

def test_cart_update_quantity_zero_removes(fake_st, session_state):
    session_state["user_id"] = "guest"
    from utils import cart
    cart.add_to_cart("p1", "Widget", 9.99)
    assert cart.get_cart_count() == 1

    cart.update_quantity("p1", 0)
    assert cart.is_in_cart("p1") is False
    assert cart.get_cart_count() == 0
