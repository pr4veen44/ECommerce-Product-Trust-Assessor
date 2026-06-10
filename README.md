# ECommerce Product Trust Assessor

An explainable AI system that generates a 0–100 Trust Score from product listings, reviews, and seller data. Uses an ensemble of XGBoost, LightGBM, and DistilBERT to go beyond star ratings and actually answer: *"Can I trust this product?"*

---

## Overview

This project simulates a real-world product trust evaluation pipeline where listing data and reviews are processed through multiple specialized models, each scoring a different dimension of trust.

Each input (product title, description, reviews, seller stats) is passed through five modules — review authenticity, sentiment quality, listing quality, seller reliability, and return risk. The results are combined into a single weighted score with SHAP explanations so you can see *why* a product scored the way it did, not just what it scored.

You can also inject your own product data through the frontend form or hit the API directly to test different scenarios.

---

## Tech Stack

- **Machine Learning** — XGBoost, LightGBM, scikit-learn
- **NLP** — DistilBERT (HuggingFace Transformers)
- **Explainability** — SHAP TreeExplainer
- **Backend** — FastAPI + Uvicorn
- **Frontend** — Next.js 15, TypeScript, Tailwind CSS, Recharts

---

## Project Structure

```
ECommerce-Product-Trust-Assessor/
├── notebooks/
│   ├── 01_review_authenticity_model.ipynb
│   ├── 02_sentiment_quality_distilbert.ipynb
│   └── 03_seller_reliability_return_risk.ipynb
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/routes.py
│   │   ├── models/schemas.py
│   │   ├── services/
│   │   │   ├── trust_analyzer.py
│   │   │   ├── authenticity_scorer.py
│   │   │   ├── sentiment_scorer.py
│   │   │   ├── listing_scorer.py
│   │   │   ├── seller_return_scorer.py
│   │   │   └── shap_explainer.py
│   │   └── scoring/trust_engine.py
│   └── requirements.txt
└── frontend/
    ├── app/
    ├── components/
    └── lib/
```

---

## Running the Project

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

Open `http://localhost:3000`.

---

## How It Works

- Product data is submitted through the frontend form or API
- Each module independently scores a different trust signal
- Scores are combined using a fixed weighted formula
- SHAP values explain which features drove the final score up or down

The models are trained on real datasets — Amazon Reviews 2023 for the review modules, and the Olist Brazilian E-Commerce dataset for seller and return risk.

---

## Trust Score Formula

```
Trust Score =
  30% × Review Authenticity
+ 25% × Sentiment Quality
+ 20% × Seller Reliability
+ 15% × Listing Quality
+ 10% × Return Risk Safety
```

---

## Features

- Five-module scoring pipeline with independent models
- Weighted ensemble into a single 0–100 Trust Score
- SHAP explanations for every prediction
- Strengths and weaknesses surfaced automatically
- Return risk classification (LOW / MEDIUM / HIGH)

---

## Demo Flow

1. Open the analyzer → paste in a product listing
2. Submit → all five modules run in parallel
3. View the Trust Score gauge and radar breakdown
4. Read the SHAP panel → see which features drove the score
5. Check the return risk classification and listed weaknesses

---

## Model Details

| Module | Model | Weight |
|--------|-------|--------|
| Review Authenticity | XGBoost | 30% |
| Sentiment Quality | DistilBERT | 25% |
| Seller Reliability | LightGBM | 20% |
| Listing Quality | Rule-based NLP | 15% |
| Return Risk | LightGBM | 10% |

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/analyze` | Run full trust analysis on a product |
| `GET /api/health` | Check backend status |
