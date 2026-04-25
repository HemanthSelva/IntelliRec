"""
utils/model_loader.py
IntelliRec — Central Model Loading Hub
All saved_models are loaded ONCE via st.cache_resource and shared.
Sourcesys Technologies Internship Project
"""

# NumPy compatibility shim for pkl files trained on numpy 1.x
# Suppresses FutureWarning when assigning deprecated np.bool/int/float/etc.
import warnings as _warnings
try:
    import numpy as _np_shim
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        # These aliases were removed in numpy 2.0 but some older pickled models need them
        if not hasattr(_np_shim, 'bool') or _np_shim.bool is not bool:
            _np_shim.bool = bool
        if not hasattr(_np_shim, 'int') or _np_shim.int is not int:
            _np_shim.int = int
        if not hasattr(_np_shim, 'float') or _np_shim.float is not float:
            _np_shim.float = float
        if not hasattr(_np_shim, 'complex') or _np_shim.complex is not complex:
            _np_shim.complex = complex
        if not hasattr(_np_shim, 'object') or _np_shim.object is not object:
            _np_shim.object = object
        if not hasattr(_np_shim, 'str') or _np_shim.str is not str:
            _np_shim.str = str
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
    Uses huggingface_hub library which correctly handles LFS binary files
    (urllib.request.urlretrieve downloads the LFS pointer text, not the binary).

    IMPORTANT: Must NOT call Streamlit UI functions — runs at import time before
    any Streamlit page context exists. Uses print() for logging instead.
    """
    os.makedirs(MODEL_DIR, exist_ok=True)

    def _is_valid_pkl(path: str) -> bool:
        """Return True if file exists and is larger than 1 KB (not an LFS pointer)."""
        try:
            return os.path.exists(path) and os.path.getsize(path) > 1024
        except Exception:
            return False

    missing = [
        f for f in _REQUIRED
        if not _is_valid_pkl(os.path.join(MODEL_DIR, f))
    ]

    if not missing:
        return True

    print(f"[IntelliRec] Downloading {len(missing)} model file(s) from HuggingFace Hub…")

    # Try huggingface_hub first (handles LFS correctly)
    try:
        from huggingface_hub import hf_hub_download
        for i, filename in enumerate(missing):
            dest = os.path.join(MODEL_DIR, filename)
            try:
                hf_hub_download(
                    repo_id=HF_REPO,
                    filename=filename,
                    local_dir=MODEL_DIR,
                    local_dir_use_symlinks=False,
                )
                size_kb = os.path.getsize(dest) // 1024 if os.path.exists(dest) else 0
                print(f"[IntelliRec] Downloaded ({i+1}/{len(missing)}): {filename} ({size_kb} KB)")
            except Exception as e:
                print(f"[IntelliRec] hf_hub_download failed for {filename}: {e}")
                # Fallback: direct URL with proper accept header for LFS
                _download_direct(filename, dest)
    except ImportError:
        print("[IntelliRec] huggingface_hub not available, using direct download fallback")
        for filename in missing:
            dest = os.path.join(MODEL_DIR, filename)
            _download_direct(filename, dest)

    still_missing = [f for f in _REQUIRED if not _is_valid_pkl(os.path.join(MODEL_DIR, f))]
    if still_missing:
        print(f"[IntelliRec] WARNING: {len(still_missing)} file(s) still missing or invalid: {still_missing}")
        return False

    print("[IntelliRec] All model files ready!")
    return True


def _download_direct(filename: str, dest: str):
    """Direct HTTP download with LFS media-type header as fallback."""
    url = f"{HF_BASE}/{filename}?download=true"
    try:
        req = urllib.request.Request(url, headers={
            "Accept": "application/octet-stream",
            "User-Agent": "IntelliRec/1.0",
        })
        with urllib.request.urlopen(req) as resp, open(dest, 'wb') as out:
            while True:
                chunk = resp.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
        size_kb = os.path.getsize(dest) // 1024
        print(f"[IntelliRec] Direct download OK: {filename} ({size_kb} KB)")
    except Exception as e:
        print(f"[IntelliRec] Direct download also failed for {filename}: {e}")


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
    # NOTE: mmap_mode='r' is NOT used here because all pkl files are compressed
    # (joblib default). mmap_mode is only compatible with uncompressed files.
    return joblib.load(os.path.join(MODEL_DIR, filename))


# ── Cached loaders ─────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def get_svd():
    """Return the trained Surprise SVD model (loaded once)."""
    if not MODELS_READY:
        return None
    filepath = os.path.join(MODEL_DIR, "svd_model.pkl")
    try:
        # joblib without mmap_mode (compressed pkl files are incompatible with mmap)
        model = joblib.load(filepath)
        print(f"[IntelliRec] SVD model loaded OK: {type(model).__name__}")
        return model
    except Exception as e1:
        print(f"[IntelliRec] SVD joblib load failed: {e1}, trying pickle...")
    try:
        import pickle
        with open(filepath, 'rb') as f:
            model = pickle.load(f)
        print(f"[IntelliRec] SVD model loaded via pickle: {type(model).__name__}")
        return model
    except Exception as e2:
        print(f"[IntelliRec] SVD pickle load also failed: {e2}")
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
        print(f"[IntelliRec] TF-IDF loaded OK — matrix shape: {matrix.shape}")
        return vec, matrix, indices
    except Exception as e:
        print(f"[IntelliRec] TF-IDF load error: {e}")
        return None, None, None


@st.cache_data(show_spinner=False)
def get_products_df() -> pd.DataFrame:
    """Return the full product metadata DataFrame with all columns cast to safe types."""
    if not MODELS_READY:
        return pd.DataFrame()
    filepath = os.path.join(MODEL_DIR, "products_df.pkl")
    df = None

    # Try joblib first (no mmap_mode — compressed pkls are incompatible)
    try:
        df = joblib.load(filepath)
    except Exception as e1:
        print(f"[IntelliRec] products_df joblib load failed: {e1}, trying pickle...")

    # Fallback to pickle
    if df is None or not isinstance(df, pd.DataFrame):
        try:
            import pickle
            with open(filepath, 'rb') as f:
                df = pickle.load(f)
        except Exception as e2:
            print(f"[IntelliRec] products_df pickle load also failed: {e2}")
            return pd.DataFrame()

    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame()

    # ── Normalise all column dtypes to plain Python types ────────────────────
    # Covers both legacy 'object' dtype AND pandas nullable StringDtype / BooleanDtype
    try:
        for col in df.columns:
            col_dtype = str(df[col].dtype)
            if col_dtype in ('object', 'string', 'str') or 'String' in col_dtype:
                # Cast nullable StringDtype → regular str; NA → 'nan' then we strip below
                df[col] = df[col].astype(object).fillna('').astype(str)
                # Replace the literal 'nan' string introduced by astype(str) on NA
                df[col] = df[col].replace({'nan': '', '<NA>': ''})
            elif 'boolean' in col_dtype or 'Boolean' in col_dtype:
                df[col] = df[col].astype(object).fillna(False).astype(bool)
    except Exception as _cast_err:
        print(f"[IntelliRec] dtype normalisation warning: {_cast_err}")

    print(f"[IntelliRec] products_df loaded OK — {len(df):,} rows, columns: {list(df.columns)}")
    return df


@st.cache_resource(show_spinner=False)
def get_sentiments() -> dict:
    """Return {product_id: {compound, label, score, review_count}} dict."""
    if not MODELS_READY:
        return {}
    try:
        data = _pkl("product_sentiments.pkl")
        print(f"[IntelliRec] Sentiments loaded OK — {len(data):,} entries")
        return data
    except Exception as e:
        print(f"[IntelliRec] Sentiments load error: {e}")
        return {}


@st.cache_data(show_spinner=False)
def get_metrics() -> dict:
    """Return the model_metrics dict (or fallback dummy)."""
    path = os.path.join(MODEL_DIR, "model_metrics.pkl")
    if os.path.exists(path):
        try:
            return joblib.load(path), True   # (metrics, is_real)
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
    """Safely convert any price value to a float, handling NaN/NA/None/empty."""
    try:
        if raw is None:
            return 0.0
        # Handle pandas NA and numpy nan BEFORE converting to string
        try:
            import math
            if isinstance(raw, float) and math.isnan(raw):
                return 0.0
        except Exception:
            pass
        # Handle pandas NA type
        raw_str = str(raw)
        if raw_str in ('', 'nan', 'NaN', '<NA>', 'None', 'NA'):
            return 0.0
        cleaned = raw_str.replace("$", "").replace(",", "").strip()
        # Handle 'from X.XX' patterns found in Amazon data
        if cleaned.lower().startswith("from"):
            cleaned = cleaned[4:].strip()
        result = float(cleaned)
        # Guard against float('nan') result
        import math
        return result if not math.isnan(result) else 0.0
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
    Falls back to curated sample products when models are unavailable.
    """
    from sklearn.metrics.pairwise import cosine_similarity as cos_sim

    _, tfidf_matrix, product_indices = get_tfidf()
    products   = get_products_df()
    sentiments = get_sentiments()

    if tfidf_matrix is None or products.empty or product_indices is None:
        return _load_fallback_recs(n)

    # Resolve the product's row index in the matrix
    if product_id not in product_indices.index:
        return _load_fallback_recs(n)

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


