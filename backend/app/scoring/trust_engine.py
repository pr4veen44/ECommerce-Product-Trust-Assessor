"""
Trust Score Engine

Configurable weighted framework that combines all 5 module scores
into a single, interpretable Product Trust Score (0–100).
"""

from __future__ import annotations
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Default weights — must sum to 1.0
WEIGHTS: dict[str, float] = {
    "review_authenticity": 0.30,
    "sentiment_quality": 0.25,
    "seller_reliability": 0.20,
    "listing_quality": 0.15,
    "return_risk": 0.10,
}


@dataclass
class TrustScoreResult:
    trust_score: float
    component_contributions: dict[str, float]
    weights_used: dict[str, float]
    strengths: list[str]
    weaknesses: list[str]


class TrustScoreEngine:
    """
    Calculates the final Trust Score and derives qualitative
    strength/weakness labels from each module's output.
    """

    STRENGTH_THRESHOLD = 80.0
    WEAKNESS_THRESHOLD = 60.0

    STRENGTH_LABELS: dict[str, str] = {
        "review_authenticity": "Reviews appear authentic and trustworthy",
        "sentiment_quality": "Customers express consistently positive experiences",
        "listing_quality": "Detailed, complete product listing",
        "seller_reliability": "Seller has a strong reliability track record",
        "return_risk": "Low probability of product return",
    }

    WEAKNESS_LABELS: dict[str, str] = {
        "review_authenticity": "Some reviews show signs of inauthenticity",
        "sentiment_quality": "Mixed or negative customer sentiment detected",
        "listing_quality": "Product listing lacks detail or completeness",
        "seller_reliability": "Seller reliability data is limited or weak",
        "return_risk": "Elevated risk of product return",
    }

    @staticmethod
    def validate_weights(weights: dict[str, float]) -> None:
        required = set(WEIGHTS.keys())
        provided = set(weights.keys())
        if provided != required:
            raise ValueError(f"Weights must cover exactly: {required}")
        total = sum(weights.values())
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total:.4f}")
        for k, v in weights.items():
            if not (0.0 <= v <= 1.0):
                raise ValueError(f"Weight '{k}' must be in [0, 1], got {v}")

    @classmethod
    def calculate(
        cls,
        review_authenticity: float,
        sentiment_quality: float,
        listing_quality: float,
        seller_reliability: float,
        return_risk_score: float,
        weights: dict[str, float] | None = None,
    ) -> TrustScoreResult:
        """
        Compute the weighted Trust Score from 5 module outputs.

        All inputs are expected in range [0, 100].
        Return risk is inverted (lower raw risk → higher score contribution).
        """
        w = weights or WEIGHTS

        scores = {
            "review_authenticity": review_authenticity,
            "sentiment_quality": sentiment_quality,
            "listing_quality": listing_quality,
            "seller_reliability": seller_reliability,
            "return_risk": return_risk_score,
        }

        contributions = {k: scores[k] * w[k] for k in w}
        trust_score = round(sum(contributions.values()), 2)
        trust_score = max(0.0, min(100.0, trust_score))

        strengths: list[str] = []
        weaknesses: list[str] = []

        for key, score in scores.items():
            if score >= cls.STRENGTH_THRESHOLD:
                strengths.append(cls.STRENGTH_LABELS[key])
            elif score < cls.WEAKNESS_THRESHOLD:
                weaknesses.append(cls.WEAKNESS_LABELS[key])

        logger.debug(
            f"Trust score calculated: {trust_score:.1f} | "
            f"contributions={contributions}"
        )

        return TrustScoreResult(
            trust_score=trust_score,
            component_contributions=contributions,
            weights_used=w,
            strengths=strengths,
            weaknesses=weaknesses,
        )
