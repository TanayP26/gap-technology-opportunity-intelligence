import type { ReactNode } from "react";

type IconName =
  | "research"
  | "patents"
  | "news"
  | "search"
  | "trends"
  | "grid"
  | "evidence"
  | "check"
  | "error"
  | "trophy"
  | "arrow"
  | "globe"
  | "spark";

const paths: Record<IconName, ReactNode> = {
  research: (
    <>
      <path d="M5 5.5h9.2a1.8 1.8 0 0 1 1.8 1.8V18H6.8A1.8 1.8 0 0 1 5 16.2V5.5Z" />
      <path d="M8.5 9h5M8.5 12h5M8.5 15h3.2" />
      <path d="M16 8.3h2.8V19H9" />
    </>
  ),
  patents: (
    <>
      <path d="M7 4.5h8l3 3v10A1.5 1.5 0 0 1 16.5 19h-9A1.5 1.5 0 0 1 6 17.5V6A1.5 1.5 0 0 1 7.5 4.5Z" />
      <path d="M15 4.8V8h3.2" />
      <circle cx="11.5" cy="12" r="2.2" />
      <path d="m10.1 13.7-.8 2.6 2.2-1 2.2 1-.8-2.6" />
    </>
  ),
  news: (
    <>
      <rect x="4.5" y="5" width="15" height="14" rx="2" />
      <path d="M8 8.5h4.5v4H8zM14.5 8.5H17M14.5 11H17M8 15.5h9" />
    </>
  ),
  search: (
    <>
      <circle cx="10.5" cy="10.5" r="5.5" />
      <path d="m14.8 14.8 4.2 4.2" />
    </>
  ),
  trends: (
    <>
      <path d="M5 17V7M5 17h14" />
      <path d="m8 14 3-3 2.5 2 4-5" />
      <path d="M15.5 8H18v2.5" />
    </>
  ),
  grid: (
    <>
      <rect x="5" y="5" width="5" height="5" rx="1" />
      <rect x="14" y="5" width="5" height="5" rx="1" />
      <rect x="5" y="14" width="5" height="5" rx="1" />
      <rect x="14" y="14" width="5" height="5" rx="1" />
    </>
  ),
  evidence: (
    <>
      <path d="M7 4.5h8l3 3v10A1.5 1.5 0 0 1 16.5 19h-9A1.5 1.5 0 0 1 6 17.5V6A1.5 1.5 0 0 1 7.5 4.5Z" />
      <path d="M15 4.8V8h3.2M9 11h6M9 14h6M9 17h3.5" />
    </>
  ),
  check: <path d="m5.5 12.3 4 4 9-9" />,
  error: (
    <>
      <circle cx="12" cy="12" r="8" />
      <path d="M12 8v5M12 16.5h.01" />
    </>
  ),
  trophy: (
    <>
      <path d="M8 5h8v4.2a4 4 0 0 1-8 0V5Z" />
      <path d="M8 7H5.5v1.5A3.5 3.5 0 0 0 9 12M16 7h2.5v1.5A3.5 3.5 0 0 1 15 12M12 13.5V17M9 19h6" />
    </>
  ),
  arrow: <path d="M5 12h13M14 8l4 4-4 4" />,
  globe: (
    <>
      <circle cx="12" cy="12" r="8" />
      <path d="M4 12h16M12 4a13 13 0 0 1 0 16M12 4a13 13 0 0 0 0 16" />
    </>
  ),
  spark: (
    <>
      <path d="m12 4 1.1 4.1L17 9.5l-3.9 1.4L12 15l-1.1-4.1L7 9.5l3.9-1.4L12 4Z" />
      <path d="m18 14 .5 1.8 1.7.7-1.7.6L18 19l-.5-1.9-1.7-.6 1.7-.7L18 14Z" />
    </>
  ),
};

export function GlyphIcon({ name, size = 18 }: { name: IconName; size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name]}
    </svg>
  );
}
