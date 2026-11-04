# P2279E historical Python replay — 2026-11-04

**Status: PASS for historical Python execution, NOT certified for production or FTMO.**

## Method
Recovered the original 4,894-byte `p2279e_robustness_walkforward.py` from authenticated Google Drive (ID `1Dl1og6d1mRroyFKiuP36hWeIN7wCoNga`; SHA-256 `e2cac147cf19a842d6d58848d6d35e1f8619fe133d7b9761a38d4ab340278074`).

Recovered the P2279D original portfolio CSV (Drive ID `1aEfzIFdtFqCA4EFnYd4lwWgezwAy6b6s`) and ten historical MT5 CSVs, with their provenance and SHA-256 documented in `reports/audits/P2279E_MT5_REPLAY_EVIDENCE_20261104.md`.

Ran **original Python algorithm** with only two hardcoded file paths (`EV` and `PORT`) redirected to an isolated temporary directory. A temporary copy of the portfolio mapped its 12 original Windows dataset paths to the authenticated recovered files. No trading API or live order capability was used. Python subprocess returned exit code 0.

## Actual output
- `portfolio_edges=12`
- `robust_approved=11`
- `weak_or_rejected=1`
- `approved_symbols=EURUSD,GER40,NZDUSD,USDCAD,USDCHF,USDJPY,XAUUSD`
- Rejected/weak edge: **UK100 M15 SMA_CROSS 20,50**, WF_WEAK, ROBUSTNESS_WEAK; PF windows `9.7906|0.8518|0.6478|0.7558`.

## Reconstructed artifacts (SHA-256; local isolated execution)
- `p2279e_robustness_results.csv`: 12 rows; `1ed74bea9b9535dffdb3187c74036a16d1675bdfd00c7dee86f05af84036c532`
- `p2279e_approved_robust_edges.csv`: 11 rows; `d5a8733fb8a0fcf4217b5be1df493c9c345bc29f425bd8de93412b2f0073bce5`
- `summary.json`: `94bc9826a82722efa6b26c500220be249a839a86d2a2853d4bd2177694bfa780`

**Important:** These are hashes of reconstructed outputs, not verified hashes of the missing historical output CSVs. Original input bytes are retained in the authenticated Drive; original historical Python source was used for the algorithm.

## GitHub deduplication gate
Searched default branch for `walk_forward`, `robustness`, `mind_trader`, `EMA_CROSS`; search returned no indexed matches, which **does not establish absence**. Direct fetch confirmed `mind_trader/__init__.py` and `app/__init__.py` exist. Existing core implementations, branch history, interfaces, and tests are **not yet fully inventoried**. No runtime or production integration authorized.

## Pending
1. Obtain historical P2279E output and compare row by row.
2. Inventory existing GitHub runtime/modules before adding any engine.
3. Run independent OOS, spread/slippage, Monte Carlo with recorded seed, FTMO risk checks.
4. Add automated isolated tests and only then consider guarded integration.

Safety: `PAPER_ONLY`; `REAL_ORDERS=FORBIDDEN`; `FTMO_REAL=FORBIDDEN`. No broker connection, orders, or paid resources.
