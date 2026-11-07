# ET665.MB.R18 — P69–P75 dependency review and DEMO risk governor hardening

Date: 2026-11-07. Current branch source fetched directly from GitHub. No broker or network process executed.

## Findings
- `p1621f_transcript_download_strategy_extraction/engine.py`: `fetch_subtitles` and `run` immediately raise ET665_BR external execution guard. Confirms R17 pending exact-current-source review.
- `p74_mt5_demo_order_router_dry_run/engine.py`: returns `sent_to_mt5=False` and `real_order_sent=False`; calls P69–P73 governor. No order transport observed in file.
- `p75_mt5_demo_order_execution_controlled/engine.py`: permission is separate from `sent_to_mt5_demo=False`; depends on P69–P73 governor.
- `p69_73_mt5_ftmo_demo_governor/engine.py`: before patch, `p71_pre_trade_governor` only checked `proposed_risk_pct <= max`, so negative/zero/NaN values were not robustly rejected; some non-numeric values raised rather than returning safe rejection. **Actual risk validation gap**. The return label `ALLOW_DEMO_TRADE` remains a simulation/governor decision and does not evidence broker transport.

## Changes
- `3894aca24748fd5ac67318b608267ea685ee8577`: reject non-numeric, bool, nonfinite, zero, negative, or above-limit risk; retain DEMO-only policy.
- `a48ff55a11c29c6e2732bb2cfb34f8ef56f9b9b0`: 11 tests (9 invalid, 1 valid DEMO, 1 REAL account rejection).
- `64504dee64c2a591bf7c8dbb766847e5aa5af16a`: consolidate 264 expected tests.

## Certification scope
253/253 PASS and ZIP integrity PASS refer only to prior tested commit `d7bf41752d86ffef59cd18d5a93583d35f94dba0`. **R18 patch and 11 new tests have not been executed.** The 264-case suite must be run offline before R18 is certified. Complete residual route inventory still outstanding.

`R18=PATCH_PUBLISHED_UNTESTED`
`PHASE_B=BLOCKED`
`REAL_ORDERS=FORBIDDEN`
`FTMO_REAL=FORBIDDEN`
`MAIN_MERGE=BLOCKED`
