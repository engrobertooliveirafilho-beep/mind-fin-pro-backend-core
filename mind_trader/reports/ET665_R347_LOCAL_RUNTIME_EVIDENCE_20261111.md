# ET665.R347 — runtime reproduction evidence (2026-11-11)

Source: GitHub branch audit/et665-r346-offline-local-runner-20261111, Python files R341/R347 manually reproduced in isolated local environment. This is not a byte-for-byte checkout attestation.

- 4/4 R347 unittest tests PASS (local Python execution).
- CLI valid input: 1 synthetic row, structural validator returned STRUCTURAL_ONLY_NOT_OOS_CERTIFIED.
- Input SHA-256: 890e5426591fcd4a636a994da254e7e4a799e3b76150f2992543c12e38445d68.
- Evidence JSON SHA-256: ea0f2c993d4cb643c623dd9a77ef9e8fd70132dc2e92287aea280df69dc29bca.
- Runtime log SHA-256: 04ac73fb5e81cc97f9d87e149c5fb8900c3f2faf069baa0cf6ca857efab210a1.
- Tampered CSV: exit code 2, no evidence file produced.
- Runtime bundle created locally: ET665_R347_RUNTIME_EVIDENCE.zip (not published in GitHub).

Scope limitations: only R347 4 tests were executed; the 19 R341 tests were not rerun in this session. Original S20/S21 data and provenance, true market-data E2E, walk-forward, OOS, 16 FASE B and 19 HP19 are NOT certified. No production/main changes. PAPER_ONLY, REAL_ORDERS=FORBIDDEN, FTMO_REAL=FORBIDDEN, R$0.

Next action stays within the same macroetapa: validate original historical S20/S21 input and independently attest source SHA-256 in an authorized checkout before promotion.
