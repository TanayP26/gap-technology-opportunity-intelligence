const pipeline = [
  "Query plan",
  "Source retrieval",
  "Normalization",
  "Signal scoring",
  "Persistence",
];

export function AnalysisRunOverlay({ elapsed }: { elapsed: number }) {
  return (
    <div className="run-overlay" role="status" aria-live="polite" aria-label="Analysis running">
      <div className="run-overlay-card">
        <div className="run-overlay-topline">
          <span className="eyebrow">Live analysis</span>
          <span className="mono run-timer">{String(elapsed).padStart(2, "0")}s</span>
        </div>

        <h2>Building the evidence landscape</h2>
        <p>
          GAP is retrieving source evidence, deriving deterministic signals, and persisting
          the completed landscape. This view stays intentionally indeterminate until the
          backend returns a finished analysis.
        </p>

        <div className="pipeline-rail" aria-hidden="true">
          {pipeline.map((item, index) => (
            <div className="pipeline-node" key={item} style={{ animationDelay: `${index * 140}ms` }}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <strong>{item}</strong>
            </div>
          ))}
        </div>

        <div className="source-pulse-grid">
          {[
            ["Scholar", "research"],
            ["Patents", "IP"],
            ["Trends", "attention"],
            ["News", "events"],
            ["Search", "market"],
          ].map(([name, role], index) => (
            <div className="source-pulse" key={name} style={{ animationDelay: `${index * 110}ms` }}>
              <i />
              <div>
                <strong>{name}</strong>
                <span>{role}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="run-overlay-foot">
          <span>Keep this tab open</span>
          <span className="mono">cached results are reused when available</span>
        </div>
      </div>
    </div>
  );
}
