# R345 — Independent DE40 dataset authority gate

Status: BLOCKED (not a CI failure or successful backtest).

- The original P2383C source expects seven raw-candle files (M1, M5, M15, M30, H1, H4, D1).
- Drive metadata search for the exact M1 basename yielded inventory/log references, not authenticated raw-candle bytes.
- The R334 P0 recovery queue has 10 Drive IDs with sha256_expected=null. They are NOT independent historical hash references.
- Neither a source file's self-computed SHA-256 nor a newly created manifest establishes an independent historical baseline.
- No original strategy may be certified on synthetic fixtures or a directional signal derived from future prices.
- R342/R344 regression tests are safety tests, not a historical backtest.
- The R343 GitHub Actions run is NOT certified: commit-workflow-run lookup and combined-status lookup yielded no evidence of PASS. The workflow-run lookup is limited to PR-triggered runs.

Required before integration: obtain original raw-candle bytes, independent historical hash manifest, documented train/test cutoff, and reproducible CI job URL/logs; reconcile with original entry/exit rules. Keep historical sources immutable, no live orders, no strategy promotion.
