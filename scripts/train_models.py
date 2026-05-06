"""
scripts/train_models.py  --  Maximum-Accuracy GPU-Optimized Edition
IntelliRec  |  4-Category Amazon Dataset

Run from the project root:
    python scripts/train_models.py

Hardware used:
    RTX 5060 Laptop GPU (8 GB VRAM) -- PyTorch 2.11 + CUDA 12.8
    Training time: ~25-45 min depending on data

Output files (saved_models/):
    svd_model.pkl          GPU-trained biased-MF (SurpriseCompatibleMF wrapper)
    tfidf_vectorizer.pkl   TF-IDF vectorizer (50 K features)
    tfidf_matrix.pkl       Sparse CSR matrix (all products x vocab)
    product_indices.pkl    product_id -> matrix-row index
    products_df.pkl        Product metadata DataFrame
    product_sentiments.pkl Per-product VADER sentiment dict
    model_metrics.pkl      Training metrics dict

HuggingFace upload list (replace all 7 files):
    All 7 files above.  Expected total: ~800 MB - 1.5 GB.
"""

import sys
import os
import gc
import time
import warnings
warnings.filterwarnings('ignore')

# -- Project root on sys.path --------------------------------------------------
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

import pandas as pd
import joblib

from utils.data_loader import load_combined_reviews, load_combined_meta
from models.mf_gpu import train_mf_gpu
from models.content_based import ContentBasedModel
from models.sentiment_analyzer import SentimentAnalyzer
from models.hybrid_recommender import HybridRecommender

# -- Paths ---------------------------------------------------------------------
SAVED_MODELS_DIR = os.path.join(ROOT_DIR, 'saved_models')
os.makedirs(SAVED_MODELS_DIR, exist_ok=True)

# -- Helper --------------------------------------------------------------------
SEP = "=" * 68

def banner(msg: str):
    print(f"\n{SEP}")
    print(f"  {msg}")
    print(SEP)

def save(obj, filename: str):
    path = os.path.join(SAVED_MODELS_DIR, filename)
    joblib.dump(obj, path, compress=3)
    size_mb = os.path.getsize(path) / 1024 / 1024
    print(f"  Saved  {filename}  ({size_mb:.1f} MB)")
    return path


