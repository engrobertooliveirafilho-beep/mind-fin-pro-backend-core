# ET665 — ELDORA TRADER reconciliation
Date: 2026-11-21
Branch: engineering/et665-realdna-reconciliation-20261121
Base: main
Scope: P2071–P2100.

## Drive evidence
- Archived P2071 console output and final certification both report FAIL; P2080 is PENDING.
- 1,500 cycles, 1,500 frames, 4,329 signals, 411 closed trades, 3 open positions.
- Realized equity 99,030.6331 from 100,000; realized PnL -969.3669.
- 369 of 411 closed trades are negative (89.78%). Three positions remained open.
- Archived test suite contains two tests. Offline replay of archived Drive source with a deterministic three-specialist fixture: 1 PASS / 1 FAIL. The failing assertion expected PASS although P2080 remained PENDING.
- P2091 archived output claims PASS while P2071 archived certification reports FAIL. P2091 output equity (99,046.94686) also differs from P2071 runtime_state realized equity (99,030.6331).
- Archived P2091 implementation assigned portfolio PnL equally across specialists, derived fallback ranking scores from list order and accepted OVERACTIVE behavior.

## Corrections on isolated branch
- P2071: remove fabricated portfolio fallback; validate specialist IDs and strategy metadata; preserve all specialists; do not silently reuse RANGE_REVERSION logic for unsupported RealDNA strategies; distinguish synthetic feed from certified real-time feed; P2080 may certify simulation scope only.
- P2081: remove fabricated specialist fallback and reject incomplete upstream metrics; existing P2071 PASS/readiness dependency gate remains fail-closed.
- P2091: require explicit specialist scores; require specialist-level PnL evidence reconciled to portfolio PnL; require positive portfolio PnL; reject OVERACTIVE behavior.
- PAPER_ONLY and all real-order/broker locks remain unchanged.

## Tests
Added four regression suites for P2071, P2081 and P2091. No current-branch test execution is claimed yet.

## Decision
P2071 real-time certification, downstream P2081–P2130 certification and E2E remain BLOCKED pending the original RealDNA portfolio, supported strategy adapters, real market-data integration, consistent ledgers, and executed regressions. No production deployment, merge or live trading.
