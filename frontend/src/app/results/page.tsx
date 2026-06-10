"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Shield, RotateCcw, AlertTriangle } from "lucide-react";
import type { ProductAnalysisResponse, ProductAnalysisRequest } from "@/types";
import { riskColor } from "@/types";
import { TrustGauge } from "@/components/charts/TrustGauge";
import { ScoreBreakdownPanel } from "@/components/dashboard/ScoreBreakdown";
import { ExplainabilityPanel } from "@/components/dashboard/ExplainabilityPanel";

export default function ResultsPage() {
  const router = useRouter();
  const [result, setResult] = useState<ProductAnalysisResponse | null>(null);
  const [request, setRequest] = useState<ProductAnalysisRequest | null>(null);

  useEffect(() => {
    const r = sessionStorage.getItem("trust_result");
    const q = sessionStorage.getItem("trust_request");
    if (!r) {
      router.replace("/analyzer");
      return;
    }
    setResult(JSON.parse(r));
    if (q) setRequest(JSON.parse(q));
  }, [router]);

  if (!result) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const rColor = riskColor(result.return_risk);

  return (
    <div className="min-h-screen">
      {/* Nav */}
      <nav className="border-b border-[#3f3f46] px-6 py-4 flex items-center justify-between sticky top-0 bg-[#09090b]/80 backdrop-blur-md z-50">
        <div className="flex items-center gap-4">
          <Link href="/analyzer" className="flex items-center gap-1.5 text-zinc-400 hover:text-zinc-100 transition-colors">
            <ArrowLeft size={16} />
            <span className="text-sm">Back</span>
          </Link>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-md bg-indigo-600 flex items-center justify-center">
              <Shield size={14} className="text-white" />
            </div>
            <span className="font-semibold text-white text-sm">Trust Analysis Report</span>
          </div>
        </div>
        <Link href="/analyzer" className="flex items-center gap-1.5 btn-ghost text-sm">
          <RotateCcw size={14} />
          Analyze another
        </Link>
      </nav>

      <main className="max-w-6xl mx-auto px-6 py-10">
        {/* Product title */}
        {request?.title && (
          <div className="mb-8">
            <p className="label mb-1">Product analyzed</p>
            <h1 className="text-xl font-bold text-white line-clamp-2">{request.title}</h1>
            <div className="flex items-center gap-3 mt-2 flex-wrap">
              {request.category && (
                <span className="text-xs bg-zinc-800 text-zinc-400 px-3 py-1 rounded-full">{request.category}</span>
              )}
              <span className="text-xs text-zinc-600">
                {result.review_count_analyzed} review{result.review_count_analyzed !== 1 ? "s" : ""} analyzed
              </span>
              <span className="text-xs text-zinc-600">Model v{result.model_version}</span>
            </div>
          </div>
        )}

        {/* Main grid */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Left: Gauge + Risk */}
          <div className="lg:col-span-1 space-y-4">
            <div className="card p-6 flex flex-col items-center">
              <p className="label mb-4 self-start">Trust Score</p>
              <TrustGauge
                score={result.trust_score}
                confidence={result.confidence}
              />
            </div>

            {/* Return Risk badge */}
            <div className="card p-5">
              <p className="label mb-3">Return Risk</p>
              <div
                className="flex items-center gap-3 px-4 py-3 rounded-lg"
                style={{ backgroundColor: rColor + "18", border: `1px solid ${rColor}30` }}
              >
                <AlertTriangle size={18} style={{ color: rColor }} />
                <div>
                  <div className="font-semibold text-white">{result.return_risk}</div>
                  <div className="text-xs text-zinc-500">Return probability</div>
                </div>
              </div>
            </div>

            {/* Score cards */}
            <div className="grid grid-cols-2 gap-3">
              {([
                ["Authenticity", result.breakdown.review_authenticity],
                ["Sentiment", result.breakdown.sentiment_quality],
                ["Listing", result.breakdown.listing_quality],
                ["Seller", result.breakdown.seller_reliability],
              ] as [string, number][]).map(([label, score]) => {
                const color = score >= 80 ? "#22c55e" : score >= 60 ? "#f59e0b" : "#ef4444";
                return (
                  <div key={label} className="card-sm p-3 text-center">
                    <div className="text-xl font-bold" style={{ color }}>{Math.round(score)}</div>
                    <div className="text-xs text-zinc-500 mt-0.5">{label}</div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right: Breakdown + Explainability */}
          <div className="lg:col-span-2 space-y-6">
            <ScoreBreakdownPanel breakdown={result.breakdown} />
            <ExplainabilityPanel
              explanations={result.shap_explanations}
              strengths={result.strengths}
              weaknesses={result.weaknesses}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
