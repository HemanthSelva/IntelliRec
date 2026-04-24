"""
utils/chatbot_engine.py
IntelliRec — AI Chatbot Engine v1.0

Architecture:
  1. Query Parser   — extract category, budget, intent, keywords
  2. Intent Classifier — recommendation | general | unknown
  3. Recommendation Bridge — reuses existing model_loader functions (NO new logic)
  4. Response Generator — format results + explanations
  5. Grok API (optional) — for general questions, with rule-based fallback

Sourcesys Technologies Internship Project
"""

import os
import re
from datetime import datetime


# ── Category keyword map ───────────────────────────────────────────────────────
_CATEGORY_KEYWORDS = {
    "Electronics": [
        "laptop", "phone", "mobile", "smartphone", "tablet", "ipad",
        "computer", "pc", "monitor", "keyboard", "mouse", "headphone",
        "earphone", "speaker", "camera", "tv", "television", "gaming",
        "console", "playstation", "xbox", "nintendo", "charger", "battery",
        "router", "wifi", "smartwatch", "watch", "earbuds", "airpods",
        "electronics", "gadget", "tech", "device", "processor", "cpu",
    ],
    "Home & Kitchen": [
        "kitchen", "home", "cookware", "pan", "pot", "blender", "mixer",
        "microwave", "oven", "refrigerator", "fridge", "washing machine",
        "vacuum", "cleaner", "furniture", "sofa", "chair", "table", "bed",
        "pillow", "mattress", "curtain", "lamp", "light", "fan", "air",
        "cooler", "purifier", "instant pot", "air fryer", "coffee", "kettle",
        "toaster", "dishwasher", "mop", "broom", "storage", "organiser",
    ],
    "Clothing & Shoes": [
        "clothing", "shirt", "tshirt", "t-shirt", "jeans", "pants", "dress",
        "shoes", "sneakers", "boots", "sandals", "jacket", "coat", "sweater",
        "hoodie", "fashion", "wear", "outfit", "clothes", "apparel", "kurta",
        "saree", "leggings", "shorts", "skirt", "cap", "hat", "gloves",
        "socks", "underwear", "bra", "lingerie",
    ],
    "Beauty & Personal Care": [
        "beauty", "skincare", "skin", "cream", "moisturiser", "moisturizer",
        "face wash", "sunscreen", "makeup", "lipstick", "foundation",
        "mascara", "shampoo", "conditioner", "hair", "perfume", "fragrance",
        "deodorant", "body wash", "soap", "serum", "toner", "lotion",
        "personal care", "grooming", "razor", "toothbrush", "toothpaste",
        "nail", "cologne", "wellness",
    ],
}

# Intent keywords for general vs recommendation
_GENERAL_QUESTION_WORDS = [
    "what is", "how does", "explain", "tell me about", "define",
    "difference between", "why is", "when was", "who is", "history of",
    "how to", "what are", "what's the",
]

_RECOMMENDATION_WORDS = [
    "suggest", "recommend", "best", "top", "show me", "find me",
    "give me", "i want", "i need", "looking for", "buy", "purchase",
    "under", "below", "within budget", "cheap", "affordable", "good",
]

# Greeting words — detected before any other intent
_GREETING_WORDS = [
    "hi", "hello", "hey", "hiya", "howdy", "greetings",
    "good morning", "good evening", "good afternoon", "good night",
    "what's up", "whats up", "sup", "yo",
]

# Greeting responses (rotated for variety)
_GREETING_RESPONSES = [
    "Hey there! 👋 I'm your **IntelliRec AI assistant**. I can help you find products, "
    "explain recommendations, or answer shopping questions. What are you looking for today?",

    "Hello! 😊 Great to see you. I'm powered by **SVD + TF-IDF + Sentiment AI** to find "
    "the perfect products for you. Try asking: *'Best laptops under ₹50,000'* or "
    "*'Top beauty products'*.",

    "Hi! 👋 I'm **IntelliRec's AI assistant** — here to make shopping smarter. "
    "Ask me for recommendations, budget finds, or explanations of how AI picks products for you!",
]

