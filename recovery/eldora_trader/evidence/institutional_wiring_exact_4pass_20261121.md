# Institutional wiring safety — exact-source regression (2026-11-21)

- Engine: `app/runtime/mind_trader_institutional_wiring.py`, Git blob `5389c69bb16b951d54f690e4c7332619eb282766`.
- Tests: `tests/test_institutional_wiring_safety.py`, Git blob `76e5c3998294fa04c9f202020d4b75df3acbba87`.
- Both blobs independently verified with local `git hash-object` after reconstructing the exact published bytes.
- Python 3 isolated offline `unittest discover`: **4 tests, 4 PASS, 0 FAIL**.
- Log SHA-256: `d8bd1e7e4e4560f004c27bea90fe3574405a3c89e9a40909cc12d74c31126337`.
- Cases: health does not invoke run; import failure is DEGRADED; failed import does not claim operational; import-only success is UNCERTIFIED.
- Scope: mocked dependency boundary; no real broker, no full app startup, no institutional E2E claim.

`PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | MAIN=INTACTA | E2E_CERTIFIED=FALSE | COST=R$0`
