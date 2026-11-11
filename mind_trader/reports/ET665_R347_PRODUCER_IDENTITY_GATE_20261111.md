# ET665.R347 — producer identification gate (2026-11-11)

No new front. Reconciliation of real market data and causal-decision validator.

Verified:
- Existing R347 executor takes an operator-supplied CSV with decision_id,strategy_id,symbol,decision_ts,signal_ts,price_ts,price,source_sha256; it does not generate trading decisions.
- Drive original AUDCAD_H1_RAW.csv has timestamp,ftmo_symbol,mt5_symbol,timeframe,open,high,low,close,volume,spread,real_volume,source,mode, not decision records.
- GitHub default-branch code searches for decision_ts, signal_ts, strategy_id, P2405 returned zero results; search scope was default branch only, not isolated branches.
- Prior run 43031688159 exact Git source Docker offline 23/23 PASS; historical source-to-decision E2E still not demonstrated.

Required before closing historical E2E: locate and inspect the existing P2405/S20/S21 decision producer in isolated branches or Drive artifacts, confirm its decision timestamp semantics and data lineage, supply original immutable source SHA-256, then execute actual producer->R347 validator->evidence JSON under PAPER_ONLY.

Never transform OHLC rows into invented historical strategy decisions. No main or production changes, no real orders, no costs. FASE B 0/16 and HP19 0/19 remain unverified.
