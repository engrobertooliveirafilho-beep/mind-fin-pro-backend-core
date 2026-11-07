# ET665.MB.R16 — Verified R15 evidence integrity receipt

Date: 2026-11-07. Source: user-provided PowerShell stdout from executing the pinned R15 evidence verifier on Windows.

## Verification observed
- Checkout HEAD: `d8bdb8e7629514f63b3ca5b91fd1bc662ad026e1`.
- Tool: `mind_trader.security.et665_mb_r15_evidence_verifier`.
- Evidence ZIP: `ET665_R13_20261107_195723.zip`.
- Pinned ZIP SHA-256: `29712eca7e1f454c652efb5155ff6c148b7e48e3c89d3062469c0bab52606c87`.
- 20/20 checks PASS: ZIP_SHA256, EXACT_MEMBERS, NO_DUPLICATE_MEMBERS, ZIP_CRC, LOG_SHA256, JUNIT_SHA256, MISSION, JUNIT_COUNTS, DECISION_COUNTS, EXIT_CODE, LOG_AND_JUNIT_LINK, FOCUSED_GATE, P15_GATE, P15_GUARDS, P15_CASES, BLOCKED_PHASE_B, NO_REAL_ORDERS, NO_FTMO_REAL, RESIDUAL_NOT_CERTIFIED, SECURITY_NOT_CERTIFIED.
- Final output: `INDEPENDENT_ARTIFACT_CHECK=PASS`; `PHASE_B=BLOCKED`.
- JUnit evidence supports 253 tests, 0 failures, 0 errors, 0 skipped, at tested source commit `d7bf41752d86ffef59cd18d5a93583d35f94dba0`.

## Scope and authority
The verifier was executed by the user on the Windows host. This audit records its output and code-pinned integrity assertions; it does not claim that the GitHub connector directly accessed the ZIP bytes or independently reran pytest. This is artifact-integrity verification, **not** an independent full-system security review.

## Outstanding gates
- `focused_regressions=PASS`
- `artifact_integrity=PASS`
- `p15_synthetic_end_to_end=PASS_SYNTHETIC`
- `complete_residual_inventory=NOT_CERTIFIED`
- `independent_security_approval=NOT_CERTIFIED` (previously waived by owner, not passed)
- `governed_github_publication=NOT_CERTIFIED`
- `phase_b=BLOCKED`
- `real_orders=FORBIDDEN`
- `ftmo_real=FORBIDDEN`
- `main_merge=BLOCKED`
