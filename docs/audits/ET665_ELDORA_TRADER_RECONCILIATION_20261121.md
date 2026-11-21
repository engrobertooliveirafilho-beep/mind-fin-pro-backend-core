# ET665 — ELDORA TRADER evidence reconciliation
Date: 2026-11-21
Branch: engineering/et665-p2071-paper-safety-20261121
Scope: P2071–P2100, historical Drive evidence versus current GitHub runtime.

## Findings confirmed from Drive
- P2071_2080 console_output.txt and P2071_2080_FINAL_CERTIFICATION.json both report status=FAIL; P2080_REALTIME_RUNTIME_CERTIFICATION=PENDING.
- The historical run reports 1,500 cycles, 1,500 frames, 4,329 signals, 411 closed trades, 3 open positions, final equity 99,030.6331 and paper PnL -969.3669.
- The recovered runtime_state.json reconciles 411 closed positions to -969.3669; 369/411 closed positions are negative (89.78%). Three positions remain open.
- The old monitor snapshot reported drawdown_abs=0.0 despite negative realized PnL. This made the historical risk observation incomplete.
- The recovered test suite has only two tests. Replaying the Drive version offline with a deterministic three-specialist fixture produced 1 PASS / 1 FAIL: the certification test expects PASS while the executor returns FAIL because P2080 remains pending.
- P2091 historical console output reports PASS using the same frame/signal/trade counts, while its historical P2081 equity is 99,046.94686, not the P2071 final equity 99,030.6331. This is an unreconciled dependency/metric discrepancy.
- The historical P2091 implementation assigned portfolio PnL equally to specialists, generated default ranking scores from list order, and accepted OVERACTIVE behavior. The current branch removes those unsupported assumptions.

## Published corrections on isolated branch
- P2071: removed fabricated fallback specialist; validate nonempty portfolio, IDs, duplicates and strategy metadata; do not truncate the specialist list; only explicitly implemented RANGE_REVERSION emits signals; unsupported RealDNA strategies force P2073 failure.
- P2081: removed fallback specialist and reject incomplete upstream runtime metrics; P2071 status/readiness gates remain fail-closed.
- P2091: ranking requires explicit specialist scores; attribution requires specialist-level PnL evidence and reconciliation; portfolio intelligence requires positive PAPER PnL; OVERACTIVE behavior no longer passes.
- PAPER_ONLY locks remain unchanged. Synthetic deterministic feed remains explicitly non-certified as a real-time market feed.

## Regression coverage added
- tests/test_p2071_2080_real_dna_fail_closed.py
- tests/test_p2081_2090_evidence_fail_closed.py
- tests/test_p2091_2100_evidence_integrity.py
- tests/test_p2091_2100_behavior_gates.py

## Certification decision
Historical PASS labels for P2081–P2130 are not accepted as current end-to-end certification until the exact source hashes, inputs, ledgers and runtime outputs reconcile. No test run against the current branch has been observed in this session. Do not merge or enable any live/broker execution.
