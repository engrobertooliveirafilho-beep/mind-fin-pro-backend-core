# Offline regression evidence — 2026-11-21

Scope: isolated local snapshots under /mnt/data, **not** a checkout of the branch.
Python pytest and unittest, no network, no broker, no real orders.

- /mnt/data/et_p2382_fix: python -m pytest -q tests/test_gate.py => **9 passed in 0.04s**.
- /mnt/data/eldora_validation: python -m pytest -q test_p2382.py => **4 passed in 0.03s**.
- /mnt/data/p2397_gate_validation: python -m unittest discover -s tests -p 'test_*.py' -v => **4 tests, OK**.

Total **17 tests PASS, 0 FAIL**. This verifies the isolated local modules only.
It does **not** certify P2377→P2397 E2E, nor assert equality to the current GitHub branch.
PAPER_ONLY=TRUE; REAL_ORDERS=FORBIDDEN; FTMO_REAL=FORBIDDEN; E2E_CERTIFIED=FALSE.
