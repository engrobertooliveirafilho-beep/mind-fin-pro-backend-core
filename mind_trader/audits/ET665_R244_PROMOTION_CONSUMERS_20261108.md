# ET665.R244 — Promotion consumers and independent certification gate

Status: SOURCE_INSPECTED / CODE_PATCHED / TESTS_PUBLISHED_NOT_EXECUTED / PHASE_B_OPEN.

Base: PR #17 HEAD 1c5bc7b04b69fabd38f46204a4e02de3ffd5ba76. Isolated branch; no main or production modification.

## Trace (authenticated GitHub source inspection)
- P15.6–P15.10 writes `reports/P15.6_P15.10_REAL_EDGE_RESEARCH_RUNTIME/promoted_edges.json`. Its `promoted` boolean is computed from PF, trade count, a walk-forward proxy and Monte Carlo; it denotes a research candidate, NOT independent approval.
- P15.11 reads that JSON and writes `approved_edges.json` when `forensic_score >= 7`; its score is derived from the same metrics, not an independent reviewer.
- P15.12 consumes P15.11 approved edges, enforces PF>=1.50, trades>=30, WF and MC, and correctly labels outputs `EDGE_CANDIDATE_STRONG`, with `CAUSALITY=NOT_PROVEN`.
- P15.16 writes `combo_promoted_edges.json` from metrics, with `EDGE=COMBO_CANDIDATE_FOUND`, `CAUSALITY=NOT_PROVEN`. No independent approval evidenced in that producer.
- P15.18 consumes P15.17 approved edges and computes proxy correlations and portfolio approval. Its `portfolio_approved` is a simulated research metric, not institutional certification.
- **Critical finding:** P15.19–P15.25 consumes P15.17 approved edges, promotes any reconstruction with >=20 trades to `PAPER_CANDIDATE`, then sets `P15_25_CERTIFICATION=PAPER_RESEARCH_CERTIFIED` when at least one such candidate exists. That is an unapproved metric-to-certification transition. This branch changes that output to `RESEARCH_ONLY` and `APPROVED_EDGES=0`, with explicit `INDEPENDENT_APPROVAL=NOT_PROVEN`.
- P15.25B and P16 were previously patched to remain `RESEARCH_ONLY` absent independent evidence.

## Limitations / remaining blockers
- This is a targeted source trace, not a full dataflow proof across the truncated repository tree.
- Verify all downstream readers of `institutional_certification.json` and other `PAPER_RESEARCH_CERTIFIED` markers.
- Run new offline negative tests, retain JUnit and SHA256 evidence. No CI or Docker execution is claimed here.
- Verify independent authority, MT5/process isolation, R113 gateway integration, R60 Drive/GitHub reconciliation, HP19 0/19 and formal reviewer sign-off.
- Branch protection previously observed as disabled. No merge authorized.

Security constraints: PAPER/DEMO only; REAL_ORDERS=FORBIDDEN; FTMO_REAL=FORBIDDEN; COST=R$0.
