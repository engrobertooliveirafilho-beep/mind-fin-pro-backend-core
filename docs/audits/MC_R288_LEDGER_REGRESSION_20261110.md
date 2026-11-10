# MC-R288 — SQLite replay ledger regression (2026-11-10)

## Scope
Add regression tests only to R287. No R4/R5/R6/R7/R8 runtime changes, no merge or production changes.

## Offline evidence
Executed a locally reproduced copy of the R287 ledger_guard.py, with five corresponding test cases, Python unittest. Result: **5 tests PASS in 0.011 seconds**. Test cases: valid ledger with URI metacharacters, missing ledger not created, ancestor symlink rejection, invalid schema rejection, corrupted file rejection. Local test run is **not** a checkout of the exact GitHub commit and does not certify full integration.

## Risks and remaining gates
- TOCTOU between path validation and sqlite3.connect remains unproven safe under adversarial concurrent replacement. Do not claim robust race-free isolation.
- Existing R285/R287 regressions have not been executed in an exact checkout in this run.
- R5->R6->R7->R8 integration, process restart and HP19 19/19 are still uncertified.
- Master Ledger Drive write remains blocked HTTP 403 per R286; no claim of sync.
- Fail closed; no real orders, no deployment, R$0.