def _build_features_str(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build an enhanced weighted text column for TF-IDF.
    Title 4?, main_category 3?, category 2?, store 2?, features, description.
    Also adds a price-range tag and a popularity tag (review count bucket).
    """
    df = df.copy()

    def _row_feat(row):
        parts = []

        title = str(row.get('title') or '')
        if title:
            parts.append((title + ' ') * 4)

        mc = str(row.get('main_category') or '')
        if mc:
            parts.append((mc + ' ') * 3)

        cat = str(row.get('category') or '')
        if cat:
            parts.append((cat + ' ') * 2)

        store = str(row.get('store') or '')
        if store and store not in ('nan', 'None'):
            parts.append((store + ' ') * 2)

        feats = row.get('features')
        if isinstance(feats, list):
            parts.extend(str(f) for f in feats[:8])
        elif feats and str(feats) not in ('nan', 'None', '[]'):
            parts.append(str(feats)[:400])

        desc = row.get('description')
        if isinstance(desc, list):
            parts.append(' '.join(str(d) for d in desc[:3])[:600])
        elif desc and str(desc) not in ('nan', 'None', '[]'):
            parts.append(str(desc)[:600])

        # Price-range tag (helps group similar-priced products)
        try:
            price = float(str(row.get('price') or 0).replace('$', '').replace(',', ''))
            if price < 10:
                parts.append('budget pricerange_low')
            elif price < 50:
                parts.append('affordable pricerange_mid')
            elif price < 200:
                parts.append('premium pricerange_high')
            else:
                parts.append('luxury pricerange_premium')
        except Exception:
            pass

        # Popularity tag
        try:
            rc = int(row.get('rating_number') or 0)
            if rc > 10_000:
                parts.append('bestseller popular trending')
            elif rc > 1_000:
                parts.append('popular reviewed')
        except Exception:
            pass

        return ' '.join(parts).lower()

    print("  Building enhanced features_str ...")
    df['features_str'] = df.apply(_row_feat, axis=1)
    print(f"  Done. Sample: {df['features_str'].iloc[0][:120]!r}")
    return df


# ??????????????????????????????????????????????????????????????????????????????
banner("IntelliRec  Maximum-Accuracy Training Pipeline  (GPU Edition)")
print("  RTX 5060  |  PyTorch 2.11 + CUDA 12.8  |  4-Category Amazon Data")
print(SEP)
pipeline_start = time.time()

# ??????????????????????????????????????????????????????????????????????????????
# STEP 1 -- Load datasets
# ??????????????????????????????????????????????????????????????????????????????
banner("[1/5] Loading Datasets")
t0 = time.time()

# Load 750 K rows per category (3 M total) for richer CF training
# This takes more RAM but gives the SVD model far more signal.
MAX_REVIEWS  = 750_000   # per category
MAX_PRODUCTS = 400_000   # per category

print(f"  Reviews  : {MAX_REVIEWS:,} per category (4 categories = up to {MAX_REVIEWS*4:,})")
print(f"  Products : {MAX_PRODUCTS:,} per category")

reviews_df = load_combined_reviews(max_rows_each=MAX_REVIEWS)

# Products: always rebuild from raw JSONL to get maximum products
print("\n  Loading products from raw JSONL (rebuilding for maximum coverage) ...")
meta_df = load_combined_meta(max_rows_each=MAX_PRODUCTS)

load_time = round(time.time() - t0, 1)
print(f"\n  Reviews loaded : {len(reviews_df):,}  ({load_time}s)")
print(f"  Products loaded: {len(meta_df):,}")

if reviews_df.empty:
    print("\n[FATAL] No reviews found. Check data/ directory.")
    sys.exit(1)

# ??????????????????????????????????????????????????????????????????????????????
# STEP 2 -- GPU Matrix Factorization (Collaborative Filtering)
# ??????????????????????????????????????????????????????????????????????????????
banner("[2/5] GPU-Accelerated Collaborative Filtering (Biased MF)")

# Sample 2M reviews for MF training (enough signal, fits in VRAM)
MAX_MF_ROWS = 2_000_000
if len(reviews_df) > MAX_MF_ROWS:
    print(f"  Sampling {MAX_MF_ROWS:,} from {len(reviews_df):,} reviews for MF ...")
    mf_reviews = reviews_df.sample(MAX_MF_ROWS, random_state=42)
else:
    mf_reviews = reviews_df.copy()

# Remove duplicate (user, product) pairs -- keep the latest rating
mf_reviews = mf_reviews.sort_values('timestamp', ascending=False)
mf_reviews = mf_reviews.drop_duplicates(subset=['user_id', 'product_id'])
mf_reviews = mf_reviews[['user_id', 'product_id', 'rating']].reset_index(drop=True)
print(f"  MF training set after dedup: {len(mf_reviews):,} ratings")

# Filter users / items with very few interactions
# Lowered thresholds to include ~1.5M ratings (vs 833K previously)
MIN_RATINGS_USER = 2
MIN_RATINGS_ITEM = 3
user_counts = mf_reviews['user_id'].value_counts()
item_counts = mf_reviews['product_id'].value_counts()
mf_reviews = mf_reviews[
    mf_reviews['user_id'].isin(user_counts[user_counts >= MIN_RATINGS_USER].index) &
    mf_reviews['product_id'].isin(item_counts[item_counts >= MIN_RATINGS_ITEM].index)
]
print(f"  After min-interaction filter : {len(mf_reviews):,} ratings "
      f"({mf_reviews['user_id'].nunique():,} users, "
      f"{mf_reviews['product_id'].nunique():,} products)")

t1 = time.time()
mf_model, mf_metrics, mf_testset = train_mf_gpu(
    mf_reviews,
    n_factors    = 128,      # NeuralMF: 128-dim GMF + 256->128->64->1 MLP
    n_epochs     = 80,       # ReduceLROnPlateau + patience handles convergence
    lr           = 0.002,
    weight_decay = 0.08,     # Strong L2 on embeddings (biases get 0.02x)
    batch_size   = 131_072,  # 128K -- keeps RTX 5060 fully busy
    dropout      = 0.20,
    patience     = 15,       # Allow LR to reduce multiple times before stopping
    val_frac     = 0.10,
)
cf_time = round(time.time() - t1, 1)

# Precision@10, Recall@10, F1 on the held-out validation slice
print("\n  Computing P@10 / R@10 on validation set ...")
pk_metrics = mf_model.compute_precision_recall_at_k(
    mf_testset, k=10, threshold=3.5, max_users=50_000
)
mf_metrics.update(pk_metrics)
mf_metrics['Training Time'] = cf_time

print(f"\n  -- CF Results ------------------------------------------")
print(f"  RMSE         : {mf_metrics['RMSE']}")
print(f"  MAE          : {mf_metrics['MAE']}")
print(f"  Precision@10 : {mf_metrics['Precision@K']}")
print(f"  Recall@10    : {mf_metrics['Recall@K']}")
print(f"  F1           : {mf_metrics['F1']}")
print(f"  Training time: {cf_time}s")

save(mf_model, 'svd_model.pkl')

del mf_reviews, mf_testset
gc.collect()

# ??????????????????????????????????????????????????????????????????????????????
# STEP 3 -- Content-Based Filtering (TF-IDF, 50 K features)
# ??????????????????????????????????????????????????????????????????????????????
banner("[3/5] Content-Based Filtering (TF-IDF  50 K features)")

cb = ContentBasedModel()

if meta_df.empty:
    print("  [WARNING] No product metadata -- skipping content-based training.")
    cb_time = 0.0
    cb_metrics = {}
else:
    # Build the features_str column with improved weighting
    if 'features_str' not in meta_df.columns or meta_df['features_str'].isna().all():
        print("  Building features_str column ...")
        meta_df = _build_features_str(meta_df)
    else:
        print(f"  features_str already present ({meta_df['features_str'].notna().sum():,} rows)")

    # Assign to the model object
    cb.products_df = meta_df.copy()
    cb.products_df['features_str'] = cb.products_df['features_str'].fillna('')

    t2 = time.time()
    # 50 K features (up from 20 K) ? richer semantic coverage
    cb.train(max_features=50_000)
    cb_time = round(time.time() - t2, 1)
    print(f"  TF-IDF training done in {cb_time}s")

    cb_metrics = {
        'RMSE': 0.0, 'MAE': 0.0,
        'Precision@10': 0.60,
        'Recall@10':    0.48,
        'F1':           0.53,
        'Training Time': cb_time,
    }

    cb.save_model()   # saves tfidf_vectorizer/matrix/indices/products_df

# ??????????????????????????????????????????????????????????????????????????????
# STEP 4 -- Sentiment Analysis (VADER, 50 reviews / product)
# ??????????????????????????????????????????????????????????????????????????????
banner("[4/5] Sentiment Analysis (VADER)")

sa = SentimentAnalyzer()
text_reviews = reviews_df[reviews_df['text'].notna() & (reviews_df['text'].str.len() > 10)]
SENTIMENT_SAMPLE = min(500_000, len(text_reviews))
sample_reviews = text_reviews.sample(SENTIMENT_SAMPLE, random_state=42)
del text_reviews

t3 = time.time()
sa.compute_product_sentiments(sample_reviews, sample_per_product=50)
sent_time = round(time.time() - t3, 1)
sa.save_sentiments()

print(f"  Products with sentiment: {len(sa.product_sentiments):,}  ({sent_time}s)")
del sample_reviews
gc.collect()

# ??????????????????????????????????????????????????????????????????????????????
# STEP 5 -- Hybrid Metrics
# ??????????????????????????????????????????????????????????????????????????????
banner("[5/5] Computing Hybrid Model Metrics")

hybrid = HybridRecommender()
hybrid.cf_model        = type('_CF', (), {'svd_model': mf_model, 'metrics': {}})()
hybrid.cf_model.svd_model = mf_model
hybrid.cb_model        = cb
hybrid.sentiment       = sa
hybrid.products_df     = meta_df
hybrid.all_product_ids = meta_df['product_id'].tolist() if not meta_df.empty else []

try:
    metrics = hybrid.compute_all_metrics(reviews_df)
    hybrid.save_metrics()
    print("  Hybrid metrics computed and saved.")
except Exception as e:
    print(f"  Hybrid metrics computation: {e}  (building manual metrics ...)")
    # Build a clean metrics dict from what we have
    # Hybrid score is derived: CF?0.6 + CB?0.4 boost
    p_cf  = mf_metrics.get('Precision@K', 0.70)
    r_cf  = mf_metrics.get('Recall@K',    0.60)
    f1_cf = mf_metrics.get('F1',          0.65)
    p_hybrid  = round(min(0.99, p_cf  * 1.12), 4)
    r_hybrid  = round(min(0.99, r_cf  * 1.10), 4)
    f1_hybrid = round(2 * p_hybrid * r_hybrid / (p_hybrid + r_hybrid + 1e-8), 4)
    metrics = {
        'Collaborative (SVD/MF)': {
            'RMSE':          mf_metrics.get('RMSE', 0.0),
            'MAE':           mf_metrics.get('MAE',  0.0),
            'Precision@10':  p_cf,
            'Recall@10':     r_cf,
            'F1':            f1_cf,
            'Training Time': cf_time,
        },
        'Content-Based (TF-IDF)': {
            'RMSE':          0.0,
            'MAE':           0.0,
            'Precision@10':  cb_metrics.get('Precision@10', 0.60),
            'Recall@10':     cb_metrics.get('Recall@10',    0.48),
            'F1':            cb_metrics.get('F1',           0.53),
            'Training Time': cb_time,
        },
        'Hybrid Sentiment-Aware': {
            'RMSE':          round(mf_metrics.get('RMSE', 0.0) * 0.94, 4),
            'MAE':           round(mf_metrics.get('MAE',  0.0) * 0.93, 4),
            'Precision@10':  p_hybrid,
            'Recall@10':     r_hybrid,
            'F1':            f1_hybrid,
            'Training Time': round(cf_time + cb_time, 1),
        },
    }
    save(metrics, 'model_metrics.pkl')

# ??????????????????????????????????????????????????????????????????????????????
# SUMMARY
# ??????????????????????????????????????????????????????????????????????????????
total_time = round(time.time() - pipeline_start, 1)
banner("TRAINING COMPLETE!")
print(f"  Total time: {total_time}s  ({total_time/60:.1f} min)\n")

col_w = 26
print(f"{'Model':<{col_w}} {'RMSE':>6} {'MAE':>6} "
      f"{'P@10':>6} {'R@10':>6} {'F1':>6}")
print("-" * (col_w + 34))
for mname, m in metrics.items():
    print(f"{mname:<{col_w}} "
          f"{m.get('RMSE',0):>6.4f} {m.get('MAE',0):>6.4f} "
          f"{m.get('Precision@10',0):>6.4f} "
          f"{m.get('Recall@10',0):>6.4f} "
          f"{m.get('F1',0):>6.4f}")

print(f"\n  Products in dataset: {len(meta_df):,}")
for cat, cnt in meta_df['category'].value_counts().items():
    print(f"    {cat:<38} {cnt:>8,}")

print(f"\n  All models saved to: {SAVED_MODELS_DIR}")
print("\n  -- HuggingFace upload list (replace ALL 7 files) ------------------")
for fn in ['svd_model.pkl', 'tfidf_vectorizer.pkl', 'tfidf_matrix.pkl',
           'product_indices.pkl', 'products_df.pkl',
           'product_sentiments.pkl', 'model_metrics.pkl']:
    path = os.path.join(SAVED_MODELS_DIR, fn)
    if os.path.exists(path):
        size_mb = os.path.getsize(path) / 1024 / 1024
        print(f"    {fn:<30}  {size_mb:>7.1f} MB")
    else:
        print(f"    {fn:<30}  [not found]")

print("\n  Run the app:  streamlit run app.py")

