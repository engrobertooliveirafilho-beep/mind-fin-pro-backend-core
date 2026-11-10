# MC-R293 — Safe dispatch and research fail-closed adapters
Date: 2026-11-10

## Implemented (new isolated modules; NOT wired into production router)
- `app/cognition/safe_dispatch_allocator.py`: deterministic capacity/latency-aware shard placement; validates IDs, duplicate IDs, capacity, latency, weight and fanout; rejects insufficient total capacity instead of silently overloading; uses stable ID tie-break.
- `app/cognition/research_provider_gate.py`: disables synthetic research for all modes unless an actual callable provider is explicitly supplied; raises 503-style ResearchUnavailable otherwise.

## Validation
- 6/6 local tests PASS against the implementation: capacity bounds, insufficient capacity, duplicate cluster/agent IDs, invalid fanout, research fail-closed across all modes, and provider contract.
- Repeatable suite committed at `audits/hp19/r293/test_r293_safety_contracts.py`.
- GitHub readback/CI execution not yet performed; do not claim remote tests passed.

## Limits / next gates
- New modules are isolated adapters; original Step450/452 router paths were not modified or activated. Runtime integration requires canonical source authority, dependency compatibility and additional endpoint-level tests.
- Scheduler currently treats fanout as capacity-consuming shards; product semantics for replicas vs independent work must be approved before production use.
- Real provider implementation and credentials are absent; research remains unavailable by design.
- Master Ledger append remains blocked by HTTP 403 (R289); this report is GitHub-only pending sync.

R4 unchanged; main/production unchanged; no merge/deploy; REAL_ORDERS and FTMO_REAL forbidden; cost R$0. HP19/global certification BLOCKED.
