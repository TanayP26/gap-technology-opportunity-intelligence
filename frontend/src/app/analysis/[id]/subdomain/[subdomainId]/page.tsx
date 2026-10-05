"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { EvidenceList } from "@/components/EvidenceList";
import { LoadingState } from "@/components/LoadingState";
import { ScoreMethod } from "@/components/ScoreMethod";
import { SignalBars } from "@/components/SignalBars";
import { getEvidence, getLandscape } from "@/lib/api";
import { pct, score } from "@/lib/format";
import type {
  EvidenceListResponse,
  EvidenceType,
  LandscapeEntry,
  LandscapeResponse,
} from "@/lib/types";

const filters: Array<{ label: string; value?: EvidenceType }> = [
  { label: "All" },
  { label: "Papers", value: "paper" },
  { label: "Patents", value: "patent" },
  { label: "News", value: "news" },
  { label: "Market", value: "market" },
];

function signalRead(entry: LandscapeEntry) {
  if (entry.score_status !== "scored") {
    return "This subdomain is intentionally left unranked because one or more required signals are unavailable.";
  }
  const demand = entry.demand_momentum ?? 0;
  const market = entry.signals.market ?? 0;
  const technical = entry.technical_momentum ?? 0;
  if (demand - market >= 0.2) {
    return `Demand momentum (${pct(demand, 1)}) materially exceeds visible market presence (${pct(market, 1)}), while technical momentum sits at ${pct(technical, 1)}.`;
  }
  if (technical >= 0.5 && demand >= 0.5) {
    return `Technical and demand momentum are both above 50%, but visible market presence at ${pct(market, 1)} reduces the remaining whitespace.`;
  }
  return `The signals are comparatively aligned: technical momentum is ${pct(technical, 1)}, demand is ${pct(demand, 1)}, and visible market presence is ${pct(market, 1)}.`;
}

export default function SubdomainPage() {
  const params = useParams<{ id: string; subdomainId: string }>();
  const analysisId = params.id;
  const subdomainId = params.subdomainId;
  const [landscape, setLandscape] = useState<LandscapeResponse | null>(null);
  const [entry, setEntry] = useState<LandscapeEntry | null>(null);
  const [evidence, setEvidence] = useState<EvidenceListResponse | null>(null);
  const [filter, setFilter] = useState<EvidenceType | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);
  const [loadingEvidence, setLoadingEvidence] = useState(false);

  useEffect(() => {
    let live = true;
    getLandscape(analysisId)
      .then((data) => {
        if (!live) return;
        setLandscape(data);
        const match = data.entries.find((item) => item.subdomain_id === subdomainId) ?? null;
        setEntry(match);
        if (!match) setError("Subdomain not found in this analysis.");
      })
      .catch((err) => {
        if (!live) return;
        setError(err instanceof Error ? err.message : "Could not load landscape.");
      });
    return () => { live = false; };
  }, [analysisId, subdomainId]);

  useEffect(() => {
    let live = true;
    setLoadingEvidence(true);
    getEvidence(subdomainId, filter, 50, 0)
      .then((data) => { if (live) setEvidence(data); })
      .catch((err) => {
        if (live) setError(err instanceof Error ? err.message : "Could not load evidence.");
      })
      .finally(() => { if (live) setLoadingEvidence(false); });
    return () => { live = false; };
  }, [subdomainId, filter]);

  const rank = useMemo(() => {
    if (!landscape || !entry) return null;
    return landscape.entries.findIndex((item) => item.subdomain_id === entry.subdomain_id) + 1;
  }, [landscape, entry]);

  if (error) {
    return (
      <AppShell methodHref="#method">
        <div className="page"><div className="error-banner">{error}</div></div>
      </AppShell>
    );
  }

  if (!entry || !landscape) {
    return (
      <AppShell methodHref="#method">
        <div className="page loading-page">
          <LoadingState label="Loading signal detail" detail="Resolving the ranked score and persisted evidence state." />
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell
      methodHref="#method"
      context={<span className="context-label mono">signal / {subdomainId.slice(0, 8)}</span>}
    >
      <div className="page detail-page page-enter">
        <section className="analysis-head">
          <div>
            <div className="breadcrumb">
              <Link href="/">Discover</Link><span>/</span>
              <Link href={`/analysis/${analysisId}`}>{landscape.technology}</Link><span>/</span>
              <span>{entry.name}</span>
            </div>
            <div className="detail-title-row">
              <span className="rank-chip mono">#{String(rank ?? 0).padStart(2, "0")}</span>
              <h1>{entry.name}</h1>
            </div>
            <p>{entry.evidence_count} persisted evidence items · {entry.source_error_count} source errors</p>
          </div>
          <Link className="secondary-button" href={`/analysis/${analysisId}`}>← Landscape</Link>
        </section>

        <section className="detail-grid">
          <div className="panel score-panel premium-score-panel">
            <span className="eyebrow">GAP score</span>
            <div className="big-score mono">{score(entry.gap_score)}</div>
            <div className="score-state">
              <span className={`status-badge ${entry.score_status}`}><i /> {entry.score_status.replace("_", " ")}</span>
              <span className="mono">{pct(entry.signals.confidence, 1)} confidence</span>
            </div>

            <div className="score-breakdown">
              <div><span>Technical momentum</span><strong className="mono">{score(entry.technical_momentum)}</strong></div>
              <div><span>Demand momentum</span><strong className="mono">{score(entry.demand_momentum)}</strong></div>
              <div><span>Whitespace</span><strong className="mono">{score(entry.whitespace)}</strong></div>
            </div>

            {entry.missing_signals.length > 0 && (
              <div className="warning-box">
                Missing required signals: {entry.missing_signals.join(", ")}. This item is not ranked as a complete score.
              </div>
            )}
          </div>

          <div className="detail-right-stack">
            <div className="panel signal-read-panel">
              <span className="eyebrow">Signal read</span>
              <p>{signalRead(entry)}</p>
              <div className="signal-read-meta">
                <span><i className="read-dot technical" /> technical {pct(entry.technical_momentum, 0)}</span>
                <span><i className="read-dot demand" /> demand {pct(entry.demand_momentum, 0)}</span>
                <span><i className="read-dot market" /> market {pct(entry.signals.market, 0)}</span>
              </div>
            </div>

            <div className="panel signals-panel">
              <div className="panel-head compact">
                <div><span className="eyebrow">Signal vector</span><h2>Inspect before interpreting</h2></div>
                <span className="mono muted">{entry.source_error_count} source errors</span>
              </div>
              <SignalBars values={entry.signals} />
            </div>
          </div>
        </section>

        <section className="evidence-section">
          <div className="section-head">
            <div><span className="section-index mono">03</span><h2>Evidence ledger</h2></div>
            <span className="section-note">normalized records persisted from source searches</span>
          </div>

          <div className="evidence-toolbar">
            <div className="filter-tabs" role="tablist" aria-label="Evidence type">
              {filters.map((item) => (
                <button
                  key={item.label}
                  type="button"
                  className={filter === item.value ? "active" : ""}
                  onClick={() => setFilter(item.value)}
                >
                  {item.label}
                </button>
              ))}
            </div>
            <span className="mono muted">{loadingEvidence ? "refreshing…" : `${evidence?.total ?? 0} records`}</span>
          </div>

          {loadingEvidence && !evidence ? (
            <div className="evidence-skeleton" aria-hidden="true">
              <i /><i /><i />
            </div>
          ) : (
            <EvidenceList items={evidence?.items ?? []} />
          )}
        </section>

        <ScoreMethod />
      </div>
    </AppShell>
  );
}
