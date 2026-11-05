# ET-659 — S20 writer lineage, historical recovery and GitHub confrontation (2026-11-05)

## Newly discovered historical authority
Drive `TRADER_S21_R13_R2D_R6_R5_R2_R1_FINAL_REPORT.txt` ID `1v-kYhMR-ferb9dI-JfbvhUgl47vVYti8`, run `20260810_111839`, supersedes prior R6-R5-R1 unresolved state:
- `CANONICAL_WRITER_RESOLVED=True`, `CANONICAL_FACTORY_SHA256=3E4A66308FDF69BEEC2A1DE3309C68A14F8AD285787CD63EAF56A0FB237B7C42`
- `CANONICAL_FACTORY=.../app/runtime/mind_trader_institutional_wiring.py`
- `FACTORY_METHOD_CANDIDATES=5`, `RETURN_ROWS=4`, `ALIAS_ASSIGNMENTS=10`, `CONCRETE_CALLABLE_DEFINITIONS=2`
- `S20_SYMBOL_PRESENT=False`, `AUTHORITY_MODE=CANONICAL_WRITER_INSTANCE_RESOLVED_SYMBOL_INCAPABLE`
- `SOURCE_MUTATION=FALSE`, `RUNTIME_STARTED=FALSE`, `DECISION_SYMBOL_MAP_BUILT=FALSE`, `REALIZED_OUTCOME_LEDGER=NOT_BUILT`.
- Suggested next historical stage R6-R6 controlled writer schema patch specification, **not an authorization to patch**.

Drive R9-B final report ID `1I9iYbJTpUMedwcpYmpvGTthFG6O2RSN5` run `20260811_075955` independently says `SERIALIZER_RESOLVED=False`, 0 resolved callee modules, 0 serializer candidates, exact serializer file/hash NULL. Do not conflate writer instance resolution with proven serialization/decision lineage.

## GitHub confrontation
Authenticated branch `audit/et651-paper-execution-chain-20261105` already contains `app/runtime/mind_trader_institutional_wiring.py`, Git blob SHA `c4cb0cb6759c2df6c7c6717d5708372c0b7c26b4` (Git blob SHA **not** SHA-256). This branch file implements a generic institutional module import/run/health aggregator, not demonstrably the exact historical factory or S20 decision writer. The original historical SHA-256 is not verified against this GitHub file; do not equate path with source identity or overwrite existing module.

## Gate
The 58-symbol Feature Store manifest is hash-certified ET-658, but no explicit `day+tick -> symbol` join nor `day+tick -> realized outcome` was proven. Historical R2D join coverage 0/84000. No runtime integration, OOS backtest or FTMO certification authorized. No new tests executed this stage. `PAPER_ONLY`, `REAL_ORDERS=0`, `FTMO_BLOCKED`, main unchanged.
