# ET-607 — P2354 local isolated pytest

- 2026-11-05: reproduced exact P2354 module and 5 tests from PR #2 in a temporary local isolated directory.
- Command: `PYTHONPATH=. pytest -q -o cache_dir=/tmp/eldora_pytest_cache tests/test_p2354_conflicting_directions.py`.
- Output: `..... [100%]` and `5 passed in 0.06s` (pytest 9.0.2).
- Tests stub P2353 intentionally, exactly as in PR; does NOT validate original P2353 or full P2302/P2362 integration.
- Critical unresolved gap: missing `context.candidate_signals` keeps the legacy fail-open path. Do not merge, no paper emission without complete batch proof.
- `PAPER_ONLY`; `REAL_ORDERS=FORBIDDEN`; `FTMO_REAL=FORBIDDEN`.
