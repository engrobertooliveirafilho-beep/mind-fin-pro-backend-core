# ME-RS-074 — Windows isolated regression evidence

Status: **PASS — 7/7 synthetic tests, 0 failures** (user-executed output, 2026-11-08).

## Integrity and execution

- GitHub test-file blob SHA-1: `a85253b8a51cdc31d1fc314cd8ed7be67b1e233a` — verified against GitHub Contents API payload and bytes before execution.
- Test file: `tests/test_me_rs_068_r7_late_approval.py`.
- Executor: `code/engineering_pipeline/post_r6.py`; previously downloaded with verified GitHub blob SHA-1 `01bbc83f30a2414179eca81e6fdd5a1679dc4959` in ME-RS-072.
- Environment: user Windows PowerShell, Python 3.12, temporary SQLite test databases.
- Command: `python -m unittest discover -s tests -p 'test_me_rs_068_r7_late_approval.py' -v`.
- Result: **Ran 7 tests in 7.601s — OK**, exit code 0.
- Report path on user workstation: `D:\MIND_TEMP\MIND_ENGINEERING_ACTIVE_WORKSPACE\ME_RS_072_ISOLATED\ME_RS_074_RESULTS.txt`.
- User-reported report SHA-256: `FF0478E3D5D7061B3241DB68803144D1647F839C217CBCFCAD1CD66ABF2F612D`.
- Production mutation: false.

## Seven passed cases

1. Atomic rollback if the second PENDING approval has invalid lineage.
2. Incomplete approval manifest rejected without promotion.
3. Late R4 mismatch rejected.
4. Late R5 mismatch rejected.
5. New R4 mismatch rejected.
6. New R5 mismatch rejected.
7. Valid late approval and replay idempotency.

## Certification boundaries

This is a transcript of user-executed results, not independently reproduced CI logs. The report's SHA-256 is user-reported; the underlying report file has not been uploaded for independent hash verification. These tests use synthetic inputs. The original executor's binary SHA-256 and historical R6 input still require independent provenance and integration verification. **Do not merge or certify R8 on this evidence alone.**
