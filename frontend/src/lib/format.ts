export function pct(value: number | null, digits = 0) {
  if (value == null) return "—";
  return `${(value * 100).toFixed(digits)}%`;
}

export function score(value: number | null) {
  if (value == null) return "—";
  return value.toFixed(4);
}

export function shortScore(value: number | null) {
  if (value == null) return "—";
  return value.toFixed(3);
}

export function formatDate(value: string | null) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export function compactNumber(value: number) {
  return new Intl.NumberFormat("en", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}
