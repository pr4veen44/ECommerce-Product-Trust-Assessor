"""
API Routes - REST endpoints for product trust analysis.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import logging
import time

from app.models.schemas import ProductAnalysisRequest, ProductAnalysisResponse
from app.services.trust_analyzer import TrustAnalyzer

logger = logging.getLogger(__name__)
router = APIRouter()
analyzer = TrustAnalyzer()


@router.post("/analyze", response_model=ProductAnalysisResponse)
async def analyze_product(
    request: ProductAnalysisRequest,
    background_tasks: BackgroundTasks,
) -> ProductAnalysisResponse:
    """
    Analyze a product and return a comprehensive Trust Score with explanations.

    - Runs all 5 ML scoring modules in parallel
    - Returns SHAP-based explanations for every prediction
    - Identifies strengths and weaknesses automatically
    """
    start = time.perf_counter()

    try:
        result = await analyzer.analyze(request)
        elapsed = time.perf_counter() - start
        logger.info(
            f"Analysis completed | trust_score={result.trust_score:.1f} | "
            f"latency={elapsed:.3f}s | reviews={result.review_count_analyzed}"
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error during analysis")
        raise HTTPException(status_code=500, detail="Analysis failed. Please try again.")


@router.get("/categories")
async def list_categories():
    """Return supported product categories for the UI dropdown."""
    return {
        "categories": [
            "Electronics",
            "Clothing & Apparel",
            "Home & Kitchen",
            "Books",
            "Sports & Outdoors",
            "Beauty & Personal Care",
            "Toys & Games",
            "Automotive",
            "Health & Wellness",
            "Food & Grocery",
            "Tools & Hardware",
            "Other",
        ]
    }


@router.get("/weights")
async def get_scoring_weights():
    """Return current Trust Score component weights."""
    from app.scoring.trust_engine import WEIGHTS
    return {"weights": WEIGHTS}


@router.post("/weights")
async def update_scoring_weights(weights: dict[str, float]):
    """Update Trust Score component weights (admin use)."""
    from app.scoring.trust_engine import TrustScoreEngine
    try:
        TrustScoreEngine.validate_weights(weights)
        return {"status": "updated", "weights": weights}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
