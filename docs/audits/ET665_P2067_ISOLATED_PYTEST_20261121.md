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
