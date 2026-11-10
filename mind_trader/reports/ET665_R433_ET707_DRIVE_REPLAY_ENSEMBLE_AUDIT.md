# ET665.R433 / ET-707 — Drive forensic continuation — 2026-11-10

Pending insertion into [canonical remediation ledger](https://docs.google.com/document/d/1WYqMJ-wzqmDWTaRzwJGFk4Hj4b7MuBNR7m0F9ct99mI/edit). Google Docs edit permission was denied (HTTP 403 in R432). This report does not assert certification.

## Newly located original primary sources

- P2403E: Google Drive ID `1N3fiXTa3Stl_WXjQZYObI3usSLf3MM8-`; source `p2403e_rebuild_de40_replay_series.py`. Trade series file `1SnbELsnL4G9S5QH_qZC3A63JvXQZnZZB`, replay statistics `11KFCBGUXLnQyQXmh132xcl2vYRLpFXAY`.
- P2406: Google Drive ID `1vjXvvUatJzoi266msxwHuGmj0ayDRs6u`; source `p2406_edge_ensemble_optimizer.py`. Weight file `1ILOj4in_NEgEU_tRNL6AUdF9INSeaU7F`.
- P2389 governance lock: Drive ID `1qEG6s9i6izAKOFtz0DAEgXo52jJaYXgA`.

## New fail-closed findings

**P2403E signal lineage:** `seed=SHA256(edge_id+"|DE40|M15")`; `stride=5+seed%19`, `offset=seed%stride`, `hold=2+seed%10`. Entry and exit scheduling is deterministic from identifier, not proven execution of candidate signal logic. Although `pnl_r` uses real OHLC close differences and an ATR-derived divisor, that is not a demonstrated strategy backtest. The module does not visibly account for spread, slippage, commissions or chronological train/test separation in the inspected replay loop. `P2403E_STRATEGY_REPLAY_CERTIFIED=FALSE`.

**P2406 ensemble context:** Generated `P2406EdgeEnsembleOptimizer.vote(context)` filters members only by status, then computes quorum and sum of weights. The supplied `context` is not used to evaluate actual directional member votes. The return value `allowed=True` for a `PAPER_SIGNAL_CANDIDATE` can be produced solely by static member count and weights, not evidence of consensus. `P2406_CONTEXTUAL_VOTE_CERTIFIED=FALSE`.

**P2389 lock:** Manifest explicitly states `real_execution_allowed=false`, `paper_forward_allowed=true`; historical `certification` fields in the source are declarations, not current independent E2E evidence.

## Required corrective acceptance tests

1. P2403E: replay only signals emitted by actual recovered strategy code on past-only bars, record signal-time, entry-time, fill price, costs, and immutable OHLC source digest; use walk-forward splits and verify no future-data leakage.
2. P2406: reject missing context, zero/NaN/negative weights, absent directional votes, stale timestamps, contradictory directions, low quorum, and unsafe routes; return PAPER-only candidate only on matching fresh independently emitted votes.
3. Recalculate P2404 pairwise return correlation using independently verified trade series, not P2405H's descriptor-based correlation proxy.
4. HP19: trace a real component through each of 19 executors with input/output SHA-256, identity, time, outcome and failure path; do not count contract presence as execution.
5. No main merge, no live orders, no paid services.

`PHASE_B=0/16 | HP19=0/19 | E2E_CERTIFIED=FALSE | PAPER_ONLY | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | R$0`
