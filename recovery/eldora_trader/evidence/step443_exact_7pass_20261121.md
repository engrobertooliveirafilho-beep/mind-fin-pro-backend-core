# STEP443 — exact Git-blob offline regression (2026-11-21)

Original Drive `1VozSoxcoKUIditWxhbKDSoNXBihznZ0O`.

**Executed** Python 3.13, FastAPI 0.128.2, Pydantic 2.13.5, offline: `PYTHONPATH=. python -m unittest discover -s tests -v`. **7/7 PASS**, zero FAIL, 0.001s. Log SHA256: `db9f2b3da22ba22256cee181ea3576d5452de9d775adcd2eefc416525f3b4546`.

Exact Git blob verification via `git hash-object`:
- Engine `app/infra/rate_limit_step443/engine.py`: `fdf35e8948eadfa976df428d93de331112d25d46`
- Tests `tests/test_step443_canonical_recovery.py`: `223a33573c562b26960d3bb6f584c908bac10a2c`

Validated: balanced and conservative decisions, error throttling, duplicate model rejection, NaN/Infinity rejection, UTC. **Scope:** policy recommendation only; not a real API rate limiter, no main application boot or live provider calls.

`MAIN=INTACTA | PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | E2E_CERTIFIED=FALSE | COST=R$0`

## Post-certification change (2026-11-21)

The original 7/7 PASS and blob hashes above apply **only to the prior revision**. Subsequent fix commit `029c2f5797357a110ef565a2da50c2df14ef309c` changed zero-RPM/TPM behavior; new tests commit `b5e1a067c9f5519a2e73231548e75232098340d3`. Three isolated arithmetic assertions passed, **not a canonical regression**. Current STEP443 certification is **OPEN** until exact-source 9-test rerun. Do not count the historical 7/7 as certification of the new HEAD.
