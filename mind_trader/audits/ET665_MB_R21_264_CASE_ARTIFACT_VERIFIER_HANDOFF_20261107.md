# ET665.MB.R21 — Independent R19 264-test ZIP integrity verification handoff

Date: 2026-11-07. Verification is prepared but not yet executed on the operator's Windows host.

- Tested source commit: `9e31b58b8f25ad569d077e6bdbb6fbc6586e7ff4`.
- R19 264/264 PASS output recorded in `ET665_MB_R20_R19_264_TEST_EVIDENCE_RECEIPT_20261107.md`.
- Verifier: `mind_trader/security/et665_mb_r21_evidence_verifier.py` (commit `ccee424686d775f13420774935f45ffac1274153`).
- Expected ZIP: `ET665_R19_20261107_200335.zip`.
- Expected SHA-256: `8ad07238d895793fcb0b109c7620813efebe4b69f66c99eec05eee4f87901d6c`.
- Expected JUnit: 264 cases, 0 failures/errors/skips.
- The runner's `mission` field is still `ET665.MB.R13`; verifier retains that literal because it matches the actual R19 decision.json. This label is legacy metadata, not the tested source identity.
- This verification checks ZIP CRC, exact members, internal SHA-256, JUnit and decision consistency, P15 synthetic tests, and forbidden real-order/FTMO flags.
- `R19_ARTIFACT_INTEGRITY=PENDING` until actual verifier output is supplied.
- `PHASE_B=BLOCKED`, `REAL_ORDERS=FORBIDDEN`, `FTMO_REAL=FORBIDDEN`, `MAIN_MERGE=BLOCKED`.
