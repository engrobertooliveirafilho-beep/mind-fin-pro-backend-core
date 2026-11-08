# ET665.R185 — Alternative execution and dependency review (2026-11-08)

## Grounded source
GitHub PR #12 head: `c2e20fb92a33073554f5d1df0c5dcee9e5207501`, isolated branch; default `main` observed at `1b5916fbdc8c90173061315400abb92f3bbbb13a`. Repository-wide recursive tree was `truncated=true` (52,480 entries), therefore coverage is PARTIAL.

## Verified residual findings by direct source inspection
1. `mind_trader/app/p139_mt5_historical_data_puller/engine.py`: `pull()` unconditionally raises `ET665_MT5_UNCERTIFIED_ENTRYPOINT_BLOCKED`, but `run()` creates `reports/P13.9_MT5_HISTORICAL_DATA_PULLER` BEFORE invoking `pull()`. This is a fail-closed ordering defect with premature local side effects. Source also retains an unreachable `IMPLEMENTED` label. Do not certify.
2. `mind_trader/app/p138_platform_connectors/engine.py`: `mt5_probe()` unconditionally raises the same error, but `run()` creates its report directory BEFORE calling `mt5_probe()`. The remaining `profit_probe()` and `ftmo_probe()` also create local directories if called directly. `IMPLEMENTED` is an unverified claim; no blanket functionality certification.
3. `mind_trader/app/p1310_mt5_normalized_dataset_certification/engine.py`: `certified = len(rows)>=200 and not missing` checks only OHLC column presence and row count; source designation is inferred from filename prefix `MT5_`. This is **not** provenance/chronological integrity or original Drive manifest certification. Consumers must not treat this flag as institutional proof of dataset authenticity.
4. `mind_trader/app/p1515_web_research_to_backtest_queue/engine.py`: `certified_datasets()` trusts pre-existing report field `dataset.certified` without independently reconciling hashes/original manifests. This establishes a potential unverified-trust propagation path, not a proven real-order route.
5. `mind_trader/app/p1621e_real_video_fetch_loop/engine.py`: `run()` and `fetch_metadata()` raise explicit external-execution blockers. No real execution observed in source. Report status `IMPLEMENTED` is unreachable while guard is in place.
6. `mind_trader/app/p86_execution_intelligence_domain/engine.py`: `mt5_snapshot()` raises; no global MT5 isolation attested from this inspection.
7. Some alternate engines (e.g. P14.16B) use `runner.py` rather than `engine.py`. A fixed filename-only inventory is incomplete. Global code search returned no matches for two sensitive terms; this absence MUST NOT be interpreted as proof of safe repository-wide coverage.

## Institutional governance finding
Authenticated GitHub `GET /branches/main` reported `protected=false`, `protection.enabled=false`. 'Main unchanged' is a verified snapshot; 'main protected by GitHub branch rules' is NOT verified. No settings were changed.

## R185 limits and required follow-up
- No engine, Docker suite, MT5 terminal, broker, subprocess, network fetch, or Drive reconciliation executed in this review.
- This report is **inspection evidence only**, not security certification.
- R186: consolidate regression matrix and dependency gates. R187: execute offline Docker regressions, capture logs/JUnit/hash and restricted network evidence. R188: reconcile R60 original manifests, independent review, and 12 gates.
- Remediation candidates: move P13.8/P13.9 block ahead of directory creation; separate dataset schema validity from provenance certification; prevent unverified `certified` fields promoting queue authority. Changes require isolated tests and independent review.
- Do not merge current PRs. Do not enable real orders, FTMO real, production actions, or paid infrastructure.

`PHASE_B=OPEN | R185=INSPECTION_ONLY | COVERAGE=PARTIAL | TESTS=NOT_EXECUTED | MAIN=UNCHANGED | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0,00`
