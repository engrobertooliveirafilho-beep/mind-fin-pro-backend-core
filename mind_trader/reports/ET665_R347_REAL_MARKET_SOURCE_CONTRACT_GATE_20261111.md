# ET665.R347 — Source-of-truth historical market data found (2026-11-11)

Read-only Drive inventory:
- Original raw MT5 data: https://drive.google.com/drive/folders/1Ra9D1RGVgHbww_yplGDfLKGlCzkaQXiX
- Normalized Parquet: https://drive.google.com/drive/folders/16kcUzF6gzK-MmrUknqZ9BFbizmTrbG-8
- 10 AUDCAD RAW CSVs (MN1, W1, D1, H12, H8, H6, H4, H3, H2, H1), and 10 normalized Parquet files.
- Concrete file: AUDCAD_H1_RAW.csv, Drive ID 17DarAojawmAlMFCPHddcBWM1dUYaAWZf.
- Readable first row: timestamp=2018-12-03 00:00:00+00:00; ftmo_symbol=AUDCAD; mt5_symbol=AUDCAD; timeframe=H1; open=0.97638; high=0.97684; low=0.97542; close=0.97556; volume=2327; spread=40; real_volume=0; source=MT5; mode=BACKTEST_PAPER_ONLY.
- Raw header: timestamp,ftmo_symbol,mt5_symbol,timeframe,open,high,low,close,volume,spread,real_volume,source,mode.

CRITICAL CONTRACT MISMATCH: R347 expects decision_id,strategy_id,symbol,decision_ts,signal_ts,price_ts,price,source_sha256. Raw market OHLC data do not prove historical strategy decisions. Never manufacture decisions or claim genuine S20/S21 execution from OHLC alone. Need independently attested full-file SHA-256 and existing real decision/event producer; then validate its output with R347. Do not create a new trading strategy or start another front.

Previously certified: GitHub Actions 43031688159, 23/23 exact-source synthetic structural tests PASS. Historical R347 E2E remains BLOCKED; FASE B 0/16; HP19 0/19. No main/production mutation; PAPER_ONLY; R$0.
