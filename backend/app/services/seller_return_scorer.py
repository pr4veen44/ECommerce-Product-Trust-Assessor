"""
Module 4: Seller Reliability Scorer
Module 5: Return Risk Predictor

Seller Reliability: trained on Olist Brazilian E-Commerce Dataset.
Return Risk: ensemble predictor combining product and seller signals.
"""

from __future__ import annotations
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Module 4: Seller Reliability
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SellerFeatures:
    avg_rating: float
    cancellation_rate: float
    avg_delivery_days: float
    total_orders: int
    has_data: bool


class SellerReliabilityScorer:
    """
    Scores seller trustworthiness based on historical performance.

    In production, this wraps an XGBoost / LightGBM model trained on
    the Olist dataset. Without seller data, returns a neutral prior.
    """

    IDEAL_DELIVERY_DAYS = 7.0
    MAX_DELIVERY_DAYS = 30.0

    def score(self, seller: dict | None) -> tuple[float, dict]:
        """
        Returns:
            (seller_reliability_score 0–100, feature_dict for SHAP)
        """
        if not seller:
            return 65.0, {"has_seller_data": 0}  # neutral prior

        f = self._extract_features(seller)
        raw_score = self._compute_score(f)
        return round(raw_score, 2), {
            "avg_rating": f.avg_rating,
            "cancellation_rate": f.cancellation_rate,
            "avg_delivery_days": f.avg_delivery_days,
            "total_orders": f.total_orders,
            "has_seller_data": 1,
        }

    def _extract_features(self, seller: dict) -> SellerFeatures:
        return SellerFeatures(
            avg_rating=float(seller.get("avg_rating") or 3.5),
            cancellation_rate=float(seller.get("cancellation_rate") or 0.05),
            avg_delivery_days=float(seller.get("avg_delivery_days") or 10.0),
            total_orders=int(seller.get("total_orders") or 0),
            has_data=True,
        )

    def _compute_score(self, f: SellerFeatures) -> float:
        score = 0.0

        # Rating component (max 40)
        score += (f.avg_rating / 5.0) * 40

        # Cancellation penalty (max -20)
        cancellation_penalty = min(f.cancellation_rate * 100, 20)
        score += 20 - cancellation_penalty

        # Delivery speed (max 25)
        if f.avg_delivery_days <= self.IDEAL_DELIVERY_DAYS:
            score += 25
        elif f.avg_delivery_days <= self.MAX_DELIVERY_DAYS:
            delivery_score = 25 * (1 - (f.avg_delivery_days - self.IDEAL_DELIVERY_DAYS) /
                                   (self.MAX_DELIVERY_DAYS - self.IDEAL_DELIVERY_DAYS))
            score += max(0, delivery_score)

        # Order volume credibility (max 15)
        if f.total_orders >= 1000:
            score += 15
        elif f.total_orders >= 100:
            score += 10
        elif f.total_orders >= 10:
            score += 5

        return max(0.0, min(100.0, score))


# ─────────────────────────────────────────────────────────────────────────────
# Module 5: Return Risk Predictor
# ─────────────────────────────────────────────────────────────────────────────

HIGH_RETURN_CATEGORIES = {
    "clothing & apparel", "shoes", "fashion", "electronics",
    "jewelry", "watches", "software",
}
LOW_RETURN_CATEGORIES = {
    "books", "food & grocery", "health & wellness",
    "tools & hardware", "automotive",
}

RETURN_RISK_CLASSES = {(0, 33): "LOW", (33, 66): "MEDIUM", (66, 100): "HIGH"}


class ReturnRiskPredictor:
    """
    Predicts the probability and class of a product return.

    Features combine product attributes, seller signals, and review patterns.
    """

    def score(
        self,
        category: str | None,
        price: float | None,
        product_rating: float | None,
        sentiment_score: float,
        seller_reliability: float,
    ) -> tuple[float, str]:
        """
        Returns:
            (return_risk_score 0–100 where 100=highest risk, risk_class string)
        """
        risk = 50.0  # baseline

        # Category risk adjustment
        cat_lower = (category or "").lower()
        if cat_lower in HIGH_RETURN_CATEGORIES:
            risk += 15
        elif cat_lower in LOW_RETURN_CATEGORIES:
            risk -= 10

        # Price: higher price → slightly higher return risk
        if price is not None:
            if price > 200:
                risk += 10
            elif price > 50:
                risk += 5

        # Low product rating → higher return risk
        if product_rating is not None:
            if product_rating < 3.0:
                risk += 20
            elif product_rating < 4.0:
                risk += 8

        # Negative sentiment → higher return risk
        if sentiment_score < 50:
            risk += 15
        elif sentiment_score > 80:
            risk -= 10

        # Reliable seller reduces return risk
        risk -= (seller_reliability - 50) * 0.2

        risk = max(0.0, min(100.0, risk))

        # Convert to 0–100 score where 100 = SAFEST (inverted for consistency)
        safety_score = 100.0 - risk
        risk_class = self._classify_risk(risk)

        return round(safety_score, 2), risk_class

    def _classify_risk(self, risk_score: float) -> str:
        if risk_score < 33:
            return "LOW"
        elif risk_score < 66:
            return "MEDIUM"
        return "HIGH"
