# ET-655 — Chronological OOS diagnostic (2026-11-05)
Historical source: Drive file AUDCAD_MN1_RAW.csv (file ID 1Shtn1fDKCGjPvTTCFdVhebG3t0g-XCQM).
SHA-256 of source bytes: `4456c606b29fa77219873aacd8e5a679e97e4f458565d8054c4491e72b01a894`.
91 monthly AUDCAD rows, 2019-01 through 2026-07, timestamps strictly increasing, unique, OHLC valid. Train first 63 rows through 2024-03; OOS last 28 rows 2024-04 through 2026-07.
**Diagnostic-only**, fixed SMA(3)/SMA(12) long-or-flat rule, signal shifted one month, monthly close-to-close returns, estimated spread at position changes, no commissions/slippage. OOS cumulative estimated return +8.4002%; max drawdown -4.8298%; 19 months exposure; 4 position changes. This is NOT a test of the canonical Eldora strategy and NOT FTMO validation. No hyperparameter fitting, no broker execution.
Re-executed 30 local recovered-source regression tests: 30 PASS, 0 FAIL, 0.05 s. Exact GitHub branch source execution remains unverified. Seven GitHub blob SHA-1 IDs were collected in ET-654 but these do not establish SHA-256 identity with original Drive source; the GitHub sources were adapted.
Gate: FTMO BLOCKED; REAL_ORDERS=0; PAPER_ONLY. Canonical OOS and published-code integration tests still pending.
