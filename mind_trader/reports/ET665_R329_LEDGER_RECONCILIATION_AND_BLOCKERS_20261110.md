# ET665.R329 — Remediation ledger delta (2026-11-10)

Authority: Google Docs ELDORA_TRADER_MASTER_REMEDIATION_LEDGER V1 (ID 1WYqMJ-wzqmDWTaRzwJGFk4Hj4b7MuBNR7m0F9ct99mI). Read succeeded: 726 paragraphs, original ledger through ET-704. Document update attempted this session and denied HTTP 403. This file is a PROVISIONAL write-ahead journal, not a claim that the Google Doc was updated.

## ET-705 — R327
TESTED_SCOPED / NOT_GLOBAL_CERTIFIED. User-presented Docker result 17/17 PASS, offline, read-only, no network or added privileges. Local operator-reported evidence D:\MIND_TEMP\ET665_R327_DOCKER_VALIDATION\R327_20261110_081116\EVIDENCE. Evidence bytes not independently fetched in this session. Does not prove causal market profitability or 16/16 certification.

## ET-706 — R328
IMPLEMENTED / REGRESSION_PENDING. P2405E3 generates combinatorial candidates and P2405F hash-derived metrics; P2403E lineage quarantined. R328 module evaluates strictly ordered, embargoed train/validation/test windows, per-edge net-of-spread/slippage/commission R and drawdown, explicitly blocks runtime promotion. Commit 264443c1f91d7ca1a140ab3cacc82d24391a92e2. 21 regression tests published, Docker 38 expected, no PASS evidence in this session. No OHLC-derived original reviewed trade file found.

## ET-707 — R329
PATCHED_NOT_CERTIFIED. Source inspection identified (1) test suite calls nonexistent evaluate_causal_oos_csv, (2) immutable R315 reader hardcodes 3-column schema vs R328 13-column contract. Fixes on isolated branch:
- 0f55a7b27f1a0a4b76d8c3cc3965583ccd6a4c9f: call actual evaluate_cost_aware_oos_csv and preserve immutable error wrappers.
- f16c58a5cfb8557256b309b4e29e34c91e2a0269: opt-in explicit expected_columns for immutable snapshot, retaining legacy default.
- 596c8cb10dd4ab30c13cedeb41ea39b201bcb065: R328 requests its exact 13-column schema.
Rollback: revert these commits in reverse order on isolated branch.
GitHub workflow run for latest commit reported failure and startup_failure; no successful Docker execution inferred. Explicit task: execute complete 38-case offline Docker regression; review any failure and repair only proven defects, then checksum and publish logs.

## Remaining gates
1. Obtain GER40 causal OHLC and actual per-trade decision/entry/exit records with source provenance, logical signal rules and costs; reject P2403E/P2405E3/P2405F as measured market edges.
2. Verify leakage via future-candle mutation, embargo/purge, in-sample-only fitting, no test selection/reuse; add an externally verifiable reviewer and market-source hashes.
3. Validate each P2405 strategy separately, then genuine portfolio simulator including capital, simultaneous trades, exposure and cross-strategy correlation, without forcing overlapping trades into single-edge model.
4. Reconcile S20 symbol writer lineage, original OHLC, FTMO loss-equity and risk policy, PAPER broker/gateway, MT5/P15/P16 subprocess isolation, HP19 (19 original implementations, 0 certified), MIND Central authority and 16 security/certification fronts.
5. Commit source/test/evidence/dependency mapping and obtain original source readback. Do not merge, enable production, or authorize real/FTMO orders.

State: PHASE_B_OPEN; 0/16 globally certified; HP19 0/19; R327_SCOPED_DOCKER_17_PASS_REPORTED; R328_38_NOT_PASS; R329_PATCHED_NOT_EXECUTED; GDRIVE_LEDGER_WRITE=403; MAIN untouched by R329; PAPER_ONLY; REAL_ORDERS=FORBIDDEN; FTMO_REAL=FORBIDDEN; COST=R$0.
