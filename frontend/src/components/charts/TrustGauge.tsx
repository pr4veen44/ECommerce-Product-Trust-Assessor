"use client";

import { scoreColor, scoreTier } from "@/types";

interface TrustGaugeProps {
  score: number;
  confidence: number;
  size?: number;
}

export function TrustGauge({ score, confidence, size = 220 }: TrustGaugeProps) {
  const radius = 80;
  const cx = size / 2;
  const cy = size / 2 + 10;

  // Arc: 210° total sweep, starting at -210° from right (lower-left to lower-right)
  const startAngle = -210;
  const totalAngle = 210;
  const fillAngle = (score / 100) * totalAngle;

  const toRad = (deg: number) => (deg * Math.PI) / 180;

  const arcPath = (startDeg: number, endDeg: number, r: number) => {
    const s = toRad(startDeg);
    const e = toRad(endDeg);
    const x1 = cx + r * Math.cos(s);
    const y1 = cy + r * Math.sin(s);
    const x2 = cx + r * Math.cos(e);
    const y2 = cy + r * Math.sin(e);
    const large = Math.abs(endDeg - startDeg) > 180 ? 1 : 0;
    return `M ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2}`;
  };

  const color = scoreColor(score);
  const tier = scoreTier(score);

  const TIER_LABELS = {
    excellent: "Highly Trustworthy",
    good: "Generally Trustworthy",
    fair: "Mixed Signals",
    poor: "Low Trust",
  };

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size * 0.8} viewBox={`0 0 ${size} ${size * 0.8}`}>
        <defs>
          <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#4f46e5" />
            <stop offset="50%" stopColor={color} />
            <stop offset="100%" stopColor={color} />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Background track */}
        <path
          d={arcPath(startAngle, startAngle + totalAngle, radius)}
          fill="none"
          stroke="#27272a"
          strokeWidth="14"
          strokeLinecap="round"
        />

        {/* Filled arc */}
        {score > 0 && (
          <path
            d={arcPath(startAngle, startAngle + fillAngle, radius)}
            fill="none"
            stroke="url(#gaugeGrad)"
            strokeWidth="14"
            strokeLinecap="round"
            filter="url(#glow)"
          />
        )}

        {/* Tick marks */}
        {[0, 25, 50, 75, 100].map((tick) => {
          const angle = startAngle + (tick / 100) * totalAngle;
          const rad = toRad(angle);
          const x1 = cx + (radius - 22) * Math.cos(rad);
          const y1 = cy + (radius - 22) * Math.sin(rad);
          const x2 = cx + (radius - 14) * Math.cos(rad);
          const y2 = cy + (radius - 14) * Math.sin(rad);
          return (
            <line key={tick} x1={x1} y1={y1} x2={x2} y2={y2}
              stroke="#3f3f46" strokeWidth="2" strokeLinecap="round" />
          );
        })}

        {/* Score text */}
        <text x={cx} y={cy - 10} textAnchor="middle" fill="white" fontSize="42" fontWeight="700" fontFamily="var(--font-inter)">
          {Math.round(score)}
        </text>
        <text x={cx} y={cy + 14} textAnchor="middle" fill="#71717a" fontSize="13" fontFamily="var(--font-inter)">
          out of 100
        </text>

        {/* Confidence */}
        <text x={cx} y={cy + 34} textAnchor="middle" fill="#52525b" fontSize="11" fontFamily="var(--font-mono)">
          {Math.round(confidence * 100)}% confidence
        </text>
      </svg>

      <div
        className="mt-1 text-sm font-semibold px-4 py-1.5 rounded-full"
        style={{ color, backgroundColor: color + "20", border: `1px solid ${color}40` }}
      >
        {TIER_LABELS[tier]}
      </div>
    </div>
  );
}
