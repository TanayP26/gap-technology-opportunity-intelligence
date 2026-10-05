import type { EvidenceItem } from "@/lib/types";

function hostname(url: string | null) {
  if (!url) return null;
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return null;
  }
}

export function EvidenceList({ items }: { items: EvidenceItem[] }) {
  if (!items.length) {
    return <div className="empty-box">No persisted evidence matched this filter.</div>;
  }

  return (
    <div className="evidence-list">
      {items.map((item, index) => {
        const host = hostname(item.url);
        return (
          <article className="evidence-row" key={item.id} style={{ animationDelay: `${Math.min(index, 8) * 45}ms` }}>
            <div className="evidence-type-wrap">
              <span className={`evidence-type evidence-${item.evidence_type}`}>{item.evidence_type}</span>
              <span className="mono evidence-index">{String(index + 1).padStart(2, "0")}</span>
            </div>
            <div className="evidence-main">
              <h3>
                {item.url ? (
                  <a href={item.url} target="_blank" rel="noreferrer">
                    {item.title}<span className="external-mark" aria-hidden="true">↗</span>
                  </a>
                ) : item.title}
              </h3>
              <div className="evidence-meta">
                {item.source_name && <span>{item.source_name}</span>}
                {host && <span className="mono">{host}</span>}
                {item.published_at && <span>{item.published_at}</span>}
              </div>
              {item.snippet && <p>{item.snippet}</p>}
            </div>
          </article>
        );
      })}
    </div>
  );
}
