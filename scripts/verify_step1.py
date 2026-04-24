"""Step 1 Verification: products_df.pkl has 4 categories and ~560K rows."""
import pickle, os, sys

print("=" * 55)
print("  STEP 1 VERIFICATION")
print("=" * 55)

path = os.path.join("saved_models", "products_df.pkl")
with open(path, "rb") as f:
    df = pickle.load(f)

total = len(df)
cats  = df['category'].value_counts().to_dict()

print("  Total rows   : %d" % total)
print("  Categories   :")
for cat, cnt in cats.items():
    print("    %-40s %8d" % (cat, cnt))

# Checks
ok = True
if total < 500_000:
    print("  [FAIL] Row count too low (expected ~560K)")
    ok = False
else:
    print("  [PASS] Row count: %d" % total)

expected_cats = {'Electronics', 'Home & Kitchen', 'Clothing & Shoes', 'Beauty & Personal Care'}
missing = expected_cats - set(cats.keys())
if missing:
    print("  [FAIL] Missing categories: %s" % missing)
    ok = False
else:
    print("  [PASS] All 4 categories present")

# Check backup exists
backup = path.replace('.pkl', '_backup_pre_expansion.pkl')
if os.path.exists(backup):
    print("  [PASS] Backup file exists: %s" % os.path.basename(backup))
else:
    print("  [WARN] Backup not found (non-critical)")

# Check new_category_reviews.pkl
rev_path = os.path.join("saved_models", "new_category_reviews.pkl")
if os.path.exists(rev_path):
    with open(rev_path, "rb") as f:
        rev_df = pickle.load(f)
    print("  [PASS] new_category_reviews.pkl: %d rows" % len(rev_df))
else:
    print("  [WARN] new_category_reviews.pkl not found")

print("=" * 55)
if ok:
    print("  STEP 1 PASSED -- safe to run train_models.py")
else:
    print("  STEP 1 FAILED -- check errors above")
    sys.exit(1)
