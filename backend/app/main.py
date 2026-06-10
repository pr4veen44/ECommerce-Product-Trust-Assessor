"""
ECommerce Product Trust Assessor - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.routes import router
from app.services.model_loader import ModelLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load ML models on startup."""
    logger.info("Loading ML models...")
    ModelLoader.load_all()
    logger.info("All models loaded successfully.")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="ECommerce Product Trust Assessor",
    description="Explainable AI system for analyzing product trustworthiness",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
