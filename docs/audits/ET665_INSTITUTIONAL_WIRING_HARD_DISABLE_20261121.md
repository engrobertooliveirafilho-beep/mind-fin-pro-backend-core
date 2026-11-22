# ET665 — institutional wiring hard-disable and offline evidence

## Authority
Google Drive: ELDORA_TRADER_MASTER_REMEDIATION_LEDGER (2026-10-29), id `1WYqMJ-wzqmDWTaRzwJGFk4Hj4b7MuBNR7m0F9ct99mI`. ET-009–ET-013 document symbol lineage and writer schema blockers; ET-011 reports multiple conflicting runtime factories.

## Remediation
GitHub isolated branch `engineering/et665-realdna-reconciliation-20261121`, source `app/runtime/mind_trader_institutional_wiring.py`, commit `414c7c8d6b2f896bdea2fdc2fcf55a8b069dc598`. Public run returns inventory with NOT_CERTIFIED, health is side-effect free, legacy callable raises UNVERIFIED_TRADER_WIRING_DISABLED. Git historical source retained.

Regression source commit `184cb2e021c5a1db07bfeed9784fd0bb3ab88dd4`.

## Executed offline reproduction
`python -m pytest -q /mnt/data/et665_wiring_offline/test_wiring.py`: **4 passed in 0.04s**.
- reconstructed `wiring.py` SHA256 `f3f6ae87962ca014aabb2c81387bd24a6b15a77d91439fd3b6371493f39e93fc`
- `test_wiring.py` SHA256 `815f6c2c59aea09a1ff6caa69e1cb8cf11a939ab4469ae584bc2b21f3e5530c0`
- `pytest.log` SHA256 `a00d95dfbc084b6eb22229f4a5b545b4452162a59797c0faa121535a79212580`

**Scope:** offline reconstructed public logic, not an import of original repository source and not integrated E2E certification.

`PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | E2E_CERTIFIED=FALSE | COST=R$0`
