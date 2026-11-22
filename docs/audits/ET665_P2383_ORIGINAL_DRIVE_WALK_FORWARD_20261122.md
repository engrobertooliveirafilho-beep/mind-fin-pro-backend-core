# ET665 — P2383 original P2380 population walk-forward evidence

Date: 2026-11-22
Repository: `engrobertooliveirafilho-beep/mind-fin-pro-backend-core`
Base branch: `main` (PR #37 remains draft; no merge)
Working branch: `engineering/et665-realdna-reconciliation-20261121`
PR base HEAD: `10b778d64f479698a866774328e306ad704cc77b`

## Original Drive source recovered
- P2380 folder: `1rVmxHZJwh47fvIW03t_efE6BIana50ot`
- Canonical feedback CSV: `de40_forward_paper_feedback_all.csv`
- Drive file ID: `1djqqQ7NrpM-uQRYrPU0uB9BHpdOhUZbQ`
- Bytes: 261,383
- SHA-256: `31aa0c813150b249aa6c653971dbb5f9766b6905c642807e81796d455bd4c197`
- Rows: 500; unique signal IDs: 500; distinct entry timestamps: 499.
- All 500 rows are PAPER_ONLY, REAL_ORDERS=FORBIDDEN, FTMO_REAL=FORBIDDEN and carry `PAPER_FEEDBACK_PROXY_NOT_REAL_PNL`.
- Historical P2380 metrics reconcile to 243 positive, 254 negative, 3 zero; expectancy -0.083805 R; PF 0.832504. These are proxy outcomes, not actual broker fills or realized live PnL.

## P2383 exact contract executed on the original population
- Existing `app/runtime/p2383_walk_forward_contract.py` and existing 8-test suite were read from PR #37 HEAD and executed in an isolated Python harness.
- New source-backed integration test added: `tests/test_p2383_original_drive_population.py`. It requires the Drive CSV to be provided through `P2380_FEEDBACK_CSV`, verifies the exact SHA-256, source safety flags, full 500-row population and all five strict chronological folds.
- Execution: **9/9 PASS**, 0 failures, 0.03 seconds. The 9 tests are 8 existing contract tests plus 1 original-Drive integration test.
- Five expanding folds: initial train 250; test windows 50 each. Boundaries:
  1. train ends 2025-06-17 15:00; test ends 2026-01-05 10:00.
  2. train ends 2026-01-05 10:00; test starts 2026-01-05 18:45; ends 2026-03-20 01:45.
  3. train ends 2026-03-20 01:45; test starts 2026-03-20 04:40; ends 2026-04-22 22:16.
  4. train ends 2026-04-22 22:16; test starts 2026-04-23 12:30; ends 2026-05-21 19:21.
  5. train ends 2026-05-21 19:21; test starts 2026-05-22 05:20; ends 2026-06-23 06:02.
- Fold-level proxy diagnostics (not strategy certification): F1 28W/22L, expectancy -0.119447 R, PF 0.728529; F2 30W/20L, +0.148891 R, PF 1.372228; F3 22W/28L, -0.199884 R, PF 0.643065; F4 20W/30L, -0.163096 R, PF 0.718972; F5 29W/21L, +0.094365 R, PF 1.224679.
- One duplicate timestamp exists in the population, but no fold boundary splits equal timestamps; all five train/test boundaries are strictly chronological.

## Material leakage confirmed in P2381/P2382
- P2381 output folder: `1unpqgP-L2HwcAdqHhGMrJ7UgtFTN0Tzt`; patched candidates CSV: `1Aa5a9cRWGlTBCwkWa_TeArS7yExd4S46`; loss memory graph: `1HD74aroxPSZ4oWUBXUAKGt5FAbPRWE`.
- P2381 produced 254 loss-memory nodes and selected 227 replay candidates using the full 500-row outcome population.
- Of the 227 selected candidates, 117 fall in P2383's future/test half (not available to a train-only selection process): F1=26, F2=28, F3=20, F4=18, F5=25.
- Every one of those 117 selected future rows has positive `realized_r`; this directly explains why P2382's 224W/0L result is selection-contaminated. P2382's survivors remain diagnostic only and are not used as P2383 input.
- P2381 original engine source was not recovered in this pass; only its outputs and run log were found. Therefore fold-specific train-only loss-memory regeneration is still blocked and no P2381 patch is applied to test windows.

## Certification boundary / next
- P2383 chronological split: **executed against canonical 500-row Drive CSV**.
- Performance: **NOT CERTIFIED**; outcomes are explicitly proxy PnL and no actual broker fill ledger is present.
- P2381 train-only patch replay: **BLOCKED** until original P2381 engine source and dependencies are recovered or a separately specified replacement is approved.
- No strategy promotion, broker execution, MT5 consumption claim, merge, production change, or paid service.
- Main intact; PAPER_ONLY; REAL_ORDERS and FTMO_REAL forbidden; Drive originals read-only; cost R$0.

`P2383_ORIGINAL_POPULATION=500 | SHA256_VERIFIED | WALK_FORWARD=5_FOLDS | TESTS=9/9_PASS | P2381_TRAIN_ONLY_REPLAY=BLOCKED | PERFORMANCE_CERTIFIED=FALSE | MAIN=INTACTA | PRODUCTION=INTACTA | COST=R$0`
