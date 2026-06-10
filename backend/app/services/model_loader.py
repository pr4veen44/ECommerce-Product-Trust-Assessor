"""
Model Loader

Handles loading of all serialized ML models at startup.
Uses a singleton pattern — models stay in memory for the lifetime of the process.
"""

from __future__ import annotations
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).parent.parent.parent / "models"


class ModelLoader:
    """
    Centralized model registry.

    In production, each module's model is loaded from disk (joblib / safetensors).
    Falls back gracefully to heuristic scorers if model files are absent.
    """

    _registry: dict[str, object] = {}

    @classmethod
    def load_all(cls) -> None:
        cls._load_authenticity_model()
        cls._load_sentiment_model()
        cls._load_listing_model()
        cls._load_seller_model()
        cls._load_return_risk_model()

    @classmethod
    def get(cls, name: str):
        return cls._registry.get(name)

    @classmethod
    def _load_authenticity_model(cls):
        path = MODELS_DIR / "authenticity" / "rf_authenticity.joblib"
        cls._try_load_joblib("authenticity", path)

    @classmethod
    def _load_sentiment_model(cls):
        # DistilBERT is loaded lazily inside sentiment_scorer.py
        logger.info("Sentiment model: lazy-loaded on first inference.")

    @classmethod
    def _load_listing_model(cls):
        path = MODELS_DIR / "listing" / "listing_quality.joblib"
        cls._try_load_joblib("listing", path)

    @classmethod
    def _load_seller_model(cls):
        path = MODELS_DIR / "seller" / "xgb_seller.joblib"
        cls._try_load_joblib("seller", path)

    @classmethod
    def _load_return_risk_model(cls):
        path = MODELS_DIR / "return_risk" / "lgbm_return_risk.joblib"
        cls._try_load_joblib("return_risk", path)

    @classmethod
    def _try_load_joblib(cls, name: str, path: Path) -> None:
        if path.exists():
            try:
                import joblib
                model = joblib.load(path)
                cls._registry[name] = model
                logger.info(f"Loaded model '{name}' from {path}")
            except Exception as e:
                logger.warning(f"Failed to load model '{name}': {e}. Using heuristic fallback.")
        else:
            logger.info(f"Model '{name}' not found at {path}. Using heuristic fallback.")
