"""
utils/data_loader.py
IntelliRec — Data Loading Utilities
Sourcesys Technologies Internship Project
Team: Hemanthselva AK, Monish Kaarthi RK, Vishal KS, Vishal M

Categories supported:
  Electronics          (Electronics.jsonl.gz)
  Home & Kitchen       (Home_and_Kitchen.jsonl.gz)
  Clothing & Shoes     (Clothing_Shoes_and_Jewelry.jsonl.gz)   ← NEW
  Beauty & Personal Care (Beauty_and_Personal_Care.jsonl.gz)  ← NEW
"""

import gzip
import json
import pandas as pd
import numpy as np
import os
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, *args, **kwargs):  # type: ignore[misc]
        return iterable

# ── Directory paths ────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'saved_models')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)


def load_jsonl_gz(filepath, max_rows=500000, columns=None):
    """Load a gzipped JSONL file into a DataFrame with optional column filtering."""
    records = []
    with gzip.open(filepath, 'rt', encoding='utf-8') as f:
        for i, line in enumerate(tqdm(f, desc=f"Loading {os.path.basename(filepath)}")):
            if i >= max_rows:
                break
            try:
                record = json.loads(line.strip())
                if columns:
                    record = {k: record.get(k) for k in columns}
                records.append(record)
            except Exception:
                continue
    return pd.DataFrame(records)


def load_electronics_reviews(max_rows=500000):
    """Load Electronics review dataset."""
    path = os.path.join(DATA_DIR, 'Electronics.jsonl.gz')
    if not os.path.exists(path):
        print(f"[WARNING] File not found: {path}")
        return pd.DataFrame(columns=['user_id', 'product_id', 'rating',
                                     'timestamp', 'text', 'title'])
    cols = ['user_id', 'parent_asin', 'rating', 'timestamp', 'text', 'title']
    df = load_jsonl_gz(path, max_rows=max_rows, columns=cols)
    df = df.rename(columns={'parent_asin': 'product_id'})
    df = df.dropna(subset=['user_id', 'product_id', 'rating'])
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df = df[df['rating'].between(1.0, 5.0)]
    print(f"Electronics reviews loaded: {len(df):,} rows")
    return df


def load_hk_reviews(max_rows=500000):
    """Load Home & Kitchen review dataset."""
    path = os.path.join(DATA_DIR, 'Home_and_Kitchen.jsonl.gz')
    if not os.path.exists(path):
        print(f"[WARNING] File not found: {path}")
        return pd.DataFrame(columns=['user_id', 'product_id', 'rating',
                                     'timestamp', 'text', 'title'])
    cols = ['user_id', 'parent_asin', 'rating', 'timestamp', 'text', 'title']
    df = load_jsonl_gz(path, max_rows=max_rows, columns=cols)
    df = df.rename(columns={'parent_asin': 'product_id'})
    df = df.dropna(subset=['user_id', 'product_id', 'rating'])
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df = df[df['rating'].between(1.0, 5.0)]
    print(f"Home & Kitchen reviews loaded: {len(df):,} rows")
    return df


def load_electronics_meta(max_rows=200000):
    """Load Electronics product metadata."""
    path = os.path.join(DATA_DIR, 'meta_Electronics.jsonl.gz')
    if not os.path.exists(path):
        print(f"[WARNING] File not found: {path}")
        return pd.DataFrame(columns=['product_id', 'title', 'price',
                                     'average_rating', 'rating_number'])
    cols = ['parent_asin', 'title', 'price', 'average_rating',
            'rating_number', 'features', 'description',
            'store', 'categories', 'main_category']
    df = load_jsonl_gz(path, max_rows=max_rows, columns=cols)
    df = df.rename(columns={'parent_asin': 'product_id'})
    df = df.dropna(subset=['product_id', 'title'])
    print(f"Electronics metadata loaded: {len(df):,} rows")
    return df


def load_hk_meta(max_rows=200000):
    """Load Home & Kitchen product metadata."""
    path = os.path.join(DATA_DIR, 'meta_Home_and_Kitchen.jsonl.gz')
    if not os.path.exists(path):
        print(f"[WARNING] File not found: {path}")
        return pd.DataFrame(columns=['product_id', 'title', 'price',
                                     'average_rating', 'rating_number'])
    cols = ['parent_asin', 'title', 'price', 'average_rating',
            'rating_number', 'features', 'description',
            'store', 'categories', 'main_category']
    df = load_jsonl_gz(path, max_rows=max_rows, columns=cols)
    df = df.rename(columns={'parent_asin': 'product_id'})
    df = df.dropna(subset=['product_id', 'title'])
    print(f"Home & Kitchen metadata loaded: {len(df):,} rows")
    return df


def load_clothing_reviews(max_rows=500000):
    """Load Clothing, Shoes & Jewelry review dataset."""
    path = os.path.join(DATA_DIR, 'Clothing_Shoes_and_Jewelry.jsonl.gz')
    if not os.path.exists(path):
        print(f"[WARNING] File not found: {path}")
        return pd.DataFrame(columns=['user_id', 'product_id', 'rating',
                                     'timestamp', 'text', 'title'])
    cols = ['user_id', 'parent_asin', 'rating', 'timestamp', 'text', 'title']
    df = load_jsonl_gz(path, max_rows=max_rows, columns=cols)
    df = df.rename(columns={'parent_asin': 'product_id'})
    df = df.dropna(subset=['user_id', 'product_id', 'rating'])
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df = df[df['rating'].between(1.0, 5.0)]
    print(f"Clothing & Shoes reviews loaded: {len(df):,} rows")
    return df


