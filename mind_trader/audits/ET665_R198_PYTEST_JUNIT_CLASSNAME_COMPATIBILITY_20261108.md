# ET665.R198 — Pytest unittest JUnit compatibility (2026-11-08)

R197 added the R196 `unittest.TestCase` module to pytest, but R196's exact-classname check used only the final dot-separated component. Real pytest JUnit for unittest classes reports e.g. `test_junit_gate.GateTests`; therefore the final component is the class name, not the module. This could reject valid offline runs.

A local pytest invocation of the existing standalone R196 fixture implementation produced **8 passed** and a JUnit testcase classname `test_junit_gate.GateTests` (observed directly from the generated XML). R198 changes the gate to match exact dot-delimited classname components and adds a fixture for `module.GateTests`. Substring matches remain disallowed.

Scope limitation: the local test is the previously available standalone fixture, not the published repository suite. The newly published regression and Docker harness have **not** been executed in the authorized offline container. No security certification, merge or production change.

`R198=PATCH_PUBLISHED | LOCAL_STANDALONE_PYTEST=8_PASS | DOCKER_SUITE=NOT_EXECUTED | PHASE_B=OPEN | MAIN=UNCHANGED | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0`
