# ET665.MB.R14 — Evidence receipt for R13 offline consolidated run

Date: 2026-11-07. This record transcribes user-provided Windows PowerShell output; the evidence ZIP has not been independently downloaded, opened, or rehashed by the reviewer.

## Tested source
- Branch: `audit/et665h-paper-ci-security-review-20261106`
- Exact HEAD: `d7bf41752d86ffef59cd18d5a93583d35f94dba0`
- Runner: `mind_trader.security.et665_mb_r8_consolidated_runner`
- Report mission: `ET665.MB.R13`
- UTC: `2026-11-07T22:57:27.951729+00:00`

## User-reported run
- 253 tests, 0 failures, 0 errors, 0 skipped; pytest exit code 0.
- `focused_regressions=PASS`.
- `p15_synthetic_end_to_end=PASS_SYNTHETIC`; required IDs `p1516`, `p1525b`, `p153_p155`, `p156_p1510`.
- `p15_integration_and_write_guard_confirmed=true`.
- ZIP: `ET665_R13_20261107_195723.zip`.
- ZIP SHA-256 shown in runner JSON and Windows Get-FileHash: `29712eca7e1f454c652efb5155ff6c148b7e48e3c89d3062469c0bab52606c87`.
- `execution.log` SHA-256 (reported): `2a7b2ad0d55fafb7c3aace0df4836bce748036a0c416ddb4639f78f28172be67`.
- `junit.xml` SHA-256 (reported): `8b58ef1da2ed102dac30f0e4befedc6c70b16d4dcf229e451097607a45a4dbf8`.

## Audit disposition
The observed run supports PASS of the focused suite at the tested commit. The prior 249/250 failure is no longer reproduced. The ZIP bytes and JUnit were not independently examined here, so the artifact's independent integrity status remains pending.

Remaining gates from the generated decision:
- `complete_residual_inventory=NOT_CERTIFIED`
- `independent_security_approval=NOT_CERTIFIED` (review previously waived by owner, not passed)
- `governed_github_publication=NOT_CERTIFIED`
- `phase_b=BLOCKED`
- `real_orders=FORBIDDEN`
- `ftmo_real=FORBIDDEN`
- `main_merge=BLOCKED`

This GitHub audit commit is later than the tested source commit; it is not included in the 253-test run.
