# ET665 — Evidence reconciliation P2066–P2090, 2026-11-21

## Drive primary evidence (read directly)
- Original P2066–P2070 readiness JSON: Drive file 1ehwUddbLPDcsERWuH5o7PNJJ3_QFMvD7, timestamp 2026-06-18. Historical 3-specialist portfolio, P2067 fixed paper micro-size 0.01, daily loss 1%, total drawdown 3%.
- P2071–P2080 audit: Drive file 1fo3wvD_8WjmPlLi6GAHr60V3LIhD-34_. Historical status FAIL, P2080 PENDING, 1500 cycles, 4329 signals, 411 closed trades, P&L -969.3669; historical drawdown_abs reported 0.0 and is not credible as maximum drawdown.
- P2081–P2090 audit: Drive file 1oWQwpzBIYmuDjJc6pK1KOPu84fPFXQX5. Historical status PASS, claimed governance certification, but explicitly consumes P2071–P2080 certification file as dependency. Its metrics report mark-to-market P&L -953.05314 and drawdown -0.00953053. Historical P2081–P2090 PASS **cannot override** the upstream P2080 FAIL/PENDING.
- Search hits for strategy names and agents were mostly console/evidence/inventory references, not authenticated original strategy adapter source. Do not count those as recovered motors or agents.

## Branch technical changes
- Paper quantity capped at 0.01 (synthetic unit, not broker lot certification).
- Realized/unrealized P&L quantity-weighted.
- Invalid signal side and nonfinite prices/confidence rejected.
- Daily realized loss gate 1%, total loss gate 3%, one position per specialist, max three positions.
- Admission now uses marked-to-market equity for unrealized losses.
- Boundary RSI tests and peak-to-trough drawdown correction.
- Regression tests committed but not yet run on the complete GitHub branch.

## Remaining critical defects / gates
- Current risk admission is a simplified check, not a certified P2067 risk engine. Full intraday high-water marks, persistent sessions, mark-to-market breach response, spread, slippage, commission, fill mechanics, symbol/contract sizing, and execution cost attribution remain unverified.
- Original MEAN_REVERSION and TREND_PULLBACK strategy adapters not recovered; fail closed.
- P2081–P2090 governance cannot be certified while P2080 and its real-time feed remain uncertified.
- Current data feed synthetic only. No broker or real-order execution.
- Container cannot resolve github.com, so branch code has not been run in local Docker or pytest; do not report test PASS.

## Status
GITHUB_BRANCH_PATCHED=TRUE
GITHUB_READBACK=TRUE
TESTS_PUBLISHED=TRUE
TESTS_EXECUTED=FALSE
P2067_RISK_CERTIFIED=FALSE
P2080_E2E_CERTIFIED=FALSE
P2090_GOVERNANCE_CERTIFIED=FALSE
PAPER_ONLY=TRUE
REAL_ORDERS=FORBIDDEN
COST_BRL=0
