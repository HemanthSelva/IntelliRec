"""
utils/explainer.py
IntelliRec — Shared Explanation Engine v1.0
Used by 02_For_You.py cards AND 08_AI_Assistant.py chatbot.
"""

from datetime import datetime


def _get_time_context() -> str:
    h = datetime.now().hour
    if h < 6:   return "late_night"
    elif h < 12: return "morning"
    elif h < 17: return "afternoon"
    elif h < 21: return "evening"
    else:        return "night"


_CONTEXT_AFFINITY = {
    "morning":    ["Electronics", "Books", "Sports"],
    "afternoon":  ["Electronics", "Home & Kitchen", "Clothing & Shoes"],
    "evening":    ["Home & Kitchen", "Beauty & Personal Care", "Books"],
    "night":      ["Beauty & Personal Care", "Home & Kitchen"],
    "late_night": ["Electronics", "Books"],
}

_ENGINE_OPENERS = {
    "Collaborative Filtering": [
        "Users with similar tastes love this —",
        "Popular among shoppers like you —",
        "Your twin shoppers gave this high marks —",
    ],
    "Content-Based": [
        "Matches your category interest perfectly —",
        "Top pick in your preferred category —",
    ],
    "Hybrid": [
        "Our AI engines unanimously picked this —",
        "Cross-validated by 3 recommendation engines —",
    ],
}

_SENTIMENT_PHRASES = {
    "Positive": ["buyers consistently praise it", "customers love this product"],
    "Mixed":    ["most buyers find good value", "reviews lean positive overall"],
    "Critical": ["selected for its technical merits"],
    "Negative": ["selected based on category relevance"],
}


def _rating_label(r: float) -> str:
    if r >= 4.7: return "exceptional"
    elif r >= 4.5: return "outstanding"
    elif r >= 4.0: return "highly rated"
    elif r >= 3.5: return "well-reviewed"
    return "reviewed"


def _price_label(p: float) -> str:
    if p == 0:   return None
    elif p < 20:  return "budget-friendly"
    elif p < 100: return "mid-range"
    elif p < 500: return "premium"
    return "professional-grade"


def generate_explanation(product: dict, user_prefs: list = None, idx: int = 0) -> str:
    """Generate a rich, product-specific explanation for a card or chatbot."""
    try:
        pid      = str(product.get("product_id") or product.get("asin") or "")
        engine   = product.get("engine", "Hybrid")
        sent     = product.get("sentiment_label", "Mixed")
        rating   = float(product.get("rating") or product.get("predicted_rating") or 3.5)
        price    = float(product.get("price") or 0)
        category = product.get("category", "")

        # Use index to seed variation robustly across products
        seed = abs(hash(pid) + idx * 31)

        openers  = _ENGINE_OPENERS.get(engine, _ENGINE_OPENERS["Hybrid"])
        opener   = openers[seed % len(openers)]
        phrases  = _SENTIMENT_PHRASES.get(sent, _SENTIMENT_PHRASES["Mixed"])
        s_phrase = phrases[(seed + 1) % len(phrases)]

        parts = [opener, f"it's {_rating_label(rating)} (★{rating:.1f}) and {s_phrase}."]

        if user_prefs and category in user_prefs:
            parts.append(f"It's in your favourite {category} category.")

        p_label = _price_label(price)
        if p_label:
            parts.append(f"A {p_label} option at ${price:.0f}.")

        ctx = _get_time_context()
        if category in _CONTEXT_AFFINITY.get(ctx, []):
            notes = {
                "morning": "a great way to start your day.",
                "afternoon": "perfect for this time of day.",
                "evening": "ideal for your evening.",
                "night": "a relaxing evening pick.",
                "late_night": "for the night owls.",
            }
            # Only append time notes occasionally (1 in 3 chance) to avoid repetitiveness
            if seed % 3 == 0:
                parts.append(notes.get(ctx, "a timely pick."))

        return " ".join(parts)
    except Exception:
        return "Recommended by our AI engines based on your preferences."


def generate_chatbot_summary(products: list, intent_info: dict) -> str:
    """Generate a conversational header for chatbot recommendation responses."""
    try:
        count  = len(products)
        cats   = intent_info.get("categories", [])
        budget = intent_info.get("budget")

        if count == 0:
            return "I couldn't find any products matching your request. Try broadening your criteria."

        cat_str = " & ".join(cats) if cats else "your interest"
        lines   = [f"Found **{count} recommendation{'s' if count > 1 else ''}** for {cat_str}."]

        if budget:
            lines.append(f"All results are within your **${budget:,.0f}** budget.")

        ratings = [float(p.get("rating") or p.get("predicted_rating") or 0) for p in products]
        valid   = [r for r in ratings if r > 0]
        if valid:
            lines.append(f"Average rating: **★ {sum(valid)/len(valid):.1f}**.")

        pos = sum(1 for p in products if p.get("sentiment_label") == "Positive")
        if pos >= count * 0.6:
            lines.append(f"**{pos} of {count}** have positive community sentiment.")

        return " ".join(lines)
    except Exception:
        return f"Here are {len(products)} recommendations for you."
