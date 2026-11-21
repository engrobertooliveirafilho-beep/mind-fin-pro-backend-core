# P2286D corrected replay — ET665 evidence
Date: 2026-11-21
Status: RESEARCH_ONLY; not a production runtime or profitability certification.

## Source and dataset provenance
- Original Drive source: p2286d_backtest.py; Drive ID 1pU_YUjc6Swhgq3c4BOo3CeFHKSeWyQmw; SHA-256 ab57b28317c0a8a21d5621354e459265ff299e453bca23dc966a082747e14736.
- GER40 H1 features: Drive ID 19SqsLE8VITXohLnrwKvwiMvfSDys7qxK; 50,000 rows; SHA-256 ae4217d5df8b75c66e3b80ece50599d53e58cff4029feec18de5227a396faaca.
- GER40 M15 raw: Drive ID 1nBp7u69OaSTCorsCzivoObtv-vtuQYQs; 5,000 rows; SHA-256 ea117d0e564c806c3bbbcb1519d899a63644a113bd840c29ffbc4c241075188c.
- Corrected adapter SHA-256 71647a017df1b011600d8c8205fe24419a6b5f3663696eae8642327523c9f256; regression suite SHA-256 01c73a7acd2e6dd585bdc459ab635075ea5fc274f46c1d0a605344429719c0e7.

## Corrections
- Explicitly requires a nonnegative cost per side; refuses implicit/invalid costs.
- Executes signals at next-bar open; suppresses repeated same-side re-entry.
- Closes on opposite signal and at final bar close.
- Charges both entry and exit costs; records per-trade ledger.
- Rejects unsupported strategies and malformed/non-finite numeric inputs.
- Keeps the implementation isolated from broker/order APIs.

## Local execution
- Unit tests: 8/8 PASS.
- GER40 H1: 50,000 rows; TREND_PULLBACK, SMA9; 951 closed trades; terminal position closed.
- Cost sensitivity (price units per side; hypothetical, not broker-calibrated):
  - 0.0: gross/net -4,628.88; PF 0.9430; max DD 9,196.98.
  - 0.5: total costs 951.00; net -5,579.88; PF 0.9318; max DD 9,803.98.
  - 1.0: total costs 1,902.00; net -6,530.88; PF 0.9208; max DD 10,410.98.
  - 2.0: total costs 3,804.00; net -8,432.88; PF 0.8992; max DD 11,624.98.
  - 5.0: total costs 9,510.00; net -14,138.88; PF 0.8383; max DD 15,266.98.
- This replay is an independently authored corrected adapter based on the recovered P2286D signal semantics; it is NOT a byte-for-byte replay of the original P2286D executor.
- Cost values are scenario assumptions in dataset price units, not actual GER40 contract costs. No position sizing, contract multiplier, historical spread reconstruction, commission schedule or slippage calibration was applied.
- M15 raw dataset was recovered and hashed but not yet transformed/replayed; no FTMO/OOS/multi-year certification.

## Decision
P2286D research adapter passes its local regression suite, but the tested strategy configuration is unprofitable in this replay and must not be promoted. PAPER_ONLY; REAL_ORDERS=FORBIDDEN; FTMO_REAL=FORBIDDEN; no merge/deployment.
