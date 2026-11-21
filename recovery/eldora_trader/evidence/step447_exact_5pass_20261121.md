# STEP447 — exact canonical offline regression (2026-11-21)

Drive original: `1OmrO7V4ypWpXgFhXilqJmjsZUvVMMe9n`.

**Executed:** `PYTHONPATH=. python -m unittest discover -s tests -v` in isolated local Python environment: **5/5 PASS**, 0 FAIL. Log SHA256 `0e238d8b22a6f82678ee97460bcfaecd6a701163a1292ec8f1f759e57bcf18c9`.

Exact byte identity verified with `git hash-object`:
- `app/cognition/self_critique_step447/engine.py`: `3c7a4216d973018695c786fb517a8b0386d1c23c`
- `tests/test_step447_canonical_recovery.py`: `3d0009d04db2c54a5d2e7e55c734ce8594427c6c`

Tests: medium severity floor, high severity, financial-context risk detection, empty output rejection, UTC metadata.

**Scope:** only deterministic heuristic checks; does not perform LLM reasoning or autonomous correction. Full FastAPI application boot, PAPER broker integration and E2E not tested.

`PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | MAIN=INTACTA | E2E_CERTIFIED=FALSE | COST=R$0`
