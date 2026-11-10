# ET665.R319 — New historical Drive finding: P2404 authority mismatch (2026-11-10)

## Verified Drive artifacts
- Folder `P2404_CORRELATION_ANALYZER_20260625_125024`: `1vvF-FyXyX5Mg4nN_P-mMOJb6uaT6vKe7`
- `AUDIT_FINAL.txt`: `17fCf3EBIHPYxExcTEeZflrP6sB3jK45b`
- Also present: `p2404_correlation_analyzer.py`, `test_p2404_correlation_analyzer.py`, `summary.json`, `p2404_pairwise_correlation.csv`, `p2404_pearson_matrix.csv`, `p2404_anti_redundancy_edge_pool.csv`.

## Historical claims — not current certification
The original audit says GER40 M15, 20 edges, 2,252 timestamps, 190 pairs, 3 redundant pairs, greedy pool of 18, mean absolute Pearson 0.067498. It labels the correlation analyzer `CERTIFIED`, while explicitly declaring its input to be `P2403E_REBUILD_REPLAY_SERIES_FROM_DE40_CANONICAL_OHLC`. Subsequent R-series work quarantined P2403E because hash-scheduled entries are not independently causal trading signals. Therefore historical computational completion **must not** be promoted into causal-edge, portfolio, FTMO or runtime certification.

## Actions and gates
1. Preserve historical artifacts as evidence, not executable authority.
2. Keep R309/R311/R315/R316 pure correlation, pinned source and immutable CSV snapshot guards.
3. No promotion of the 18-edge pool until original trade lineage, independently causal entry timestamps, no lookahead, OOS walk-forward, execution costs and review are verified.
4. Existing Docker `et665-pytest-offline:py312`: 116/116 historical PASS on 2026-11-09 (R386 evidence), **not** a current R319 full-suite run.
5. Google Docs ET-705 update attempted on 2026-11-10, denied HTTP 403 PERMISSION_DENIED. No ledger write claimed.

Status: `PHASE_B=OPEN`; `CERTIFIED_FRONTS=0/16`; `HP19=0/19`; `PAPER_ONLY`; `REAL_ORDERS=FORBIDDEN`; `FTMO_REAL=FORBIDDEN`; `COST=R$0`.