# General Q&A knowledge base (rule-based fallback)
_KNOWLEDGE_BASE = {
    "collaborative filtering": (
        "**Collaborative Filtering** is a recommendation technique that predicts "
        "what a user will like based on the preferences of *similar users*. "
        "IntelliRec uses **SVD (Singular Value Decomposition)** to decompose the "
        "user-item interaction matrix and surface hidden patterns. "
        "It excels at discovering non-obvious connections but can struggle with new users (cold-start problem)."
    ),
    "content based": (
        "**Content-Based Filtering** recommends items similar to ones the user has "
        "liked before, using item *features* like title, category, and description. "
        "IntelliRec uses **TF-IDF vectorisation** and cosine similarity to match "
        "products to your stated preferences. It works well even for new users."
    ),
    "hybrid recommender": (
        "IntelliRec's **Hybrid Engine** blends Collaborative Filtering (SVD) and "
        "Content-Based (TF-IDF) recommendations, then applies a **VADER sentiment boost** "
        "that nudges products with positive community reviews higher in your results. "
        "The diversity slider controls the CF:CB ratio."
    ),
    "svd": (
        "**SVD (Singular Value Decomposition)** is a matrix factorisation technique. "
        "IntelliRec uses it via the Surprise library to learn latent user and item "
        "factors from rating data, enabling personalised score predictions for any user-product pair."
    ),
    "tfidf": (
        "**TF-IDF (Term Frequency-Inverse Document Frequency)** converts product text "
        "(titles, descriptions) into numeric vectors. IntelliRec uses cosine similarity "
        "on these vectors to find products that are textually similar to your interests."
    ),
    "vader": (
        "**VADER (Valence Aware Dictionary and sEntiment Reasoner)** is a rule-based "
        "sentiment analyser tuned for social text. IntelliRec applies it to product reviews "
        "to compute a compound sentiment score, which is then used to boost or dampen "
        "match scores in the hybrid recommendation pipeline."
    ),
    "sentiment": (
        "IntelliRec analyses product reviews using **VADER sentiment analysis** to classify "
        "each product as Positive, Mixed, or Critical. This sentiment score contributes "
        "20% to the final match score in hybrid mode, ensuring highly-reviewed products "
        "surface above technically-similar but poorly-reviewed ones."
    ),
    "intellirec": (
        "**IntelliRec** is an AI-powered product recommendation platform built by "
        "Sourcesys Technologies. It uses three AI engines — SVD Collaborative Filtering, "
        "TF-IDF Content-Based, and VADER Sentiment Analysis — to generate personalised "
        "product recommendations from a catalogue of 560,000+ products across 4 categories."
    ),
}

# ── Query Parser ───────────────────────────────────────────────────────────────

def parse_query(text: str) -> dict:
    """
    Parse a user query into structured components.

    Returns
    -------
    dict with keys: intent, categories, budget, keywords, raw
    """
    text_lower = text.lower().strip()

    result = {
        "raw":        text,
        "intent":     None,   # filled by classify_intent
        "categories": [],
        "budget":     None,
        "keywords":   [],
    }

    # 1. Extract budget — patterns like "under 50000", "below 500", "within 1000", "₹500", "$200"
    budget_patterns = [
        r"(?:under|below|within|less than|max|upto|up to)\s*[₹$]?\s*([\d,]+)",
        r"[₹$]\s*([\d,]+)",
        r"([\d,]+)\s*(?:rs|inr|rupees|dollars?)",
        r"budget\s*(?:of|is|:)?\s*[₹$]?\s*([\d,]+)",
    ]
    for pat in budget_patterns:
        m = re.search(pat, text_lower)
        if m:
            try:
                raw_num = m.group(1).replace(",", "")
                result["budget"] = float(raw_num)
                break
            except (ValueError, AttributeError):
                pass

    # 2. Extract categories
    for cat, keywords in _CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                if cat not in result["categories"]:
                    result["categories"].append(cat)
                break

    # Default to Electronics for ambiguous "gaming", "tech" queries if no cat found
    if not result["categories"] and any(w in text_lower for w in ["gaming", "tech", "gadget"]):
        result["categories"] = ["Electronics"]

    # 3. Extract keywords (non-stop meaningful words)
    _STOP = {"a", "an", "the", "me", "my", "for", "in", "of", "to", "and",
              "or", "is", "are", "was", "i", "want", "need", "give", "show",
              "please", "can", "you", "with", "some", "good", "best", "top"}
    words = re.findall(r"\b[a-z]+\b", text_lower)
    result["keywords"] = [w for w in words if w not in _STOP and len(w) > 2][:8]

    return result


