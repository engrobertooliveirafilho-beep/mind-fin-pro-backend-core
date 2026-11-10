# ET665.R328 — Drive/GitHub reconciliation and causal OOS gate

Date: 2026-11-10
Branch: `audit/et665-r317-csv-guard-regressions`
Scope: historical P2405/P2405B/P2405C/P2405E3/P2405F source reconciliation; offline research gate only.

## Confirmed source findings

- Drive original P2405F source `p2405f_factory_walk_forward_validation.py`, ID `1vVB0zl24EujGEXR6Be1a-E8bF1N1WctC`, 6,285 bytes; SHA-256 `36df2f9be5814bfbcbe62eb8e3b0064129674973cbdb05921005378c557e2916`. Hash matches the R325 source fingerprint.
- P2405F `eval_cand` derives PF, win rate, expectancy, drawdown, sample count and passing windows from `rnd(seed + metric)`; `rnd` is SHA-256 modulus. These are not metrics calculated from market trades or OHLC. The historical 544 labels remain invalid as empirical validation.
- Drive original P2405E3 source SHA-256: `62c9e4032379a9d3cfc2d22adcb40bb399f0eb3e443849b306f0607efd5099ce`. It enumerates combinations of family/pattern/session/regime/timeframe/direction/risk/filter and derives IDs/novelty by SHA-256. The candidate-generation loop does not consume OHLC prices or trade outcomes. The 1,219,354 figure is combinatorial candidate volume, not evidence of 1,219,354 market-tested edges.
- Original P2405, P2405B and P2405C all load `P2403E/p2403e_de40_edge_trade_series.csv`. R319 has already quarantined that hash-scheduled replay lineage as noncausal. Therefore their historical portfolio metrics and 10-edge selection are not eligible for empirical promotion.
- GitHub `mind_core/app/runtime/p2405*.py` copies are safety stubs, not byte-identical originals. They keep `runtime_allowed() == False`; they cannot be treated as restored P2405 engines.

## R328 implementation

- Added `mind_trader/research/et665_r328_causal_oos_costs.py`.
- Requires trade-level records with signal, entry and exit timestamps; gross PnL; spread, slippage and commission; logic/data/execution evidence hashes; review ID.
- Uses R315 immutable, hash-pinned CSV snapshot; one verified descriptor snapshot is parsed.
- Applies caller-defined chronological train/validation/test boundaries, embargo and purging of gap/cross-boundary trades.
- Evaluates one edge at a time; blocks mixed-edge CSVs and overlapping positions. Computes PF, win rate, expectancy and drawdown in realized-exit order on net R after execution costs.
- Fails closed on missing evidence metadata, invalid hashes, duplicate signal IDs, nonchronological signals, impossible event order, nonfinite values, negative costs, invalid boundaries or insufficient samples.
- Explicitly returns causal/provenance verification false and never allows runtime promotion or real execution.

## Regression and execution status

- Added 21 R328 adversarial tests in `tests/test_et665_r328_causal_oos_costs.py`.
- Updated the isolated Docker workflow to run the R326 and R328 test modules together (38 expected tests).
- R327 Docker result supplied by operator: 17/17 PASS.
- R328 suite is published but has NOT yet been executed in Docker. No R328 PASS is claimed.
- No valid trade-level causal CSV with independently reviewable source lineage was recovered in this pass; R328 cannot be run against P2403E/P2405F synthetic/hash-derived outputs.

## Decision

P2405 historical results stay quarantined. The next admissible input is independently sourced GER40 OHLC plus signal logic that records decision time, entry/exit, and execution costs without lookahead. Until that dataset exists and passes R328, do not promote, activate, merge or execute any edge.

`PHASE_B=OPEN | CERTIFIED=0/16 | HP19=0/19 | PAPER_ONLY | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0 | NO_MERGE`
