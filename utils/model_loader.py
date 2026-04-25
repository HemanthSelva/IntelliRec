"""
utils/model_loader.py
IntelliRec — Central Model Loading Hub
All saved_models are loaded ONCE via st.cache_resource and shared.
Sourcesys Technologies Internship Project
"""

# NumPy compatibility shim for pkl files trained on numpy 1.x
try:
    import numpy as np
    if not hasattr(np, 'bool'):
        np.bool = bool
    if not hasattr(np, 'int'):
        np.int = int
    if not hasattr(np, 'float'):
        np.float = float
    if not hasattr(np, 'object'):
        np.object = object
    if not hasattr(np, 'str'):
        np.str = str
except Exception:
    pass

from datetime import datetime

import os
import urllib.request
import joblib
import pandas as pd
import streamlit as st
from utils.helpers import normalize_categories

# ── Absolute path to saved_models/ ────────────────────────────────────────────
_BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR  = os.path.join(_BASE_DIR, "saved_models")

# ── HuggingFace Hub auto-download config ──────────────────────────────────────
HF_REPO = "Hemanth1429/intellirec-recommendation-model"
HF_BASE = f"https://huggingface.co/{HF_REPO}/resolve/main"

# Required files that must all exist for live mode
_REQUIRED = [
    "svd_model.pkl",
    "tfidf_vectorizer.pkl",
    "tfidf_matrix.pkl",
    "product_indices.pkl",
    "products_df.pkl",
    "product_sentiments.pkl",
    "model_metrics.pkl",
]


def ensure_models_exist():
    """
    Check for missing model files and auto-download from HuggingFace Hub.
    This enables Streamlit Cloud deployment without bundling large files.

    IMPORTANT: This function must NOT call any Streamlit UI functions (st.info,
    st.progress, st.error, st.success) because it is called at module import time,
    before any Streamlit page context exists. Doing so raises an exception that
    prevents 'MODELS_READY' from being defined, causing ImportError in all pages.
    Uses print() for logging instead.
    """
    os.makedirs(MODEL_DIR, exist_ok=True)

    missing = [
        f for f in _REQUIRED
        if not os.path.exists(os.path.join(MODEL_DIR, f))
    ]

    if not missing:
        return True

    print(f"[IntelliRec] Downloading {len(missing)} model files from HuggingFace…")

    for i, filename in enumerate(missing):
        filepath = os.path.join(MODEL_DIR, filename)
        url = f"{HF_BASE}/{filename}"
        try:
            urllib.request.urlretrieve(url, filepath)
            print(f"[IntelliRec] Downloaded ({i+1}/{len(missing)}): {filename}")
        except Exception as e:
            print(f"[IntelliRec] Failed to download {filename}: {e}")
            return False

    print("[IntelliRec] All model files downloaded successfully!")
    return True


# Attempt auto-download before checking readiness.
# Wrapped in try/except so that ANY failure still allows MODELS_READY to be set.
try:
    ensure_models_exist()
except Exception as _ensure_exc:
    print(f"[IntelliRec] ensure_models_exist() raised: {_ensure_exc}")

MODELS_READY: bool = all(
    os.path.exists(os.path.join(MODEL_DIR, f)) for f in _REQUIRED
)


def _pkl(filename: str):
    """Load a joblib/pickle file from MODEL_DIR."""
    return joblib.load(os.path.join(MODEL_DIR, filename), mmap_mode='r')


# ── Cached loaders ─────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def get_svd():
    """Return the trained Surprise SVD model (loaded once)."""
    if not MODELS_READY:
        return None
    try:
        import pickle
        filepath = os.path.join(MODEL_DIR, "svd_model.pkl")

        # Try joblib first
        try:
            model = joblib.load(filepath, mmap_mode='r')
            return model
        except Exception as e1:
            print(f"SVD joblib load failed: {e1}")

        # Try pickle as fallback
        try:
            with open(filepath, 'rb') as f:
                model = pickle.load(f)
            return model
        except Exception as e2:
            print(f"SVD pickle load failed: {e2}")

        return None

    except Exception as e:
        st.warning(f"SVD load error: {e}")
        return None


@st.cache_resource(show_spinner=False)
def get_tfidf():
    """Return (tfidf_vectorizer, tfidf_matrix, product_indices) tuple."""
    if not MODELS_READY:
        return None, None, None
    try:
        vec     = _pkl("tfidf_vectorizer.pkl")
        matrix  = _pkl("tfidf_matrix.pkl")
        indices = _pkl("product_indices.pkl")
        return vec, matrix, indices
    except Exception as e:
        st.warning(f"TF-IDF load error: {e}")
        return None, None, None


