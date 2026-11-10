# ET665.R250 — Regressões locais reproduzidas (2026-11-10)

GitHub source inspected: branch audit/et665-r246-mtm-ensemble-20261110, HEAD f55c5ef1f060e357563216ba5107f39d5388ea70.

Local Python reconstruction of two inspected source files was executed in isolated /mnt/data/et665_r250; **NOT a Git checkout or byte-for-byte verified GitHub source**. pytest -q: **9 passed in 0.06s**, 0 failures, exit code 0. JUnit and SHA256 produced locally; not uploaded to GitHub by this audit.

Local reconstructed SHA256:
- module: 1ff3d8273f6875280e64577c62aa8c16a637ebf8f07541e446b7060612e2b9b6
- tests: 12d92f0a1a257efdd7e532de578d573ea29426820099efc72eb6c9a1ad3035ef
- JUnit: 660d9386483800551378258e4466763d2aab35830c347e11fbf280ce590ac55b

**Scope**: 9 locally reproduced behavioral assertions for intrabar adverse MTM and structural ensemble feasibility. No independent source identity proof, no market-data replay, no real strategy rule reconstruction, no external broker connectivity.

**New historical source insight**: P2400 original source Drive file 16rhMiWH65QNMXpruorHRu22P26fPc-Hc generates mutations from P2392 best_promoted key and P2397 summary. Its published runtime module provides rank_candidate and allow_runtime=False; it does not generate price-derived entry/exit signals. Its original source declares research_only=True and runtime_allowed=False.

**Open**: recover P2398 executable, P2391 true signal rules, causal FX and fill chronology, reconcile local source hashes to GitHub, run authenticated GitHub CI, validate OOS and governance. No integration into main.

PAPER_ONLY | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0 | CERTIFICATION_BLOCKED.
