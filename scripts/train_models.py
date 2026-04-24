"""
scripts/train_models.py
IntelliRec — Full ML Training Pipeline (4-Category Edition)
Sourcesys Technologies Internship Project
Team: Hemanthselva AK, Monish Kaarthi RK, Vishal KS, Vishal M

Run from the project root:
    python scripts/train_models.py

IMPORTANT:
  - Run `python scripts/process_new_categories.py` FIRST to build
    the expanded products_df.pkl before running this script.

Expected runtime: 30–60 minutes depending on data size and hardware.
RTX 5060 (CUDA) will be used automatically for PyTorch ops where applicable.
"""

import sys
import os
import time

# Allow imports from project root regardless of working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from utils.data_loader import (
    load_combined_reviews,
    load_combined_meta,
)
from models.collaborative_filtering import CollaborativeFilteringModel
from models.content_based import ContentBasedModel
from models.sentiment_analyzer import SentimentAnalyzer
from models.hybrid_recommender import HybridRecommender

# ── Directories ────────────────────────────────────────────────────────────────
ROOT_DIR         = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVED_MODELS_DIR = os.path.join(ROOT_DIR, 'saved_models')
os.makedirs(SAVED_MODELS_DIR, exist_ok=True)

BANNER = "=" * 62

def banner(msg):
    print(f"\n{BANNER}")
    print(f"  {msg}")
    print(BANNER)

# ══════════════════════════════════════════════════════════════════════════════
banner("IntelliRec  Model Training Pipeline  (4-Category Edition)")
print("  Sourcesys Technologies — Internship Submission")
print("  Team: Hemanthselva AK | Monish Kaarthi RK | Vishal KS | Vishal M")
print(BANNER)

pipeline_start = time.time()

# ── Step 1: Load datasets ──────────────────────────────────────────────────────
print("\n[1/5] Loading datasets...")
t0 = time.time()

# ── Reviews: load all 4 categories ────────────────────────────────────────────
# The combined loader already includes Clothing & Beauty via data_loader.py
reviews_df = load_combined_reviews(max_rows_each=500_000)

# ── Metadata / products_df ────────────────────────────────────────────────────
# Prefer the pre-built expanded products_df.pkl (from process_new_categories.py)
# because it has smart-sampled 80K per new category.
# Fall back to loading fresh from raw if pkl is missing.
products_pkl = os.path.join(SAVED_MODELS_DIR, 'products_df.pkl')

if os.path.exists(products_pkl):
    print("  Loading pre-built products_df.pkl (expanded dataset)…")
    meta_df = pd.read_pickle(products_pkl)
    print(f"  Products (from pkl): {len(meta_df):,} rows")
    print(f"  Categories: {meta_df['category'].value_counts().to_dict()}")
else:
    print("  products_df.pkl not found — loading fresh from raw files…")
    print("  (Run process_new_categories.py first for best results)")
    meta_df = load_combined_meta(max_rows_each=200_000)

load_time = round(time.time() - t0, 1)

print(f"\n  Reviews  : {len(reviews_df):>10,} rows")
print(f"  Products : {len(meta_df):>10,} rows")
print(f"  Load time: {load_time}s")

if reviews_df.empty:
    print("\n[ERROR] No review data found. Check DATA_DIR path.")
    sys.exit(1)

# ── Step 2: Collaborative Filtering (SVD) ─────────────────────────────────────
print("\n[2/5] Training Collaborative Filtering (SVD)...")

# Sample reviews for SVD to keep RAM + training time manageable.
# With 4 categories and 500K each we could have 2M rows → cap at 1M.
MAX_SVD_ROWS = 1_000_000
if len(reviews_df) > MAX_SVD_ROWS:
    print(f"  Sampling {MAX_SVD_ROWS:,} reviews for SVD (from {len(reviews_df):,} total)…")
    svd_reviews = reviews_df.sample(MAX_SVD_ROWS, random_state=42)
else:
    svd_reviews = reviews_df

