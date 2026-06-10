"use client";

import { TrendingUp, TrendingDown } from "lucide-react";
import type { SHAPExplanation } from "@/types";

interface ExplainabilityPanelProps {
  explanations: SHAPExplanation[];
  strengths: string[];
  weaknesses: string[];
}

export function ExplainabilityPanel({
  explanations,
  strengths,
  weaknesses,
}: ExplainabilityPanelProps) {
  const positives = explanations.filter((e) => e.direction === "positive");
  const negatives = explanations.filter((e) => e.direction === "negative");

  const maxImpact = Math.max(...explanations.map((e) => e.impact), 0.01);

  return (
    <div className="space-y-5">
      {/* SHAP bar chart */}
      <div className="card p-6">
        <p className="label mb-4">Feature Impact (SHAP)</p>
        <div className="space-y-3">
          {explanations.slice(0, 8).map((item) => {
            const isPos = item.direction === "positive";
            const barWidth = (item.impact / maxImpact) * 100;
            return (
              <div key={item.feature} className="flex items-center gap-3">
                <span className="text-xs text-zinc-400 w-48 shrink-0 truncate" title={item.feature}>
                  {item.feature}
                </span>
                <div className="flex-1 h-6 bg-zinc-800 rounded overflow-hidden relative">
                  <div
                    className="h-full rounded transition-all duration-500"
                    style={{
                      width: `${barWidth}%`,
                      backgroundColor: isPos ? "#22c55e" : "#ef4444",
                      opacity: 0.8,
                    }}
                  />
                </div>
                <span
                  className="text-xs font-mono w-12 text-right"
                  style={{ color: isPos ? "#22c55e" : "#ef4444" }}
                >
                  {isPos ? "+" : "−"}{(item.impact * 100).toFixed(1)}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid sm:grid-cols-2 gap-4">
        {/* Strengths */}
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp size={16} className="text-green-400" />
            <p className="label text-green-400">Strengths</p>
          </div>
          {strengths.length === 0 ? (
            <p className="text-xs text-zinc-600">No strong signals detected.</p>
          ) : (
            <ul className="space-y-2">
              {strengths.map((s, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-zinc-300">
                  <span className="text-green-400 mt-0.5 shrink-0">✓</span>
                  {s}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Weaknesses */}
        <div className="card p-5">
          <div className="flex items-center gap-2 mb-4">
            <TrendingDown size={16} className="text-red-400" />
            <p className="label text-red-400">Weaknesses</p>
          </div>
          {weaknesses.length === 0 ? (
            <p className="text-xs text-zinc-500">No significant weaknesses found.</p>
          ) : (
            <ul className="space-y-2">
              {weaknesses.map((w, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-zinc-300">
                  <span className="text-red-400 mt-0.5 shrink-0">✗</span>
                  {w}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
