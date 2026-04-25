import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import joblib
import pandas as pd

MODEL_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'saved_models'
)

print("Loading products_df.pkl...")
try:
    df = joblib.load(os.path.join(MODEL_DIR, 'products_df.pkl'))
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nUnique categories:")
    cats = df['category'].value_counts()
    for cat, count in cats.items():
        print(f"  '{cat}': {count} products")
    print(f"\nSample rows (first 3):")
    print(df[['product_id', 'title', 'category', 'average_rating', 'price']].head(3).to_string())
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
