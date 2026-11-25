# ELDORA TRADER — P9.4 source-provenance remediation

Date: 2026-11-25  
Branch: `engineering/eldora-p9-failclosed-remediation-20261125`  
Scope: P9.4 DNA extraction only; original Drive artifacts remain read-only.

## Reconciliation

The original GitHub P9.4 implementation used a built-in sample research string whenever `run()` received no source. It therefore emitted DNA/genome candidates without an actual research input. The original source identifier hashed only the first 500 characters, and DNA IDs used only the first 200 characters, allowing different full documents with a shared prefix to collide.

## Correction

- Removed the implicit sample source; `run()` without an explicit source now writes an empty, blocked manifest (`P9.4_BLOCKED_SOURCE_REQUIRED`).
- Explicit source input is validated against supported source types and title constraints.
- Source identity and candidate IDs are SHA-256 derived from the full source content, source type, and candidate identity.
- Every DNA and genome candidate carries the same source hash; mismatched provenance is rejected.
- Extraction is explicitly labeled `BOUNDED_KEYWORD_TAGGING`, not semantic understanding.
- Candidates remain unvalidated; edge, causality, promotion, and export readiness remain false.

## Verification

Isolated Python 3.13.5 test run: **8 passed, 0 failed**. JUnit and SHA-256 evidence are stored under `mind_trader/evidence/p9/`. The local source/test files were run in an isolated sandbox; GitHub readback verified the published files. No repository-wide suite or CI workflow was executed.

## Boundary

This validates source-required behavior, provenance identity, and fail-closed candidate handling. It does not establish semantic extraction quality, backtest validity, edge, FTMO readiness, or production integration.

`PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | MAIN=INTACTA`

## Additional remediation — P9.1 dataset registry

The original P9.1 code generated a catalog of dataset slots, but its manifest marked `EXPORT_READY=true`. It did not ingest or validate any market-data file. The catalog contains 47 assets × 8 timeframes × 4 source types = **1,504 placeholders**, each marked `REGISTERED_PENDING_DATA`.

Correction:
- Status is now `P9.1_CATALOG_ONLY_AWAITING_REAL_DATA`.
- Explicit fields: `DATASET_SLOTS_ONLY=true`, `INGESTION_EXECUTED=0`, `REAL_DATA_FILES=0`, `EXPORT_READY=false`.
- No data ingestion or certification is claimed.

Verification: isolated Python 3.13.5 tests **4 passed, 0 failed**. JUnit and SHA-256 evidence published in `mind_trader/evidence/p9/`.

Drive ledger update was attempted against the existing master ledger but rejected with Google Docs 403 permission denied; the Drive original remains unchanged. GitHub branch and PR contain the authoritative code/evidence for this increment.

## Additional remediation — P9.2 genome identity

The original `gid()` hashed the complete generated record, including `index`. Consequently, two identical strategy phenotypes generated at different positions received different IDs. This made the uniqueness counter describe generation positions rather than distinct strategy configurations.

Correction:
- Genome identity now hashes only phenotype/configuration fields, excluding `index` and `genome_id`.
- Generation index remains metadata and no longer changes strategy identity.
- Manifest now distinguishes generated count, unique phenotypes, and duplicate phenotypes.
- Candidate status is explicit: backtest required, promotion forbidden, edge/causality unproven.

Verification: isolated Python 3.13.5 tests **5 passed, 0 failed**, including 10,000 generated records, stable identity under index changes, and identity changes under phenotype changes. JUnit and SHA-256 evidence published in `mind_trader/evidence/p9/`.

## Downstream fail-closed regressions

A focused isolated harness reconstructed from the published branch readback executed the P9.3, P9.5, P9.6, P9.7, and P9.100 contracts: **13 passed, 0 failed** under Python 3.13.5. The log explicitly records that this was not a full repository checkout or GitHub CI run. JUnit and log are published under `mind_trader/evidence/p9/`.

These tests prove the blocked-state behavior only. They do not prove a real backtest, actual execution of the ten research steps, statistical validity, or FTMO readiness.

## New Drive discovery — canonical GER40.cash M1 dataset

Recovered a separate read-only source manifest from the TRADER.1.004 industrial data-lake evidence:
- Source run: `20260719_074124`.
- Relative path: `lake/raw/mt5/m1/symbol=GER40_cash/timeframe=M1/GER40_cash_M1.csv`.
- Broker/canonical mapping: `GER40.cash` → `GER40_CASH`; timeframe `M1`.
- Declared size: 126,671,713 bytes.
- Declared SHA-256: `D8BAFFAFA857E69615E39DB391F6AA14C9855B04023484EED4730DA7669E6097`.
- Declared MD5: `58af269806c0ae22b16256e4bc913504`.
- Source policy: `READ_ONLY`.

This is manifest evidence only. The raw CSV bytes were not retrieved in this operation, so the declared SHA-256 was not recomputed, OHLC/spread units were not revalidated, and no backtest was executed. P9.1 now includes GER40.cash in its index universe and preserves this exact source record with `MANIFEST_ONLY_HASH_NOT_RECOMPUTED` and `NOT_INGESTED` states. The catalog now has 1,536 slots (48 assets × 8 timeframes × 4 source classes), still placeholders rather than ingested datasets.

Regression after this code change: **5/5 PASS** under Python 3.13.5; JUnit and SHA-256 evidence published under `mind_trader/evidence/p9/`.
