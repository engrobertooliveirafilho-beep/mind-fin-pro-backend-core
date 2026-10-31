# R347 — DE40 provenance trace and CI evidence (2026-10-31)

## Independent historical inventory — authoritative location clue, NOT recovered bytes
Google Sheet MIND_FULL_INVENTORY_BASELINE_20260819
ID: 1WOVsYCd0N5TdnFmVvOIG9eihMOByv85y761eDPs2ErE
Rows 1850-1856, historical inventory dated 2026-08-19.
All paths share directory:
`/MIND/MIND_LOCAL_ARCHIVE_20260625_153948/mind-fin-pro-backend-core_evidence/P2363C_VALIDATE_DE40_5Y_DATASET_DOTNET_20260623_180821/`

| TF | Historical filename (extension is literal _csv) | Historical bytes |
|---|---|---:|
| D1 | mind_ger40_5y_p2363b_DE40_D1_csv | 94321 |
| H4 | mind_ger40_5y_p2363b_DE40_H4_csv | 559719 |
| H1 | mind_ger40_5y_p2363b_DE40_H1_csv | 2037554 |
| M30 | mind_ger40_5y_p2363b_DE40_M30_csv | 4110488 |
| M15 | mind_ger40_5y_p2363b_DE40_M15_csv | 7551385 |
| M5 | mind_ger40_5y_p2363b_DE40_M5_csv | 7398235 |
| M1 | mind_ger40_5y_p2363b_DE40_M1_csv | 7346292 |

Inventory has blank ID_GOOGLE_DRIVE for all seven entries. Current Google Drive search for P2363C parent folder ID 1OfjaefbJQpun8E8R7Mphav4YayizvjWY returned zero direct children; therefore content-byte recovery, SHA-256 and semantic OOS verification are NOT established.

Alternative later-timeframe data inventory rows 7653-7689 lists `/MIND/__CORE_CANON/trader/market_data_raw/mt5_industrial/GER40_CASH_{D1,H4,H1,M30,M15,M5,M1}_RAW.csv`, but these are NOT proven byte-for-byte identical to the P2363B originals. Do NOT substitute them without independent checks.

## Verified GitHub Actions success
Workflow R343 DE40 causal certification, event push, SHA `050a4317a4aebe50b16d3fae431a2eecda272f4f`
Run ID **41231592718**, job ID **124626761543**, status completed, conclusion **success**.
URL: https://github.com/engrobertooliveirafilho-beep/mind-fin-pro-backend-core/actions/runs/41231592718
Job logs: CPython 3.12.15; R342 5 tests, R344 4 tests, both OK; printed `PROMOTION=BLOCKED; FTMO_READY=FALSE`.
This proves nine isolation/regression tests only, not the original motors or any performance/out-of-sample claim.

## Other CI issue not to conflate
R334 Drive recovery workflows failed repeatedly, including run **41231699285**, conclusion failure. Root cause not yet established from logs.

## Release gates
DATASETS_RECOVERED=0/7 (historically enumerated 7/7).
ORIGINAL_SHA256_VERIFIED=0/7.
R342_R344_CI_TESTS=9/9 PASS.
ORIGINAL_DE40_E2E=UNVERIFIED.
PROMOTION=BLOCKED; FTMO_READY=FALSE; REAL_ORDERS=FORBIDDEN.
