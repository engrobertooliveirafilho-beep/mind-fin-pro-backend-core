# ET665.MB.R8 — Consolidated offline regression gate

Date: 2026-11-07. GitHub source review and artifact publication only; **214 tests not executed together**.

## Deliverable
Commit `398df64f093757137688e6519e2ed1fe5ee8acea` adds `mind_trader/security/et665_mb_r8_consolidated_runner.py` without changing the original MB runner, the disabled CI workflow, main, broker integration, or historical Drive.

The new runner reuses the existing offline evidence protocol: isolated TEMP output directory, no overwrite, pytest plugin autoload disabled, 180-second timeout, JUnit XML, stdout/stderr, SHA-256 manifest and ZIP. It requires exactly 214 tests with zero failures, errors or skips; checks the four synthetic P15 engine cases and four historical Drive-write rejection cases. Even with all tests green, Phase B stays BLOCKED pending the full residual route inventory and security decision.

## Count
- Historical MB: 50 tests previously executed PASS against an older commit.
- R2 adapter: 20 prepared.
- R3 FTMO config: 42 prepared.
- R4 session: 27 prepared.
- R5 PnL: 14 prepared.
- R6 fill: 54 prepared.
- R7 FTMO cost: 7 prepared.
- Consolidated expected: **214**; execution result: **NOT_RUN**.

## Execution contract
From the repository root with Python and pytest already available, execute once in an offline isolated Windows environment:
`python -m mind_trader.security.et665_mb_r8_consolidated_runner --output %TEMP%\\ET665_MB_R8_UNIQUE_RUN`

The output path must be a new unique TEMP subdirectory. Network isolation and absence of live broker credentials must be established externally; this runner does not itself sandbox subprocess/network permissions. It is not safe to infer full security certification from pytest PASS.

## Decision
`R8_RUNNER=PUBLISHED_UNEXECUTED`
`R8_TESTS=214_EXPECTED_NOT_EXECUTED`
`PHASE_B=OPEN`
`REAL_ORDERS=FORBIDDEN`
`FTMO_REAL=FORBIDDEN`
`MAIN_MERGE=BLOCKED`
