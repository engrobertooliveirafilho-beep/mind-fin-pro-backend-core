# P2279E MT5 replay — evidence gate (2026-11-04)

Status: **RESEARCH / PAPER_ONLY**. No live trading, no FTMO_REAL, no merge authorization.

## Provenance
Authenticated Google Drive historical tree: `ELDORA.LAUNCH_V1_R2_R1_PRODUCTION_HUMANIZATION_AND_RELEASE_BOUNDARY_CLOSURE_20260722_193310/RELEASE_BOUNDARY/CHANGED_FILES/mind_trader/data/raw/mt5/`.
Original portfolio: P2279D `ftmo_candidate_portfolio.csv` Drive ID `1aEfzIFdtFqCA4EFnYd4lwWgezwAy6b6s`.
Original P2279E source: `p2279e_robustness_walkforward.py`, Drive ID `1Dl1og6d1mRroyFKiuP36hWeIN7wCoNga`.
Source P2300–P2304: `p2300_p2304_robustness_lab.py`, Drive ID `19lHWLmejBfpSE0FdDIBxuhfZT7c9336z`.

## Input inventory (SHA-256 of authenticated connector-returned CSV text)
| MT5 CSV | Candles | SHA-256 |
|---|---:|---|
| USDCAD_H1 | 5000 | 02dcd2463bed0e795910fdd8ec19dcee4b9f06ebc4135b4ab007168fb7df9a31 |
| XAUUSD_D1 | 1500 | 47aac74356684ce41b9ac6c93f03bfeb1727556bb14d9ca81125017b83e0ccdb |
| XAUUSD_M30 | 5000 | d4a62d9f61c03036c95dd13d66dcd4cbc3b1ae3a21756b602fcfb43ef1f3e8e7 |
| EURUSD_D1 | 1500 | 615dd85d94193d95a3fb6f470a72148e5885f694212a9f3a9cf2ce7117e07216 |
| NZDUSD_M15 | 5000 | 084cd31fd36b27bbc17b5752d8026807abc588aa283e310bb91bce6dab98c91c |
| UK100_M15 | 5000 | b1606e9c304a86f643e7b6d2532ac069a9a591e0a6f82c6b3695f2ddb0b1c32a |
| USDCHF_M15 | 5000 | 22d23c3ccd32742b20b9e68739fd3e303b7f7814a42b553ba2bc81a4552a62ff |
| USDJPY_D1 | 1500 | 959e4e46e47a5aab3e9e00415896c53156265b7174d79696d69f9dc04f5adef4 |
| GER40_H4 | 3000 | ca2afe1ce4b570843cee7aaa075535fe48e6566cae94f0ca39465defc9accbcf |
| USDJPY_H1 | 5000 | c39c8b3d7347c80c6728711966d397243e5644fc9506e1e00c109fde6ee241b1 |

## Independent deterministic reconstruction
An isolated JavaScript implementation of the historical EMA/SMA crossover, four walk-forward partitions and selection thresholds was run against the 10 authentic CSV contents. Result: **11/12 robustness-approved**, **1 WF_WEAK (UK100 M15 SMA 20/50)**, matching the historical P2279E summary count.

**Qualification:** This is NOT an execution of the original Python file, NOT a row-by-row comparison to the missing original `p2279e_approved_robust_edges.csv`, and NOT independent out-of-sample or FTMO certification. Matching a summary count does not establish strategy profitability or runtime correctness.

Three independently retrieved Drive release copies of USDCAD_H1 had identical full text. Remaining copy equivalence is unverified.

## Release gates
- [x] Historical tree and authentic CSV contents recovered
- [x] Independent deterministic 12-edge replay of historical logic
- [ ] Run original Python on mapped original datasets and compare row by row
- [ ] Retrieve original P2279E result CSV and verify SHA-256
- [ ] Check existing GitHub engine interfaces and deduplicate before integration
- [ ] Reproduce P2300–P2304 robustness and seed-sensitive Monte Carlo
- [ ] Independent OOS, costs, slippage and risk gates
- [ ] Ledger ET-562 sync (Google Docs write previously blocked)

No executable engine or production route changed. No order was sent. `PAPER_ONLY`, `REAL_ORDERS=FORBIDDEN`, `FTMO_REAL=FORBIDDEN`.
