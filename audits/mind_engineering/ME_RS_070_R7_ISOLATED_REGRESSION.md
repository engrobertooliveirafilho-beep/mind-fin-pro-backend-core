# ME-RS-070 — R7 isolated regression evidence

Status: **5/5 PASS (synthetic local reconstruction only)**. Production unchanged.

## Scope

Reconstructed the R7 executor from the user-provided ME-RS-068 console paste and changed the late PENDING approval branch to explicitly reject R4/R5 mismatches with `ValueError('APPROVAL_LINEAGE_MISMATCH')`. Tests ran in an isolated local Python process with temporary SQLite files, no production database or Drive access.

## Executed results

- `test_new_r4`: PASS — mismatch rejected; no records persisted.
- `test_new_r5`: PASS — mismatch rejected; no records persisted.
- `test_late_r4`: PASS — mismatch rejected; existing record stays PENDING.
- `test_late_r5`: PASS — mismatch rejected; existing record stays PENDING.
- `test_valid`: PASS — valid late approval succeeds and replay is idempotent.

Local run: 5 tests, 0.049 seconds, OK. The synthetic harness was executed in a disposable local environment, not GitHub Actions.

## Integrity caveat

The reconstructed source from the console paste hashes to `c138d700679a7ea9b0e54c771da34b7e2c0ea4e4464ea6f141d02b581a323219`, **not** the original raw-file SHA-256 `58e559debb6181b4a34f857572a3fd1c84f1994def82637ad696106aaecd9d63`. Console paste is not byte-preserving evidence. Thus do **not** claim binary provenance or certified recovery of the original executor.

The PR #4 patch and `tests/test_me_rs_068_r7_late_approval.py` are available for reproducible tests, but GitHub-hosted execution remains unverified. The five earlier ME-RS-063 tests intentionally target the original SHA and must remain historical reproduction checks.

## Gates before merge

1. Recover original executor as raw bytes, verify its SHA-256 and compare semantic delta to patched source.
2. Run repository regression tests on the exact PR HEAD, capture test output and commit SHA.
3. Audit R8 original source bodies, crash/restart, and historical R4–R8 integration.
4. Keep PR draft; no production mutation, no R8 certification or automatic PENDING promotion.
