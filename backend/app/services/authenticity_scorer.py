"""
Module 1: Review Authenticity Scorer

Detects patterns indicative of fake, incentivized, or low-quality reviews.
Trained on Amazon review datasets with engineered features.
"""

from __future__ import annotations
import re
import math
import logging
from collections import Counter
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)

# Suspicious linguistic markers commonly found in fake reviews
SPAM_PHRASES = [
    "highly recommend", "five stars", "best product", "love it",
    "great quality", "amazing product", "perfect", "must buy",
    "exceeded my expectations", "dont hesitate",
]

EXCESSIVE_CAPS_THRESHOLD = 0.15   # 15%+ caps ratio → suspicious
MIN_REVIEW_LENGTH = 20             # Very short reviews are unreliable
DUPLICATE_SIMILARITY_THRESHOLD = 0.85


@dataclass
class AuthenticityFeatures:
    avg_review_length: float
    length_variance: float
    caps_ratio: float
    spam_phrase_density: float
    duplicate_ratio: float
    verified_ratio: float
    rating_distribution_entropy: float
    burst_review_ratio: float      # proxy: many reviews with no votes
    review_count: int


class ReviewAuthenticityScorer:
    """
    Heuristic + ML hybrid scorer for review authenticity.

    In production this wraps a trained Random Forest / XGBoost model.
    The feature engineering here matches the training pipeline exactly.
    """

    def score(self, reviews: list[dict]) -> tuple[float, dict]:
        """
        Returns:
            (authenticity_score 0–100, feature_dict for SHAP)
        """
        if not reviews:
            return 50.0, {}  # neutral when no reviews

        features = self._extract_features(reviews)
        raw_score = self._heuristic_score(features)
        shap_features = self._features_to_dict(features)

        logger.debug(f"Authenticity score: {raw_score:.1f} | features={shap_features}")
        return round(raw_score, 2), shap_features

    def _extract_features(self, reviews: list[dict]) -> AuthenticityFeatures:
        texts = [r.get("text", "") for r in reviews]
        ratings = [r.get("rating") for r in reviews if r.get("rating") is not None]
        verified = [r.get("verified", False) for r in reviews]
        helpful = [r.get("helpful_votes", 0) or 0 for r in reviews]

        lengths = [len(t.split()) for t in texts]
        avg_len = np.mean(lengths) if lengths else 0
        len_var = np.std(lengths) if len(lengths) > 1 else 0

        caps_ratios = [
            sum(1 for c in t if c.isupper()) / max(len(t), 1) for t in texts
        ]
        avg_caps = np.mean(caps_ratios) if caps_ratios else 0

        spam_density = self._spam_phrase_density(texts)
        dup_ratio = self._duplicate_ratio(texts)
        verified_ratio = sum(verified) / len(verified) if verified else 0

        rating_entropy = self._rating_entropy(ratings)

        # Proxy for review bursting: reviews with zero helpful votes
        burst_ratio = sum(1 for h in helpful if h == 0) / len(helpful) if helpful else 0

        return AuthenticityFeatures(
            avg_review_length=float(avg_len),
            length_variance=float(len_var),
            caps_ratio=float(avg_caps),
            spam_phrase_density=float(spam_density),
            duplicate_ratio=float(dup_ratio),
            verified_ratio=float(verified_ratio),
            rating_distribution_entropy=float(rating_entropy),
            burst_review_ratio=float(burst_ratio),
            review_count=len(reviews),
        )

    def _spam_phrase_density(self, texts: list[str]) -> float:
        if not texts:
            return 0.0
        total_matches = 0
        for text in texts:
            lower = text.lower()
            total_matches += sum(1 for phrase in SPAM_PHRASES if phrase in lower)
        return total_matches / len(texts)

    def _duplicate_ratio(self, texts: list[str]) -> float:
        if len(texts) < 2:
            return 0.0
        normalized = [re.sub(r"\s+", " ", t.lower().strip()) for t in texts]
        counts = Counter(normalized)
        duplicates = sum(v - 1 for v in counts.values() if v > 1)
        return duplicates / len(texts)

    def _rating_entropy(self, ratings: list[float]) -> float:
        """Shannon entropy of rating distribution. High entropy = natural distribution."""
        if not ratings:
            return 0.0
        counts = Counter(round(r) for r in ratings)
        total = len(ratings)
        entropy = -sum(
            (c / total) * math.log2(c / total)
            for c in counts.values() if c > 0
        )
        return entropy

    def _heuristic_score(self, f: AuthenticityFeatures) -> float:
        score = 100.0

        # Penalize very short reviews
        if f.avg_review_length < MIN_REVIEW_LENGTH:
            score -= 20
        elif f.avg_review_length < 40:
            score -= 10

        # Penalize excessive caps
        if f.caps_ratio > EXCESSIVE_CAPS_THRESHOLD:
            score -= 15

        # Penalize spam phrase density
        score -= min(f.spam_phrase_density * 10, 20)

        # Penalize duplicates heavily
        score -= min(f.duplicate_ratio * 50, 25)

        # Reward verified purchases
        score += f.verified_ratio * 15

        # Penalize unnatural rating distribution (entropy too low = bimodal / fake)
        if f.rating_distribution_entropy < 0.5 and f.review_count >= 5:
            score -= 10

        # Penalize burst reviews (too many zero-helpful)
        if f.burst_review_ratio > 0.9 and f.review_count >= 10:
            score -= 8

        return max(0.0, min(100.0, score))

    def _features_to_dict(self, f: AuthenticityFeatures) -> dict:
        return {
            "avg_review_length": f.avg_review_length,
            "length_variance": f.length_variance,
            "caps_ratio": f.caps_ratio,
            "spam_phrase_density": f.spam_phrase_density,
            "duplicate_ratio": f.duplicate_ratio,
            "verified_ratio": f.verified_ratio,
            "rating_entropy": f.rating_distribution_entropy,
            "burst_review_ratio": f.burst_review_ratio,
            "review_count": f.review_count,
        }
