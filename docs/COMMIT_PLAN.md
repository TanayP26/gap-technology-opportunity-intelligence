# Suggested implementation commits

This is an implementation order, not a script for manufacturing fake history. Commit when each unit genuinely works.

1. `chore: initialise gap api and local postgres`
2. `feat: add analysis preview and query planner`
3. `test: cover signal formulas and query budget`
4. `feat: add serpapi client and request fingerprinting`
5. `feat: normalise scholar and patent evidence`
6. `feat: normalise trends news and market evidence`
7. `feat: persist analysis runs and source status`
8. `feat: calculate versioned technology signals`
9. `feat: add taxonomy generation with manual fallback`
10. `feat: build landscape screen from live analysis data`
11. `feat: add evidence detail and source traceability`
12. `feat: add evidence graph`
13. `test: add parser fixtures and partial-source cases`
14. `docs: document evaluation and serpapi usage`
15. `fix: harden demo path and setup instructions`

Avoid giant commits such as `complete full project` or twenty unrelated files with no intermediate runnable state.
