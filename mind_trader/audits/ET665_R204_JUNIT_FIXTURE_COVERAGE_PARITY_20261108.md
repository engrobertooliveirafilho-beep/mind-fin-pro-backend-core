# ET665.R204 — JUnit fixture coverage parity (2026-11-08)

Authenticated source inspection found a discrepancy: the R196 unittest fixture's MODULES tuple covered five modules, while the R187 offline Docker runner's JUnit gate requires six (including `test_et665_r196_junit_identity_gate`). The fixture therefore did not mirror the full declared suite identity.

R204 adds the sixth module to the fixture and makes the spoofed-name fixture size derive from `len(MODULES)`. This is a test fixture alignment, **not** proof that the duplicated fixture validator is the same implementation as the runner's embedded Python gate.

A locally adapted prior fixture copy executed with `pytest -q` and returned **8 passed**. That copy was not byte-verified against the newly published GitHub fixture, which contains an additional testcase; do not claim the published file was executed. Docker remains unavailable here, and no full six-module regression run occurred.

`R204=TEST_FIXTURE_PATCH_PUBLISHED | LOCAL_ADAPTED_FIXTURE=8_PASS | PUBLISHED_FIXTURE=NOT_EXECUTED | DOCKER_TESTS=NOT_EXECUTED | PHASE_B=OPEN | MAIN=UNCHANGED | PRODUCTION=UNTOUCHED | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0`
