# P2288C — integration gate (PAPER ONLY)

Status: REPLAY_VERIFIED; PATCH_UNIT_TESTED; CORE_INTEGRATION_BLOCKED; FTMO_NOT_CERTIFIED.

## Historical authority (Google Drive)
- Original executor: Drive ID 117isysR64sm-dMMOAsIDG1yptEVQHTk5; SHA256 c0e35bc40039ef3d3475f6d041220566dfbe071fd4a4a8156f2b22873ae2e9ca.
- Input: Drive ID 1UzSX5hjUnfeJhL1MypkJYQIFbXCiutCu; SHA256 fdb606fe3799a86c3f766be5554a92799db4dae2523af201898bccbd29dcc27f.
- Historical output: Drive ID 1y-Fc5vo1r3bIzNkaX-7CC0OBfeONViay; SHA256 491e563cc78a895009b62b02e3728a77d2b362f77e4d26d1b2efe822815ce242.
- GER40/H1 dataset: Drive ID 19SqsLE8VITXohLnrwKvwiMvfSDys7qxK; 50,000 rows; SHA256 ae4217d5df8b75c66e3b80ece50599d53e58cff4029feec18de5227a396faaca.
- GBPUSD/H4 dataset: Drive ID 1RJF0q_Fv4xYDsIz8R4eKxkoR0upD43qK; 20,000 rows; SHA256 5dbb87d8c9d0348337f3f0073601fa2c851999ccea21f411da020f8c5143cd1d.

## Verified local replay
- 35/35 historical rows reproduced, 0 field divergences across 17 fields; 0 approved, 18 watchlist, 17 rejected.
- 35 configurations collapse to 15 operational signatures because fast/slow are unused by historical backtester.
- Isolated corrected module has 9/9 unit tests passing locally. NOT yet tested against canonical GitHub runtime.

## Fail-closed blockers
1. Establish canonical integration interface and eliminate semantic duplication across branches.
2. Source actual spread, commission, slippage and swaps for the FTMO product; hypothetical price-unit costs are NOT a financial certification.
3. Test deterministic integration with runtime, risk guard, portfolio, writer and lineage; no live brokerage connectivity.
4. Certify out-of-sample strategy performance and applicable FTMO evaluation rules separately.

Do not import this historical motor into production or change execution wiring from this document.
PAPER_ONLY | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | MERGE=BLOCKED.
