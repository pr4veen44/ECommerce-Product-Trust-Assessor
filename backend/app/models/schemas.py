"""
Pydantic schemas for API request and response validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum


class ReturnRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ReviewInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    verified: Optional[bool] = None
    helpful_votes: Optional[int] = Field(None, ge=0)

    model_config = {"str_strip_whitespace": True}


class SellerInfo(BaseModel):
    seller_id: Optional[str] = None
    avg_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    total_orders: Optional[int] = Field(None, ge=0)
    cancellation_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    avg_delivery_days: Optional[float] = Field(None, ge=0.0)


class ProductAnalysisRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    description: str = Field(..., min_length=10, max_length=10000)
    category: Optional[str] = Field(None, max_length=100)
    price: Optional[float] = Field(None, ge=0.0)
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    reviews: list[ReviewInput] = Field(default_factory=list, max_length=200)
    seller: Optional[SellerInfo] = None

    @field_validator("reviews")
    @classmethod
    def validate_reviews(cls, v):
        if len(v) > 200:
            raise ValueError("Maximum 200 reviews allowed per analysis")
        return v

    model_config = {"str_strip_whitespace": True}


class SHAPExplanation(BaseModel):
    feature: str
    impact: float
    direction: str  # "positive" | "negative"


class ScoreBreakdown(BaseModel):
    review_authenticity: float = Field(..., ge=0, le=100)
    sentiment_quality: float = Field(..., ge=0, le=100)
    listing_quality: float = Field(..., ge=0, le=100)
    seller_reliability: float = Field(..., ge=0, le=100)
    return_risk_score: float = Field(..., ge=0, le=100)


class ProductAnalysisResponse(BaseModel):
    trust_score: float = Field(..., ge=0, le=100)
    breakdown: ScoreBreakdown
    return_risk: ReturnRisk
    strengths: list[str]
    weaknesses: list[str]
    shap_explanations: list[SHAPExplanation]
    confidence: float = Field(..., ge=0.0, le=1.0)
    review_count_analyzed: int
    model_version: str = "1.0.0"