def classify_intent(parsed: dict) -> str:
    """
    Classify intent as: greeting | recommendation | general | unknown.

    Returns str intent label.
    """
    text = parsed["raw"].lower().strip()

    # ── 0. Greeting check (highest priority) ──────────────────────────────────
    # Match exact single-word greetings or short greeting phrases
    text_stripped = text.rstrip("!.,?")
    if text_stripped in _GREETING_WORDS:
        return "greeting"
    # Also catch greetings at the start of a short message (≤ 4 words)
    words_in_msg = text_stripped.split()
    if len(words_in_msg) <= 4:
        for gw in _GREETING_WORDS:
            if text_stripped.startswith(gw):
                return "greeting"

    # ── 1. General question signals ───────────────────────────────────────────
    if any(phrase in text for phrase in _GENERAL_QUESTION_WORDS):
        return "general"

    # ── 2. Recommendation signals ─────────────────────────────────────────────
    has_rec_word = any(w in text for w in _RECOMMENDATION_WORDS)
    has_category = bool(parsed.get("categories"))
    has_budget   = parsed.get("budget") is not None

    if has_rec_word or has_category or has_budget:
        return "recommendation"

    # ── 3. Keyword fallback → recommendation ──────────────────────────────────
    # Single keywords like "laptop", "shoes", "shampoo" should trigger recs
    if parsed.get("keywords"):
        for kw in parsed["keywords"]:
            for cat_kws in _CATEGORY_KEYWORDS.values():
                if kw in cat_kws:
                    return "recommendation"

    return "unknown"


# ── Recommendation Bridge ─────────────────────────────────────────────────────

def get_chatbot_recommendations(parsed: dict, user_id: str, n: int = 8) -> list:
    """
    Call existing recommender functions — ZERO new recommendation logic.
    Applies budget filter AFTER prediction (same pattern as For You page).
    """
    try:
        from utils.model_loader import (
            MODELS_READY, get_hybrid_recommendations, get_cb_recommendations
        )

        if not MODELS_READY:
            return []

        cats = parsed.get("categories") or [
            "Electronics", "Home & Kitchen",
            "Clothing & Shoes", "Beauty & Personal Care"
        ]
        budget = parsed.get("budget")

        # Use hybrid by default; fall back to CB if no user_id
        if user_id and user_id != "guest":
            recs = get_hybrid_recommendations(user_id, n=n * 2, categories=cats)
        else:
            recs = get_cb_recommendations(categories=cats, n=n * 2)

        # Apply budget filter post-prediction (same as For You page — no model change)
        if budget:
            recs = [r for r in recs if float(r.get("price") or 0) <= budget]

        return recs[:n]

    except Exception as e:
        return []


# ── Grok API (optional) ───────────────────────────────────────────────────────

