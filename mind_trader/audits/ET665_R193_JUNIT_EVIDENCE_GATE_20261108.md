# ET665.R193 — JUnit evidence acceptance gate (2026-11-08)

Authenticated source inspection of the R187–R192 offline runner found that Docker/pytest exit status zero alone was treated as a completed test run even when no JUnit file existed. That could allow a false success message if the runner was replaced or output was suppressed.

R193 requires host Python 3 for standard-library XML validation and, after Docker exit zero, verifies that JUnit is present, parseable, includes at least one executed test, has zero failures/errors, and is not entirely skipped. Missing/invalid JUnit converts success to a nonzero exit status, which is written into the evidence manifest.

The JUnit gate validates the format and reported results, **not** the authenticity of the test runner, image, Docker daemon or isolation. Independent evidence review and approved offline Docker execution are still required. This is a published source change, not an executed test or Phase B certification.

`R193=SOURCE_PATCH_PUBLISHED | TESTS=NOT_EXECUTED | PHASE_B=OPEN | MAIN=UNCHANGED | PRODUCTION=UNTOUCHED | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0`
