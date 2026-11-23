# ELDORA TRADER — P2376–P2383D causal reconciliation
Date: 2026-11-23
Base: main @ 1b5916fbdc8c90173061315400abb92f3bbbb13a
Branch: audit/p2376-p2383d-causal-reconciliation-20261123

## Scope and safety
This is an isolated forensic record only. No production runtime, original Drive source, MAIN, or historical ledger was modified. PAPER_ONLY remains mandatory; REAL_ORDERS and FTMO_REAL remain forbidden. No merge or financial certification is authorized.

## Previously completed — do not repeat
- P2403D/D2: GER40/DE40 OHLC recovery already completed; do not repeat dataset discovery.
- P2403E: hash-selected synthetic replay invalidated; never reuse its 4,400 records.
- P2376: original X-Ray engine recovered.
- P2377: original router recovered; causal leakage already identified; gate/audit records exist.
- P2378–P2382: historical outputs preserved; their chain is not accepted as a valid edge proof.
- Historical audit commit reported in conversation: 826f0dfd4fc52324bd08776f90d9d4ad55b028e5 (not found in this repository's commit search during this pass).

## Direct source inspection — current MAIN
P2377 file: app/runtime/p2377_de40_regime_first_signal_router_with_xray_lifecycle.py
Blob SHA: fdc826403a84f76d07b894b634ed3641f4942896
Observed: classify_lifecycle() reads post_mfe_atr, post_mae_atr, post_efficiency and post_followthrough from the context row and uses them to assign lifecycle and score. These are future-window outcomes in the P2376 context contract. The router therefore cannot be used to make a decision at event time without a causal replacement.
P2376 blob SHA: de50c447cd77df673a9fe42bde5cae0a69abc573.
P2378 blob SHA: ebc491833cfe29d18666710cbb757b96c9895253 (source retrieved; future-outcome fields also present; exact call graph still requires line-level review).
P2379 blob SHA: 23cfcb188d684350112acdc733e2d761e0e9e444.
P2380 blob SHA: c8971714e0543e74c66424f8879960d8dea98dc8.
P2381 blob SHA: 94792b12a2baad20742ef39111ca5228738861e4.
P2382 blob SHA: 669df7d3dd9905ea542295aa6c7b08c7cf030d45.

## P2383D historical evidence re-read from Drive
Folder: P2383D_EXACT_PLAYBOOK_TO_RAW_CANDLE_VALIDATOR_20260624_141656 (Drive folder ID 1ZuNFZoqaLm9G9_de4E0GEWwruLyTPa7M).
AUDIT_FINAL declares 3,980 matched OOS trades, 1,865 wins, 2,030 losses, WR 46.859296%, PF 1.033224, expectancy 0.009917, DD 111.593895, 5 promoted and 55 rejected. The summary is a historical claim, not reproduced now.
Cross-check of timeframe audit CSV: M1/M5/M15 samples total 3,980, but wins+losses total only 3,895 (85 outcomes unaccounted); M30/H1/H4/D1 have zero matched OOS trades despite positive OOS event counts. All seven timeframe rows show passed=False.
Promoted CSV contains five distinct playbook IDs with identical M15/TREND_DOWN/OFF_SESSION/LIQUIDITY_SWEEP_REVERSAL_UP/LIQUIDITY_REVERSAL_ENTRY metrics (38 samples, 24 wins, 13 losses, PF 1.916269, expectancy 0.137846). This requires deduplication and provenance audit; the five family labels are not five independent edges.
The context results CSV shows only one context passing and other contexts failing. Therefore P2383D's top-level CERTIFICATION/ORIGINAL EDGE CERT=True claim is not sufficient to accept the promoted rows as independent or fully reconciled.

## Required repair sequence
1. Recover and hash the exact P2376–P2382 original source/test/data artifacts; preserve Drive originals read-only.
2. Replace P2377 lifecycle classification with strictly event-time features. Add tests proving future context columns cannot affect routing.
3. Audit P2378 promotion scoring and sequence construction for any future-window data leakage; reject any outcome-derived inputs at decision time.
4. Rebuild P2379 signals only from timestamped causal events after candle close.
5. Rebuild P2380–P2382 with complete immutable trade ledger; preserve every loss and reconcile counts (samples = wins + losses + unresolved).
6. Reconcile P2383D's 85 missing outcomes, timeframe coverage, five duplicate-context promotions, and cost model before any promotion.
7. Run offline regressions and deterministic replay on verified raw candles; record command, exit code, test counts, SHA-256, and Drive readback.
8. No edge promotion unless independent chronological OOS/walk-forward passes with costs and no look-ahead.

## Status
SOURCE_INSPECTION=PARTIAL
P2377_CAUSAL_DEFECT=CONFIRMED_BY_CODE_READ
P2378_LEAKAGE_REVIEW=OPEN
P2380_P2382_LOSS_PRESERVATION=REPORTED_DEFECT_REQUIRES_REPRODUCTION
P2383D_RECONCILIATION=FAILED_COUNTS_AND_DUPLICATE_PROMOTIONS
PATCHES=NOT_APPLIED
TESTS=NOT_RUN
EDGE_CERTIFIED=FALSE
PAPER_ONLY=TRUE
REAL_ORDERS=FORBIDDEN
FTMO_REAL=FORBIDDEN
MAIN=UNCHANGED
