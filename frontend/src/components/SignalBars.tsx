import { pct } from "@/lib/format";
import type { SignalVector } from "@/lib/types";

const signals: Array<{
  key: keyof Omit<SignalVector, "confidence">;
  label: string;
  source: string;
}> = [
  { key: "research", label: "Research momentum", source: "Google Scholar" },
  { key: "patents", label: "Patent momentum", source: "Google Patents" },
  { key: "attention", label: "Public attention", source: "Google Trends" },
  { key: "events", label: "Commercial events", source: "Google News" },
  { key: "market", label: "Visible market presence", source: "Google Search" },
];

export function SignalBars({ values }: { values: SignalVector }) {
  return (
    <div className="signal-bars">
      {signals.map((item, index) => {
        const value = values[item.key];
        return (
          <div className="signal-row" key={item.key}>
            <div className="signal-name">
              <strong>{item.label}</strong>
              <span>{item.source}</span>
            </div>
            <div className="bar-track" aria-hidden="true">
              <div
                className={value == null ? "bar-fill unavailable" : "bar-fill"}
                style={{
                  width: value == null ? "0%" : `${value * 100}%`,
                  transitionDelay: `${index * 70}ms`,
                }}
              />
            </div>
            <span className="signal-value mono">{pct(value, 1)}</span>
          </div>
        );
      })}
      <div className="signal-row confidence-row">
        <div className="signal-name">
          <strong>Evidence confidence</strong>
          <span>source coverage + retrieval health</span>
        </div>
        <div className="bar-track" aria-hidden="true">
          <div className="bar-fill confidence" style={{ width: `${values.confidence * 100}%`, transitionDelay: "380ms" }} />
        </div>
        <span className="signal-value mono">{pct(values.confidence, 1)}</span>
      </div>
    </div>
  );
}
