# R387 — Reconciliation of MIND agent and Trader evidence (2026-10-31)

## Certified by current CI
- R383 original-source static suite: GitHub Actions 41232864017 SUCCESS, Python 3.12.
- R384 quarantine fixes: GitHub Actions 41233603652 SUCCESS, job 124632664576, 9/9 tests, commit 809c9bdcfd98b86d1a2f7ce208eb77e663ece13f.
- R343 Trader DE40 structural/causal tests: GitHub Actions 41231592718 SUCCESS, 9/9, commit 050a4317a4aebe50b16d3fae431a2eecda272f4f.

## New historical Drive source
DOSSIE_AUDITORIA_PROFUNDA_P2383_P2391.pdf, Drive file ID 1-qBzDz-p6ct7u0Un37FFrlDvOhcev_1O.
The dossie REPORTS (not independently reproduced): P2385 920 candidates, 230 PAPER and 690 blocked, PF=1.543464, WR=56.521739%, expectancy=0.104782R; P2388 230 learning events, NetR=24.099759; P2391 99,998 events, 4,288 candidates, 40 promoted, 352 observed, 3,896 rejected, best PF=4.161794, WR=63.33%, expectancy=0.279106R. Historical next stage: P2392_EDGE_WALK_FORWARD_VALIDATION. These historical metrics are NOT verified OOS or FTMO certification. Governance remains PAPER_ONLY, REAL_ORDERS=FORBIDDEN, FTMO_REAL=FORBIDDEN.

## Required blockers
- Independent SHA-256 provenance for original source files and seven DE40 datasets is missing.
- No original executable end-to-end agent runtime or independent OOS/forward replay certified.
- R384 fixes are isolated, not integrated into the canonical runtime.
- R334 Drive recovery workflow has unresolved failures.
- No assertion of FTMO readiness or profitable execution is authorized.

## Gates
DOSSIER_GROUNDING_GATE=PASS_FOR_DOCUMENTARY_CLAIMS_ONLY
FINALIZATION_LINE_GATE=BLOCKED
CHAT_DRIFT_INTERLOCK=PASS
PROMOTION=BLOCKED
FTMO_READY=FALSE
