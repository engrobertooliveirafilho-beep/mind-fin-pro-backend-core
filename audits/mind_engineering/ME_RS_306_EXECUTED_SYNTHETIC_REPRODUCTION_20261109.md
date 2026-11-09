# ME-RS-306 — Executed synthetic POST_R6 regression (2026-11-09)

## Actual execution
- Isolated local Linux container; Python unittest; temporary SQLite fixtures; no Drive/network/production.
- Command: `python -m unittest discover -s tests -v`.
- **10 tests ran; 10 PASS; 0 failures; 0 errors; 0.073 seconds**.
- Executed tests cover approval, invalid R5 lineage, conflicting approvals, late-approval mismatch, incomplete approval manifest, incomplete source tail, prefix modification, source rebinding, incremental replay and source truncation.
- SHA-256 of captured log: `d35cfcb3b21b572fda001a54d076a30f744d20055c82b70bc72c087a06b86db9`.
- SHA-256 of manually reconstructed local POST_R6 module: `c185004a4d7e555d5e54ac71144792051f2195915c59906e5612f85b42547397`.
- SHA-256 of independent local test suite: `c66c7a0fc5bb0d663b2c495c89d5b9911b715e7b2c8aef2d502be5d1b770b0b1`.

## Strict scope
The local module and tests were reconstructed manually from connector-returned GitHub content, and are **NOT byte-for-byte authenticated to GitHub blobs**. The original repository's test suite `tests/test_me_rs_303_post_r6_offline.py` and runner `tools/run_me_rs_305_offline.py` were NOT executed in this run. The result is a useful independent reproduction, **not an authenticated CI PASS**.

Historical 2,513 remaining R6 rows were NOT processed; original R8 checkpoint 11/32 NOT recovered; parallel R4–R8 NOT tested; no PR merge or production change.

## Observed output
```
Ran 10 tests in 0.073s

OK
```

**Decision:** SYNTHETIC_PASS_NOT_CERTIFIED; keep PR Draft and ME-RS-077 open.
