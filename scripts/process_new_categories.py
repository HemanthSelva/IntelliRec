"""
scripts/process_new_categories.py
IntelliRec — Safe New-Category Integration Pipeline
Sourcesys Technologies Internship Project
Team: Hemanthselva AK, Monish Kaarthi RK, Vishal KS, Vishal M

Adds Clothing & Shoes and Beauty & Personal Care to the existing processed dataset.

Run from the project root:
    python scripts/process_new_categories.py

Strategy:
  - Loads existing products_df.pkl (Electronics + Home & Kitchen, 400K rows)
  - Processes new metadata in chunks → never loads full raw file into memory
  - Smart-samples 80K per new category (prioritised by review count)
  - Deduplicates by product_id
  - Atomic save: writes to tmp file then renames → no corruption on crash

Expected RAM peak:  ~4–5 GB
Expected runtime:   10–25 minutes
"""

import sys
import os
import time
import gzip
import json
import shutil
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, *args, **kwargs):
        return iterable

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT_DIR         = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR         = os.path.join(ROOT_DIR, 'data')
SAVED_MODELS_DIR = os.path.join(ROOT_DIR, 'saved_models')
os.makedirs(SAVED_MODELS_DIR, exist_ok=True)

BANNER = "=" * 62

def banner(msg):
    print("\n" + BANNER)
    print("  " + msg)
    print(BANNER)

# ── New category definitions ───────────────────────────────────────────────────
NEW_CATEGORIES = [
    {
        "name":        "Clothing & Shoes",
        "meta_file":   "meta_Clothing_Shoes_and_Jewelry.jsonl.gz",
        "review_file": "Clothing_Shoes_and_Jewelry.jsonl.gz",
        "sample_size": 80_000,
    },
    {
        "name":        "Beauty & Personal Care",
        "meta_file":   "meta_Beauty_and_Personal_Care.jsonl.gz",
        "review_file": "Beauty_and_Personal_Care.jsonl.gz",
        "sample_size": 80_000,
    },
]

# Metadata columns to extract (same schema as Electronics / Home & Kitchen)
META_COLS = [
    'parent_asin', 'title', 'price', 'average_rating',
    'rating_number', 'features', 'description',
    'store', 'categories', 'main_category'
]

# Review columns to extract (for SVD review file)
REVIEW_COLS = [
    'user_id', 'parent_asin', 'rating', 'timestamp', 'text', 'title'
]


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def _safe_price(raw) -> float:
    """Robustly convert any Amazon price field to float."""
    if raw is None:
        return np.nan
    try:
        cleaned = str(raw).replace('$', '').replace(',', '').strip()
        if cleaned.lower().startswith('from'):
            cleaned = cleaned[4:].strip()
        val = float(cleaned)
        # Sanity: prices above $50K are almost certainly parsing errors
        return val if 0.0 < val < 50_000 else np.nan
    except (ValueError, TypeError):
        return np.nan


def _normalize_text(text) -> str:
    """Lowercase and strip a text field; handle list types."""
    if isinstance(text, list):
        text = ' '.join(str(t) for t in text[:3])
    if not text or (isinstance(text, float) and np.isnan(text)):
        return ''
    return str(text).lower().strip()


def _create_feature_string(row) -> str:
    """Mirror of ContentBasedModel._create_feature_string for feature columns."""
    parts = []
    if pd.notna(row.get('title')):
        parts.append((str(row['title']) + ' ') * 3)
    if pd.notna(row.get('main_category')):
        parts.append((str(row['main_category']) + ' ') * 2)
    if pd.notna(row.get('category')):
        parts.append(str(row['category']))
    if pd.notna(row.get('store')):
        parts.append(str(row['store']))
    features = row.get('features')
    if features:
        if isinstance(features, list):
            parts.extend([str(f) for f in features[:5]])
        elif pd.notna(features):
            parts.append(str(features))
    description = row.get('description')
    if description:
        if isinstance(description, list):
            parts.append(' '.join(str(d) for d in description[:2]))
        elif pd.notna(description):
            parts.append(str(description)[:300])
    return ' '.join(parts).lower()