@st.cache_data(show_spinner=False)
def get_products_df() -> pd.DataFrame:
    """Return the full 400K-product metadata DataFrame."""
    if not MODELS_READY:
        return pd.DataFrame()
    try:
        import pickle
        filepath = os.path.join(MODEL_DIR, "products_df.pkl")

        # Try joblib first
        try:
            df = joblib.load(filepath, mmap_mode='r')
            if isinstance(df, pd.DataFrame) and not df.empty:
                # Fix any dtype incompatibilities (StringDtype → str)
                for col in df.select_dtypes(include=['object']).columns:
                    try:
                        df[col] = df[col].astype(str)
                    except Exception:
                        pass
                return df
        except Exception as e1:
            print(f"joblib load failed: {e1}")

        # Try pickle as fallback
        try:
            with open(filepath, 'rb') as f:
                df = pickle.load(f)
            if isinstance(df, pd.DataFrame):
                return df
        except Exception as e2:
            print(f"pickle load failed: {e2}")

        return pd.DataFrame()

    except Exception as e:
        st.warning(f"Products DF load error: {e}")
        return pd.DataFrame()


@st.cache_resource(show_spinner=False)
def get_sentiments() -> dict:
    """Return {product_id: {compound, label, score, review_count}} dict."""
    if not MODELS_READY:
        return {}
    try:
        return _pkl("product_sentiments.pkl")
    except Exception as e:
        st.warning(f"Sentiments load error: {e}")
        return {}


@st.cache_data(show_spinner=False)
def get_metrics() -> dict:
    """Return the model_metrics dict (or fallback dummy)."""
    path = os.path.join(MODEL_DIR, "model_metrics.pkl")
    if os.path.exists(path):
        try:
            return joblib.load(path, mmap_mode='r'), True   # (metrics, is_real)
        except Exception:
            pass
    # Fallback dummy
    return {
        "Collaborative (SVD)": {
            "RMSE": 0.89, "MAE": 0.68,
            "Precision@10": 0.65, "Recall@10": 0.55,
            "F1": 0.59, "Training Time": 12.5
        },
        "Content-Based (TF-IDF)": {
            "RMSE": 0.95, "MAE": 0.73,
            "Precision@10": 0.60, "Recall@10": 0.50,
            "F1": 0.55, "Training Time": 4.2
        },
        "Hybrid Sentiment-Aware": {
            "RMSE": 0.81, "MAE": 0.61,
            "Precision@10": 0.82, "Recall@10": 0.74,
            "F1": 0.78, "Training Time": 18.0
        },
    }, False


# ── Recommendation helpers ─────────────────────────────────────────────────────

def _parse_price(raw) -> float:
    """Safely convert any price value to a float."""
    try:
        if raw is None:
            return 0.0
        cleaned = str(raw).replace("$", "").replace(",", "").strip()
        # Handle 'from X.XX' patterns found in Amazon data
        if cleaned.lower().startswith("from"):
            cleaned = cleaned[4:].strip()
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0


def _row_to_card(row: pd.Series, sentiment: dict) -> dict:
    """Convert a products_df row → UI card dict."""
    return {
        "product_id":   str(row["product_id"]),
        "asin":         str(row["product_id"]),   # alias for legacy UI
        "title":        str(row.get("title") or "Unknown Product"),
        "category":     str(row.get("category") or "Electronics"),
        "price":        _parse_price(row.get("price")),
        "rating":       float(row.get("average_rating") or 0),
        "review_count": int(row.get("rating_number") or 0),
        "store":        str(row.get("store") or ""),
        "sentiment_label": sentiment.get("label", "Mixed"),
        "sentiment_score": sentiment.get("score", 0.5),
        "sentiment_compound": sentiment.get("compound", 0.0),
        "is_trending":  False,
        "is_bestseller": False,
    }


def get_similar_products(product_id: str, n: int = 12) -> list:
    """
    Return n products most similar to the given product_id using
    TF-IDF cosine similarity over the saved model artifacts.
    """
    from sklearn.metrics.pairwise import cosine_similarity as cos_sim

    _, tfidf_matrix, product_indices = get_tfidf()
    products   = get_products_df()
    sentiments = get_sentiments()

    if tfidf_matrix is None or products.empty or product_indices is None:
        return []

    # Resolve the product's row index in the matrix
    if product_id not in product_indices.index:
        return []

    idx = product_indices[product_id]
    # Handle duplicate product_ids → take the first
    if hasattr(idx, '__len__'):
        idx = idx.iloc[0]

    product_vec = tfidf_matrix[idx]
    sim_scores  = cos_sim(product_vec, tfidf_matrix).flatten()

    # Get top (n+1) and drop self
    top_indices = sim_scores.argsort()[::-1][1:n + 1]

    results = []
    for i in top_indices:
        if i >= len(products):
            continue
        row = products.iloc[i]
        pid = str(row["product_id"])
        card = _row_to_card(row, sentiments.get(pid, {}))
        card["match_score"]      = min(99, max(1, int(sim_scores[i] * 100)))
        card["predicted_rating"] = float(row.get("average_rating") or 0)
        card["explanation"]      = "Similar to the product you selected"
        card["engine"]           = "Content-Based (Similar)"
        results.append(card)

    return results


