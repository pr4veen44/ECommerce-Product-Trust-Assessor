// ─── API Types ────────────────────────────────────────────────────────────────

export type ReturnRisk = "LOW" | "MEDIUM" | "HIGH";

export interface ReviewInput {
  text: string;
  rating?: number;
  verified?: boolean;
  helpful_votes?: number;
}

export interface SellerInfo {
  seller_id?: string;
  avg_rating?: number;
  total_orders?: number;
  cancellation_rate?: number;
  avg_delivery_days?: number;
}

export interface ProductAnalysisRequest {
  title: string;
  description: string;
  category?: string;
  price?: number;
  rating?: number;
  reviews: ReviewInput[];
  seller?: SellerInfo;
}

export interface ScoreBreakdown {
  review_authenticity: number;
  sentiment_quality: number;
  listing_quality: number;
  seller_reliability: number;
  return_risk_score: number;
}

export interface SHAPExplanation {
  feature: string;
  impact: number;
  direction: "positive" | "negative";
}

export interface ProductAnalysisResponse {
  trust_score: number;
  breakdown: ScoreBreakdown;
  return_risk: ReturnRisk;
  strengths: string[];
  weaknesses: string[];
  shap_explanations: SHAPExplanation[];
  confidence: number;
  review_count_analyzed: number;
  model_version: string;
}

// ─── UI State Types ───────────────────────────────────────────────────────────

export type AnalysisStatus = "idle" | "loading" | "success" | "error";

export interface AnalysisState {
  status: AnalysisStatus;
  result: ProductAnalysisResponse | null;
  error: string | null;
}

// ─── Score label helpers ──────────────────────────────────────────────────────

export function scoreTier(score: number): "excellent" | "good" | "fair" | "poor" {
  if (score >= 80) return "excellent";
  if (score >= 65) return "good";
  if (score >= 45) return "fair";
  return "poor";
}

export function scoreColor(score: number): string {
  if (score >= 80) return "#22c55e";   // green-500
  if (score >= 65) return "#84cc16";   // lime-500
  if (score >= 45) return "#f59e0b";   // amber-500
  return "#ef4444";                    // red-500
}

export function riskColor(risk: ReturnRisk): string {
  switch (risk) {
    case "LOW":    return "#22c55e";
    case "MEDIUM": return "#f59e0b";
    case "HIGH":   return "#ef4444";
  }
}

export const SCORE_LABELS: Record<keyof ScoreBreakdown, string> = {
  review_authenticity: "Review Authenticity",
  sentiment_quality:   "Sentiment Quality",
  listing_quality:     "Listing Quality",
  seller_reliability:  "Seller Reliability",
  return_risk_score:   "Return Safety",
};
