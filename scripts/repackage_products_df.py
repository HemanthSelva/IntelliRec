"""
scripts/repackage_products_df.py

One-shot local utility to convert saved_models/products_df.pkl into a
version-portable parquet file that survives pandas/pyarrow upgrades.

Why: the pkl was created with a pandas/pyarrow version whose StringDtype
constructor signature differs from Streamlit Cloud's (pandas==2.2.3).
Unpickling fails on the cloud with:
    StringDtype.__init__() takes from 1 to 2 positional arguments but 3 were given
which forces every Hybrid recommendation call to fall back to the
42-item assets/sample_products.json sample.

Parquet stores schema explicitly (no Python class pickling), reads ~3×
faster than joblib, and compresses 30–50% smaller.

Run: python scripts/repackage_products_df.py
Output: saved_models/products_df.parquet (upload this to HuggingFace)
"""
from __future__ import annotations

import os
import sys
import time

import joblib
import pandas as pd

ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKL_PATH  = os.path.join(ROOT, "saved_models", "products_df.pkl")
OUT_PATH  = os.path.join(ROOT, "saved_models", "products_df.parquet")


def main() -> int:
    if not os.path.exists(PKL_PATH):
        print(f"ERROR: {PKL_PATH} not found")
        return 1

    print(f"Reading {PKL_PATH} ...")
    t0 = time.time()
    df = joblib.load(PKL_PATH)
    print(f"  Loaded {len(df):,} rows × {len(df.columns)} cols in {time.time()-t0:.1f}s")
    print(f"  Original dtypes:\n{df.dtypes}\n")

    # Cast pandas nullable StringDtype → plain object/str (the source of the
    # cloud-side unpickle error).  Also normalize any nullable Boolean/Int.
    str_cols = ("product_id", "title", "store", "category", "main_category")
    for col in df.columns:
        dt = str(df[col].dtype)
        if col in str_cols or dt in ("string", "str") or "String" in dt:
            s = df[col].astype(object)
            df[col] = s.where(s.notna(), "").astype(str).replace({"nan": "", "<NA>": ""})
        elif "boolean" in dt or "Boolean" in dt:
            df[col] = df[col].astype(object).fillna(False).astype(bool)
        elif "Int" in dt:
            df[col] = df[col].astype("int64", errors="ignore")
        elif "Float" in dt:
            df[col] = df[col].astype("float64", errors="ignore")

    # Coerce price → float (some rows hold currency strings / unicode garbage)
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0.0).astype("float64")

    # `categories` is a Python list per row — keep as object, parquet handles it
    # via list<string> if entries are uniform.  Coerce non-list entries to [].
    if "categories" in df.columns:
        def _norm_cats(v):
            if isinstance(v, list):
                return [str(x) for x in v]
            if v is None or (isinstance(v, float) and v != v):  # NaN
                return []
            return [str(v)]
        df["categories"] = df["categories"].apply(_norm_cats)

    # Drop columns the runtime never uses (saves cloud RAM)
    heavy = [c for c in ("features_str", "description", "features") if c in df.columns]
    if heavy:
        df = df.drop(columns=heavy)
        print(f"  Dropped heavy training-only columns: {heavy}")

    print(f"  Normalized dtypes:\n{df.dtypes}\n")
    print(f"Writing {OUT_PATH} ...")
    t0 = time.time()
    df.to_parquet(OUT_PATH, engine="pyarrow", compression="zstd", index=False)
    out_mb = os.path.getsize(OUT_PATH) / 1024 / 1024
    print(f"  Wrote {out_mb:.1f} MB in {time.time()-t0:.1f}s")

    # Round-trip verify — read back and compare row count + dtypes
    print("Verifying round-trip ...")
    df2 = pd.read_parquet(OUT_PATH)
    assert len(df2) == len(df), f"row count mismatch: {len(df2)} vs {len(df)}"
    assert list(df2.columns) == list(df.columns), "column order mismatch"
    print(f"  OK — {len(df2):,} rows round-tripped cleanly")
    print("\nDONE. Upload this file to HuggingFace:")
    print(f"   {OUT_PATH}")
    print("   Repo: Hemanth1429/intellirec-recommendation-model")
    print("   Filename on HF: products_df.parquet")
    return 0


if __name__ == "__main__":
    sys.exit(main())
