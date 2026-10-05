import Link from "next/link";
import type { ReactNode } from "react";
import { GlyphIcon } from "@/components/GlyphIcon";

export function AppShell({
  children,
  context,
  methodHref = "/#method",
}: {
  children: ReactNode;
  context?: ReactNode;
  methodHref?: string;
}) {
  return (
    <div className="site-frame">
      <div className="app-shell">
        <header className="topbar">
          <div className="topbar-inner">
            <Link className="brand" href="/" aria-label="GAP home">
              <strong>GAP</strong>
              <span className="brand-rule" aria-hidden="true" />
              <small>Technology<br />Opportunity Intelligence</small>
            </Link>

            <nav className="topbar-nav" aria-label="Primary">
              <Link className="nav-active" href="/">Discover</Link>
              <Link href={methodHref}>Method</Link>
              <Link href="/#analyse">Analyses</Link>
            </nav>

            <div className="topbar-right">
              {context && <div className="topbar-context">{context}</div>}
              <button className="icon-button" type="button" aria-label="Search">
                <GlyphIcon name="search" size={16} />
              </button>
              <span className="user-avatar" aria-label="User profile">TR</span>
            </div>
          </div>
        </header>

        <main className="app-main">{children}</main>

        <footer className="footer">
          <span>GAP · evidence before narrative</span>
          <span>Transparent ranking heuristics, not forecasts.</span>
        </footer>
      </div>
    </div>
  );
}
