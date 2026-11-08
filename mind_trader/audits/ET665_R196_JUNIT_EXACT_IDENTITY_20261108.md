# ET665.R196 — Exact JUnit identity gate (2026-11-08)

R195 searched for substring tokens `r180`, `r182`, `r183`, `r184`, `r186` in arbitrary testcase names and classnames. An unrelated testcase named with these tokens could pass coverage checks. R196 requires exact expected module basenames in the testcase `classname` final component.

A standalone Python standard-library fixture implementation was run locally: 8/8 PASS, including valid report, missing module, testcase-name spoof, substring spoof, skipped suite, count mismatch, malformed XML and testcase failure. The initial test fixture was corrected after its first run failed due to a malformed failure injection; the rerun passed. The test source is now published at `mind_trader/tests/security_review/test_et665_r196_junit_identity_gate.py`.

**Limits:** The local test run did not execute the GitHub-hosted copy, full pytest suite, Docker harness or MT5 engines. JUnit classname values remain self-reported and are not cryptographic execution proof. Docker and independent review remain required. No production or main changes.

`R196=SOURCE_PATCH_PUBLISHED | LOCAL_FIXTURES=8/8_PASS | REPO_PYTEST=NOT_EXECUTED | DOCKER=UNAVAILABLE | PHASE_B=OPEN | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0`
