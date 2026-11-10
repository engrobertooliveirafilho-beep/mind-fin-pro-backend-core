# MC R267 — Cognitive dependency source validation (2026-11-10)

New source reads from Google Drive:
- `app/cognition/purpose_kernel.py` Drive `1Nz9OgFwIR7hSnfh4ReNVmUCZwsIMkJkg`: `PurposeKernel.evaluate_action` weighted scoring user_benefit .35, safety .25, long_term .2, cashflow .1, learning .1; fallback missing/invalid scores to 0.5. **Risk**: `float('nan')` is not rejected and may propagate NaN into score, making all threshold comparisons false.
- `app/cognition/reality_model.py` Drive `1s52B2x7RD362TIrMKTTOd1dCfvV5QA-w`: evidence score = min(1, count * .3), speculation keywords heuristic, certainty formula; **Risk**: evidence is counted, not authenticated; four arbitrary list elements can give certainty=1.0 and grounded classification.
- `app/cognition/internal_state_orchestrator.py` Drive `1vXT2aB_nQ_k96-6DFj-V6dDRx90Y-qV3`: 5 modes (analysis/focus/creative/rest/guard), high_risk prioritizes guard, mode switch mutates process-local state, history truncates >1000 to last 500. **Risk**: no durable history or institutional permission enforcement; `switch_mode` is not a security boundary.

Dependency graph extension: `global_coherence` depends on all three above, plus computational_will and auto_explanation, which remain to be resolved. Do not duplicate engines or integrate until source hashes and isolated tests are checked.

This is source inspection, **not** executed functional tests. HP19 0/19, main/production unchanged. Master ledger write previously failed with 403; this is a pending append record.
