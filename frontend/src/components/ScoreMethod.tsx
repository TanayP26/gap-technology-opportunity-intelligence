export function ScoreMethod() {
  return (
    <section className="method-panel" id="method">
      <div>
        <span className="eyebrow">Scoring method · v1</span>
        <h2>Signal divergence, not prediction.</h2>
      </div>
      <div className="formula-grid mono">
        <p><span>Technical</span>0.55R + 0.45P</p>
        <p><span>Demand</span>0.55A + 0.45E</p>
        <p><span>Whitespace</span>Technical × Demand × (1 − M)</p>
        <p><span>GAP</span>Whitespace × Confidence</p>
      </div>
      <p className="method-note">
        R research · P patents · A attention · E commercial events · M visible market presence.
        Coefficients are transparent product heuristics. Missing required signals are marked as
        insufficient evidence instead of being treated as zero.
      </p>
    </section>
  );
}
