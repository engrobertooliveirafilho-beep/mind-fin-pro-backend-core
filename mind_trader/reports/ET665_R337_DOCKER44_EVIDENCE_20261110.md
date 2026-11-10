# ET665.R337 — R336 Docker 44/44 operator evidence

Date: 2026-11-10. Evidence source: operator-provided console log, not independently audited files.

- Test commit `22d9d2c52d02a62c9100a47fec6c80af7bee6d97`.
- Runner commit `8423d57b1967df8110d8f8510f914ff96693a131`.
- 17 R326 tests and 27 R328/R334/R336 tests all passed.
- Output: `Ran 44 tests in 0.421s`, `OK`, `R336 EXIT=0`.
- Evidence path: `D:\MIND_TEMP\ET665_R330_OFFLINE_REGRESSION\20261110_133749_060_87c46398\EVIDENCE`.
- New tests cover whitespace-only and padded signal IDs and padded review IDs.
- Independent verification of local evidence SHA-256, source-market causality, and broker execution remains pending.

Decision: `R336_REGRESSION=PASS`, `FASE_B=OPEN`, `PAPER_ONLY`, `REAL_ORDERS=FORBIDDEN`, `FTMO_REAL=FORBIDDEN`, `MAIN=UNTOUCHED`. No promotion or merge.
