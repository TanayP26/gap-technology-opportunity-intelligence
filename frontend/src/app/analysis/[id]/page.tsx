"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { GlyphIcon } from "@/components/GlyphIcon";
import { LandscapeChart } from "@/components/LandscapeChart";
import { LoadingState } from "@/components/LoadingState";
import { ScoreMethod } from "@/components/ScoreMethod";
import { getAnalysis, getLandscape } from "@/lib/api";
import { compactNumber, formatDate, score } from "@/lib/format";
import type { AnalysisResponse, LandscapeResponse } from "@/lib/types";

export default function AnalysisPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const id = params.id;
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [landscape, setLandscape] = useState<LandscapeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let live = true;
    Promise.all([getAnalysis(id), getLandscape(id)])
      .then(([analysisData, landscapeData]) => {
        if (!live) return;
        setAnalysis(analysisData);
        setLandscape(landscapeData);
      })
      .catch((err) => {
        if (!live) return;
        setError(err instanceof Error ? err.message : "Could not load analysis.");
      });
    return () => {
      live = false;
    };
  }, [id]);

  const totals = useMemo(() => {
    if (!landscape) return null;
    return {
      evidence: landscape.entries.reduce((sum, entry) => sum + entry.evidence_count, 0),
      errors: landscape.entries.reduce((sum, entry) => sum + entry.source_error_count, 0),
      scored: landscape.entries.filter((entry) => entry.score_status === "scored").length,
    };
  }, [landscape]);

  if (error) {
    return (
      <AppShell methodHref="#method">
        <div className="page"><div className="error-banner">{error}</div></div>
      </AppShell>
    );
  }

  if (!analysis || !landscape || !totals) {
    return (
      <AppShell methodHref="#method">
        <div className="page loading-page">
          <LoadingState
            label="Loading persisted analysis"
            detail="Fetching the landscape, score state and source-health totals."
          />
        </div>
      </AppShell>
    );
  }

  const top = landscape.entries.find((entry) => entry.score_status === "scored");

  const metrics = [
    { icon: "grid" as const, tone: "blue", value: landscape.entries.length, label: "Subdomains", note: "analysed" },
    { icon: "evidence" as const, tone: "blue", value: compactNumber(totals.evidence), label: "Evidence items", note: "persisted" },
    { icon: "check" as const, tone: "green", value: `${totals.scored}/${landscape.entries.length}`, label: "Scored", note: "successfully" },
    { icon: "error" as const, tone: "red", value: totals.errors, label: "Source errors", note: "across sources" },
  ];

  return (
    <AppShell methodHref="#method">
      <div className="page analysis-page reference-analysis page-enter">
        <section className="reference-analysis-head">
          <div>
            <div className="breadcrumb">
              <Link href="/">Analyses</Link>
              <span>›</span>
              <span>{id.slice(0, 8).toUpperCase()}</span>
              <span>›</span>
              <span>Technology Landscape</span>
            </div>
            <h1>{analysis.technology}</h1>
            <p>
              Technology landscape and opportunity analysis based on {compactNumber(totals.evidence)} evidence items from research papers, patents, news and search trends.
            </p>
          </div>
          <div className="reference-analysis-actions">
            <span>{formatDate(analysis.completed_at)}</span>
            <Link className="reference-export" href={`/analysis/${id}/graph`}>
              Evidence graph <span>⌄</span>
            </Link>
          </div>
        </section>

        <section className="reference-metric-row">
          {metrics.map((metric) => (
            <div className="reference-metric-card" key={metric.label}>
              <span className={`reference-metric-icon ${metric.tone}`}><GlyphIcon name={metric.icon} size={17} /></span>
              <div>
                <strong>{metric.value}</strong>
                <span>{metric.label}</span>
                <small>{metric.note}</small>
              </div>
            </div>
          ))}
          <div className="reference-metric-card reference-top-card">
            <span className="reference-metric-icon amber"><GlyphIcon name="trophy" size={17} /></span>
            <div>
              <strong>{top?.name ?? "—"}</strong>
              <span>Top opportunity</span>
              <small>GAP {score(top?.gap_score ?? null)}</small>
            </div>
          </div>
        </section>

        <section className="reference-landscape-grid">
          <div className="reference-panel reference-map-panel">
            <div className="reference-panel-title">
              <div>
                <h2>Opportunity Map</h2>
                <p>Technical momentum × demand momentum</p>
              </div>
              <span className="tiny-info">i</span>
            </div>
            <LandscapeChart analysisId={id} entries={landscape.entries} />
          </div>

          <aside className="reference-panel reference-ranking-panel">
            <div className="reference-panel-title ranking-title">
              <h2>Subdomain Rankings</h2>
            </div>
            <div className="reference-ranking-head">
              <span>#</span><span>Subdomain</span><span>GAP Score</span>
            </div>
            <div className="reference-ranking-list">
              {landscape.entries.map((entry, index) => (
                <Link
                  className={index === 0 ? "reference-ranking-row top" : "reference-ranking-row"}
                  href={`/analysis/${id}/subdomain/${entry.subdomain_id}`}
                  key={entry.subdomain_id}
                >
                  <span className={`reference-rank rank-${index + 1}`}>{index + 1}</span>
                  <strong>{entry.name}</strong>
                  <span className="reference-ranking-score">{score(entry.gap_score)}</span>
                  <span className="reference-chevron">›</span>
                </Link>
              ))}
            </div>
          </aside>
        </section>

        <section className="reference-map-guide reference-panel">
          <div className="reference-guide-copy">
            <span className="reference-guide-icon"><GlyphIcon name="grid" size={16} /></span>
            <div>
              <strong>How to read this map</strong>
              <p>Each bubble represents a technology subdomain. Position shows momentum; size shows GAP score; ring shows market presence; opacity shows confidence.</p>
            </div>
          </div>
          <div className="reference-guide-axis">
            <div className="mini-axis">
              <span className="mini-axis-y">Higher demand<br />momentum</span>
              <span className="axis-v" />
              <span className="axis-h" />
              <span className="mini-axis-x">Higher technical<br />momentum</span>
            </div>
          </div>
          <div className="reference-guide-legend">
            <div><strong>Bubble size</strong><span className="legend-bubble" /><small>Higher<br />GAP score</small></div>
            <div><strong>Ring</strong><span className="legend-ring" /><small>Greater<br />market presence</small></div>
            <div><strong>Opacity</strong><span className="legend-opacity" /><small>Higher<br />confidence</small></div>
          </div>
        </section>

        <div className="reference-below-fold">
          <section className="rank-section compact-table-section">
            <div className="section-head">
              <div><h2>Signal matrix</h2></div>
              <span className="section-note">transparent inputs behind each ranking</span>
            </div>
            <div className="data-table-wrap">
              <table className="data-table">
                <thead><tr><th>#</th><th>Subdomain</th><th>Research</th><th>Patents</th><th>Attention</th><th>Events</th><th>Market</th><th>Confidence</th><th>GAP</th><th>Evidence</th></tr></thead>
                <tbody>
                  {landscape.entries.map((entry, index) => (
                    <tr
                      className="signal-matrix-row"
                      key={entry.subdomain_id}
                      role="link"
                      tabIndex={0}
                      aria-label={`Open ${entry.name} detail`}
                      onClick={() => router.push(`/analysis/${id}/subdomain/${entry.subdomain_id}`)}
                      onKeyDown={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                          event.preventDefault();
                          router.push(`/analysis/${id}/subdomain/${entry.subdomain_id}`);
                        }
                      }}
                    >
                      <td>{String(index + 1).padStart(2, "0")}</td>
                      <td><Link onClick={(event) => event.stopPropagation()} href={`/analysis/${id}/subdomain/${entry.subdomain_id}`}>{entry.name}</Link></td>
                      <td>{Math.round((entry.signals.research ?? 0) * 100)}%</td>
                      <td>{Math.round((entry.signals.patents ?? 0) * 100)}%</td>
                      <td>{Math.round((entry.signals.attention ?? 0) * 100)}%</td>
                      <td>{Math.round((entry.signals.events ?? 0) * 100)}%</td>
                      <td>{Math.round((entry.signals.market ?? 0) * 100)}%</td>
                      <td>{Math.round((entry.signals.confidence ?? 0) * 100)}%</td>
                      <td>{score(entry.gap_score)}</td>
                      <td>{entry.evidence_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
          <ScoreMethod />
        </div>
      </div>
    </AppShell>
  );
}
