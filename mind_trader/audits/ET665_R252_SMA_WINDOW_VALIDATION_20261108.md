# ET665.R252 — SMA window validation

Date: 2026-11-08. Draft PR #18, P15.25.

## Finding
The P15.25 `reconstruct()` accepted SMA periods of zero, negative values and `fast >= slow`. Zero could trigger division by zero in `sma()` with sufficiently long input; other invalid periods could invalidate the intended crossover strategy.

## Patch
Reject `fast <= 0`, `slow <= 0`, and `fast >= slow` before the simulation loop. New offline unit tests cover six invalid pairs and one valid positive control.

## Evidence boundary
Code and tests published, **not executed**. No CI/Docker PASS, review, R113 gateway integration, R60 reconciliation or MT5 isolation evidence. Keep PR draft/unmerged, no production changes, no real orders. FASE_B=0/16; HP19=0/19; COST=R$0.
