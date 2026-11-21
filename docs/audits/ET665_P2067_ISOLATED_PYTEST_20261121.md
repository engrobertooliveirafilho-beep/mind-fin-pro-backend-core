# ET665 P2067 — isolated offline test execution

Scope: standalone reconstruction of the two source files published in branch; not a repository checkout and not a complete P2071–P2080 regression. Python pytest executed in isolated local directory without broker integration.

Command: PYTHONPATH=. python -m pytest -q tests/test_p2067_allocation_contract.py

Output:
```
........                                                                 [100%]
8 passed in 0.04s
```

Local source SHA256:
- app/runtime/p2067_allocation_contract.py: e78db100c17e64db1304d1245b56e31d7925c29029556a1646bc19970f440bf9
- tests/test_p2067_allocation_contract.py: fc4cba43499201f963d01bbfd3cc1a1c11670b5a95a62517d17db6aeda84b178

IMPORTANT: hashes are of the local reconstruction; they have NOT been verified byte-for-byte against connected GitHub files. This test is evidence of isolated behavior only. The P2067 historical 0.085857 residual remains undeclared in its original Drive record. No automatic normalization or promotion is authorized.

PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | E2E_CERTIFIED=FALSE

## Follow-up execution (2026-11-21)

Executed `python -m pytest -q test_contract.py` in an offline local directory containing a **manual reproduction** of the current P2067 contract and 10 tests, not a GitHub checkout or byte-identical published test file. Output:

```
..........                                                               [100%]
10 passed in 0.04s
```

Evidence path in execution container: `/mnt/data/et665_r_current/pytest.log`. This does **not** certify the P2071 loader, the latest GitHub test suite, the historical P2070 JSON, or end-to-end trading. No live orders.

## Executed offline P2067 contract — 16 cases (2026-11-21)

Direct Python execution in an isolated local directory using a transcription of the current published P2067 allocation module. The 16 locally authored test cases are **not** the complete GitHub test suite and do **not** execute the P2071 loader.

```
PYTHONPATH=. python -m pytest -q tests/test_contract.py
................                                                         [100%]
16 passed in 0.04s
```

SHA-256 of locally transcribed module: `ff24c23f798f2c7487be5211061eaf7dd2cc668b7957cbab69758db899f36d9d`. Local log: `/mnt/data/et665_p2067_20261121/pytest.log`. Source text was inspected via connected GitHub, but independent byte-for-byte verification of the remote blob was not performed. E2E remains blocked.

Drive original dossier inspected: `DOSSIE_AUDITORIA_MIND_TRADER_P2003J_P2070_2026-08-04.pdf` (Drive ID `1CGBpxYazN9XUoyY2_QM4V-b9lxSEj4fl`), which explicitly describes historical P2066–P2070 PASS and notes no confirmed P2071–P2075 execution at its snapshot.
