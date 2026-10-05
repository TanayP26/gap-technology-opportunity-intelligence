export function LoadingState({
  label,
  detail = "Loading persisted evidence and score state.",
}: {
  label: string;
  detail?: string;
}) {
  return (
    <div className="loading-state" role="status" aria-live="polite">
      <div className="loading-orbit" aria-hidden="true">
        <span />
        <span />
        <span />
      </div>
      <div>
        <strong>{label}</strong>
        <p>{detail}</p>
      </div>
      <div className="loading-rails" aria-hidden="true">
        <i />
        <i />
        <i />
      </div>
    </div>
  );
}
