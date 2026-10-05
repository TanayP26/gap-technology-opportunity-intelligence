# GAP Phase 4.2 — Apple-like minimal premium UI

This pass implements the approved light, premium product direction without changing the Phase 3.1 backend or scoring model.

## Design changes

- Light premium palette: soft blue-white canvas, crisp white surfaces, cobalt primary accent, restrained semantic chart colors.
- Tighter 1180px product canvas to remove the stretched dashboard feel.
- Landing page rebuilt as a balanced two-column product shell with the analysis workflow on the left and a restrained evidence-source visualization on the right.
- No fake source counts or fabricated market claims are shown on the landing page.
- Analysis view rebuilt around a compact metric strip, opportunity map, ranked subdomain rail, map-reading guide, and transparent signal matrix.
- The opportunity map keeps the agreed encoding: X technical momentum, Y demand momentum, bubble size GAP score, ring visible market presence, opacity confidence.
- Subdomain detail, evidence ledger, provenance graph, loading states, controls, and method section all share the same design system.
- Animations are limited to useful micro-interactions, route entrance, source visualization motion, loading feedback, and graph/chart emphasis.
- `prefers-reduced-motion` is respected.
- Mobile and tablet breakpoints are retained.

## Product rules preserved

- Scores remain ranking heuristics, not forecasts.
- Missing required signals are not converted to zero.
- Source provenance remains visible.
- No chatbot, fake AI insight cards, fabricated metrics, gradient-heavy glassmorphism, or decorative feature clutter was added.
