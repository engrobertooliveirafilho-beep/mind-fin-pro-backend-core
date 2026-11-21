# P2286D corrected replay — ET665 evidence
Date: 2026-11-21
Status: RESEARCH_ONLY; no production integration or profitability certification.

## Source and dataset provenance
- Original Drive source p2286d_backtest.py, Drive ID 1pU_YUjc6Swhgq3c4BOo3CeFHKSeWyQmw; SHA-256 ab57b28317c0a8a21d5621354e459265ff299e453bca23dc966a082747e14736.
- GER40 H1 features, Drive ID 19SqsLE8VITXohLnrwKvwiMvfSDys7qxK; 50,000 rows; SHA-256 ae4217d5df8b75c66e3b80ece50599d53e58cff4029feec18de5227a396faaca.
- GER40 M15 raw, Drive ID 1nBp7u69OaSTCorsCzivoObtv-vtuQYQs; 5,000 rows; SHA-256 ea117d0e564c806c3bbbcb1519d899a63644a113bd840c29ffbc4c241075188c.
- Derived M15 features SHA-256 b5f26626a9c122c76c9e705549fdfd829ce2200775f711e7a537b43d00edf535; 5,000 rows; 4,801 rows have SMA200.
- Replay adapter SHA-256 71647a017df1b011600d8c8205fe24419a6b5f3663696eae8642327523c9f256; test file SHA-256 01c73a7acd2e6dd585bdc459ab635075ea5fc274f46c1d0a605344429719c0e7.
- Feature builder SHA-256 b6c038c88137a4ce67386f0dd35ae231cf5550d4a6ca0914f8d4d5b668a32196; feature tests SHA-256 db68b12185b93ac3e75b9fafc8373014de4867c3310435c36c9ffcf1ec77d160.

## Corrections
- Requires explicit, finite, nonnegative cost per side; rejects implicit/invalid costs.
- Signals are evaluated at bar close and filled at next bar open.
- Repeated same-side signals do not reset entry or create phantom trades.
- Opposite signals close and reverse; final open position is closed at final close.
- Both entry and exit costs are charged and included in per-trade ledger.
- Feature builder uses trailing rolling windows; prefix-invariance test checks no future-bar leakage.
- Session remains UNKNOWN because source timezone mapping is not authenticated.

## Local execution
- Regression tests: 11/11 PASS (8 replay + 3 feature-builder); py_compile PASS.
- GER40 H1, 50,000 rows, TREND_PULLBACK/SMA9: 951 closed trades; terminal close confirmed. Gross PnL -4,628.88 price units.
- H1 cost scenarios per side: 0.5 => total cost 951, net -5,579.88, PF 0.9318, max DD 9,803.98; 1.0 => net -6,530.88, PF 0.9208; 2.0 => net -8,432.88, PF 0.8992; 5.0 => net -14,138.88, PF 0.8383.
- GER40 M15, 5,000 raw bars; features derived with trailing SMA9/21/55/200 and ATR14. TrendPullback/SMA9: 93 closed trades; gross PnL +1,541.30 price units. Cost scenarios per side: 0.5 => total cost 93, net +1,448.30, PF 1.2111, max DD 1,773.80; 1.0 => net +1,355.30, PF 1.1959; 2.0 => net +1,169.30, PF 1.1663; 5.0 => net +611.30, PF 1.0829.
- These are in-sample, single-symbol, single-configuration research observations. Cost inputs are hypothetical price units, not broker-calibrated spread/commission/slippage or contract costs. No sizing, multiplier, session attribution, OOS, multi-year, or FTMO certification. M15 session was deliberately left UNKNOWN.
- This adapter is independently authored from recovered P2286D signal semantics, not a byte-identical replay of the original executor.

## Decision
H1 configuration rejected for this dataset. M15 result remains research-only and is not promoted: no OOS, calibrated costs, sizing or portfolio validation. PAPER_ONLY; REAL_ORDERS=FORBIDDEN; FTMO_REAL=FORBIDDEN; no merge/deployment.
