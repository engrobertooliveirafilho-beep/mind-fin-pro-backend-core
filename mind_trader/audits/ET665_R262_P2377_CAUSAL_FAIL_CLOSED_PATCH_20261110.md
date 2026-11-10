# ET665.R262 — P2377 future-label leakage correction
Date 2026-11-10. Isolated branch audit/et665-r246-mtm-ensemble-20261110.

Patched original app/runtime/p2377_de40_regime_first_signal_router_with_xray_lifecycle.py: classify_lifecycle no longer reads future context, maps event type to unconfirmed as-of-event lifecycle with lifecycle_score=0; context_score no longer uses post_efficiency; decision-facing router/library rows no longer export post MFE/MAE/efficiency; permission always BLOCK_UNCERTIFIED_CAUSAL_LIFECYCLE until causal classifier and OHLC OOS certification. P2376 historical outcome generation unchanged for retrospective research; MUST NOT feed decisions.

Original source update commit 0129f480c0d557f52103500059183d072af01403, blob 32a359501563caafed8c48790dfebbad45d1d5f5.

Offline test executed locally using manually transcribed patched functions: 3/3 PASS in 0.03 seconds. Not byte-identical imported original GitHub module. Test script /mnt/data/et665_r262/test_causal_gate.py. Source-import test tests/test_et665_r262_p2377_causal_gate.py published but not run; existing R261 source-import metamorphic regression also pending CI. Network access to GitHub raw from sandbox failed, and no GitHub workflow dispatch action available; no claim of source-level CI PASS.

No merge, no production, no real orders, no PAPER candidate promotion. Historical P2377 metrics must be recomputed and must not be compared directly after this intentional fail-closed correction. Ledger Google Doc remains 403 write blocked; ET-712 pending.
