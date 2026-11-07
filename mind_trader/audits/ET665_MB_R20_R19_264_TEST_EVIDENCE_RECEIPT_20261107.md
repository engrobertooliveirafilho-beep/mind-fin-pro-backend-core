# ET665.MB.R20 — R19 264-test offline execution evidence receipt

Date: 2026-11-07. User-supplied Windows PowerShell output; no direct access to the ZIP bytes by the GitHub connector.

## Tested source and observed results
- Exact tested HEAD: `9e31b58b8f25ad569d077e6bdbb6fbc6586e7ff4`.
- Runner: `mind_trader.security.et665_mb_r8_consolidated_runner`.
- Runner mission field remains `ET665.MB.R13` (legacy label; **not** proof of testing the R13 source only).
- Timestamp: `2026-11-07T23:03:39.477520+00:00`.
- 264 tests, 0 failures, 0 errors, 0 skipped; pytest exit code 0.
- `focused_regressions=PASS`; `p15_synthetic_end_to_end=PASS_SYNTHETIC`.
- `p15_integration_and_write_guard_confirmed=true`.
- ZIP: `ET665_R19_20261107_200335.zip`.
- ZIP SHA-256 (runner and PowerShell agree): `8ad07238d895793fcb0b109c7620813efebe4b69f66c99eec05eee4f87901d6c`.
- `execution.log` SHA-256: `987429792b0331623b373a8a8fdad534319f09690bce11231ef99b759f8d00a2`.
- `junit.xml` SHA-256: `e8b7e59bee426166a3ac7434cd863103ac7ae40cd9c1c31a190bc4ecbc8d314c`.

## Limits and pending work
- The operator ran the tests on Windows; this receipt does not independently inspect the ZIP or rerun tests.
- The independent R15 ZIP verifier is pinned to the **earlier 253-test R13 ZIP**, so it must not be used to certify this R19 264-test artifact without updating expected hashes/count and verifying it.
- Complete residual route inventory is `NOT_CERTIFIED`.
- Independent security approval is `NOT_CERTIFIED` (previous owner waiver is not an approval).
- Governed publication remains `NOT_CERTIFIED`.

`R19_TESTS=264_PASS_USER_OBSERVED`
`R19_ZIP_INDEPENDENT_INTEGRITY=PENDING`
`PHASE_B=BLOCKED`
`REAL_ORDERS=FORBIDDEN`
`FTMO_REAL=FORBIDDEN`
`MAIN_MERGE=BLOCKED`
