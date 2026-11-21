# TRADER.1.004–1.006 reconciliation and feature-store contract gate
Date: 2026-11-21
Repository: `engrobertooliveirafilho-beep/mind-fin-pro-backend-core`
Branch: `engineering/p2614-replay-failclosed-20261120`

## Drive evidence reconciled
- TRADER.1.004 run `20260719_074124`: certificate says CERTIFIED; 268 lake files, 58 assets, 6 timeframes, 6,412,100,031 bytes; source mutation NONE; Drive certification TRUE. This supersedes the earlier initial R1 failure, not the raw source.
- TRADER.1.005-R6: 268 asset/timeframe pairs, 42 feature definitions, 11,256 catalog rows, look-ahead failures 0; local certificate explicitly says `MATERIALIZATION: NOT STARTED / FOUNDATION ONLY`. All 11,256 catalog rows have `PENDING_TRADER_1_006`, lag=0 and future_offset=0.
- TRADER.1.006-R3-R2: controlled execution and post-execution certification completed for 300 records, 300 events, 300 feature records, 12 batches and 14 files. Certificate says CERTIFIED_NOT_PROMOTED; promotion blocked.
- TRADER.1.006-A2 audit (2026-07-30): 300 JSONL rows are classified as `TRADER_1_006_CERTIFIED_ARTIFACT_METADATA`; semantic index has no symbol/timeframe/timestamp values and marks `feature_container=False`. The GER40_CASH/M1 feature-store path contains only `_FOUNDATION.json` with `materialization=PENDING_TRADER_1_006`. Therefore the 300 certified records are artifact metadata, not the 42 market features per asset/timeframe.
- TRADER.1.003-X4 file_audit.csv exists in multiple Drive copies with identical content: 210/210 rows FAIL, 973,468 out-of-order records. Timestamps appear descending. This is a separate raw-history ordering issue; do not silently reinterpret it as an ascending dataset or as a failure of the immutable raw-lake copy.

## New code published in this branch
- `app/runtime/trader_feature_store_contract.py`: pure fail-closed validator for TRADER.1.FEATURE.STORE.V1. Checks exact feature set, provenance, SHA-256, UTC timestamps, finite values, warm-up nulls, duplicate primary keys, strict chronological ordering, nonnegative lag and future_offset<=0. It never computes features or promotes strategies.
- `app/data/trader_feature_definitions_v1.json`: 42 unique feature definitions extracted from the Drive catalog.
- `tests/test_trader_feature_store_contract.py`: 15 regression cases, including rejection of the metadata-only TRADER.1.006 record shape.

## Execution evidence
Local offline run in the isolated workspace: `PYTHONPATH=. pytest -q` → **45 passed** across P2614 chronology/fail-closed, audit/Monte Carlo hardening and feature-store contract tests. This is unit evidence with deterministic fixtures, not execution against all 6.4 GB of canonical market data.

## Remaining gate
Feature calculation/materialization is still NOT implemented or certified. The original Drive materializer source was not found in the A1 readiness inventory (0 source-code candidates). The next implementation must read the immutable P1.004 lake in ascending UTC order, calculate all 42 definitions without look-ahead, write the contract schema, and prove lineage/hash parity before any strategy replay. The Drive API/rclone quota issue recorded in the later master ledger remains a separate operational blocker for full remote traversal.

`PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | MAIN=INTACTA | PRODUCTION=INTACTA | PROMOTION=BLOCKED | E2E_CERTIFIED=FALSE | COST=R$0`
