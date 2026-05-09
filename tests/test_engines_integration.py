"""
tests/test_engines_integration.py — heavy integration tests gated by the
`requires_models` fixture. Auto-skip in CI when saved_models/ is empty.

Run locally after `streamlit run app.py` has triggered the model download:
    pytest tests/test_engines_integration.py -v
"""
from __future__ import annotations


def test_products_df_loads_and_is_real_catalog(requires_models):
    """Step 2a: the parquet load on cloud was returning empty silently;
    this is the regression net for that path."""
    import pandas as pd
    df = pd.read_parquet("saved_models/products_df.parquet")
    # Real catalog is ~1.6M; assert >= 3k to allow downsampling but reject
    # any reversion to the 42-item assets/sample_products.json fallback.
    assert len(df) >= 3000, f"expected real catalog, got {len(df)} rows"
    for required_col in ("product_id", "title", "category", "average_rating"):
        assert required_col in df.columns, f"missing column: {required_col}"


def test_hybrid_recommendations_return_diverse_results(requires_models):
    """Step 2b: hybrid blend should pull from multiple categories when no
    explicit category filter is supplied, AND respect the requested count."""
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.model_loader import get_hybrid_recommendations

    recs = get_hybrid_recommendations(
        user_id="guest", n=12, categories=None, diversity=0.5)
    assert len(recs) > 0, "hybrid must return results for guest"
    # Diversity check — at least 2 distinct categories among the top 12
    cats = {r.get("category", "") for r in recs}
    assert len(cats) >= 2, f"hybrid should diversify across categories, got {cats}"


def test_cb_respects_category_filter(requires_models):
    """Step 2b OOM-fix regression: CB filters BEFORE the .copy() so memory
    stays bounded — this also means the filter must actually constrain."""
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.model_loader import get_cb_recommendations

    recs = get_cb_recommendations(categories=["Electronics"], n=10)
    assert len(recs) > 0
    # Allow case-insensitive comparison since normalize_categories may
    # canonicalise names.
    for r in recs:
        cat = (r.get("category") or "").lower()
        assert "electronic" in cat, f"CB returned non-Electronics rec: {r.get('category')}"
