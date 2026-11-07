# ET665.MB.R22 — R19 independent ZIP integrity verification receipt

Date: 2026-11-07. Source: user-provided Windows PowerShell output after checkout of `34a1c76d04868464f650fba625d4c35f22bc280f` and execution of `mind_trader.security.et665_mb_r21_evidence_verifier`.

## Observed verification
The operator reported **20/20 PASS**: ZIP_SHA256, EXACT_MEMBERS, NO_DUPLICATE_MEMBERS, ZIP_CRC, LOG_SHA256, JUNIT_SHA256, MISSION, JUNIT_COUNTS, DECISION_COUNTS, EXIT_CODE, LOG_AND_JUNIT_LINK, FOCUSED_GATE, P15_GATE, P15_GUARDS, P15_CASES, BLOCKED_PHASE_B, NO_REAL_ORDERS, NO_FTMO_REAL, RESIDUAL_NOT_CERTIFIED, SECURITY_NOT_CERTIFIED.

Final output: `INDEPENDENT_ARTIFACT_CHECK=PASS`; `PHASE_B=BLOCKED`.

- Tested source commit: `9e31b58b8f25ad569d077e6bdbb6fbc6586e7ff4`.
- Verified evidence archive: `ET665_R19_20261107_200335.zip`.
- Pinned ZIP SHA-256: `8ad07238d895793fcb0b109c7620813efebe4b69f66c99eec05eee4f87901d6c`.
- Test count: 264, failures 0, errors 0, skipped 0.
- R19 original test evidence: `ET665_MB_R20_R19_264_TEST_EVIDENCE_RECEIPT_20261107.md`.

## Certification boundary
This is an independently coded, user-executed integrity verifier. It proves consistency and hashes of the ZIP evidence under the verifier's assertions. It is **not** a new pytest run, external auditor approval, full execution-path inventory, or release authorization. The GitHub connector did not itself access the ZIP bytes.

`ARTIFACT_INTEGRITY=PASS`
`FOCUSED_REGRESSIONS=264_PASS_USER_OBSERVED`
`P15=PASS_SYNTHETIC`
`COMPLETE_RESIDUAL_INVENTORY=NOT_CERTIFIED`
`INDEPENDENT_SECURITY_APPROVAL=NOT_CERTIFIED`
`GOVERNED_PUBLICATION=NOT_CERTIFIED`
`PHASE_B=BLOCKED`
`REAL_ORDERS=FORBIDDEN`
`FTMO_REAL=FORBIDDEN`
`MAIN_MERGE=BLOCKED`
