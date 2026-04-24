"""
models/content_based.py
IntelliRec — Content-Based Filtering (TF-IDF + Cosine Similarity)
Sourcesys Technologies Internship Project
Team: Hemanthselva AK, Monish Kaarthi RK, Vishal KS, Vishal M
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os
import time

# ── Paths ──────────────────────────────────────────────────────────────────────
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'saved_models')
os.makedirs(MODELS_DIR, exist_ok=True)


class ContentBasedModel:
    """
    Content-Based Filtering using TF-IDF vectorization over
    product title, category, brand, features, and description.
    """

    def __init__(self):
        self.tfidf          = None
        self.tfidf_matrix   = None
        self.products_df    = None
        self.product_indices = None
        self.metrics        = {}

    # ── Feature engineering ────────────────────────────────────────────────────
    def prepare_features(self, products_df):
        """Add a combined text feature column to the products DataFrame."""
        self.products_df = products_df.copy()
        self.products_df['features_str'] = self.products_df.apply(
            self._create_feature_string, axis=1
        )
        print(f"Features prepared for {len(self.products_df):,} products")
        return self.products_df

    def _create_feature_string(self, row):
        """Combine multiple product fields into a single weighted text string."""
        parts = []

        # Title weighted 3× for higher importance
        if pd.notna(row.get('title')):
            parts.append((str(row['title']) + ' ') * 3)

        # Category weighted 2×
        if pd.notna(row.get('main_category')):
            parts.append((str(row['main_category']) + ' ') * 2)

        # Category fallback
        if pd.notna(row.get('category')):
            parts.append(str(row['category']))

        # Store / brand
        if pd.notna(row.get('store')):
            parts.append(str(row['store']))

        # Product features list
        features = row.get('features')
        if features and pd.notna(features) if not isinstance(features, list) else features:
            if isinstance(features, list):
                parts.extend([str(f) for f in features[:5]])
            else:
                parts.append(str(features))

        # Description (truncated)
        description = row.get('description')
        if description and pd.notna(description) if not isinstance(description, list) else description:
            if isinstance(description, list):
                parts.append(' '.join(str(d) for d in description[:2]))
            else:
                parts.append(str(description)[:300])

        return ' '.join(parts).lower()

    # ── Training ───────────────────────────────────────────────────────────────
    def train(self, max_features=50000):
        """Fit TF-IDF vectorizer and build the product similarity matrix."""
        if self.products_df is None:
            raise ValueError("Call prepare_features() before train()")

        print(f"Fitting TF-IDF (max_features={max_features})...")
        t0 = time.time()
        self.tfidf = TfidfVectorizer(
            max_features=max_features,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            sublinear_tf=True   # dampen high-frequency terms
        )
        self.tfidf_matrix = self.tfidf.fit_transform(
            self.products_df['features_str']
        )
        self.product_indices = pd.Series(
            self.products_df.index,
            index=self.products_df['product_id']
        )
        train_time = round(time.time() - t0, 2)
        print(f"TF-IDF matrix shape: {self.tfidf_matrix.shape}  "
              f"(trained in {train_time}s)")
        return self.tfidf_matrix

    # ── Inference ──────────────────────────────────────────────────────────────
    def get_similar_products(self, product_id, n=10):
        """Return n most similar products to the given product_id."""
        if self.tfidf_matrix is None:
            return []
        if product_id not in self.product_indices:
            return []

        idx         = self.product_indices[product_id]
        product_vec = self.tfidf_matrix[idx]
        sim_scores  = cosine_similarity(product_vec,
                                         self.tfidf_matrix).flatten()
        sim_indices = sim_scores.argsort()[::-1][1:n + 1]

        results = []
        for i in sim_indices:
            row = self.products_df.iloc[i]
            results.append({
                'product_id':       row['product_id'],
                'title':            row.get('title', ''),
                'category':         row.get('category', ''),
                'price':            row.get('price', 0),
                'rating':           row.get('average_rating', 0),
                'similarity_score': round(float(sim_scores[i]), 4)
            })
        return results

    def get_recommendations_by_categories(self, categories, n=10):
        """Return top-rated products from the given categories list."""
        if self.products_df is None:
            return []

        cat_products = self.products_df[
            self.products_df['category'].isin(categories)
        ].copy()

        # Coerce average_rating to numeric
        cat_products['average_rating'] = pd.to_numeric(
            cat_products['average_rating'], errors='coerce'
        ).fillna(0.0)

        top_products = cat_products.nlargest(
            min(n * 3, len(cat_products)), 'average_rating'
        )

        results = []
        for _, row in top_products.head(n).iterrows():
            results.append({
                'product_id':       row['product_id'],
                'title':            row.get('title', ''),
                'category':         row.get('category', ''),
                'price':            row.get('price', 0),
                'rating':           float(row.get('average_rating', 0) or 0),
                'similarity_score': 1.0
            })
        return results

    # ── Evaluation ─────────────────────────────────────────────────────────────
    def compute_metrics(self, test_interactions, k=10):
        """
        Precision@K against a test DataFrame with columns
        [product_id, liked_product_id].
        """
        hits, total = 0, 0
        for _, row in test_interactions.iterrows():
            recs = self.get_similar_products(row['product_id'], n=k)
            rec_ids = [r['product_id'] for r in recs]
            if row.get('liked_product_id') in rec_ids:
                hits += 1
            total += 1
        precision = round(hits / total, 4) if total > 0 else 0
        self.metrics = {'Precision@K': precision}
        return self.metrics

    # ── Persistence ────────────────────────────────────────────────────────────
    def save_model(self):
        """Persist TF-IDF model and matrix to saved_models/."""
        joblib.dump(self.tfidf,
                    os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl'))
        joblib.dump(self.tfidf_matrix,
                    os.path.join(MODELS_DIR, 'tfidf_matrix.pkl'))
        joblib.dump(self.product_indices,
                    os.path.join(MODELS_DIR, 'product_indices.pkl'))
        self.products_df.to_pickle(
            os.path.join(MODELS_DIR, 'products_df.pkl'))
        print("Content-based model saved successfully")

    def load_model(self):
        """Load TF-IDF model and matrix from saved_models/."""
        self.tfidf = joblib.load(
            os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl'))
        self.tfidf_matrix = joblib.load(
            os.path.join(MODELS_DIR, 'tfidf_matrix.pkl'))
        self.product_indices = joblib.load(
            os.path.join(MODELS_DIR, 'product_indices.pkl'))
        self.products_df = pd.read_pickle(
            os.path.join(MODELS_DIR, 'products_df.pkl'))
        print(f"Content-based model loaded  "
              f"({len(self.products_df):,} products)")