# ══════════════════════════════════════════════════════════════════════════════
# Core: chunk-load metadata from a single new category
# ══════════════════════════════════════════════════════════════════════════════

def load_meta_chunked(filepath: str, chunk_size: int = 50_000) -> pd.DataFrame:
    """
    Stream a .jsonl.gz metadata file in fixed chunks.
    Returns a single DataFrame with all extracted rows.
    Keeps only META_COLS to minimise RAM.
    """
    path = os.path.join(DATA_DIR, filepath)
    if not os.path.exists(path):
        print(f"  [ERROR] File not found: {path}")
        return pd.DataFrame()

    chunks = []
    buffer = []
    total  = 0

    print(f"  Streaming: {filepath}")
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        for line in tqdm(f, desc=f"  ↳ Reading chunks", unit=' lines', mininterval=5.0):
            try:
                record = json.loads(line.strip())
                # Extract only the columns we need
                row = {col: record.get(col) for col in META_COLS}
                buffer.append(row)
                total += 1
            except Exception:
                continue

            if len(buffer) >= chunk_size:
                chunks.append(pd.DataFrame(buffer))
                buffer = []

    if buffer:
        chunks.append(pd.DataFrame(buffer))

    if not chunks:
        return pd.DataFrame()

    df = pd.concat(chunks, ignore_index=True)
    print("  -> Raw rows loaded: %d" % len(df))
    return df


def load_reviews_chunked(filepath: str, max_rows: int = 500_000) -> pd.DataFrame:
    """
    Stream a .jsonl.gz reviews file; return DataFrame with REVIEW_COLS.
    Capped at max_rows to keep SVD training manageable.
    """
    path = os.path.join(DATA_DIR, filepath)
    if not os.path.exists(path):
        print(f"  [WARNING] Review file not found: {path}")
        return pd.DataFrame(columns=['user_id', 'product_id', 'rating',
                                     'timestamp', 'text', 'title', 'category'])

    records = []
    print("  Streaming reviews: " + filepath)
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        for i, line in enumerate(tqdm(f, desc="  Reviews", unit=' lines', mininterval=5.0)):
            if i >= max_rows:
                break
            try:
                rec = json.loads(line.strip())
                records.append({col: rec.get(col) for col in REVIEW_COLS})
            except Exception:
                continue

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df = df.rename(columns={'parent_asin': 'product_id'})
    df = df.dropna(subset=['user_id', 'product_id', 'rating'])
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df = df[df['rating'].between(1.0, 5.0)]
    print("  -> Reviews loaded: %d" % len(df))
    return df


# ══════════════════════════════════════════════════════════════════════════════
# Core: clean and sample a metadata DataFrame
# ══════════════════════════════════════════════════════════════════════════════

