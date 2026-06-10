# ECommerce Product Trust Assessor

> **"Can I trust this product?"**
> An Explainable AI system that generates a 0–100 Product Trust Score from product listings, reviews, and seller data — powered by DistilBERT, XGBoost, LightGBM, and SHAP.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Problem Statement

Online shoppers face a critical trust problem:

- **Fake reviews** are estimated to influence $152B+ in annual purchases
- **Listing quality** varies wildly — incomplete descriptions hide product flaws
- **Seller reliability** is opaque until something goes wrong
- Existing platforms provide star ratings but **no explainability**

This project builds a production-quality AI system that goes beyond star ratings to answer: *"Can I actually trust this product?"*

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Next.js 15 Frontend                         │
│  ┌──────────────────┐  ┌──────────────────────────────────────┐ │
│  │  Product Analyzer│  │        Results Dashboard             │ │
│  │  (Input Form)    │  │  Trust Gauge · Radar · SHAP Bars     │ │
│  └────────┬─────────┘  └──────────────────────────────────────┘ │
└───────────┼─────────────────────────────────────────────────────┘
            │ POST /api/analyze
┌───────────▼─────────────────────────────────────────────────────┐
│                     FastAPI Backend                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  TrustAnalyzer (Orchestrator)             │   │
│  │                                                          │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────────────┐ │   │
│  │  │Module 1 │ │Module 2 │ │Module 3 │ │   Module 4+5   │ │   │
│  │  │Authentic│ │Sentiment│ │ Listing │ │Seller · Return │ │   │
│  │  │ XGBoost │ │DistilBERT│ │  NLP   │ │LightGBM · Rules│ │   │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └───────┬────────┘ │   │
│  │       └───────────┴───────────┴───────────────┘          │   │
│  │                         │                                 │   │
│  │              ┌──────────▼──────────┐                      │   │
│  │              │  Trust Score Engine │                      │   │
│  │              │  Weighted Ensemble  │                      │   │
│  │              └──────────┬──────────┘                      │   │
│  │                         │                                 │   │
│  │              ┌──────────▼──────────┐                      │   │
│  │              │  SHAP Explainer     │                      │   │
│  │              └─────────────────────┘                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## ML Pipeline

### Module 1: Review Authenticity (30% weight)
- **Model:** XGBoost Classifier
- **Features:** Review length, caps ratio, spam phrase density, duplicate ratio, verified purchase rate, rating distribution entropy
- **Output:** Authenticity Score 0–100
- **Dataset:** Amazon Reviews 2023

### Module 2: Sentiment Quality (25% weight)
- **Model:** DistilBERT (fine-tuned on Amazon reviews)
- **Features:** Per-review positive/negative classification, confidence scores, variance
- **Output:** Sentiment Quality Score 0–100
- **Dataset:** Amazon Reviews 2023 (Electronics category)

### Module 3: Listing Quality (15% weight)
- **Model:** Rule-based NLP + readability metrics
- **Features:** Title completeness, description word count, quality signals (dimensions, materials, warranty), Flesch readability, bullet point structure
- **Output:** Listing Quality Score 0–100

### Module 4: Seller Reliability (20% weight)
- **Model:** XGBoost / LightGBM Classifier
- **Features:** Avg rating, cancellation rate, delivery days, order volume, late delivery rate
- **Output:** Seller Reliability Score 0–100
- **Dataset:** Olist Brazilian E-Commerce

### Module 5: Return Risk (10% weight)
- **Model:** LightGBM Classifier
- **Features:** Category risk, price, product rating, sentiment score, seller reliability
- **Output:** Return Risk Score + Class (LOW / MEDIUM / HIGH)
- **Dataset:** Olist order-return data

### Final Score
```
Trust Score =
  30% × Review Authenticity
+ 25% × Sentiment Quality
+ 20% × Seller Reliability
+ 15% × Listing Quality
+ 10% × Return Risk Safety
```

---

## Datasets

| Dataset | Source | Used For |
|---------|--------|----------|
| Amazon Reviews 2023 | [HuggingFace](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023) | Modules 1 & 2 |
| Olist E-Commerce | [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) | Modules 4 & 5 |

---

## Project Structure

