"""
scripts/resume_from_beauty.py
Recovery script: Clothing metadata was already sampled (80K).
This script:
  1. Loads Clothing reviews (500K cap)
  2. Loads + samples Beauty metadata (80K)
  3. Loads Beauty reviews (500K cap)
  4. Loads BOTH: existing products_df.pkl (400K) + clothing_partial.pkl if exists
  5. Merges everything → 560K
  6. Atomically saves products_df.pkl
  7. Saves new_category_reviews.pkl
"""
import sys, os, time, gzip, json, shutil, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
import numpy as np
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, *args, **kwargs):
        return iterable

ROOT_DIR         = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR         = os.path.join(ROOT_DIR, 'data')
SAVED_MODELS_DIR = os.path.join(ROOT_DIR, 'saved_models')
BANNER = "=" * 62

def banner(msg):
    print("\n" + BANNER)
    print("  " + msg)
    print(BANNER)

META_COLS = [
    'parent_asin', 'title', 'price', 'average_rating',
    'rating_number', 'features', 'description',
    'store', 'categories', 'main_category'
]
REVIEW_COLS = ['user_id', 'parent_asin', 'rating', 'timestamp', 'text', 'title']

def _safe_price(raw):
    if raw is None:
        return np.nan
    try:
        cleaned = str(raw).replace('$','').replace(',','').strip()
        if cleaned.lower().startswith('from'):
            cleaned = cleaned[4:].strip()
        val = float(cleaned)
        return val if 0.0 < val < 50_000 else np.nan
    except (ValueError, TypeError):
        return np.nan

def _create_feature_string(row):
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

def load_meta_chunked(filepath, chunk_size=50_000):
    path = os.path.join(DATA_DIR, filepath)
    if not os.path.exists(path):
        print("  [ERROR] File not found: " + path)
        return pd.DataFrame()
    chunks, buffer = [], []
    print("  Streaming: " + filepath)
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        for line in tqdm(f, desc="  Loading", unit=' lines', mininterval=5.0):
            try:
                record = json.loads(line.strip())
                row = {col: record.get(col) for col in META_COLS}
                buffer.append(row)
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

def load_reviews_chunked(filepath, max_rows=500_000):
    path = os.path.join(DATA_DIR, filepath)
    if not os.path.exists(path):
        print("  [WARNING] Not found: " + path)
        return pd.DataFrame()
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

def clean_and_sample(df, category_name, sample_size, existing_ids, ref_columns):
    print("\n  [CLEAN] %s -- %d raw rows" % (category_name, len(df)))
    if 'parent_asin' in df.columns:
        df = df.rename(columns={'parent_asin': 'product_id'})
    df = df.dropna(subset=['product_id', 'title'])
    df = df[df['title'].astype(str).str.strip() != '']
    df = df[df['title'].astype(str).str.lower() != 'nan']
    df = df.drop_duplicates(subset=['product_id'])
    before = len(df)
    df = df[~df['product_id'].isin(existing_ids)]
    print("     After dedup: %d (removed %d)" % (len(df), before - len(df)))
    if df.empty:
        return df
    df['price'] = df['price'].apply(_safe_price)
    median_price = df['price'].median()
    if np.isnan(median_price):
        median_price = 29.99
    df['price'] = df['price'].fillna(median_price)
    df['average_rating'] = pd.to_numeric(df['average_rating'], errors='coerce').fillna(0.0)
    df['rating_number']  = pd.to_numeric(df['rating_number'],  errors='coerce').fillna(0).astype(int)
    actual_size = min(sample_size, len(df))
    if df['rating_number'].sum() > 0:
        top_n   = actual_size // 2
        rest_n  = actual_size - top_n
        top     = df.nlargest(top_n, 'rating_number')
        rest_df = df.drop(top.index)
        bottom  = rest_df.sample(min(rest_n, len(rest_df)), random_state=42)
        sampled = pd.concat([top, bottom], ignore_index=True)
    else:
        sampled = df.sample(actual_size, random_state=42)
    sampled = sampled.sample(frac=1, random_state=42).reset_index(drop=True)
    print("     Sampled: %d products" % len(sampled))
    sampled['category'] = category_name
    print("     Building features_str...")
    sampled['features_str'] = sampled.apply(_create_feature_string, axis=1)
    for col in ref_columns:
        if col not in sampled.columns:
            sampled[col] = None
    sampled = sampled[ref_columns]
    return sampled

