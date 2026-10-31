# R427 — Historical lineage P2369 → P2370 → P2371 → P2372

Date: 2026-10-31. Source of truth: Google Drive historical run logs, read only. This inventory records historical claims, not independent functional certification.

| Stage | Predecessor | Historical evidence | Implementation | Commit | Reproducible test |
|---|---|---|---|---|---|
| P2369 DE40 edge discovery | P2363C dataset | R425: seven reports, 3024 combinations, 149 observed, 0 promoted; four TF bounded | original P2369 recovered; unmodified | R425 audit f85a6466ec646606a67e1e1611d1ae6b12776228 | bounded only; full 4 TF pending |
| P2370 institutional family expansion | P2369 | run_p2370.log: 11 families, 55 variants, 360 catalog candidates, SCALP/INTRADAY/SWING | source code not yet verified | none | historical log only |
| P2371 catalog backtest | P2370 | run_p2371.log: 260 tested, 260 rejected, 0 observed, 0 promoted | source code not yet verified | none | historical log only |
| P2372 parametric variation | P2370 catalog, P2371 decision | run_p2372.log: 360 base rows, 78000 generated, M2 skipped because no real M2 dataset | source code not yet verified | none | historical log only |

Drive evidence:
- P2370 log: https://drive.google.com/file/d/1_QRLHqK23kUUpEvHN8YP2EV1f2vs_bms/view
- P2371 log: https://drive.google.com/file/d/1LW5PmnTL824vi13CFIL75cQNwr3YgH1Q/view
- P2372 log: https://drive.google.com/file/d/17p13WjwXNSRuClLJlpIc2Pyg1QJxYF4b/view

Safety: PAPER_ONLY, REAL_ORDERS FORBIDDEN, FTMO_REAL FORBIDDEN. Historical 'CERTIFIED' status does not mean OOS performance, cost-aware trading validity, or FTMO readiness. Promotion gate remains blocked. Next recover source and tests for P2370, P2371, P2372; verify hashes, isolated execution and equivalence; complete P2369 full four TF and independent cost-aware OOS before any promotion.
