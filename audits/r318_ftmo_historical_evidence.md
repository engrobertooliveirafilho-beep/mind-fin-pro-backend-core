# R318 — Historical FTMO / out-of-sample evidence (2026-10-31)

Status: DOCUMENTARY_ONLY. NOT FTMO_READY. PAPER_ONLY. REAL_ORDERS=FORBIDDEN. FTMO_REAL=FORBIDDEN.

## Source
Google Drive historical dossier `MIND_TRADER_DOSSIE_AUDITORIA_PROFUNDA_P2368_P2382_20260804.pdf`, Drive file ID `16x5f7suH3oUcdfL4TShGzu3Obpom93C5`.

## Verified historical findings (document claims, not rerun)
- DE40 dataset described as 389,921 certified candles across M1, M5, M15, M30, H1, H4 and D1.
- P2368/P2368A: 100,000 M5 candles, 14,445 trades, 24 contexts, 0 promoted, 3 observed, 21 rejected. Semicolon-delimited CSV loader hotfix documented.
- P2369: 3,024 parameter combinations, 0 promoted, 79 observed, 2,945 rejected.
- Evolution: P2368 backtest -> P2369 discovery -> P2370 families -> P2372 candidates -> P2374 walk-forward -> P2375 reverse engineering -> P2376 institutional footprints (inferred) -> P2377 router -> P2378 playbooks -> P2379 PAPER emission -> P2380 feedback -> P2381 loss patch -> P2382 replay.
- P2382 224 wins / 0 losses is explicitly **not** certified out-of-sample; dossier flags survivorship bias and leakage risk.
- Required successor: P2383_DE40_WALK_FORWARD_AFTER_PATCH.

## Known implementation paths (historical, not recovered executable in this commit)
- `app/runtime/p2368_de40_context_backtest_with_2r_targeting.py`
- `tests/test_p2368_de40_context_backtest_with_2r_targeting.py`

## Certification gates
- [x] Source identified and document read.
- [x] Historical claims classified as documentary evidence.
- [ ] Original source code + SHA256 independently recovered.
- [ ] Real strategy dependencies recovered and imported.
- [ ] Dataset bytes and chronology verified.
- [ ] Leak-free walk-forward / purged split / untouched holdout.
- [ ] P2383 rerun with reproducible pytest and CI.
- [ ] FTMO rule compliance evaluated on verified simulated trades.

Do not promote historical performance or execute broker orders based on this document.
