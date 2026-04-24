"""Pre-run checks for IntelliRec 4-category pipeline."""
import os, sys

sm = 'saved_models'
data = 'data'

print("=" * 55)
print("  Pre-run saved_models check")
print("=" * 55)
required_models = [
    'products_df.pkl',
    'tfidf_matrix.pkl',
    'svd_model.pkl',
    'product_sentiments.pkl',
    'product_indices.pkl',
    'tfidf_vectorizer.pkl',
]
all_ok = True
for f in required_models:
    p = os.path.join(sm, f)
    exists = os.path.exists(p)
    size_mb = round(os.path.getsize(p) / 1024**2, 1) if exists else 0
    status = "OK  " if exists else "MISS"
    print("  [%s] %-40s %8.1f MB" % (status, f, size_mb))
    if not exists:
        all_ok = False

print()
print("=" * 55)
print("  Raw data files check")
print("=" * 55)
raw_files = [
    ('Clothing_Shoes_and_Jewelry.jsonl.gz',     'reviews'),
    ('meta_Clothing_Shoes_and_Jewelry.jsonl.gz','metadata'),
    ('Beauty_and_Personal_Care.jsonl.gz',       'reviews'),
    ('meta_Beauty_and_Personal_Care.jsonl.gz',  'metadata'),
]
for fname, ftype in raw_files:
    p = os.path.join(data, fname)
    exists = os.path.exists(p)
    size_gb = round(os.path.getsize(p) / 1024**3, 2) if exists else 0
    status = "OK  " if exists else "MISS"
    print("  [%s] %-52s %.2f GB" % (status, fname, size_gb))
    if not exists:
        all_ok = False

print()
if all_ok:
    print("  All checks PASSED. Safe to proceed.")
else:
    print("  Some checks FAILED. Resolve before continuing.")
    sys.exit(1)
