# STEP441 — isolated regression; byte identity OPEN (2026-11-21)

Drive original `1OJBmh9HRyqdoq-mnGH2r-lwzox7gmJrX`.

Historical source preserved commit `287a27ab10770bdeefc8effaf827d27f920da591`; finite-input and UTC hardening commit `15e42a9684871f0b0e1c435cce613385f547f523`.

**Executed:** local isolated FastAPI TestClient: **9/9 PASS**, covering horizontal expansion, downscale, hold, latency expansion, negative/out-of-range CPU, NaN CPU, Infinity latency, and UTC. This is a **local reconstruction test**, not exact GitHub-source certification.

**Integrity discrepancy:** locally tested engine Git blob `94e90588b5eea3981005635305d9a54a570d27ec` vs GitHub published `d5472ee6eb27ab510c54243f2261edd976be5ad2`. Historical source local `220f6abc668a1537472d64c296a5f4c8c0c35a2e` vs GitHub original `78c1819cfc5edaba03d35493d62948d88bf16acd`. Do **not** certify byte-identical source or full application boot.

**Scope:** static autoscaling recommendations only, not actual infrastructure control. Module intentionally unmounted. No production, paid resources or orders affected.

`PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | MAIN=INTACTA | E2E_CERTIFIED=FALSE | COST=R$0`

## Exact-source reconciliation and certification (2026-11-21)

Reconstructed the **current GitHub source** in isolated Python 3.13 and verified `git hash-object app/infra/autoscaling_policy_step441/engine.py` = `d5472ee6eb27ab510c54243f2261edd976be5ad2`, matching GitHub. Executed isolated FastAPI TestClient: **9/9 PASS** (CPU expansion, latency expansion, downscale, hold, negative CPU, CPU over 100, negative latency, latency above bound, UTC). Local log SHA-256: `f087df3c0857b4fb2ec49570f28199f13aa4d3f3aaa4806ad48eebd020df8a5b`. This supersedes the earlier byte-integrity discrepancy for the **current engine only**; historical original hash discrepancy remains documented. Not a full-app E2E certification; module remains unmounted.

## Historical FTMO authority reconciliation (2026-11-21)

Newly recovered Drive master remediation ledger ID `1WYqMJ-wzqmDWTaRzwJGFk4Hj4b7MuBNR7m0F9ct99mI` (2026-10-29) and final technical certification ID `1Hi-hhRD9lTR9bM6XcvJjnAJBybwhzBZk` (RUN_ID `20260914_204802`). Historical final report states PAPER/BACKTEST-only E2E, risk, PnL/equity and FTMO-like checks PASS, `REAL_ORDER_COUNT=0`, with no FTMO real evaluation. The ledger explicitly warns this does not establish symbol lineage, S21 walk-forward or source-code equivalence. Thus **historical PAPER E2E PASS != current GitHub E2E certification**. The canonical trader writer and institutional runtime remain unverified. Do not promote generic STEP441-445 helpers as substitutes for FTMO engines.
