# MC-R296 — AgentLongTermMemory source reconciliation
Date: 2026-11-10

## New Drive finding
Compared four independently located Drive copies of the original `app_agent_longterm_memory.py`:
- `1Z4_Laor3FtgviDpNENNKl_dvjbslEUN2`
- `18OrpZbbTc2q_Rsardw0-5kv8p_4n9TVN`
- `1E1Gg7-MKiVy50pS9OUeT6rd3xXMIx7jn`
- `1KqWguIc14-ctthLJmz1bPTJbEfFKH0wW`
All four returned exactly 2,958 characters and were byte-for-byte equal as fetched text. This corroborates a single historical implementation across the four copies; it does not establish current runtime authority.

## Reconciliation result
- R295 repair preserves the historical API by default and adds explicit opt-in SQLite persistence.
- Existing default-branch GitHub code search for `AgentLongTermMemory(`, `agent_longterm_memory`, `lifespan FastAPI`, and `include_router cognition` returned no matches. GitHub code search is default-branch/index dependent; this is NOT proof that no runtime use site exists.
- Therefore canonical initialization and dependency wiring remain UNKNOWN. Do not enable SQLite or wire into runtime until a repository tree/entrypoint audit and explicit storage policy are approved.

## State
R295 code/test/report remain isolated in branch `mind-rs-r295-agent-memory-persistence-20261110`; this R296 reconciliation report is isolated separately. No code changes to the runtime. Master Ledger write remains HTTP 403. Main/production unchanged; R4 preserved; R$0; HP19 0/19 certified; global certification BLOCKED.
