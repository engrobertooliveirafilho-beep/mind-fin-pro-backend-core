# ET665.R450 / ET-724 — P2386B historical ATR-PnL source audit

2026-11-10. New original Drive sources:
- P2386B allowed `1DcMKBhCkothmE9jSBxePW3vW5GPgwZUx`
- P2386B blocked `1h59tIrK-4H52iuo99zH-kf1gbQUjxVge`
- P2387 validated `1exmB0b-70RlcEhKXnJc6WbUAfxo3-Db_`
- P2387 bridge `1youoi0oLG7Lch3yrl5kPtroAMYEzkL9B`

**12/12 checks PASS on original CSVs.** 230 PAPER allowed, 690 blocked. All 920 historical PnL values reproducible as `(next_close-entry_close)/ATR` for BUY direction, within rounding tolerance 1e-6. P2386B already supplies `next_close` and `realized_r_backtest` in each of the 230 permitted signals; P2387 receives these values before P2388 reuses them as simulated forward closes. 230/230 signal IDs match P2387 validated and bridge. Real MT5 permission DENIED.

**Implication:** historical PnL arithmetic is independently reproduced from the CSV price/ATR columns; independent signal generation, contemporaneous prediction, cost-aware fills and out-of-sample forward performance remain **unproved**. This is not a claim of live-data lookahead in original generation code, which has not been recovered.

Reproducible offline local script `et665_r450_p2386b_atr_audit.py` SHA256 `e9a1e7cd5e9b79ba55f556b6702b73a0239e6afc85f4298bec904edd40d68ff2`; evidence `ET665_R450_P2386B_ATR_LINEAGE.json`. No strategy promotion, no main mutation, no real orders.

`FASE_B=0/16 | HP19=0/19 | E2E=FALSE | PAPER_ONLY | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | R$0`