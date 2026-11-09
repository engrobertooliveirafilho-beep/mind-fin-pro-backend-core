# ME-RS-304 — POST_R6 isolated synthetic regression evidence (2026-11-09)

## Execution
- Environment: disposable Linux container, Python unittest, temporary SQLite databases.
- Test command: `python -m unittest discover -s tests -p test_me_rs_303_post_r6_offline.py -v`.
- Result: **10 tests ran, 10 OK, 0 failures, 0 errors** (0.094 seconds).
- Test cases: bounded resume/idempotence; late approval; mismatch rollback; prefix mutation; partial tail; invalid record rollback; conflicting approvals; source rebinding; truncation; partial approval manifest.
- Test files and POST_R6 module were manually reconstructed in an isolated container from the GitHub source read at commit `bab835dc44ebdaa0b15fa1d36fdbf4958fe0f606`. **Byte-for-byte equivalence of the local reconstructed module to the GitHub blob has NOT been established.** Accordingly this is a useful synthetic reproduction, **not an authenticated GitHub checkout or certified CI run**.
- No Drive source, historical ledger, production runtime, MT5, broker or paid infrastructure was accessed.

## Certification boundaries
- R6 historical source: 127004 rows; historical SQLite 124491; remaining 2513 still not executed.
- R8 original 11/32 checkpoint remains unverified.
- R4→R5→R6→R7→R8 parallel integration remains NOT_RUN.
- No promotion of R8, no production release, no merge.
- Keep PR Draft until authenticated checkout, original-data validation and complete offline integration are proven.

## Local result excerpt
```
Ran 10 tests in 0.094s

OK
```
