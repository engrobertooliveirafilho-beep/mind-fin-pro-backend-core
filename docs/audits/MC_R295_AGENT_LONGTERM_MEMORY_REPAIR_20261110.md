# MC-R295 — AgentLongTermMemory repair
Date: 2026-11-10

## Grounded source
Drive original: `1Z4_Laor3FtgviDpNENNKl_dvjbslEUN2`; original test: `1KBzCTiKhqD3ihnWftppMhkvsO7ai_kGF`. Original behavior confirmed in source: in-memory dict only; `last_events(..., limit=0)` slices `[-0:]` and returns all events; no durable persistence. Existing original test checks ordering/filtering but not zero/negative limits or restart persistence.

## Repair published (isolated branch)
- Restored API at `app/agent_longterm_memory.py`, preserving in-memory default.
- Fixed limit=0 to return empty; negative/non-integer/bool limits rejected.
- Added opt-in SQLite persistence via explicit `db_path`, parameterized inserts, per-agent filtering, timestamp ordering with stable insertion tie-break, and connection close/rollback.
- Input validation rejects empty identities and bool timestamps.
- No implicit database created; existing consumers retain in-memory behavior unless they explicitly configure db_path.

## Tests
9/9 local Python unittest PASS against exact branch source and tests. Re-run with ResourceWarning promoted to error: 9/9 PASS, no connection-leak warnings. Covers zero/negative limits, stable order, agent isolation, capped results, restart persistence across separate instances, SQLite ordering, invalid event and bool limit.
- GitHub readback/CI has not been executed; no remote CI PASS claimed.
- Original test compatibility is maintained by default constructor and existing add_event/last_events API, but original test file was not run as a separate checkout test in this turn.

## Remaining authority/integration gates
- No canonical runtime import/use site for AgentLongTermMemory was found in repository code search; module is added but not wired to production runtime.
- SQLite durability is opt-in and requires explicit approved db_path, backup/retention policy, access controls and lifecycle integration before use by agents.
- No migration of old in-memory events to disk; no production data changed.
- Master Ledger append remains blocked HTTP 403; this report is GitHub-only pending synchronization.

R4 untouched; main and production untouched; no merge/deploy; REAL_ORDERS/FTMO_REAL forbidden; cost R$0. HP19 remains 0/19 certified; global MIND Central certification BLOCKED.
