# ET665.R256 — Certification export readiness gate

Date: 2026-11-08. Draft PR #18; P15.25.

## Source finding
The persisted institutional certification report set `EXPORT_READY=True` unconditionally even though `P15_25_CERTIFICATION=RESEARCH_ONLY`, `INDEPENDENT_APPROVAL=NOT_PROVEN` and `APPROVED_EDGES=0`. This could mislead downstream consumers into treating research output as export-certified. No downstream misuse has been demonstrated.

## Patch
The report now sets `EXPORT_READY=False` and `CERTIFICATION_EVIDENCE=NOT_EXECUTED_OR_INDEPENDENTLY_VERIFIED`. Added a persisted-artifact regression for an empty synthetic research run. This flag must not be flipped without independently reviewed execution evidence and explicit authority.

## Verification boundary
Changes published only, tests NOT EXECUTED. No Docker, CI, JUnit, SHA-256 execution evidence, independent review, R113 integration, MT5 isolation or R60 reconciliation. PR draft/unmerged. FASE_B=0/16; HP19=0/19; REAL_ORDERS=FORBIDDEN; FTMO_REAL=FORBIDDEN; COST=R$0.