```
ECommerce-Product-Trust-Assessor/
├── frontend/                    # Next.js 15 + TypeScript + Tailwind
│   └── src/
│       ├── app/
│       │   ├── page.tsx         # Landing page
│       │   ├── analyzer/        # Product input form
│       │   └── results/         # Analysis dashboard
│       ├── components/
│       │   ├── charts/          # TrustGauge (SVG)
│       │   └── dashboard/       # ScoreBreakdown, ExplainabilityPanel
│       ├── lib/api.ts           # Axios API client
│       └── types/index.ts       # Shared TypeScript types
├── backend/                     # FastAPI + Python
│   ├── app/
│   │   ├── main.py              # App entry point
│   │   ├── api/routes.py        # REST endpoints
│   │   ├── models/schemas.py    # Pydantic I/O schemas
│   │   ├── services/
│   │   │   ├── trust_analyzer.py       # Orchestrator
│   │   │   ├── authenticity_scorer.py  # Module 1
│   │   │   ├── sentiment_scorer.py     # Module 2
│   │   │   ├── listing_scorer.py       # Module 3
│   │   │   ├── seller_return_scorer.py # Modules 4 & 5
│   │   │   ├── shap_explainer.py       # SHAP explanations
│   │   │   └── model_loader.py         # Model registry
│   │   └── scoring/trust_engine.py    # Weighted Trust Score
│   └── requirements.txt
├── notebooks/
│   ├── 01_review_authenticity_model.ipynb
│   ├── 02_sentiment_quality_distilbert.ipynb
│   └── 03_seller_reliability_return_risk.ipynb
├── models/
│   ├── authenticity/
│   ├── sentiment/
│   ├── listing/
│   ├── seller/
│   └── return_risk/
├── docker-compose.yml
└── README.md
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional)

### Option A: Docker (recommended)

```bash
git clone https://github.com/your-username/ECommerce-Product-Trust-Assessor
cd ECommerce-Product-Trust-Assessor
docker-compose up --build
```

Open [http://localhost:3000](http://localhost:3000)

---

### Option B: Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

---

## API Usage

### Analyze a Product

```http
POST /api/analyze
Content-Type: application/json

{
  "title": "Sony WH-1000XM5 Headphones",
  "description": "Industry-leading noise cancellation...",
  "category": "Electronics",
  "price": 279.99,
  "rating": 4.4,
  "reviews": [
    {
      "text": "Incredible noise cancellation, worth every penny.",
      "rating": 5,
      "verified": true,
      "helpful_votes": 234
    }
  ],
  "seller": {
    "avg_rating": 4.7,
    "total_orders": 12500,
    "cancellation_rate": 0.02,
    "avg_delivery_days": 3.2
  }
}
```

**Response:**
```json
{
  "trust_score": 87.4,
  "breakdown": {
    "review_authenticity": 91.0,
    "sentiment_quality": 88.5,
    "listing_quality": 94.0,
    "seller_reliability": 86.0,
    "return_risk_score": 72.0
  },
  "return_risk": "LOW",
  "strengths": [
    "Reviews appear authentic and trustworthy",
    "Customers express consistently positive experiences",
    "Detailed, complete product listing"
  ],
  "weaknesses": [],
  "shap_explanations": [
    { "feature": "Verified purchase rate", "impact": 0.32, "direction": "positive" },
    { "feature": "Spam/promotional language density", "impact": 0.08, "direction": "negative" }
  ],
  "confidence": 0.9,
  "review_count_analyzed": 5,
  "model_version": "1.0.0"
}
```

---

## Model Training

Run the Colab notebooks in order:

1. `notebooks/01_review_authenticity_model.ipynb` — XGBoost authenticity classifier
2. `notebooks/02_sentiment_quality_distilbert.ipynb` — DistilBERT fine-tuning (GPU required)
3. `notebooks/03_seller_reliability_return_risk.ipynb` — Seller + return risk models

After training, copy the `models/` directory to the backend root.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, Recharts |
| Backend | FastAPI, Pydantic v2, Uvicorn |
| ML Core | XGBoost, LightGBM, scikit-learn |
| NLP | DistilBERT (HuggingFace Transformers) |
| Explainability | SHAP TreeExplainer |
| Containerization | Docker, Docker Compose |

---

## Future Improvements

- [ ] Real-time review scraping integration (Amazon product URL input)
- [ ] Multi-language review support (multilingual BERT)
- [ ] Temporal trust decay (recent reviews weighted higher)
- [ ] Batch analysis API for price-comparison tools
- [ ] Browser extension for in-page trust scores
- [ ] A/B testing framework for weight optimization
- [ ] PostgreSQL + Redis caching for repeated product lookups
- [ ] User feedback loop to improve model accuracy

---

## License

MIT — free to use for portfolio, research, and commercial projects.

---

*Built as a portfolio project demonstrating production ML engineering: multi-model ensembles, transformer fine-tuning, SHAP explainability, FastAPI async design, and modern full-stack TypeScript.*