def load_beauty_reviews(max_rows=500000):
    """Load Beauty & Personal Care review dataset."""
    path = os.path.join(DATA_DIR, 'Beauty_and_Personal_Care.jsonl.gz')
    if not os.path.exists(path):
        print(f"[WARNING] File not found: {path}")
        return pd.DataFrame(columns=['user_id', 'product_id', 'rating',
                                     'timestamp', 'text', 'title'])
    cols = ['user_id', 'parent_asin', 'rating', 'timestamp', 'text', 'title']
    df = load_jsonl_gz(path, max_rows=max_rows, columns=cols)
    df = df.rename(columns={'parent_asin': 'product_id'})
    df = df.dropna(subset=['user_id', 'product_id', 'rating'])
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df = df[df['rating'].between(1.0, 5.0)]
    print(f"Beauty & Personal Care reviews loaded: {len(df):,} rows")
    return df


def load_clothing_meta(max_rows=200000):
    """Load Clothing, Shoes & Jewelry product metadata."""
    path = os.path.join(DATA_DIR, 'meta_Clothing_Shoes_and_Jewelry.jsonl.gz')
    if not os.path.exists(path):
        print(f"[WARNING] File not found: {path}")
        return pd.DataFrame(columns=['product_id', 'title', 'price',
                                     'average_rating', 'rating_number'])
    cols = ['parent_asin', 'title', 'price', 'average_rating',
            'rating_number', 'features', 'description',
            'store', 'categories', 'main_category']
    df = load_jsonl_gz(path, max_rows=max_rows, columns=cols)
    df = df.rename(columns={'parent_asin': 'product_id'})
    df = df.dropna(subset=['product_id', 'title'])
    print(f"Clothing & Shoes metadata loaded: {len(df):,} rows")
    return df


def load_beauty_meta(max_rows=200000):
    """Load Beauty & Personal Care product metadata."""
    path = os.path.join(DATA_DIR, 'meta_Beauty_and_Personal_Care.jsonl.gz')
    if not os.path.exists(path):
        print(f"[WARNING] File not found: {path}")
        return pd.DataFrame(columns=['product_id', 'title', 'price',
                                     'average_rating', 'rating_number'])
    cols = ['parent_asin', 'title', 'price', 'average_rating',
            'rating_number', 'features', 'description',
            'store', 'categories', 'main_category']
    df = load_jsonl_gz(path, max_rows=max_rows, columns=cols)
    df = df.rename(columns={'parent_asin': 'product_id'})
    df = df.dropna(subset=['product_id', 'title'])
    print(f"Beauty & Personal Care metadata loaded: {len(df):,} rows")
    return df


def load_combined_reviews(max_rows_each=500000):
    """Load and combine reviews from all four categories."""
    elec = load_electronics_reviews(max_rows=max_rows_each)
    elec['category'] = 'Electronics'

    hk = load_hk_reviews(max_rows=max_rows_each)
    hk['category'] = 'Home & Kitchen'

    # ── New categories ──────────────────────────────────────────────────────
    clothing = load_clothing_reviews(max_rows=max_rows_each)
    clothing['category'] = 'Clothing & Shoes'

    beauty = load_beauty_reviews(max_rows=max_rows_each)
    beauty['category'] = 'Beauty & Personal Care'
    # ────────────────────────────────────────────────────────────────────────

    combined = pd.concat([elec, hk, clothing, beauty], ignore_index=True)
    combined = combined.drop_duplicates()
    print(f"Combined reviews (all 4 categories): {len(combined):,} rows")
    return combined


def load_combined_meta(max_rows_each=200000):
    """Load and combine product metadata from all four categories."""
    elec = load_electronics_meta(max_rows=max_rows_each)
    elec['category'] = 'Electronics'

    hk = load_hk_meta(max_rows=max_rows_each)
    hk['category'] = 'Home & Kitchen'

    # ── New categories ──────────────────────────────────────────────────────
    clothing = load_clothing_meta(max_rows=max_rows_each)
    clothing['category'] = 'Clothing & Shoes'

    beauty = load_beauty_meta(max_rows=max_rows_each)
    beauty['category'] = 'Beauty & Personal Care'
    # ────────────────────────────────────────────────────────────────────────

    combined = pd.concat([elec, hk, clothing, beauty], ignore_index=True)
    combined = combined.drop_duplicates(subset=['product_id'])
    print(f"Combined metadata (all 4 categories): {len(combined):,} rows")
    return combined


def get_dataset_stats(reviews_df, meta_df):
    """Return a dictionary of dataset statistics for reporting."""
    stats = {
        'total_reviews': len(reviews_df),
        'total_products': len(meta_df),
        'unique_users': reviews_df['user_id'].nunique(),
        'avg_rating': round(reviews_df['rating'].mean(), 3),
        'categories': reviews_df['category'].value_counts().to_dict()
            if 'category' in reviews_df.columns else {},
        'rating_distribution': reviews_df['rating'].value_counts().sort_index().to_dict(),
        'price_range': {
            'min': meta_df['price'].min() if 'price' in meta_df.columns else 0,
            'max': meta_df['price'].max() if 'price' in meta_df.columns else 0,
        }
    }
    return stats
