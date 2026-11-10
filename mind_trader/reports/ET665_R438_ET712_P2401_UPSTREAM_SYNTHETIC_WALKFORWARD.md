# ET665.R438 / ET-712 — P2401 upstream provenance invalidation

Date: 2026-11-10. New Google Drive primary source: `P2401_MULTI_EDGE_WALK_FORWARD_DD_FILTER`, source file ID `11VWwSomDCW9RhWLVMNOtxIxcoPsDL8cN`, SHA256 `72711f8b99c68d3b7ca3926eb9e5a0d1166c1f5a260a9e4e5689209c7e84e301`. Its promoted edges output: `1nGK8cd0l30qxTTePohn8br_Nv094BBeJ`. Downstream P2402 source: `16VXFxLKAr4hLYFHfSkHxiMT036YEoZmK`.

**New critical lineage failure:** P2401 `evaluate_candidate` derives `samples`, `passed_windows`, `pf`, `winrate`, `expectancy` and `max_dd_r` using `stable_float` from SHA256 of candidate identifier, key and direction; it sets `tested=True` and emits `PROMOTE` decisions without reading historical trade outcomes. P2402 then computes `diversity_quality_score` from these values, ranks and selects representatives for the P2403E->P2404->P2405+ downstream chain. Thus historical 'walk-forward' and derived portfolio/ensemble quality evidence cannot be accepted as empirical validation.

**Actual diagnostic run:** original P2401 `stable_float` and `evaluate_candidate` function AST extracted, compiled and executed offline. Changing supplied `real_market_return` from -1000 to +1000 and `real_trades` from 0 to 1,000,000 left all seven calculated metrics and decision unchanged. `tested=True` returned for both. 2/2 diagnostic assertions PASS. Local evidence `ET665_R438_P2401_PROVENANCE.json`.

**Required repair:** replace P2401 metric generation with verified timestamped real strategy signals, OHLC lineage, chronological walk-forward, costs and independent test-period results; propagate `empirical_evidence_id` and `source_sha256` through P2402/P2403E/P2404/P2405/P2406/P2407/P2408. Fail closed on absent lineage. Do not promote any historical strategy based on synthetic metrics.

`PHASE_B=0/16 | HP19=0/19 | E2E_CERTIFIED=FALSE | PAPER_ONLY | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | R$0`
