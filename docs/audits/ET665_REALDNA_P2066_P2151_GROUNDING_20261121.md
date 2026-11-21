# ET665 — Reconciliation of historical RealDNA portfolio and runtime (2026-11-21)

## Original evidence recovered from Google Drive
- P2066–P2070 original final portfolio: Drive ID `1SydyWbGewyTFdZBnXcCy6pLuMP-C3wor`; exact original JSON copied into `data/specialists/P2066_2070/PORTFOLIO_FINAL_LOCKED_REALDNA.json`.
- P2066–P2070 readiness record: Drive ID `1ehwUddbLPDcsERWuH5o7PNJJ3_QFMvD7`.
- Historical 3 specialists: 0004 RANGE_REVERSION, 0003 MEAN_REVERSION, 0001 TREND_PULLBACK; total historical 28,721 trades and P&L +2167.37, **not** a contemporary runtime result.
- Historical assigned weights: 0.5, 0.249856, 0.164287; sum 0.914143. The original P2067 risk record explicitly documents raw weight 0.585858 capped to 0.5 for 0004. The remaining 0.085857 is not evidence of a missing specialist or permission to renormalize.
- P2067 limits: maximum position size per specialist 0.01, maximum daily loss 0.01, maximum total drawdown 0.03. **Current runtime has qty=1.0 and does not implement those risk constraints; historical risk PASS cannot certify it.**
- P2068 explicitly describes correlation/diversification as a structural proxy, not a trade-level correlation computation.

## Reconciliation blockers
1. Runtime implements only RANGE_REVERSION. Original MEAN_REVERSION and TREND_PULLBACK adapters not recovered/certified; fail-closed status must remain.
2. Runtime uses synthetic deterministic market feed, not verified real market data.
3. Runtime quantity 1.0 and unweighted mark-to-market differ from P2067 fixed micro-size risk contract. Do not certify P2074 or P2080 against original portfolio.
4. Real-time runtime has not passed end-to-end offline regression after branch patches; tests published are not tests executed.
5. Historical downstream P2081–P2151 readiness claims depend on P2071–P2080 and must not be promoted on historical console PASS alone.
6. No financial execution, broker order, FTMO real, or main-branch mutation permitted.

## Current branch changes
- Restore exact source JSON; preserve historical P&L as provenance only.
- Add fail-closed portfolio provenance regression tests.
- Repair peak-to-trough maximum drawdown reporting.
- Repair RSI boundaries for flat, monotonically rising and falling prices.
- Replace misleading runtime audit wording with explicit simulation-only scope.

## Certification
SOURCE_RECOVERED=TRUE
SOURCE_PUBLISHED=TRUE
REGRESSION_TESTS_PUBLISHED=TRUE
REGRESSION_TESTS_EXECUTED=FALSE
P2074_RISK_CONTRACT_CERTIFIED=FALSE
P2080_E2E_CERTIFIED=FALSE
PAPER_ONLY=TRUE
REAL_ORDERS=FORBIDDEN
COST_BRL=0

## Incremental evidence — 2026-11-21
- The original REALDNA JSON was opened from the existing local mounted artifact and SHA-256 verified against the recorded Drive digest: 039647f3e5903821eeb3eaf63d7f767d9dad9c58c0b775254249f5e611f0f356 (PASS).
- JSON parse PASS; top-level array contains exactly three original specialists: XAUUSD_M1_REALDNA_0004, XAUUSD_M1_REALDNA_0003, XAUUSD_M1_REALDNA_0001.
- Isolated P2101 Scheduler contract checks executed locally: 4/4 PASS. This validates only the extracted scheduler decision logic, not the full repository suite or end-to-end runtime.
- P2101 now refuses to certify declared scheduling intervals as executed scheduling.
- No GitHub Actions execution, complete pytest run or FTMO operational certification claimed.