cf = CollaborativeFilteringModel()
cf.prepare_data(svd_reviews)
del svd_reviews  # free RAM before heavy SVD training

t1 = time.time()
svd_model, svd_metrics = cf.train_svd(
    n_factors=100,
    n_epochs=20,
    lr_all=0.005,
    reg_all=0.02
)
cf_time = round(time.time() - t1, 2)

print(f"\n  SVD RMSE:        {svd_metrics['RMSE']}")
print(f"  SVD MAE:         {svd_metrics['MAE']}")
print(f"  Training time:   {cf_time}s")
cf.save_model()

# ── Step 3: Content-Based Filtering (TF-IDF) ──────────────────────────────────
print("\n[3/5] Training Content-Based Filtering (TF-IDF)...")
cb = ContentBasedModel()

if meta_df.empty:
    print("  [WARNING] No metadata available — skipping content-based training.")
else:
    # Ensure features_str exists (process_new_categories.py builds it; raw load may not)
    if 'features_str' not in meta_df.columns:
        print("  Building features_str column…")
        cb.prepare_features(meta_df)
    else:
        # features_str already built by process_new_categories.py — assign directly
        cb.products_df = meta_df.copy()

    if cb.products_df is None:
        cb.products_df = meta_df.copy()
    cb.products_df['features_str'] = cb.products_df['features_str'].fillna('')

    t2 = time.time()
    # IMPORTANT: 20K features (down from 50K) keeps memory safe for 560K docs
    cb.train(max_features=20_000)
    cb_time = round(time.time() - t2, 2)
    print(f"  Training time: {cb_time}s")
    cb.save_model()

# ── Step 4: Sentiment Analysis (VADER) ────────────────────────────────────────
print("\n[4/5] Computing Sentiment Scores (VADER)...")
sa = SentimentAnalyzer()

# Use a representative sample to keep RAM under control
text_reviews = reviews_df[reviews_df['text'].notna()]
sample_size  = min(300_000, len(text_reviews))   # raised from 200K → 300K for 4 categories
sample_reviews = text_reviews.sample(sample_size, random_state=42)
del text_reviews  # free RAM

t3 = time.time()
sa.compute_product_sentiments(sample_reviews, sample_per_product=20)
sent_time = round(time.time() - t3, 2)
sa.save_sentiments()

print(f"  Sentiment computed for {len(sa.product_sentiments):,} products  ({sent_time}s)")

# ── Step 5: Hybrid metrics ─────────────────────────────────────────────────────
print("\n[5/5] Computing Hybrid Model Metrics...")
hybrid = HybridRecommender()
hybrid.cf_model        = cf
hybrid.cb_model        = cb
hybrid.sentiment       = sa
hybrid.products_df     = meta_df
hybrid.all_product_ids = meta_df['product_id'].tolist() if not meta_df.empty else []

metrics = hybrid.compute_all_metrics(reviews_df)
hybrid.save_metrics()

# ── Summary ────────────────────────────────────────────────────────────────────
total_time = round(time.time() - pipeline_start, 1)

banner("TRAINING COMPLETE!")
print(f"  Total pipeline time: {total_time}s\n")

col_w = 24
print(f"{'Model':<{col_w}} {'RMSE':>6} {'MAE':>6} "
      f"{'P@10':>6} {'R@10':>6} {'F1':>6}")
print("-" * (col_w + 32))
for model_name, m in metrics.items():
    print(f"{model_name:<{col_w}} "
          f"{m['RMSE']:>6.4f} {m['MAE']:>6.4f} "
          f"{m['Precision@10']:>6.4f} {m['Recall@10']:>6.4f} "
          f"{m['F1']:>6.4f}")

print(f"\nAll models saved to: {SAVED_MODELS_DIR}")
print(f"Products in dataset: {len(meta_df):,}")
if not meta_df.empty:
    for cat, cnt in meta_df['category'].value_counts().items():
        print(f"  {cat:<35} {cnt:>8,}")
print("\nRun the app:  streamlit run app.py")
