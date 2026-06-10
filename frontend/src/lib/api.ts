import axios from "axios";
import type { ProductAnalysisRequest, ProductAnalysisResponse } from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60_000,
  headers: { "Content-Type": "application/json" },
});

export async function analyzeProduct(
  req: ProductAnalysisRequest
): Promise<ProductAnalysisResponse> {
  const { data } = await api.post<ProductAnalysisResponse>("/api/analyze", req);
  return data;
}

export async function getCategories(): Promise<string[]> {
  const { data } = await api.get<{ categories: string[] }>("/api/categories");
  return data.categories;
}

export async function getScoringWeights(): Promise<Record<string, number>> {
  const { data } = await api.get<{ weights: Record<string, number> }>("/api/weights");
  return data.weights;
}
