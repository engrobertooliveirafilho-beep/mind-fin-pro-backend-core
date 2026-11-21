# P2223 broker emulator — offline behavioral regression (2026-11-21)

- Source Git blob: `33c044ef73ec36c370b66c51eb9e4ee09aca1474`, commit `a5793482ba6e89e5ee0c81a32c7e9dc3b7dc3c53`.
- Tests Git blob: `61d5dc711d9f531dbe1e1384ffd24b3cf74c0de7`, commit `662ceaa22bbcf6b0c9d66624982851750750e847`.
- Offline **behavioral local reconstruction**: Python unittest **9/9 PASS, 0 FAIL**; log SHA256 `a224a6ce7d8657fe89efebed89bd49b4274ad2ea719fc2cae9194c57eb6d1860`.
- Local reconstructed source blob `85014730a09f45d3bc2012bfefa823948b976704` differs from Git source blob; local test blob `66b03f439336244fd8edf1653caad654bdb701ca` differs from Git test blob. **Not exact-source certified**.
- Covered invalid side, zero/NaN/bool volume, sticky drawdown and session loss kill, no execution after kill, nonfinite PnL, and simulation-only status.
- Drive discovery: original P2223_BROKER_EMULATOR record `1W7lhX-985kkIBUNswbzMVYcuXGjh2rkZ` and historical test `1DHFavdc5Vs1h2EZtIhl_f6uuqa0NEjs2`; fetch of first returned invalid content, so original not yet reconciled byte-for-byte.
- Session-wide loss limit is NOT FTMO calendar-day reset; random PnL emulator is NOT market execution. No broker or E2E certification.

`PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | MAIN=INTACTA | COST=R$0`
