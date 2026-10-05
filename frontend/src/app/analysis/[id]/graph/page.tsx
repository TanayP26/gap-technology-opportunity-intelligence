"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { LoadingState } from "@/components/LoadingState";
import { getEvidence, getLandscape } from "@/lib/api";
import type { EvidenceItem, LandscapeResponse } from "@/lib/types";

type Cluster = {
  subdomainId: string;
  name: string;
  score: number | null;
  evidence: EvidenceItem[];
};

function trimLabel(value: string, max = 42) {
  if (value.length <= max) return value;
  return `${value.slice(0, max - 1)}…`;
}

export default function EvidenceGraphPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const [landscape, setLandscape] = useState<LandscapeResponse | null>(null);
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let live = true;
    getLandscape(id)
      .then(async (data) => {
        const evidence = await Promise.all(
          data.entries.map(async (entry) => ({
            subdomainId: entry.subdomain_id,
            name: entry.name,
            score: entry.gap_score,
            evidence: (await getEvidence(entry.subdomain_id, undefined, 3, 0)).items,
          })),
        );
        if (!live) return;
        setLandscape(data);
        setClusters(evidence);
      })
      .catch((err) => {
        if (!live) return;
        setError(err instanceof Error ? err.message : "Could not build evidence graph.");
      });
    return () => { live = false; };
  }, [id]);

  const height = Math.max(560, 110 + clusters.length * 105);
  const nodes = useMemo(
    () => clusters.flatMap((cluster, clusterIndex) =>
      cluster.evidence.map((item, evidenceIndex) => ({
        item,
        cluster,
        y: 85 + clusterIndex * 105 + (evidenceIndex - 1) * 24,
      })),
    ),
    [clusters],
  );

  if (error) {
    return (
      <AppShell>
        <div className="page"><div className="error-banner">{error}</div></div>
      </AppShell>
    );
  }

  if (!landscape) {
    return (
      <AppShell>
        <div className="page loading-page">
          <LoadingState
            label="Building provenance view"
            detail="Loading persisted evidence samples for each ranked subdomain."
          />
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell context={<span className="context-label mono">graph / {id.slice(0, 8)}</span>}>
      <div className="page graph-page page-enter">
        <section className="analysis-head">
          <div>
            <div className="breadcrumb">
              <Link href="/">Discover</Link><span>/</span>
              <Link href={`/analysis/${id}`}>{landscape.technology}</Link><span>/</span>
              <span>Evidence graph</span>
            </div>
            <h1>Evidence provenance</h1>
            <p>
              A trace map from technology → subdomain → persisted source record. Edges show
              provenance membership only; they do not imply causal relationships.
            </p>
          </div>
          <Link className="secondary-button" href={`/analysis/${id}`}>← Landscape</Link>
        </section>

        <section className="graph-stat-strip">
          <div><span>Technology</span><strong>{landscape.technology}</strong></div>
          <div><span>Subdomains</span><strong className="mono">{clusters.length}</strong></div>
          <div><span>Visible evidence nodes</span><strong className="mono">{nodes.length}</strong></div>
          <div><span>Graph semantics</span><strong>provenance only</strong></div>
        </section>

        <section className="panel graph-panel">
          <div className="graph-panel-head">
            <div>
              <span className="eyebrow">Trace map</span>
              <h2>From score to source</h2>
            </div>
            <div className="graph-legend">
              <span><i className="node-key technology" /> technology</span>
              <span><i className="node-key subdomain" /> subdomain</span>
              <span><i className="node-key evidence" /> evidence</span>
            </div>
          </div>

          <div className="graph-scroll">
            <svg
              className="evidence-graph"
              viewBox={`0 0 1050 ${height}`}
              role="img"
              aria-label="Evidence provenance graph"
            >
              <line x1="168" y1={height / 2} x2="330" y2={height / 2} className="graph-trunk" />
              <circle cx="120" cy={height / 2} r="46" className="graph-tech-node" />
              <circle cx="120" cy={height / 2} r="58" className="graph-tech-halo" />
              <text x="120" y={height / 2 - 4} textAnchor="middle" className="graph-tech-label">
                {trimLabel(landscape.technology, 20)}
              </text>
              <text x="120" y={height / 2 + 15} textAnchor="middle" className="graph-mini">technology</text>

              {clusters.map((cluster, index) => {
                const y = 85 + index * 105;
                return (
                  <g key={cluster.subdomainId} style={{ animationDelay: `${index * 80}ms` }} className="graph-cluster">
                    <path d={`M 330 ${height / 2} C 365 ${height / 2}, 355 ${y}, 405 ${y}`} className="graph-edge" />
                    <a href={`/analysis/${id}/subdomain/${cluster.subdomainId}`}>
                      <rect x="405" y={y - 30} width="210" height="60" rx="8" className="graph-subdomain-node" />
                      <text x="422" y={y - 5} className="graph-subdomain-label">{trimLabel(cluster.name, 28)}</text>
                      <text x="422" y={y + 15} className="graph-mini">GAP {cluster.score?.toFixed(3) ?? "—"}</text>
                    </a>
                    {cluster.evidence.map((item, evidenceIndex) => {
                      const ey = y + (evidenceIndex - 1) * 24;
                      return <path key={`${cluster.subdomainId}-${item.id}`} d={`M 615 ${y} C 665 ${y}, 660 ${ey}, 720 ${ey}`} className="graph-evidence-edge" />;
                    })}
                  </g>
                );
              })}

              {nodes.map(({ item, cluster, y }) => (
                <a
                  key={`${cluster.subdomainId}-${item.id}-node`}
                  href={item.url ?? "#"}
                  target={item.url ? "_blank" : undefined}
                  rel={item.url ? "noreferrer" : undefined}
                >
                  <rect x="720" y={y - 15} width="290" height="30" rx="5" className="graph-evidence-node" />
                  <text x="732" y={y + 4} className="graph-evidence-label">{trimLabel(item.title, 42)}</text>
                  <text x="997" y={y + 4} textAnchor="end" className="graph-evidence-type">{item.evidence_type}</text>
                </a>
              ))}
            </svg>
          </div>

          <div className="graph-footnote">
            Showing up to three persisted records per subdomain for readability. Open a subdomain for the full evidence ledger.
          </div>
        </section>
      </div>
    </AppShell>
  );
}