def _load_fallback_recs(n: int = 12, categories: list = None) -> list:
    """
    Load curated sample products from assets/sample_products.json.
    Used as fallback when ML models are unavailable or still downloading.
    """
    import json
    try:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base, "assets", "sample_products.json")
        with open(path, "r", encoding="utf-8") as f:
            items = json.load(f)
        if categories:
            norm_cats = normalize_categories(categories)
            filtered = [p for p in items if p.get("category") in norm_cats]
            items = filtered if filtered else items
        result = []
        for p in items[:n]:
            card = dict(p)
            card.setdefault("product_id", card.get("asin", ""))
            card.setdefault("asin", card.get("product_id", ""))
            card.setdefault("match_score", 62)
            card.setdefault("predicted_rating", card.get("rating", 3.5))
            card.setdefault("explanation", "Curated pick while AI engine warms up")
            card.setdefault("engine", "Curated")
            card.setdefault("sentiment_label", card.get("sentiment_label", "Mixed"))
            card.setdefault("sentiment_score", card.get("sentiment_score", 0.5))
            card.setdefault("sentiment_compound", 0.0)
            card.setdefault("store", "")
            card.setdefault("is_trending", False)
            card.setdefault("is_bestseller", False)
            result.append(card)
        return result
    except Exception as e:
        print(f"[IntelliRec] Fallback sample load failed: {e}")
        return []


def get_cf_recommendations(user_id: str, n: int = 12,
                            categories: list = None,
                            sample_size: int = 5000) -> list:
    """
    SVD-based top-n recommendations for user_id.
    Samples `sample_size` products to keep latency reasonable.
    Falls back to curated sample products when models are unavailable.
    """
    svd        = get_svd()
    products   = get_products_df()
    sentiments = get_sentiments()

    if svd is None or products.empty:
        return _load_fallback_recs(n, categories)

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
    Falls back to curated sample products when models are unavailable.
    """
    products   = get_products_df()
    sentiments = get_sentiments()

    if products.empty:
        return _load_fallback_recs(n, categories)

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
    fraction of CB results. Falls back to curated sample products
    when ML models are unavailable or still downloading.
    """
    if not MODELS_READY or get_products_df().empty:
        return _load_fallback_recs(n, categories)

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