def clean_and_sample_meta(df: pd.DataFrame,
                           category_name: str,
                           sample_size: int,
                           existing_ids: set) -> pd.DataFrame:
    """
    Clean one new category's metadata DataFrame and return a smart sample.

    Steps:
      1. Rename parent_asin → product_id
      2. Drop null / empty titles
      3. Remove product_ids already in existing dataset
      4. Fill missing prices with category median
      5. Normalize rating columns to numeric
      6. Smart-sample: prioritise by rating_number (review count)
      7. Add category column
      8. Build features_str column (same as ContentBasedModel)
    """
    print("\n  [CLEAN] %s -- %d raw rows" % (category_name, len(df)))

    # 1. Rename
    if 'parent_asin' in df.columns:
        df = df.rename(columns={'parent_asin': 'product_id'})

    # 2. Drop nulls
    df = df.dropna(subset=['product_id', 'title'])
    df = df[df['title'].astype(str).str.strip() != '']
    df = df[df['title'].astype(str).str.lower() != 'nan']
    print(f"     After null-title drop: {len(df):,}")

    # 3. Deduplicate within batch + remove existing
    df = df.drop_duplicates(subset=['product_id'])
    before = len(df)
    df = df[~df['product_id'].isin(existing_ids)]
    print(f"     After dedup vs existing: {len(df):,} (removed {before - len(df):,} dupes)")

    if df.empty:
        print("  [WARNING] No new products after dedup — skipping.")
        return df

    # 4. Price
    df['price'] = df['price'].apply(_safe_price)
    median_price = df['price'].median()
    if np.isnan(median_price):
        median_price = 29.99
    df['price'] = df['price'].fillna(median_price)
    print(f"     Median price: ${median_price:.2f}")

    # 5. Ratings
    df['average_rating'] = pd.to_numeric(df['average_rating'], errors='coerce').fillna(0.0)
    df['rating_number']  = pd.to_numeric(df['rating_number'],  errors='coerce').fillna(0).astype(int)

    # 6. Smart sample: sort by rating_number descending, then sample tail randomly
    actual_size = min(sample_size, len(df))
    if df['rating_number'].sum() > 0:
        # Give top-50% by review count priority, fill rest randomly
        top_n = actual_size // 2
        rest_n = actual_size - top_n
        top_half = df.nlargest(top_n, 'rating_number')
        remaining = df.drop(top_half.index)
        if len(remaining) >= rest_n:
            bottom_half = remaining.sample(rest_n, random_state=42)
        else:
            bottom_half = remaining
        sampled = pd.concat([top_half, bottom_half], ignore_index=True)
    else:
        sampled = df.sample(min(actual_size, len(df)), random_state=42)

    sampled = sampled.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle
    print(f"     Sampled: {len(sampled):,} products")

    # 7. Category tag
    sampled['category'] = category_name

    # 8. features_str (mirrors ContentBasedModel exactly)
    print("     Building features_str...")
    sampled['features_str'] = sampled.apply(_create_feature_string, axis=1)

    return sampled


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    banner("IntelliRec — New Category Integration")
    print("  Adding: Clothing & Shoes  +  Beauty & Personal Care")
    print(BANNER)

    pipeline_start = time.time()

    # ── Step 1: Load existing products_df ─────────────────────────────────────
    banner("Step 1/5  Load Existing products_df")
    existing_path = os.path.join(SAVED_MODELS_DIR, 'products_df.pkl')
    if not os.path.exists(existing_path):
        print("[ERROR] products_df.pkl not found. Run train_models.py first.")
        sys.exit(1)

    print("  Loading existing products_df.pkl…")
    t0 = time.time()
    existing_df = pd.read_pickle(existing_path)
    print(f"  Existing: {len(existing_df):,} rows × {len(existing_df.columns)} cols")
    print(f"  Categories: {existing_df['category'].value_counts().to_dict()}")
    existing_ids = set(existing_df['product_id'].astype(str).tolist())
    print(f"  Existing product IDs: {len(existing_ids):,}")
    print(f"  Loaded in {round(time.time()-t0, 1)}s")

    # ── Step 2: Process each new category ─────────────────────────────────────
    banner("Step 2/5  Process New Category Metadata")
    new_dfs = []
    review_frames = []   # for SVD retraining

    for cat_cfg in NEW_CATEGORIES:
        cat_name  = cat_cfg['name']
        meta_file = cat_cfg['meta_file']
        rev_file  = cat_cfg['review_file']
        n_sample  = cat_cfg['sample_size']

        print("\n" + "-"*50)
        print("  Processing: " + cat_name)
        print("-"*50)

        # Load metadata
        raw_meta = load_meta_chunked(meta_file, chunk_size=50_000)

        if raw_meta.empty:
            print(f"  [SKIP] {cat_name} — no metadata loaded.")
            continue

        # Clean + sample
        cleaned = clean_and_sample_meta(raw_meta, cat_name, n_sample, existing_ids)
        del raw_meta  # free RAM immediately

        if cleaned.empty:
            print(f"  [SKIP] {cat_name} — empty after cleaning.")
            continue

        # Align columns with existing_df exactly
        for col in existing_df.columns:
            if col not in cleaned.columns:
                cleaned[col] = None
        cleaned = cleaned[existing_df.columns]

        new_dfs.append(cleaned)
        print("  [DONE] %s: %d products ready" % (cat_name, len(cleaned)))

        # Load reviews (capped) for SVD training
        print(f"  Loading reviews for SVD…")
        reviews = load_reviews_chunked(rev_file, max_rows=500_000)
        if not reviews.empty:
            reviews['category'] = cat_name
            review_frames.append(reviews)
            print("  [DONE] Reviews for %s: %d rows" % (cat_name, len(reviews)))

    if not new_dfs:
        print("\n[ERROR] No new data was successfully processed. Exiting.")
        sys.exit(1)

    # ── Step 3: Merge with existing dataset ───────────────────────────────────
    banner("Step 3/5  Merge + Deduplicate")
    all_frames = [existing_df] + new_dfs
    final_df   = pd.concat(all_frames, ignore_index=True)
    del existing_df, new_dfs

    before_dedup = len(final_df)
    final_df = final_df.drop_duplicates(subset=['product_id'])
    print(f"  Merged rows:    {before_dedup:,}")
    print(f"  After dedup:    {len(final_df):,}")
    print(f"  Category breakdown:")
    for cat, cnt in final_df['category'].value_counts().items():
        print(f"    {cat:<35} {cnt:>8,}")

    # ── Step 4: Atomic save of products_df.pkl ────────────────────────────────
    banner("Step 4/5  Save Updated products_df.pkl")

    # Backup old file
    backup_path = existing_path.replace('.pkl', '_backup_pre_expansion.pkl')
    if not os.path.exists(backup_path):
        print("  Creating backup: " + os.path.basename(backup_path))
        shutil.copy2(existing_path, backup_path)
        print("  Backup saved [OK]")
    else:
        print("  Backup already exists -- skipping.")

    # Atomic write via tempfile
    print("  Writing updated products_df.pkl (atomic)...")
    t_save = time.time()
    tmp_fd, tmp_path = tempfile.mkstemp(dir=SAVED_MODELS_DIR, suffix='.pkl.tmp')
    os.close(tmp_fd)
    try:
        final_df.to_pickle(tmp_path)
        os.replace(tmp_path, existing_path)
        print("  Saved in %.1fs  (%.2f GB)" % (
            time.time()-t_save,
            os.path.getsize(existing_path)/1024**3))
    except Exception as e:
        os.unlink(tmp_path)
        print(f"  [ERROR] Save failed: {e}")
        sys.exit(1)

    # ── Step 5: Save review DataFrames for SVD retraining ─────────────────────
    banner("Step 5/5  Save New Reviews for SVD Retraining")
    if review_frames:
        combined_new_reviews = pd.concat(review_frames, ignore_index=True)
        del review_frames

        rev_save_path = os.path.join(SAVED_MODELS_DIR, 'new_category_reviews.pkl')
        combined_new_reviews.to_pickle(rev_save_path)
        print(f"  New reviews saved: {len(combined_new_reviews):,} rows")
        print(f"  Path: {rev_save_path}")
    else:
        print("  [WARNING] No review data collected for new categories.")

    # ── Summary ───────────────────────────────────────────────────────────────
    total_time = round(time.time() - pipeline_start, 1)
    banner("NEW CATEGORY PROCESSING COMPLETE!")
    print(f"  Total time: {total_time}s")
    print(f"  products_df: {len(final_df):,} total products")
    print(f"\n  Next steps:")
    print(f"    1. python scripts/train_models.py   ← rebuilds TF-IDF + SVD + sentiments")
    print(BANNER)