def _call_grok_api(query: str) -> str | None:
    """
    Call the Grok API for general questions.
    Returns None if key is missing or call fails.
    """
    try:
        import httpx
        api_key = os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY")
        if not api_key:
            return None

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type":  "application/json",
        }
        payload = {
            "model": "grok-beta",
            "messages": [
                {"role": "system", "content": (
                    "You are IntelliRec's AI assistant. Answer questions about "
                    "products, shopping, and AI recommendation systems concisely. "
                    "Keep answers under 150 words. Format with markdown when helpful."
                )},
                {"role": "user", "content": query},
            ],
            "max_tokens": 300,
            "temperature": 0.7,
        }
        resp = httpx.post(
            "https://api.x.ai/v1/chat/completions",
            json=payload, headers=headers, timeout=10.0
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception:
        return None


def _rule_based_answer(query: str) -> str:
    """High-quality rule-based answers when Grok is unavailable."""
    text = query.lower()

    # Search knowledge base
    for key, answer in _KNOWLEDGE_BASE.items():
        if key in text or key.replace(" ", "") in text.replace(" ", ""):
            return answer

    # Generic helpful response
    return (
        "I'm IntelliRec's AI assistant. I can:\n"
        "- **Recommend products** — just say *'suggest laptops under ₹50,000'*\n"
        "- **Answer questions** about collaborative filtering, content-based AI, "
        "SVD, TF-IDF, sentiment analysis, and recommendation systems\n"
        "- **Explain** why any product was recommended\n\n"
        "To get started, try: *'Best beauty products'* or "
        "*'Recommend electronics under $500'*"
    )


# ── Main Response Handler ─────────────────────────────────────────────────────

class ChatbotEngine:
    """
    Main chatbot orchestrator.

    Usage:
        engine = ChatbotEngine()
        response = engine.respond(user_text, user_id)
        # response = {"type": "recommendation"|"general"|"unknown",
        #             "text": str, "products": list}
    """

    def respond(self, user_text: str, user_id: str = "guest") -> dict:
        """
        Process a user message and return a structured response dict.
        Always wrapped in try/except — chatbot must NEVER crash the app.
        """
        try:
            if not user_text or not user_text.strip():
                return {
                    "type": "unknown",
                    "text": "Please type a message to get started!",
                    "products": [],
                }

            parsed = parse_query(user_text)
            intent = classify_intent(parsed)
            parsed["intent"] = intent

            if intent == "greeting":
                return self._handle_greeting()
            elif intent == "recommendation":
                return self._handle_recommendation(parsed, user_id)
            elif intent == "general":
                return self._handle_general(user_text)
            else:
                return self._handle_unknown(user_text)

        except Exception as e:
            return {
                "type": "error",
                "text": (
                    "I encountered an issue processing your request. "
                    "Try rephrasing — for example: *'Suggest laptops under ₹50,000'*"
                ),
                "products": [],
            }

    def _handle_greeting(self) -> dict:
        """Return a friendly, varied greeting response."""
        import random
        return {
            "type": "greeting",
            "text": random.choice(_GREETING_RESPONSES),
            "products": [],
        }

    def _handle_recommendation(self, parsed: dict, user_id: str) -> dict:
        from utils.explainer import generate_explanation, generate_chatbot_summary
        try:
            import streamlit as st
            from utils.helpers import normalize_categories
            pref_cats = normalize_categories(
                st.session_state.get("pref_cats") or
                st.session_state.get("preferred_categories") or
                []
            )
        except Exception:
            pref_cats = []

        products = get_chatbot_recommendations(parsed, user_id)

        # Attach explanations to each product
        for p in products:
            p["explanation"] = generate_explanation(p, pref_cats)

        summary = generate_chatbot_summary(products, parsed)

        if not products:
            cats = parsed.get("categories", [])
            budget = parsed.get("budget")
            msg = "I couldn't find products matching your request."
            if budget:
                msg += f" Your budget of **₹{budget:,.0f}** may be too restrictive — try increasing it."
            if cats:
                msg += f" Also check that you have **{', '.join(cats)}** in your category filters."
            msg += "\n\n💡 *Try: 'best laptops under ₹50,000' or 'top beauty products'*"
            return {"type": "recommendation", "text": msg, "products": []}

        # Prepend a warm intro to the AI-generated summary
        intro = "Here are some great options 👇\n\n"
        return {
            "type": "recommendation",
            "text": intro + summary,
            "products": products,
            "intent_info": parsed,
        }

    def _handle_general(self, text: str) -> dict:
        # Try Grok first; fall back to rule-based
        grok_answer = _call_grok_api(text)
        answer = grok_answer if grok_answer else _rule_based_answer(text)
        return {"type": "general", "text": answer, "products": []}

    def _handle_unknown(self, text: str) -> dict:
        # Try Grok first — it can handle open-ended questions better
        grok_answer = _call_grok_api(text)
        if grok_answer:
            return {"type": "general", "text": grok_answer, "products": []}

        # Smart shopping-focused fallback
        return {
            "type": "unknown",
            "text": (
                "I'm here to help with **product recommendations**, budgets, and shopping advice. 🛍️\n\n"
                "Here are some things you can ask me:\n"
                "- *'Best laptops under ₹50,000'* — budget recommendations\n"
                "- *'Suggest beauty products'* — category picks\n"
                "- *'Top gaming headphones'* — specific product search\n"
                "- *'What is collaborative filtering?'* — AI explanations\n\n"
                "Just tell me what you're looking for! 😊"
            ),
            "products": [],
        }
