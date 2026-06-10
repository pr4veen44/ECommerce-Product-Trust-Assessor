"use client";

import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  ResponsiveContainer, Tooltip,
} from "recharts";
import { scoreColor, SCORE_LABELS, type ScoreBreakdown } from "@/types";

interface ScoreBreakdownProps {
  breakdown: ScoreBreakdown;
}

export function ScoreBreakdownPanel({ breakdown }: ScoreBreakdownProps) {
  const radarData = Object.entries(breakdown).map(([key, value]) => ({
    subject: SCORE_LABELS[key as keyof ScoreBreakdown]
      .split(" ").slice(0, 2).join("\n"),
    score: Math.round(value),
    fullMark: 100,
  }));

  const rows = Object.entries(breakdown) as [keyof ScoreBreakdown, number][];

  return (
    <div className="space-y-6">
      {/* Radar */}
      <div className="card p-6">
        <p className="label mb-4">Score Radar</p>
        <ResponsiveContainer width="100%" height={260}>
          <RadarChart data={radarData} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
            <PolarGrid stroke="#3f3f46" />
            <PolarAngleAxis
              dataKey="subject"
              tick={{ fill: "#71717a", fontSize: 11, fontFamily: "var(--font-inter)" }}
            />
            <Radar
              name="Score"
              dataKey="score"
              stroke="#6366f1"
              fill="#6366f1"
              fillOpacity={0.25}
              strokeWidth={2}
            />
            <Tooltip
              contentStyle={{
                background: "#18181b",
                border: "1px solid #3f3f46",
                borderRadius: "8px",
                color: "#f4f4f5",
                fontSize: 12,
              }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Progress bars */}
      <div className="card p-6 space-y-5">
        <p className="label">Component Breakdown</p>
        {rows.map(([key, value]) => {
          const color = scoreColor(value);
          const pct = Math.round(value);
          return (
            <div key={key}>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-sm text-zinc-300">{SCORE_LABELS[key]}</span>
                <span
                  className="text-sm font-semibold font-mono"
                  style={{ color }}
                >
                  {pct}
                </span>
              </div>
              <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{ width: `${pct}%`, backgroundColor: color }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
