"""
tests/conftest.py — shared pytest fixtures.

Strategy: prefer mocking over real Supabase / Streamlit Cloud calls so the
suite runs in <5s in CI without secrets. Tests that genuinely need the
2 GB model artifacts (saved_models/*.pkl + .parquet) are guarded by the
`requires_models` fixture, which auto-skips when artifacts are absent.
"""
from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock

import pytest

# Make the project root importable from anywhere in tests/
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


# ── Streamlit session_state stand-in ─────────────────────────────────────────

class _SessionStateMock(dict):
    """Behaves like st.session_state — supports both dict and attribute access."""

    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError as e:
            raise AttributeError(k) from e

    def __setattr__(self, k, v):
        self[k] = v


@pytest.fixture
def session_state():
    """Fresh dict-like session_state per test."""
    return _SessionStateMock()


@pytest.fixture
def fake_st(monkeypatch, session_state):
    """Patch streamlit.session_state on the imported module."""
    import streamlit as st
    # Streamlit's SessionStateProxy is read-only; replace it on the module.
    monkeypatch.setattr(st, "session_state", session_state, raising=False)
    return st


# ── Supabase client stand-in ─────────────────────────────────────────────────

class _FakeQuery:
    """Records the chain of calls so a test can assert on table()/select()/eq()/upsert()/delete()."""

    def __init__(self, recorder, table_name):
        self.recorder = recorder
        self.table = table_name
        self._data = []

    def select(self, *a, **k):
        self.recorder.append(("select", self.table, a, k))
        return self

    def insert(self, payload, *a, **k):
        self.recorder.append(("insert", self.table, payload, k))
        return self

    def upsert(self, payload, *a, **k):
        self.recorder.append(("upsert", self.table, payload, k))
        return self

    def update(self, payload, *a, **k):
        self.recorder.append(("update", self.table, payload, k))
        return self

    def delete(self, *a, **k):
        self.recorder.append(("delete", self.table, a, k))
        return self

    def eq(self, *a, **k):           return self
    def ilike(self, *a, **k):        return self
    def order(self, *a, **k):        return self
    def execute(self):
        rv = MagicMock()
        rv.data = self._data
        return rv


@pytest.fixture
def fake_supabase():
    """Returns (client_mock, recorder_list).

    recorder_list captures every (op, table, payload, kwargs) tuple so tests
    can assert that e.g. add_to_cart() upserted into 'cart_items' with the
    right shape — without ever hitting the network.
    """
    recorder = []

    class _Client:
        def __init__(self):
            self.auth = MagicMock()
        def table(self, name):
            return _FakeQuery(recorder, name)

    return _Client(), recorder


# ── Model artifact gate ──────────────────────────────────────────────────────

@pytest.fixture
def requires_models():
    """Skip the test when saved_models artifacts are absent (CI-friendly)."""
    needed = ["products_df.parquet", "svd_model.pkl"]
    base = os.path.join(_ROOT, "saved_models")
    missing = [n for n in needed if not os.path.exists(os.path.join(base, n))]
    if missing:
        pytest.skip(f"saved_models missing: {missing} — run streamlit once to download")