# ============================================================
if __name__ == '__main__':
    banner("IntelliRec -- Resume from Beauty")
    t_start = time.time()

    # 1. Load existing products_df (400K)
    banner("1/6  Load Existing products_df")
    existing_path = os.path.join(SAVED_MODELS_DIR, 'products_df.pkl')
    existing_df = pd.read_pickle(existing_path)
    print("  Existing: %d rows" % len(existing_df))
    print("  Categories: %s" % existing_df['category'].value_counts().to_dict())
    existing_ids = set(existing_df['product_id'].astype(str).tolist())
    ref_cols = list(existing_df.columns)

    # 2. Process Clothing metadata → 80K
    banner("2/6  Process Clothing & Shoes Metadata")
    cloth_raw = load_meta_chunked('meta_Clothing_Shoes_and_Jewelry.jsonl.gz', 50_000)
    cloth_df  = clean_and_sample(cloth_raw, 'Clothing & Shoes', 80_000, existing_ids, ref_cols)
    del cloth_raw
    print("  [OK] Clothing: %d products" % len(cloth_df))

    # Update existing_ids to include Clothing so Beauty deduplication works
    existing_ids.update(cloth_df['product_id'].astype(str).tolist())

    # 3. Load Clothing reviews
    banner("3/6  Load Clothing Reviews (SVD)")
    cloth_rev = load_reviews_chunked('Clothing_Shoes_and_Jewelry.jsonl.gz', 500_000)
    if not cloth_rev.empty:
        cloth_rev['category'] = 'Clothing & Shoes'

    # 4. Process Beauty metadata → 80K
    banner("4/6  Process Beauty & Personal Care Metadata")
    beauty_raw = load_meta_chunked('meta_Beauty_and_Personal_Care.jsonl.gz', 50_000)
    beauty_df  = clean_and_sample(beauty_raw, 'Beauty & Personal Care', 80_000, existing_ids, ref_cols)
    del beauty_raw
    print("  [OK] Beauty: %d products" % len(beauty_df))

    # 5. Load Beauty reviews
    banner("5/6  Load Beauty Reviews (SVD)")
    beauty_rev = load_reviews_chunked('Beauty_and_Personal_Care.jsonl.gz', 500_000)
    if not beauty_rev.empty:
        beauty_rev['category'] = 'Beauty & Personal Care'

    # 6. Merge everything
    banner("6/6  Merge + Save")
    frames = [existing_df]
    if not cloth_df.empty:
        frames.append(cloth_df)
    if not beauty_df.empty:
        frames.append(beauty_df)

    final_df = pd.concat(frames, ignore_index=True)
    final_df = final_df.drop_duplicates(subset=['product_id'])
    print("  Final rows: %d" % len(final_df))
    for cat, cnt in final_df['category'].value_counts().items():
        print("    %-35s %8d" % (cat, cnt))

    # Backup
    backup_path = existing_path.replace('.pkl', '_backup_pre_expansion.pkl')
    if not os.path.exists(backup_path):
        shutil.copy2(existing_path, backup_path)
        print("  Backup created [OK]")
    else:
        print("  Backup already exists -- skipping")

    # Atomic save
    print("  Writing products_df.pkl (atomic)...")
    t_save = time.time()
    tmp_fd, tmp_path = tempfile.mkstemp(dir=SAVED_MODELS_DIR, suffix='.pkl.tmp')
    os.close(tmp_fd)
    try:
        final_df.to_pickle(tmp_path)
        os.replace(tmp_path, existing_path)
        print("  Saved in %.1fs  (%.2f GB)" % (
            time.time()-t_save, os.path.getsize(existing_path)/1024**3))
    except Exception as e:
        os.unlink(tmp_path)
        print("[ERROR] Save failed: %s" % e)
        sys.exit(1)

    # Save reviews for SVD
    rev_frames = [df for df in [cloth_rev, beauty_rev] if not df.empty]
    if rev_frames:
        combined_rev = pd.concat(rev_frames, ignore_index=True)
        rev_path = os.path.join(SAVED_MODELS_DIR, 'new_category_reviews.pkl')
        combined_rev.to_pickle(rev_path)
        print("  New reviews saved: %d rows -> %s" % (len(combined_rev), rev_path))

    banner("DONE!")
    print("  Total time: %.1fs" % (time.time()-t_start))
    print("  Next: python scripts/train_models.py")
    print(BANNER)
