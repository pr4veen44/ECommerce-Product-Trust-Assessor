"""
Trust Analyzer — Orchestrator

Coordinates all 5 scoring modules and the SHAP explainer,
then assembles the final ProductAnalysisResponse.
"""

from __future__ import annotations
import asyncio
import logging
from functools import partial

from app.models.schemas import (
    ProductAnalysisRequest,
    ProductAnalysisResponse,
    ScoreBreakdown,
    SHAPExplanation,
    ReturnRisk,
)
from app.services.authenticity_scorer import ReviewAuthenticityScorer
from app.services.sentiment_scorer import SentimentQualityScorer
from app.services.listing_scorer import ListingQualityScorer
from app.services.seller_return_scorer import SellerReliabilityScorer, ReturnRiskPredictor
from app.services.shap_explainer import SHAPExplainer
from app.scoring.trust_engine import TrustScoreEngine

logger = logging.getLogger(__name__)


class TrustAnalyzer:
    """
    Single entry-point for running a full product trust analysis.

    Runs CPU-bound scorers in a thread pool to keep the async event loop free.
    """

    def __init__(self):
        self.authenticity = ReviewAuthenticityScorer()
        self.sentiment = SentimentQualityScorer()
        self.listing = ListingQualityScorer()
        self.seller = SellerReliabilityScorer()
        self.return_risk = ReturnRiskPredictor()
        self.explainer = SHAPExplainer()

    async def analyze(self, req: ProductAnalysisRequest) -> ProductAnalysisResponse:
        loop = asyncio.get_event_loop()

        reviews_dicts = [r.model_dump() for r in req.reviews]
        seller_dict = req.seller.model_dump() if req.seller else None

        # Run scoring modules concurrently in thread pool
        (
            (auth_score, auth_features),
            (sent_score, sent_features),
            (list_score, list_features),
            (sel_score, sel_features),
        ) = await asyncio.gather(
            loop.run_in_executor(None, partial(self.authenticity.score, reviews_dicts)),
            loop.run_in_executor(None, partial(self.sentiment.score, reviews_dicts)),
            loop.run_in_executor(
                None,
                partial(self.listing.score, req.title, req.description, req.category),
            ),
            loop.run_in_executor(None, partial(self.seller.score, seller_dict)),
        )

        # Return risk uses outputs from other modules
        ret_score, risk_class = self.return_risk.score(
            category=req.category,
            price=req.price,
            product_rating=req.rating,
            sentiment_score=sent_score,
            seller_reliability=sel_score,
        )

        # Calculate final Trust Score
        engine_result = TrustScoreEngine.calculate(
            review_authenticity=auth_score,
            sentiment_quality=sent_score,
            listing_quality=list_score,
            seller_reliability=sel_score,
            return_risk_score=ret_score,
        )

        # Build combined feature dict for SHAP
        all_features = {
            **auth_features,
            **sent_features,
            **list_features,
            **sel_features,
        }

        positives, negatives = self.explainer.explain(all_features, top_n=5)

        shap_items = [
            SHAPExplanation(
                feature=item.label,
                impact=item.impact,
                direction=item.direction,
            )
            for item in (positives + negatives)
        ]

        # Confidence: proxy based on review count and data completeness
        confidence = self._estimate_confidence(len(req.reviews), seller_dict is not None)

        return ProductAnalysisResponse(
            trust_score=engine_result.trust_score,
            breakdown=ScoreBreakdown(
                review_authenticity=auth_score,
                sentiment_quality=sent_score,
                listing_quality=list_score,
                seller_reliability=sel_score,
                return_risk_score=ret_score,
            ),
            return_risk=ReturnRisk(risk_class),
            strengths=engine_result.strengths,
            weaknesses=engine_result.weaknesses,
            shap_explanations=shap_items,
            confidence=confidence,
            review_count_analyzed=len(req.reviews),
        )

    def _estimate_confidence(self, review_count: int, has_seller: bool) -> float:
        base = 0.5
        if review_count >= 50:
            base += 0.3
        elif review_count >= 10:
            base += 0.2
        elif review_count >= 3:
            base += 0.1
        if has_seller:
            base += 0.1
        return min(1.0, round(base, 2))
