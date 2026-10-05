"use client";

import { FormEvent, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { AnalysisRunOverlay } from "@/components/AnalysisRunOverlay";
import { AppShell } from "@/components/AppShell";
import { GlyphIcon } from "@/components/GlyphIcon";
import { ScoreMethod } from "@/components/ScoreMethod";
import { createAnalysis } from "@/lib/api";

const demoSubdomains = [
  "Spiking Neural Networks",
  "Memristive Computing",
  "Event-Based Vision",
  "Neuromorphic Processors",
  "Neuromorphic Sensors",
  "On-Device Learning",
];

const sourceCards = [
  { label: "Scholar", detail: "Research papers", tone: "blue", icon: "research" as const },
  { label: "Patents", detail: "Patent filings", tone: "violet", icon: "patents" as const },
  { label: "News", detail: "Recent coverage", tone: "amber", icon: "news" as const },
  { label: "Trends", detail: "Search interest", tone: "mint", icon: "trends" as const },
];

const sourceStrip = [
  { label: "Scholar", icon: "research" as const },
  { label: "Patents", icon: "patents" as const },
  { label: "News", icon: "news" as const },
  { label: "Search", icon: "search" as const },
  { label: "Trends", icon: "trends" as const },
];

export default function DiscoverPage() {
  const router = useRouter();
  const [technology, setTechnology] = useState("");
  const [geography, setGeography] = useState("Worldwide");
  const [subdomains, setSubdomains] = useState<string[]>(["", ""]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const [existingId, setExistingId] = useState("");

  const validSubdomains = useMemo(
    () => subdomains.map((item) => item.trim()).filter(Boolean),
    [subdomains],
  );

  function loadDemo() {
    setTechnology("Neuromorphic Computing");
    setSubdomains(demoSubdomains);
    setGeography("Worldwide");
    setError(null);
  }

  function updateSubdomain(index: number, value: string) {
    setSubdomains((current) => current.map((item, i) => (i === index ? value : item)));
  }

  function addSubdomain() {
    if (subdomains.length < 8) setSubdomains((current) => [...current, ""]);
  }

  function removeSubdomain(index: number) {
    if (subdomains.length <= 2) return;
    setSubdomains((current) => current.filter((_, i) => i !== index));
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    if (technology.trim().length < 2) {
      setError("Enter a technology to analyse.");
      return;
    }
    if (validSubdomains.length < 2) {
      setError("Add at least two subdomains.");
      return;
    }
    if (new Set(validSubdomains.map((item) => item.toLowerCase())).size !== validSubdomains.length) {
      setError("Subdomains must be unique.");
      return;
    }

    setBusy(true);
    setElapsed(0);
    const timer = window.setInterval(() => setElapsed((value) => value + 1), 1000);

    try {
      const result = await createAnalysis({
        technology: technology.trim(),
        subdomains: validSubdomains,
        geography: geography.trim() || "Worldwide",
        confirm_live_search: true,
      });
      router.push(`/analysis/${result.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed.");
      setBusy(false);
    } finally {
      window.clearInterval(timer);
    }
  }

  return (
    <AppShell methodHref="#method">
      {busy && <AnalysisRunOverlay elapsed={elapsed} />}

      <div className="page discover-page page-enter">
        <section className="reference-hero">
          <div className="reference-hero-copy">
            <span className="hero-kicker">From signals to opportunities</span>
            <h1>
              Find tomorrow&apos;s<br />opportunities in<br /><em>technology.</em>
            </h1>
            <p>
              We combine research papers, patents, market signals and search trends to surface
              promising technology gaps early — before they become obvious.
            </p>

            <form className="reference-form-card" id="analyse" onSubmit={submit}>
              <div className="reference-form-head">
                <div>
                  <h2>Start a new analysis</h2>
                </div>
                <button className="manage-button" type="button" onClick={loadDemo} disabled={busy}>
                  Use demo
                </button>
              </div>

              <div className="reference-field-grid">
                <label className="reference-field">
                  <span>Technology domain</span>
                  <input
                    value={technology}
                    onChange={(event) => setTechnology(event.target.value)}
                    placeholder="e.g. Neuromorphic Computing"
                    disabled={busy}
                  />
                </label>
                <label className="reference-field">
                  <span>Geography</span>
                  <input
                    value={geography}
                    onChange={(event) => setGeography(event.target.value)}
                    disabled={busy}
                  />
                </label>
              </div>

              <div className="reference-subdomain-block">
                <div className="reference-subdomain-head">
                  <span>Subdomains ({validSubdomains.length} selected)</span>
                  <button type="button" className="manage-button" onClick={addSubdomain} disabled={busy || subdomains.length >= 8}>
                    Manage
                  </button>
                </div>
                <div className="reference-chip-grid">
                  {subdomains.map((value, index) => (
                    <label className="reference-chip" key={index}>
                      <span className="chip-check">✓</span>
                      <input
                        value={value}
                        onChange={(event) => updateSubdomain(index, event.target.value)}
                        placeholder={`Subdomain ${index + 1}`}
                        disabled={busy}
                      />
                      {subdomains.length > 2 && (
                        <button
                          type="button"
                          onClick={() => removeSubdomain(index)}
                          disabled={busy}
                          aria-label={`Remove subdomain ${index + 1}`}
                        >
                          ×
                        </button>
                      )}
                    </label>
                  ))}
                </div>
              </div>

              {error && <div className="error-banner">{error}</div>}

              <button className="reference-primary" type="submit" disabled={busy}>
                Run Analysis <GlyphIcon name="arrow" size={17} />
              </button>
            </form>

            <div className="reference-resume-card">
              <strong>Open an existing analysis</strong>
              <div>
                <input
                  value={existingId}
                  onChange={(event) => setExistingId(event.target.value)}
                  placeholder="Enter analysis ID (e.g. GAP-2024-001)"
                />
                <button
                  type="button"
                  disabled={!existingId.trim()}
                  onClick={() => router.push(`/analysis/${existingId.trim()}`)}
                >
                  Open
                </button>
              </div>
            </div>
          </div>

          <div className="reference-hero-visual" aria-label="Evidence source network">
            <div className="reference-art-stage" aria-hidden="true">
              <img
                className="reference-sample-art"
                src="/globe-sample-exact.png"
                alt=""
                draggable={false}
              />
              <span className="reference-art-edge-mask" />

              {sourceCards.map((source, index) => (
                <div className={`reference-source-card card-${index + 1} tone-${source.tone}`} key={source.label}>
                  <span className="reference-source-icon"><GlyphIcon name={source.icon} size={17} /></span>
                  <div className="reference-source-copy">
                    <strong>{source.label}</strong>
                    <small>{source.detail}</small>
                    <span className="mini-bars" aria-hidden="true">
                      {[3, 7, 5, 10, 6, 12, 8, 13].map((height, barIndex) => (
                        <i key={barIndex} style={{ height: `${height}px` }} />
                      ))}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <div className="source-principle-line">
              <span>Real data</span><i />
              <span>Transparent method</span><i />
              <span>No black box</span>
            </div>

            <div className="trusted-source-row">
              <span>Trusted data sources</span>
              <div>
                {sourceStrip.map((source) => (
                  <div key={source.label}>
                    <GlyphIcon name={source.icon} size={17} />
                    <strong>{source.label}</strong>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="below-fold-reference">
          <ScoreMethod />
        </section>
      </div>
    </AppShell>
  );
}
