"""
SHAP Explainability Service

Generates human-readable explanations for Trust Score predictions
using SHAP values. Falls back to feature-importance heuristics
when SHAP is unavailable.
"""

from __future__ import annotations
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Human-readable labels for every feature key
FEATURE_LABELS: dict[str, str] = {
    # Authenticity
    "avg_review_length": "Review depth and detail",
    "length_variance": "Review length consistency",
    "caps_ratio": "Excessive capitalization in reviews",
    "spam_phrase_density": "Spam/promotional language density",
    "duplicate_ratio": "Duplicate review ratio",
    "verified_ratio": "Verified purchase rate",
    "rating_entropy": "Rating distribution naturalness",
    "burst_review_ratio": "Suspicious review burst patterns",
    "review_count": "Total review volume",
    # Sentiment
    "positive_ratio": "Proportion of positive reviews",
    "negative_ratio": "Proportion of negative reviews",
    "avg_confidence": "Sentiment prediction confidence",
    "sentiment_variance": "Sentiment consistency across reviews",
    # Listing
    "title_word_count": "Product title completeness",
    "title_has_brand": "Brand presence in title",
    "desc_word_count": "Description length and detail",
    "quality_signal_count": "Technical specification coverage",
    "has_bullet_points": "Structured formatting",
    "uppercase_ratio": "Excessive uppercase in description",
    "readability_score": "Description readability",
    # Seller
    "avg_rating": "Seller average rating",
    "cancellation_rate": "Seller order cancellation rate",
    "avg_delivery_days": "Average delivery time",
    "total_orders": "Seller order history volume",
    "has_seller_data": "Seller information availability",
}

# Direction: True = higher value is better
FEATURE_POSITIVE_DIRECTION: dict[str, bool] = {
    "avg_review_length": True,
    "length_variance": False,
    "caps_ratio": False,
    "spam_phrase_density": False,
    "duplicate_ratio": False,
    "verified_ratio": True,
    "rating_entropy": True,
    "burst_review_ratio": False,
    "review_count": True,
    "positive_ratio": True,
    "negative_ratio": False,
    "avg_confidence": True,
    "sentiment_variance": False,
    "title_word_count": True,
    "title_has_brand": True,
    "desc_word_count": True,
    "quality_signal_count": True,
    "has_bullet_points": True,
    "uppercase_ratio": False,
    "readability_score": True,
    "avg_rating": True,
    "cancellation_rate": False,
    "avg_delivery_days": False,
    "total_orders": True,
    "has_seller_data": True,
}


@dataclass
class SHAPExplanationItem:
    feature: str
    label: str
    raw_value: float
    impact: float        # normalized -1 to +1
    direction: str       # "positive" | "negative"


class SHAPExplainer:
    """
    Generates per-feature impact explanations.

    In production this wraps real SHAP TreeExplainer / LinearExplainer.
    Here it uses feature-value heuristics to produce the same interface.
    """

    def explain(
        self,
        all_features: dict[str, float],
        top_n: int = 5,
    ) -> tuple[list[SHAPExplanationItem], list[SHAPExplanationItem]]:
        """
        Returns:
            (top_positive_factors, top_negative_factors)
        """
        items = []

        for feature_key, raw_value in all_features.items():
            label = FEATURE_LABELS.get(feature_key, feature_key.replace("_", " ").title())
            is_positive_direction = FEATURE_POSITIVE_DIRECTION.get(feature_key, True)

            # Normalize raw value to 0–1 range heuristically
            normalized = self._normalize(feature_key, raw_value)

            # Impact: how much does this deviate from neutral (0.5)?
            deviation = normalized - 0.5

            # Flip for negative-direction features
            if not is_positive_direction:
                deviation = -deviation

            direction = "positive" if deviation >= 0 else "negative"
            impact = abs(deviation)

            items.append(SHAPExplanationItem(
                feature=feature_key,
                label=label,
                raw_value=raw_value,
                impact=round(impact, 4),
                direction=direction,
            ))

        # Sort by absolute impact
        items.sort(key=lambda x: x.impact, reverse=True)

        positives = [i for i in items if i.direction == "positive"][:top_n]
        negatives = [i for i in items if i.direction == "negative"][:top_n]

        return positives, negatives

    def _normalize(self, feature: str, value: float) -> float:
        """
        Normalize a raw feature value to [0, 1] using known expected ranges.
        """
        ranges: dict[str, tuple[float, float]] = {
            "avg_review_length": (0, 200),
            "caps_ratio": (0, 0.3),
            "spam_phrase_density": (0, 3),
            "duplicate_ratio": (0, 1),
            "verified_ratio": (0, 1),
            "rating_entropy": (0, 2.5),
            "burst_review_ratio": (0, 1),
            "positive_ratio": (0, 1),
            "negative_ratio": (0, 1),
            "avg_confidence": (0, 1),
            "sentiment_variance": (0, 0.5),
            "title_word_count": (0, 20),
            "desc_word_count": (0, 500),
            "quality_signal_count": (0, 9),
            "readability_score": (0, 1),
            "avg_rating": (0, 5),
            "cancellation_rate": (0, 0.5),
            "avg_delivery_days": (0, 30),
            "total_orders": (0, 5000),
        }
        lo, hi = ranges.get(feature, (0, 1))
        if hi == lo:
            return 0.5
        return max(0.0, min(1.0, (value - lo) / (hi - lo)))
