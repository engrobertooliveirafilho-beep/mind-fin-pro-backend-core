# ME-RS-077 — R8 corrupted journal fail-open reproduced

**Status: FAIL / R8 certification BLOCKED.** Source: user-provided ME-RS-067 ZIP, `R8_CANDIDATES/008_local_bridge_v2_integrity_candidate.py`. No production or Drive access.

## Exact isolated reproduction
- Temporary source directory with `a.json` and `b.json`.
- Initial `scan(..., max_files=100, max_seconds=30)`: `COMPLETED`, `visited=2`, `hashed=2`.
- Inject `{BAD JSON}` as **middle** line between the two valid journal entries.
- Re-run same source and output: `COMPLETED`, `visited=2`, `hashed=0`, `reused=2`, `errors=0`.
- Journal still contains three lines, including invalid middle record.

Root cause: journal loader catches `(ValueError, KeyError, TypeError)` for **every** row and silently `continue`s, treating corruption anywhere as an incomplete trailing record.

## Required minimal fix
- Strictly validate each complete journal line; malformed *middle* entries must raise a deterministic integrity error, never silently continue.
- A trailing unterminated line may be handled only with explicit recovery/quarantine and auditable status; do not silently mark `COMPLETED`.
- Do not alter source data or historical journal. Use copied fixtures and regression before integrating.
- Preserve detection of same-size/same-mtime content mutation and append-only version history.

## Evidence classification
Reproduction **executed locally** in a disposable Python environment. This is a **negative safety result**; it supersedes any broad R8 PASS claim based solely on previous synthetic resume tests. The historical checkpoint 11/32 remains unverified.
