# ET665.MB.R15 — Independent evidence ZIP verifier

Date: 2026-11-07. The prior R13 offline suite yielded 253/253 PASS at source commit `d7bf41752d86ffef59cd18d5a93583d35f94dba0`, as reported in user PowerShell output. The ZIP bytes have not been provided to this GitHub audit session.

## Deliverable
Read-only verifier: `mind_trader/security/et665_mb_r15_evidence_verifier.py`, commit `856f1421442401057fa09ca6b344ba7200f3f33c`.

The verifier pins the reported R13 ZIP SHA-256, JUnit SHA-256, execution.log SHA-256; requires exact three ZIP members and valid CRC; parses JUnit and decision.json independently; checks 253 tests with zero failure/error/skip; checks four P15 engine test pairs; confirms all live and Phase B gates remain blocked. It does not require pytest or network and does not invoke the test runner.

## Command (in existing Windows checkout)
```powershell
$ErrorActionPreference='Stop'; git fetch origin audit/et665h-paper-ci-security-review-20261106; if($LASTEXITCODE -ne 0){throw 'FETCH_FAILED'}; git -c core.longpaths=true checkout --detach 856f1421442401057fa09ca6b344ba7200f3f33c; if($LASTEXITCODE -ne 0){throw 'CHECKOUT_FAILED'}; python -m mind_trader.security.et665_mb_r15_evidence_verifier --zip (Join-Path $env:TEMP 'ET665_R13_20261107_195723.zip'); if($LASTEXITCODE -ne 0){throw 'EVIDENCE_NOT_VERIFIED'}
```

## Status
`INDEPENDENT_ARTIFACT_CHECK=PENDING_EXECUTION`.
`FOCUSED_TESTS=253_PASS_USER_REPORTED`.
`PHASE_B=BLOCKED`.
`RESIDUAL_INVENTORY=NOT_CERTIFIED`.
`INDEPENDENT_SECURITY_REVIEW=WAIVED_BY_OWNER_NOT_PASS`.
`REAL_ORDERS=FORBIDDEN`.
`FTMO_REAL=FORBIDDEN`.
`MAIN_MERGE=BLOCKED`.
