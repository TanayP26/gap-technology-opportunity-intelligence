"use client";

import { useMemo } from "react";
import { score } from "@/lib/format";
import type { LandscapeEntry } from "@/lib/types";

const pointColors = ["#2f6fed", "#7fd3c4", "#9a6ff2", "#f2b33c", "#6aa2f2", "#ef8b8b"];
const pointFills = ["#4d80ee", "#95d8cc", "#a987f0", "#f6bd55", "#7dabf0", "#f2a0a0"];

export function LandscapeChart({
  analysisId,
  entries,
}: {
  analysisId: string;
  entries: LandscapeEntry[];
}) {
  const scored = useMemo(
    () =>
      entries.filter(
        (entry) =>
          entry.score_status === "scored" &&
          entry.technical_momentum != null &&
          entry.demand_momentum != null &&
          entry.gap_score != null &&
          entry.signals.market != null,
      ),
    [entries],
  );

  if (!scored.length) {
    return <div className="empty-box">No complete scores available for this landscape.</div>;
  }

  const maxGap = Math.max(...scored.map((entry) => entry.gap_score ?? 0), 0.0001);
  const plot = { left: 62, top: 32, width: 570, height: 290 };

  return (
    <div className="reference-chart-shell">
      <svg
        className="reference-landscape-chart"
        viewBox="0 0 680 370"
        role="img"
        aria-label="Opportunity map plotting technical momentum against demand momentum"
      >
        <defs>
          <filter id="softPointShadow" x="-80%" y="-80%" width="260%" height="260%">
            <feDropShadow dx="0" dy="5" stdDeviation="7" floodColor="#6d86b0" floodOpacity="0.18" />
          </filter>
        </defs>

        <rect x={plot.left} y={plot.top} width={plot.width} height={plot.height} rx="10" className="reference-chart-field" />

        {[0, 0.2, 0.4, 0.6, 0.8, 1].map((tick) => {
          const x = plot.left + tick * plot.width;
          const y = plot.top + (1 - tick) * plot.height;
          return (
            <g key={tick}>
              <line x1={x} y1={plot.top} x2={x} y2={plot.top + plot.height} className="reference-chart-grid" />
              <line x1={plot.left} y1={y} x2={plot.left + plot.width} y2={y} className="reference-chart-grid" />
            </g>
          );
        })}

        <line x1={plot.left} y1={plot.top + plot.height} x2={plot.left + plot.width} y2={plot.top + plot.height} className="reference-chart-axis-line" />
        <line x1={plot.left} y1={plot.top} x2={plot.left} y2={plot.top + plot.height} className="reference-chart-axis-line" />

        <text x={plot.left - 10} y={plot.top + 8} textAnchor="end" className="reference-chart-tick">High</text>
        <text x={plot.left - 10} y={plot.top + plot.height} textAnchor="end" className="reference-chart-tick">Low</text>
        <text x={plot.left} y={plot.top + plot.height + 21} className="reference-chart-tick">Low</text>
        <text x={plot.left + plot.width} y={plot.top + plot.height + 21} textAnchor="end" className="reference-chart-tick">High</text>
        <text x={plot.left + plot.width / 2} y="362" textAnchor="middle" className="reference-chart-axis">Technical Momentum</text>
        <text x="14" y={plot.top + plot.height / 2} transform={`rotate(-90 14 ${plot.top + plot.height / 2})`} textAnchor="middle" className="reference-chart-axis">Demand Momentum</text>

        {scored.map((entry, index) => {
          const x = plot.left + (entry.technical_momentum ?? 0) * plot.width;
          const y = plot.top + (1 - (entry.demand_momentum ?? 0)) * plot.height;
          const ratio = (entry.gap_score ?? 0) / maxGap;
          const r = 10 + ratio * 8;
          const market = entry.signals.market ?? 0;
          const confidence = entry.signals.confidence ?? 0.8;
          const labelToLeft = x > plot.left + plot.width * 0.73;
          const labelX = labelToLeft ? x - r - 9 : x + r + 9;
          const labelAnchor = labelToLeft ? "end" : "start";
          const labelY = y - 3;

          return (
            <a
              href={`/analysis/${analysisId}/subdomain/${entry.subdomain_id}`}
              key={entry.subdomain_id}
              aria-label={`${entry.name}, GAP score ${entry.gap_score?.toFixed(4) ?? "unavailable"}`}
              className="reference-chart-point-link"
            >
              <circle
                cx={x}
                cy={y}
                r={r + 8}
                fill={pointColors[index % pointColors.length]}
                fillOpacity="0.08"
                className="reference-chart-halo"
              />
              <circle
                cx={x}
                cy={y}
                r={r + 4}
                fill="none"
                stroke={pointColors[index % pointColors.length]}
                strokeWidth={1.5 + market * 1.8}
                strokeOpacity={0.22 + market * 0.25}
                className="reference-chart-ring"
              />
              <circle
                cx={x}
                cy={y}
                r={r}
                fill={pointFills[index % pointFills.length]}
                fillOpacity={0.55 + confidence * 0.38}
                stroke={pointColors[index % pointColors.length]}
                strokeWidth="1.5"
                filter="url(#softPointShadow)"
                className="reference-chart-dot"
              />
              <text x={labelX} y={labelY} textAnchor={labelAnchor} className="reference-chart-label">{entry.name}</text>
              <text x={labelX} y={labelY + 14} textAnchor={labelAnchor} className="reference-chart-score">GAP {score(entry.gap_score)}</text>
            </a>
          );
        })}
      </svg>
    </div>
  );
}
