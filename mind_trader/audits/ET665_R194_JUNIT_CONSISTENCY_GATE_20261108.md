# ET665.R194 — JUnit consistency gate (2026-11-08)

Inspection of the R193 validator found that a suite could claim a positive `tests` count with no `testcase` elements, and partially skipped suites could pass. R194 requires the total declared tests to equal the number of testcase elements, rejects any declared failures, errors or skipped tests, and rejects testcase-level failure/error/skipped elements.

Independent local Python standard-library fixture checks were executed in the assistant's container on 2026-11-08: valid PASS; fake-count REJECT; skipped REJECT; failed REJECT; malformed REJECT; empty REJECT. **6/6 expected decisions matched.** These fixtures reimplemented the validator logic and did not run the GitHub shell script, repository pytest suite, or Docker isolation. The assistant container had no Docker executable.

Remaining: execute the pinned repository checkout with approved local Docker, preserve full JUnit/logs/hashes, independently review evidence, reconcile R60 Drive source, verify main governance. No certification or production changes.

`R194=PATCH_PUBLISHED | LOCAL_VALIDATOR_FIXTURES=6/6 | REPOSITORY_TESTS=NOT_EXECUTED | PHASE_B=OPEN | MAIN=UNCHANGED | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0`
