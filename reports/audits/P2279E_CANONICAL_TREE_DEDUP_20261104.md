# ELDORA TRADER — canonical tree and P2279E dedup audit (2026-11-04)

## GitHub inventory (main, tree SHA `1b5916fbdc8c90173061315400abb92f3bbbb13a`)
- Global recursive Git tree returned ~52.4k entries with `truncated=true`; **not a complete repository-wide inventory**.
- The `mind_trader` subtree was independently fetched by tree SHA `9993fdf9aaf6983a239b7c9002327a9ca5731f33` with `truncated=false`: **5,195 entries**, **468 Python files**, **113 Python paths** matching relevant backtest, walk-forward, risk, dataset, paper and strategy keywords.
- Thus **complete `mind_trader` subtree inventory**, but not complete entire-repository tree.

## Existing canonical implementations
- `mind_trader/app/backtest/market_core.py`: OHLCV ingestion and SMA cross backtest; input schema `ts,open,high,low,close,volume` differs from original MT5 `time,open,high,low,close,tick_volume,...`; fills and position semantics also differ. **Do not replace it with P2279E**.
- `mind_trader/app/validation/walk_forward_authority.py` (P8.81): at least 3 windows, minimum PF >1.05, positive-window ratio >=0.67, average expectancy positive, research only.
- `mind_trader/app/validation/robustness_committee.py` (P8.83): existing composite walk-forward, Monte Carlo, anti-overfitting and uncertainty gate. Production blocked and live forbidden.
- `mind_trader/app/data/dataset_lineage_gate.py`: existing dataset provenance gate.
- Existing `mind_trader/tests/test_p881_walk_forward_authority.py` and `test_p883_robustness_committee.py` already test these components.

## Semantic collision
Historical P2279E marks an edge approved with >=2 profitable windows of four and stability >=0.15. **This is not equivalent** to the stricter existing P8.81 authority and cannot promote an edge or bypass the P8.83 committee. Historical 11/12 is a retrospective research result only.

## Tests and results
- Local isolated tests of original P2279E with 10 SHA-verified Drive MT5 datasets: **3/3 PASS**, including source SHA, dataset hashes, 12-row replay, 11 approved, UK100 M15 weak, PAPER_ONLY/real-order prohibition. Local test file is a standalone fixture-based forensic harness and is not committed to the core because original datasets are not in the repository.
- New GitHub test `mind_trader/tests/test_p2279e_p881_compatibility_gate.py` exercises **existing P8.81**, not a duplicate engine: historical 2/4 profitable windows cannot bypass it; summary-only evidence rejected; a passing authority remains research-only. **Published; CI not yet confirmed**.

## Release gate
No P2279E engine copied, no modification to existing core implementations, no production route, no order. Remaining: complete other repository top-level subtrees, inspect strategy execution and data adapter dependencies, run CI on branch, implement only missing MT5 adapter if warranted, perform integrated paper-only replay with existing P8.81/P8.83.
