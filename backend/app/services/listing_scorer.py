"""
Module 3: Product Listing Quality Scorer

Evaluates the quality and completeness of a product listing
using NLP-based readability, completeness, and structure metrics.
"""

from __future__ import annotations
import re
import logging
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)

# Minimum acceptable lengths (in words)
MIN_TITLE_WORDS = 4
GOOD_TITLE_WORDS = 8
MIN_DESC_WORDS = 30
GOOD_DESC_WORDS = 100

# High-quality listing indicators
QUALITY_SIGNALS = [
    r"\d+\s*(inch|cm|mm|kg|lb|oz|watt|volt|amp|liter|ml)",  # measurements
    r"material[:\s]",        # material info
    r"dimension[s]?[:\s]",   # dimensions
    r"warranty",             # warranty info
    r"compatible with",      # compatibility
    r"package include[s]?",  # package contents
    r"what[']?s in the box",
    r"feature[s]?[:\s]",
    r"specification[s]?",
]

READABILITY_STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to",
    "for", "of", "with", "by", "from", "as", "is", "was", "are",
}


@dataclass
class ListingFeatures:
    title_word_count: int
    title_has_brand: bool
    title_has_model: bool
    desc_word_count: int
    desc_sentence_count: int
    avg_sentence_length: float
    quality_signal_count: int
    has_bullet_points: bool
    uppercase_ratio: float
    readability_score: float


class ListingQualityScorer:
    """
    Scores product listing completeness and quality.

    Evaluates: title, description, formatting, readability, keyword coverage.
    """

    def score(self, title: str, description: str, category: str | None = None) -> tuple[float, dict]:
        """
        Returns:
            (listing_quality_score 0–100, feature_dict for SHAP)
        """
        features = self._extract_features(title, description)
        raw_score = self._compute_score(features)
        feature_dict = self._features_to_dict(features)
        return round(raw_score, 2), feature_dict

    def _extract_features(self, title: str, description: str) -> ListingFeatures:
        # Title analysis
        title_words = title.split()
        title_has_brand = bool(re.search(r"^[A-Z][a-z]+\s", title))
        title_has_model = bool(re.search(r"[A-Z0-9]{2,}-?[A-Z0-9]{2,}", title))

        # Description analysis
        sentences = re.split(r"[.!?]+", description)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
        desc_words = description.split()
        avg_sent_len = (
            float(np.mean([len(s.split()) for s in sentences]))
            if sentences else 0.0
        )

        # Quality signals
        desc_lower = description.lower()
        quality_count = sum(
            1 for pattern in QUALITY_SIGNALS
            if re.search(pattern, desc_lower)
        )

        # Bullet points
        has_bullets = bool(re.search(r"(^[\-\*\•]|\n[\-\*\•])", description, re.MULTILINE))

        # Uppercase ratio (all-caps words are spammy)
        words = description.split()
        uppercase_words = sum(1 for w in words if w.isupper() and len(w) > 2)
        uppercase_ratio = uppercase_words / max(len(words), 1)

        # Flesch-Kincaid inspired readability
        readability = self._readability_score(description)

        return ListingFeatures(
            title_word_count=len(title_words),
            title_has_brand=title_has_brand,
            title_has_model=title_has_model,
            desc_word_count=len(desc_words),
            desc_sentence_count=len(sentences),
            avg_sentence_length=avg_sent_len,
            quality_signal_count=quality_count,
            has_bullet_points=has_bullets,
            uppercase_ratio=uppercase_ratio,
            readability_score=readability,
        )

    def _readability_score(self, text: str) -> float:
        """Simplified Flesch Reading Ease (normalized 0–1)."""
        words = text.split()
        if not words:
            return 0.0
        sentences = max(1, len(re.split(r"[.!?]+", text)))
        syllables = sum(self._count_syllables(w) for w in words)

        flesch = 206.835 - 1.015 * (len(words) / sentences) - 84.6 * (syllables / len(words))
        return max(0.0, min(1.0, flesch / 100))

    def _count_syllables(self, word: str) -> int:
        word = word.lower()
        vowels = "aeiouy"
        count = sum(1 for i, c in enumerate(word) if c in vowels and (i == 0 or word[i - 1] not in vowels))
        return max(1, count)

    def _compute_score(self, f: ListingFeatures) -> float:
        score = 0.0

        # Title scoring (max 25)
        if f.title_word_count >= GOOD_TITLE_WORDS:
            score += 25
        elif f.title_word_count >= MIN_TITLE_WORDS:
            score += 15
        else:
            score += 5
        if f.title_has_brand:
            score += 3
        if f.title_has_model:
            score += 2

        # Description scoring (max 40)
        if f.desc_word_count >= GOOD_DESC_WORDS:
            score += 40
        elif f.desc_word_count >= MIN_DESC_WORDS:
            score += 25
        else:
            score += 10

        # Quality signals (max 20)
        score += min(f.quality_signal_count * 4, 20)

        # Structure bonus (max 10)
        if f.has_bullet_points:
            score += 5
        if 10 <= f.avg_sentence_length <= 25:
            score += 5

        # Penalties
        if f.uppercase_ratio > 0.2:
            score -= 10

        # Readability bonus (max 5)
        score += f.readability_score * 5

        return max(0.0, min(100.0, score))

    def _features_to_dict(self, f: ListingFeatures) -> dict:
        return {
            "title_word_count": f.title_word_count,
            "title_has_brand": int(f.title_has_brand),
            "desc_word_count": f.desc_word_count,
            "quality_signal_count": f.quality_signal_count,
            "has_bullet_points": int(f.has_bullet_points),
            "uppercase_ratio": f.uppercase_ratio,
            "readability_score": f.readability_score,
        }
