# R419 — DE40 historical dataset and causal paper replay (2026-10-31)

Drive historical folder: P2363C_VALIDATE_DE40_5Y_DATASET_DOTNET_20260623_180821 (ID 1OfjaefbJQpun8E8R7Mphav4YayizvjWY). Seven raw CSVs retrieved, byte sizes match historical validation manifest; SHA256 independently computed:

| TF | bytes | SHA256 | OOS signals | mean forward return |
|---|---:|---|---:|---:|
| D1 | 94321 | 2998ff88f04a045c3d677d631b7957d3abae25370c4b56770250e0a5c25d704f | 366 | -0.0000797609 |
| H4 | 559719 | 2a2f1203752aba2e5cdc6d7b5d6b5eae2cd733c496642d46fc3038b61223815f | 2094 | 0.0000371303 |
| H1 | 2037554 | 1b0cbb08c5c335f3adc56739795016656f999e8c02d11bc432c6e8008d47b651 | 7519 | -0.0000006995 |
| M30 | 4110488 | 484617f2410672d019dc159fe280058bdc9a4a34d610f6a2e29729ff759a9942 | 14841 | -0.0000103212 |
| M15 | 7551385 | e17ba75cfd508ecddd8b3f01dd313d5b65b51498462aa6faec43cee0eba2cec0 | 28620 | -0.0000073606 |
| M5 | 7398235 | 9418e7754dde016629ac66c8a3a69a3d32dbcd293301aced46a94fc980654274 | 29445 | 0.0000100631 |
| M1 | 7346292 | 8bcbc7422ddfa3f089d1e6d6ad775de77e988552216c430ceb8f0da11efc1a40 | 28564 | -0.0000039343 |

**Implementation evidence**: isolated local /mnt/data/r419/replay.py and /mnt/data/r419/test_replay.py; 6/6 local tests PASS. CSV source uses semicolon and dotted timestamps, unlike R388's comma/ISO reader. 70/30 chronological split, signal from previous and current close only, next close used only for scoring. These are *new illustrative baseline rules*, **not original strategy/edge engine**, not independent walk-forward optimization, and not FTMO certification. No spread, slippage, transaction fees or timezone normalization. Original historical hash manifest independent of current raw bytes has not been recovered. 

STATUS: RAW_BYTES=7/7; SIZE_MATCH=7/7; SHA256_COMPUTED=7/7; HISTORICAL_SHA_CROSSCHECK=BLOCKED; LOCAL_PAPER_BASELINE=PASS; ORIGINAL_ENGINE_E2E=BLOCKED; FTMO_READY=FALSE; PROMOTION=BLOCKED; REAL_ORDERS=FORBIDDEN; COST=R$0.
