# ET665.R192 — Checkout integrity gate (2026-11-08)

The R191 harness wrote evidence files before verifying the pinned checkout commit, leaving incomplete artifacts after an admission failure. It also ignored files matched by .gitignore, including Python modules that could shadow imports.

R192 moves commit and working-tree checks before evidence directory creation; rejects ignored Python files in the checkout; writes the verified HEAD to the evidence file only after all checks pass. This is a conservative fail-closed policy and may block legitimate local environments with ignored Python caches/modules. No test execution or Docker attestation is claimed.

Pending: approved offline Docker host, complete test results and JUnit logs, R60 Drive source reconciliation, independent review and main branch governance.

`R192=PATCH_PUBLISHED | TESTS=NOT_EXECUTED | PHASE_B=OPEN | MAIN=UNCHANGED | PRODUCTION=UNTOUCHED | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0`
