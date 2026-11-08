# ET665.R197 — R196 regression suite wired into offline execution (2026-11-08)

Authenticated inspection of the published R196 tests and R187–R196 Docker harness found a coverage omission: the new R196 identity-gate tests were committed, but the offline runner still invoked only R180/R182/R183/R184/R186. Thus R196 tests would not execute or appear in JUnit.

R197 adds `test_et665_r196_junit_identity_gate.py` to the explicit pytest file list and requires its exact module classname in the JUnit coverage check. Six module groups are now required. This change only prepares execution; it is not evidence of test PASS.

Next: run the pinned commit on an approved offline Docker host, inspect all JUnit testcase outcomes, logs, image digest, source hashes and network isolation; then reconcile R60 and review independently. Main and production remain unchanged, real orders forbidden, zero paid resources.

`R197=PATCH_PUBLISHED | DOCKER_TESTS=NOT_EXECUTED | PHASE_B=OPEN | MAIN=UNCHANGED | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0`