def get_cf_recommendations(user_id: str, n: int = 12,
                            categories: list = None,
                            sample_size: int = 5000) -> list:
    """
    SVD-based top-n recommendations for user_id.
    Samples `sample_size` products to keep latency reasonable.
    """
    svd        = get_svd()
    products   = get_products_df()
    sentiments = get_sentiments()

    if svd is None or products.empty:
        return []

    df = products.copy()
    if categories:
        categories = normalize_categories(categories)
        df = df[df["category"].isin(categories)]
    if df.empty:
        return []

    sample = df.sample(min(sample_size, len(df)), random_state=42)

    preds = []
    for _, row in sample.iterrows():
        pid = row["product_id"]
        try:
            est = svd.predict(str(user_id), str(pid)).est
        except Exception:
            est = 3.0
        preds.append((pid, est))

    preds.sort(key=lambda x: x[1], reverse=True)

    results = []
    for pid, est in preds[:n]:
        rows = products[products["product_id"] == pid]
        if rows.empty:
            continue
        card = _row_to_card(rows.iloc[0], sentiments.get(pid, {}))
        card["match_score"]      = min(99, int(round(est / 5.0 * 100)))
        card["predicted_rating"] = round(est, 2)
        card["explanation"]      = "Because users like you loved this"
        card["engine"]           = "Collaborative Filtering"
        results.append(card)

    return results


def get_cb_recommendations(categories: list = None, n: int = 12) -> list:
    """
    Content-based: top-rated products from given categories.
    Uses products_df directly (no cosine similarity needed for category recs).
    """
    products   = get_products_df()
    sentiments = get_sentiments()

    if products.empty:
        return []

    df = products.copy()
    df["average_rating"] = pd.to_numeric(df["average_rating"], errors="coerce").fillna(0)

    if categories:
        categories = normalize_categories(categories)
        df = df[df["category"].isin(categories)]
    if df.empty:
        return []

    # Require at least some reviews; sort by rating descending
    df = df[df["rating_number"].fillna(0).astype(float) > 0]
    df = df.nlargest(n * 3, "average_rating")

    results = []
    for _, row in df.head(n).iterrows():
        pid  = row["product_id"]
        card = _row_to_card(row, sentiments.get(pid, {}))
        card["match_score"]      = min(99, int(round(float(row["average_rating"]) / 5.0 * 100)))
        card["predicted_rating"] = float(row["average_rating"])
        cat_label = (categories or ["Electronics"])[0]
        card["explanation"]      = f"Matches your {cat_label} interest"
        card["engine"]           = "Content-Based"
        results.append(card)

    return results


def _time_context_boost(category: str) -> int:
    """Return a small score nudge (+3) when category matches time-of-day affinity."""
    try:
        _AFFINITY = {
            "morning":    ["Electronics", "Books", "Sports"],
            "afternoon":  ["Electronics", "Home & Kitchen", "Clothing & Shoes"],
            "evening":    ["Home & Kitchen", "Beauty & Personal Care", "Books"],
            "night":      ["Beauty & Personal Care", "Home & Kitchen"],
            "late_night": ["Electronics", "Books"],
        }
        h = datetime.now().hour
        if h < 6:    ctx = "late_night"
        elif h < 12: ctx = "morning"
        elif h < 17: ctx = "afternoon"
        elif h < 21: ctx = "evening"
        else:        ctx = "night"
        return 3 if category in _AFFINITY.get(ctx, []) else 0
    except Exception:
        return 0


