"""
models/sentiment_analyzer.py
IntelliRec — VADER Sentiment Analysis
Sourcesys Technologies Internship Project
Team: Hemanthselva AK, Monish Kaarthi RK, Vishal KS, Vishal M
"""

import pandas as pd
import numpy as np
import joblib
import os
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, *args, **kwargs):  # type: ignore[misc]
        return iterable

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    print("[WARNING] vaderSentiment not installed. "
          "Install via: pip install vaderSentiment")

# ── Paths ──────────────────────────────────────────────────────────────────────
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'saved_models')
os.makedirs(MODELS_DIR, exist_ok=True)


class SentimentAnalyzer:
    """
    VADER-based sentiment analysis for individual reviews
    and aggregated product-level sentiment scoring.
    """

    def __init__(self):
        if VADER_AVAILABLE:
            self.analyzer = SentimentIntensityAnalyzer()
        else:
            self.analyzer = None
        self.product_sentiments: dict = {}

    # ── Text-level analysis ────────────────────────────────────────────────────
    def analyze_text(self, text):
        """
        Analyse a single review text and return a sentiment dict:
          compound, label, score (normalized 0-1), positive, negative, neutral
        """
        if not text or (isinstance(text, float) and pd.isna(text)):
            return {
                'compound': 0.0,
                'label': 'Neutral',
                'score': 0.5,
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0
            }

        if not VADER_AVAILABLE:
            return {'compound': 0.0, 'label': 'Neutral', 'score': 0.5,
                    'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}

        scores   = self.analyzer.polarity_scores(str(text))
        compound = scores['compound']

        if compound >= 0.05:
            label = 'Positive'
        elif compound <= -0.05:
            label = 'Negative'
        else:
            label = 'Neutral'

        normalized = (compound + 1) / 2   # map [-1, 1] → [0, 1]
        return {
            'compound': round(compound, 4),
            'label':    label,
            'score':    round(normalized, 4),
            'positive': round(scores['pos'], 4),
            'negative': round(scores['neg'], 4),
            'neutral':  round(scores['neu'], 4)
        }

    # ── Product-level aggregation ──────────────────────────────────────────────
    def compute_product_sentiments(self, reviews_df,
                                   sample_per_product=50):
        """
        Aggregate per-product sentiment by averaging VADER compound scores
        across up to sample_per_product reviews per product.
        """
        if not VADER_AVAILABLE:
            print("[WARNING] VADER unavailable; product sentiments skipped.")
            return {}

        product_sentiments = {}
        grouped = reviews_df.groupby('product_id')
        print(f"Computing sentiments for {grouped.ngroups:,} products...")

        for product_id, group in tqdm(grouped,
                                      desc="Sentiment analysis",
                                      total=grouped.ngroups):
            sample = group.head(sample_per_product)
            texts  = sample['text'].dropna().tolist()
            if not texts:
                continue

            compounds = [
                self.analyzer.polarity_scores(str(t))['compound']
                for t in texts
            ]
            avg_compound = float(np.mean(compounds))

            if avg_compound >= 0.05:
                label = 'Positive'
            elif avg_compound <= -0.05:
                label = 'Negative'
            else:
                label = 'Mixed'

            product_sentiments[product_id] = {
                'compound':     round(avg_compound, 4),
                'label':        label,
                'score':        round((avg_compound + 1) / 2, 4),
                'review_count': len(texts)
            }

        self.product_sentiments = product_sentiments
        print(f"Sentiment computed for {len(product_sentiments):,} products")
        return product_sentiments

    # ── Look-up ────────────────────────────────────────────────────────────────
    def get_product_sentiment(self, product_id):
        """Return cached sentiment for a product, defaulting to Mixed/0.5."""
        return self.product_sentiments.get(
            product_id,
            {'compound': 0.0, 'label': 'Mixed', 'score': 0.5,
             'review_count': 0}
        )

    # ── Persistence ────────────────────────────────────────────────────────────
    def save_sentiments(self, filename='product_sentiments.pkl'):
        path = os.path.join(MODELS_DIR, filename)
        joblib.dump(self.product_sentiments, path)
        print(f"Sentiments saved ({len(self.product_sentiments):,} products) -> {path}")

    def load_sentiments(self, filename='product_sentiments.pkl'):
        path = os.path.join(MODELS_DIR, filename)
        if os.path.exists(path):
            self.product_sentiments = joblib.load(path)
            print(f"Sentiments loaded ({len(self.product_sentiments):,} products) ← {path}")
        else:
            print(f"[INFO] No sentiment cache found at {path}; using empty dict.")
            self.product_sentiments = {}
