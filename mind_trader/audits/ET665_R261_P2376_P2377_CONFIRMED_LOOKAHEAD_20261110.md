# ET665.R261 — P2376/P2377 ORIGINAL SOURCE RECOVERED; LOOKAHEAD LEAK CONFIRMED
Date 2026-11-10 | GitHub default branch source recovered by direct fetch:
- app/runtime/p2376_de40_big_player_context_xray_engine.py blob de50c447cd77df673a9fe42bde5cae0a69abc573
- app/runtime/p2377_de40_regime_first_signal_router_with_xray_lifecycle.py blob fdc826403a84f76d07b894b634ed3641f4942896
- app/runtime/staging_v2/memory/tests/test_p2376_de40_big_player_context_xray_engine.py blob 9196fc8371be2202fdbac9ea6bad61d48f29dbfc
The archived test directly imports app.runtime.p2376_de40_big_player_context_xray_engine; this led to successful original-code recovery after previous unsuccessful keyword searches.

Root cause:
P2376 context_window uses candles[i+1:i+after+1] to compute post_mfe_atr, post_mae_atr, post_followthrough and post_efficiency. P2377 classify_lifecycle reads these future outcomes to choose lifecycle and lifecycle_score; context_score reads future post_efficiency and lifecycle_score; build_xray_router uses score thresholds >=70 to allow PAPER candidate, <55 to block, otherwise observe. Therefore decision at time i depends on future candles.

An isolated offline Python reproduction of the exact relevant formulas (NOT original-module import) mutated only candles 41..60 while keeping candles 0..40 and event fixed. Favorable future: MFE=2.0 MAE=0.2 lifecycle LIQUIDITY_REVERSAL_ENTRY score=75.0 permission PAPER_CANDIDATE_ALLOWED. Adverse future: MFE=0.2 MAE=2.0 lifecycle FAILED_SWEEP score=49.45 permission BLOCK_LOW_CONTEXT_SCORE. Result future mutation changes decision TRUE. File /mnt/data/et665_r261/temporal_probe_result.json in this chat environment. This demonstrates lookahead in reproduced formulas; original source code inspection establishes causal path.

Regression added to isolated branch tests/test_et665_r261_p2376_p2377_future_candle_invariance.py. Test imports original modules and asserts decision invariance; expected to FAIL on unpatched code; NOT executed against original imported modules in this environment. No CI run claimed. No source engine modification, no merge, no live connections.

Remediation: separate ex-post MFE/MAE/outcome_label into offline label-only dataset, prohibit lifecycle and permission from reading future labels, derive as-of-time lifecycle from <=i features, test mutation invariance and chronological OOS. No P2377 signals promoted until regression PASS and end-to-end replay.
LEDGER V1 ET-711 pending: direct Google Docs writes previously returned 403. GitHub report not Google Doc mutation.
MAIN UNCHANGED | PAPER_ONLY | REAL_ORDERS FORBIDDEN | FTMO_REAL FORBIDDEN | R$0 | CERTIFICATION BLOCKED.