def get_hybrid_recommendations(user_id: str, n: int = 12,
                                categories: list = None,
                                diversity: float = 0.3) -> list:
    """
    Hybrid: blend CF + CB with sentiment boosting, category boost,
    time-context nudge, and user feedback loop. diversity controls
    fraction of CB results.
    """
    sentiments = get_sentiments()

    # Read user preferred categories from session state (set via onboarding/profile)
    try:
        import streamlit as st
        pref_cats = normalize_categories(
            st.session_state.get("pref_cats") or []
        )
    except Exception:
        pref_cats = []

    # ── Read user feedback from session state ─────────────────────────────
    try:
        import streamlit as st
        from collections import Counter
        disliked_pids       = st.session_state.get("disliked_pids", set())
        liked_pids          = st.session_state.get("liked_pids", set())
        liked_cats_list     = st.session_state.get("liked_cats_feedback", [])
        disliked_cats_list  = st.session_state.get("disliked_cats_feedback", [])
        saved_cats_list     = st.session_state.get("saved_cats", [])
        # Count how many times each category was liked/disliked/saved (stronger signal = more clicks)
        liked_cat_counts    = Counter(liked_cats_list)
        disliked_cat_counts = Counter(disliked_cats_list)
        saved_cat_counts    = Counter(saved_cats_list)
    except Exception:
        disliked_pids = set()
        liked_pids = set()
        liked_cat_counts = {}
        disliked_cat_counts = {}
        saved_cat_counts = {}

    cf_n = max(1, int(n * (1 - diversity)))
    cb_n = max(1, n - cf_n)

    cf_recs = get_cf_recommendations(user_id, n=cf_n,
                                      categories=normalize_categories(categories) if categories else categories)
    cb_recs = get_cb_recommendations(categories=normalize_categories(categories) if categories else categories,
                                     n=cb_n)

    # Deduplicate by product_id
    seen   = {r["product_id"] for r in cf_recs}
    merged = cf_recs + [r for r in cb_recs if r["product_id"] not in seen]

    # ── Filter out explicitly disliked products ───────────────────────────
    if disliked_pids:
        merged = [r for r in merged if r["product_id"] not in disliked_pids]

    # Boost pipeline (applied in order, all non-destructive)
    for rec in merged:
        pid        = rec["product_id"]
        sent_score = sentiments.get(pid, {}).get("score", 0.5)
        base       = rec["match_score"]

        # 1. Sentiment boost: 0.8×base + 0.2×sentiment_score×100
        boosted = int(base * 0.8 + sent_score * 20)

        # 2. Category boost: +5 if in user preferred categories
        if pref_cats and rec.get("category") in pref_cats:
            boosted += 5

        # 3. Time-context nudge: +3 if category fits time of day
        boosted += _time_context_boost(rec.get("category", ""))

        # 4. Feedback boost: liked categories get +8 per vote, capped at +20
        cat = rec.get("category", "")
        if cat in liked_cat_counts:
            boosted += min(20, liked_cat_counts[cat] * 8)

        # 5. Feedback penalty: disliked categories get -12 per vote, capped at -30
        if cat in disliked_cat_counts:
            boosted -= min(30, disliked_cat_counts[cat] * 12)

        # 6. Specific liked product bonus: +10 if user explicitly liked this one
        if pid in liked_pids:
            boosted += 10

        # 7. Wishlist signal: saved categories get +4 per save, capped at +12
        if cat in saved_cat_counts:
            boosted += min(12, saved_cat_counts[cat] * 4)

        rec["match_score"]     = min(99, max(1, boosted))
        rec["engine"]          = "Hybrid"
        rec["sentiment_label"] = sentiments.get(pid, {}).get("label", "Mixed")
        rec["sentiment_score"] = sent_score

    merged.sort(key=lambda x: x["match_score"], reverse=True)
    return merged[:n]


def get_trending(n: int = 20) -> pd.DataFrame:
    """
    Trending: products sorted by a trend_score = 40% rating + 60% review_count.
    Returns a DataFrame compatible with 04_Trending.py display code.
    """
    products   = get_products_df()
    sentiments = get_sentiments()

    if products.empty:
        return pd.DataFrame()

    df = products.copy()
    df["average_rating"]  = pd.to_numeric(df["average_rating"],  errors="coerce").fillna(0)
    df["rating_number"]   = pd.to_numeric(df["rating_number"],   errors="coerce").fillna(0)

    # Only products with meaningful review counts
    df = df[df["rating_number"] >= 50].copy()
    if df.empty:
        df = products.copy()
        df["average_rating"] = pd.to_numeric(df["average_rating"], errors="coerce").fillna(0)
        df["rating_number"]  = pd.to_numeric(df["rating_number"],  errors="coerce").fillna(0)

    max_reviews = df["rating_number"].max() or 1
    df["trend_score"] = (
        df["average_rating"] * 0.4 +
        (df["rating_number"] / max_reviews) * 0.6
    )

    # Add sentiment + price columns for Trending page charts
    df["price"]           = df["price"].apply(_parse_price)
    df["sentiment_label"] = df["product_id"].map(
        lambda pid: sentiments.get(pid, {}).get("label", "Mixed")
    )
    df["sentiment_score"] = df["product_id"].map(
        lambda pid: sentiments.get(pid, {}).get("score", 0.5)
    )
    df["review_count"]    = df["rating_number"]
    df["rating"]          = df["average_rating"]
    df["asin"]            = df["product_id"]
    df["is_trending"]     = True
    df["is_bestseller"]   = False

    return df.nlargest(n, "trend_score").reset_index(drop=True)
