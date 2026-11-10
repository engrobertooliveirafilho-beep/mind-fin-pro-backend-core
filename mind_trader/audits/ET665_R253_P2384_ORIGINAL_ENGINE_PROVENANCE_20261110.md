# ET665.R253 — Original engine provenance and negative signal-rule findings
Date 2026-11-10. PAPER_ONLY / CERTIFICATION_BLOCKED.

## Source-level finding (NEW)
Drive archived original source app/strategy_genome/mapping.py: file ID 1yCXA1F7K-MqAMgvUN0Z1fHYyffutPoo6.
Implements StrategyGene, StrategyGenome, cosine similarity, dimension vectors, and default generic business dimensions (risco, crescimento, margem, liquidez). No OHLC/MT5 entry or exit rules in this source. Must NOT treat this as the P8 quantitative Strategy Genome engine without source-path/contract reconciliation.

## Original P2384–P2386B Drive audit trace (NEW exact distinctions)
- P2384 audit ID 1E5SOpPZXhdrcyMsjxUX0iJ8CcnOBo9lj: survivor M15 TREND_DOWN OFF_SESSION LIQUIDITY_SWEEP_REVERSAL_UP LIQUIDITY_REVERSAL_ENTRY; 920 matched; 3 cycles tested; 0 promoted; PF 1.176581, DD 13.643144R; P2385_ALLOWED=False; next P2384B classifier repair.
- P2384A audit ID 1woJrWuaKzm9RJUcB5BYeGKPMT7ARCCZO: 0 cycle promoted, 2 transition promoted, 920 high fidelity, P2385_ALLOWED=True. This does NOT imply three original cycles passed.
- P2385 audit ID 10URUWeW_cwJH1frxzOjUQC3JmMKZ3_Q2: 920 candidates, 230 PAPER allowed, 690 blocked; PF 1.543464, DD 4.544174R. Permission PAPER only.
- P2386B audit ID 1kx9WngBJmzD3HSvMFA8j8BZOhb_iCEhr: entry_time fallback to time; 230 signal rows, 690 blocked preserved, zero quarantined. Bus name mind_de40_paper_signal_bus_p2386b.csv.
- Direct Drive evidence folders for P2384, P2384A, P2385, P2386B each list only AUDIT_FINAL.txt. These historical audit reports do NOT contain original executable signal rules.

## Search scope and integration decision
GitHub default-branch code search for exact p2384_de40_institutional_cycle_engine, p2385_de40_survivor_context_execution_filter, p2386b_signal_bus_schema_repair, strategy_genome returned no results. Negative default-branch search is NOT proof of absence from other branches, archives or source-of-truth Drive.
No executable P2384–P2386B or original price-to-signal rules recovered from these folders. Do not synthesize replacement strategy or assert integration test passed. Integration remains blocked pending original code and canonical candle/signal lineage. P2384 baseline failed; only scoped transition gate P2384A advanced historically.

## Ledger
ELDORA_TRADER_MASTER_REMEDIATION_LEDGER V1 Google Doc ID 1WYqMJ-wzqmDWTaRzwJGFk4Hj4b7MuBNR7m0F9ct99mI previously rejected write 403; this GitHub record is pending append and NOT a Google Doc update.

MAIN untouched; no broker, live or FTMO real operations; cost R$0.
