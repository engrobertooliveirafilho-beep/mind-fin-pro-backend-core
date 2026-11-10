# ET665.R264 — New original P2375 reverse-engineering recovery and source governance
Date 2026-11-10 | NEW primary Drive evidence run_p2375.log ID 1fncs00UsVkAK-ZPf-RXdle0iVd3p1dZo

P2375_DE40_FAILURE_ANALYSIS_AND_REVERSE_ENGINEERING: historical 5000 batch rows, 52 walk-forward rows, seven movement timeframes; five layers: operation failure, pullback, inversion, continuation, family/timeframe/session/RR failure map. Eight named historical output files: failure_by_family, failure_by_timeframe, failure_by_session, failure_by_rr, failure_by_family_timeframe, operation_reverse_engineering, movement_reverse_engineering, summary.json. Paths are historical Windows evidence locations, not recovered row-level CSV bytes.

Original code recovered directly in GitHub app/runtime/p2375_de40_failure_analysis_and_reverse_engineering.py blob 83d0a9dee9a1df3959c751988b6a0090f7db6797 (8808 chars); functions sniff, load_csv, f, aggregate, reverse_engineer_failures, movement_reverse_engineering, write_csv, run, main. CLI requires --batch, --walk-forward, --dataset-root, --outdir. This is an offline failure-analysis engine, not certified signal generator; analysis on outcomes must not be passed as-of-time to P2376/P2377.

Source chain verified on isolated branch: P2375 original blob 83d0a9dee9a1df3959c751988b6a0090f7db6797; P2376 original blob de50c447cd77df673a9fe42bde5cae0a69abc573 (future outcome labels); P2377 patched blob 32a359501563caafed8c48790dfebbad45d1d5f5 (fail-closed). P2377 still contains 'post_efficiency' in a comment; raw string presence alone is not proof of active leakage. Full runtime execution, test suite and historical CSV replay still pending. No false test PASS claim.

Drive searches for P2412, P2413, P2414 found no relevant Trader module evidence (P2412/14 generic inventory only). P2409 in Drive refers to unrelated SOVEREIGN_COGNITIVE_EXECUTION_ENGINE, NOT Trader full-stack certificate; do not conflate numbering.

Ledger V1 ET-714 pending: Google Docs read succeeds but append previously attempted ET-713 returned 403 PERMISSION_DENIED. GitHub record is NOT an update to native Google Doc. Next: recover P2375 input CSV bytes; run original source tests with pinned hashes and offline subprocess; audit downstream P2378-P2382 for P2376 labels, independent OOS.
PAPER_ONLY | MAIN UNCHANGED | REAL_ORDERS/FTMO_REAL FORBIDDEN | R$0 | CERTIFICATION BLOCKED.
