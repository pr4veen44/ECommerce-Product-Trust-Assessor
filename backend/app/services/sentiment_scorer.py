"""
Module 2: Review Sentiment Quality Scorer

Uses DistilBERT for sentiment classification of review texts.
Aggregates per-review sentiment into a 0–100 quality score.
"""

from __future__ import annotations
import logging
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)

# Lazy import to avoid loading model until first use
_pipeline = None


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        try:
            from transformers import pipeline
            _pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                truncation=True,
                max_length=512,
                batch_size=16,
            )
            logger.info("DistilBERT sentiment pipeline loaded.")
        except Exception as e:
            logger.warning(f"Transformers not available, using fallback: {e}")
            _pipeline = None
    return _pipeline


@dataclass
class SentimentResult:
    positive_ratio: float
    negative_ratio: float
    neutral_ratio: float
    avg_confidence: float
    sentiment_variance: float
    review_count: int


class SentimentQualityScorer:
    """
    Scores the overall sentiment quality of a product's reviews.

    - Uses DistilBERT in production
    - Falls back to lexicon-based VADER-style scoring if model unavailable
    """

    POSITIVE_KEYWORDS = [
        "excellent", "great", "perfect", "love", "amazing", "fantastic",
        "wonderful", "outstanding", "superb", "brilliant", "delighted",
        "satisfied", "recommend", "happy", "pleased",
    ]
    NEGATIVE_KEYWORDS = [
        "terrible", "awful", "horrible", "broken", "damaged", "waste",
        "disappointed", "regret", "refund", "return", "defective",
        "poor", "bad", "cheap", "useless", "scam",
    ]

    def score(self, reviews: list[dict]) -> tuple[float, dict]:
        """
        Returns:
            (sentiment_score 0–100, feature_dict for SHAP)
        """
        if not reviews:
            return 50.0, {}

        texts = [r.get("text", "") for r in reviews if r.get("text")]
        if not texts:
            return 50.0, {}

        pipeline = _get_pipeline()
        if pipeline is not None:
            result = self._bert_score(texts, pipeline)
        else:
            result = self._lexicon_score(texts)

        score = self._aggregate_score(result)
        features = {
            "positive_ratio": result.positive_ratio,
            "negative_ratio": result.negative_ratio,
            "avg_confidence": result.avg_confidence,
            "sentiment_variance": result.sentiment_variance,
        }
        return round(score, 2), features

    def _bert_score(self, texts: list[str], pipeline) -> SentimentResult:
        """Run DistilBERT sentiment on all review texts."""
        truncated = [t[:512] for t in texts]
        try:
            predictions = pipeline(truncated)
        except Exception as e:
            logger.warning(f"BERT inference failed: {e}. Falling back to lexicon.")
            return self._lexicon_score(texts)

        positives = [p for p in predictions if p["label"] == "POSITIVE"]
        negatives = [p for p in predictions if p["label"] == "NEGATIVE"]
        confidences = [p["score"] for p in predictions]

        n = len(predictions)
        pos_ratio = len(positives) / n
        neg_ratio = len(negatives) / n
        avg_conf = float(np.mean(confidences))
        variance = float(np.std([
            p["score"] if p["label"] == "POSITIVE" else 1 - p["score"]
            for p in predictions
        ]))

        return SentimentResult(
            positive_ratio=pos_ratio,
            negative_ratio=neg_ratio,
            neutral_ratio=0.0,
            avg_confidence=avg_conf,
            sentiment_variance=variance,
            review_count=n,
        )

    def _lexicon_score(self, texts: list[str]) -> SentimentResult:
        """Keyword-based fallback sentiment scorer."""
        scores = []
        for text in texts:
            lower = text.lower()
            pos = sum(1 for kw in self.POSITIVE_KEYWORDS if kw in lower)
            neg = sum(1 for kw in self.NEGATIVE_KEYWORDS if kw in lower)
            if pos + neg == 0:
                scores.append(0.5)
            else:
                scores.append(pos / (pos + neg))

        pos_ratio = sum(1 for s in scores if s > 0.6) / len(scores)
        neg_ratio = sum(1 for s in scores if s < 0.4) / len(scores)
        neutral_ratio = 1 - pos_ratio - neg_ratio

        return SentimentResult(
            positive_ratio=pos_ratio,
            negative_ratio=neg_ratio,
            neutral_ratio=max(0, neutral_ratio),
            avg_confidence=float(np.mean(scores)),
            sentiment_variance=float(np.std(scores)),
            review_count=len(texts),
        )

    def _aggregate_score(self, result: SentimentResult) -> float:
        """
        Convert sentiment statistics into a 0–100 quality score.

        High positive ratio + low variance = high trust signal.
        """
        base = result.positive_ratio * 100

        # Penalize high variance (inconsistent customer experiences)
        variance_penalty = result.sentiment_variance * 20
        score = base - variance_penalty

        # Small bonus for high confidence predictions
        if result.avg_confidence > 0.85:
            score += 5

        return max(0.0, min(100.0, score))
