# Canonical agent dispatcher — offline mode gate

Drive recovery: 52 IDs from original `1IsM5-lotyUzmYQg8Ibvsy7VFz1xkr2E-` and historical test inventory `1_gnMumMCQ-gSDhJsfeylzom2PznR_Asd`.

Executed in local isolated Python runtime: `python -m unittest discover -s tests -p test_agents_unified_runtime_recovery.py -v` => **19/19 PASS, 0 FAIL** (0.001s). Test log SHA-256 `cdb36911cecfc5db55d4e7ed021ecae4c018b44343e06226a02c0681f9746c85`.

Verified local `git hash-object` against published GitHub blobs:
- `app/meta/agents_unified_runtime.py`: `89979a54d35c19652e346d9c716ef20d1d3bd158`
- `tests/test_agents_unified_runtime_recovery.py`: `f0abe6b266241ae1aa2f2347e0a6383599867ef0`

Coverage: 52 registered IDs via mock loader; stub rejection, wrong agent, missing module, nested forbidden operations, NaN/Inf, cyclic payload, deep-copy isolation, explicit rejection of live/real/None operational modes, acceptance of dry_run.

**Limits:** no original-agent integration execution in this run, no E2E certification. Five original agent files recovered in the same branch; all five remain stubs. No production/main changes.

`PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | E2E_CERTIFIED=FALSE | COST=R$0`
