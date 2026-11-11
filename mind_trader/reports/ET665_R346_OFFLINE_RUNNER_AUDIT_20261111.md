# ET665.R346 — Offline runner remediation and certification boundary

Date: 2026-11-11
Branch: `audit/et665-r346-offline-local-runner-20261111`
Base: `2dc4996e63747f184c36c5b5c0c04d3fa873f72b`
Mode: PAPER_ONLY
REAL_ORDERS=FORBIDDEN
FTMO_REAL=FORBIDDEN

## Findings verified from repository

1. R345 records an operator-provided transcript for 19/19 unit tests in the S20/S21 structural gate. The report explicitly says the transcript is not an independently retrieved signed log.
2. The 19 tests use synthetic rows and temporary CSV files. They validate required fields, timestamp ordering, positive prices, SHA-256 formatting, duplicate detection and CSV snapshot hashing. They do not process original S20 decisions or S21 market ticks.
3. The R344 runner previously downloaded its module and tests from raw.githubusercontent.com with Invoke-WebRequest. Therefore the previous runner was not offline, despite its name.
4. The R345 evidence says original S20/S21 data retrieval and execution remain pending.
5. R345's commit has no GitHub status checks and no workflow runs. CI/runtime execution is unverified.
6. HP19 is a separate 19-executor recovery/certification track. R344's 19 unit tests are not HP19=19/19.

## R346 correction

- Replaced network downloads with copies from the checked-out repository.
- Runs the same unit suite in an isolated temporary directory.
- Does not modify the source checkout.
- Fails closed if either checked-out source file is missing.
- Runtime execution has NOT been performed in this session; no PASS is claimed.

## Remaining blockers

- Execute the revised runner in the approved Windows offline environment and retain raw console transcript, exit code and SHA-256 manifest.
- Retrieve canonical original S20 decision records and S21 tick data, verify provenance, then process them end-to-end through the gate.
- Add behavioral runtime proof for the actual component, not only synthetic unit fixtures.
- Resolve the remaining Fase B 16-front evidence gates individually.
- Keep HP19 separate until its 19 executors each pass independent runtime behavior tests.

`R346=RUNNER_CORRECTED_UNEXECUTED | R344_UNIT_TESTS=19_RECORDED_OPERATOR_EVIDENCE | S20_S21_REAL_DATA=BLOCKED | HP19=0/19 | FASE_B=0/16 | MAIN=UNCHANGED | PAPER_ONLY | COST=R$0`
