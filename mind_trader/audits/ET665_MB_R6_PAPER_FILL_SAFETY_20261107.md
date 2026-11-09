# ET665.MB.R6 — PAPER fill safety

Date: 2026-11-07. Source-grounded GitHub review; no test execution, broker, MT5, CI, Drive historical write or main merge.

## Finding
`simulate_fill` previously coerced `entry` with float(), accepted non-finite values, unvalidated stop/target and costs, and could emit simulated fills with non-finite or nonpositive prices. A valid fill report could therefore be misleading despite no real broker transmission.

## Patch
`0372df9da03c4419c8aa070aa67fe7c0968949e5`: fail-closed for non-dict payload, unknown side, non-finite/boolean/non-numeric/nonpositive entry-stop-target, negative or non-finite spread/slippage/commission, and non-finite/nonpositive resulting fill. This narrows simulated fill acceptance; no broker connectivity added.

## Regression
`93d8df4255323310feffdc1fb8f8d67cd4168d62`: **54 tests prepared, NOT EXECUTED** (5 payload + 6 side + 21 prices + 18 costs + 1 overflow + 1 sell fill + 2 positive).
Prior R2–R5: 103 new unexecuted cases; cumulative R2–R6: **157 unexecuted cases**. The earlier MB 50/50 PASS applies only to its audited historical commit, not these patches.

## Remaining gates
- Verify compatibility with callers and direct broker-adapter paths, and whether ledger sanitization is sufficient.
- Complete line-level reconciliation of the original 74-reference route inventory and review import/call graph.
- Independent review waived by owner; not equivalent to security certification.

`R6_PATCH=STAGED_UNTESTED`
`R6_REGRESSIONS=54_PREPARED_NOT_EXECUTED`
`PHASE_B=OPEN`
`REAL_ORDERS=FORBIDDEN`
`FTMO_REAL=FORBIDDEN`
`MAIN_MERGE=BLOCKED`
