"""Step 2 Verification: all model files updated and shapes correct."""
import pickle, joblib, os, sys, time

print("=" * 60)
print("  STEP 2 VERIFICATION")
print("=" * 60)

sm = "saved_models"
now = time.time()
ok  = True

files = [
    "tfidf_matrix.pkl",
    "tfidf_vectorizer.pkl",
    "svd_model.pkl",
    "product_sentiments.pkl",
    "product_indices.pkl",
    "model_metrics.pkl",
]

print("\n  File timestamps (all should be recent):")
for f in files:
    p = os.path.join(sm, f)
    if not os.path.exists(p):
        print("  [FAIL] MISSING: %s" % f)
        ok = False
        continue
    mtime = os.path.getmtime(p)
    age_min = round((now - mtime) / 60, 1)
    size_mb = round(os.path.getsize(p) / 1024**2, 1)
    flag = "OK  " if age_min < 120 else "OLD "
    print("  [%s] %-35s %8.1f MB  (%.0f min ago)" % (flag, f, size_mb, age_min))

# TF-IDF shape check
print("\n  TF-IDF matrix shape:")
tfidf = joblib.load(os.path.join(sm, "tfidf_matrix.pkl"))
rows, cols = tfidf.shape
print("    Rows (products) : %d  (expected ~560000)" % rows)
print("    Cols (features) : %d  (expected ~20000)"  % cols)
if rows < 500_000:
    print("  [FAIL] Too few rows in TF-IDF")
    ok = False
else:
    print("  [PASS] TF-IDF shape OK: %d x %d" % (rows, cols))

# Sentiment count check
print("\n  Sentiment scores:")
sents = joblib.load(os.path.join(sm, "product_sentiments.pkl"))
print("    Products with sentiment: %d  (expected >100K)" % len(sents))
if len(sents) < 100_000:
    print("  [WARN] Sentiment count low")
else:
    print("  [PASS] Sentiment count OK")

# Product indices check
print("\n  Product indices:")
idx = joblib.load(os.path.join(sm, "product_indices.pkl"))
print("    Index entries: %d  (expected ~560000)" % len(idx))
if len(idx) < 500_000:
    print("  [FAIL] Product indices too low")
    ok = False
else:
    print("  [PASS] Product indices OK")

print("\n" + "=" * 60)
if ok:
    print("  STEP 2 PASSED -- ready to launch app")
else:
    print("  STEP 2 FAILED -- check errors above")
    sys.exit(1)
