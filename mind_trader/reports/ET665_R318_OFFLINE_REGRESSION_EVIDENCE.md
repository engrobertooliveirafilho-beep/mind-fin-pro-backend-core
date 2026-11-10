# ET665.R318 — offline regression evidence (2026-11-10)

- Base: R316 `3aba335d733062b25551d1e564ee7ae153ef2122`
- Test branch: `audit/et665-r317-csv-guard-regressions`
- Published tests: `tests/test_et665_r317_csv_snapshot.py`
- Command (isolated local copy): `python -m unittest discover -s tests -p 'test_et665_r317_csv_snapshot.py' -v`
- Result: **7 tests, 7 PASS, 0 FAIL**, Python 3.13, 0.006 s.
- Scope: reconstructed byte-for-byte logic of `et665_r315_immutable_csv_snapshot.py` and equivalent R317 test cases in a temporary local directory. Not a repository checkout or Docker certification.
- Tested: valid snapshot remains non-promotable; tampering, extra CSV fields, wrong schema, oversized input, malformed expected hash and symlink are rejected.
- CI: no workflow runs found for R317 head during inspection.
- PR: creation attempt failed with GitHub HTTP 403 (account requires a verified email).
- Remaining: full offline Docker suite, R314–R316 integration, security isolation, causal validation, independent review, PR.
- **No FTMO approval or Phase B certification claimed.** `PAPER_ONLY`, `REAL_ORDERS=FORBIDDEN`, `FTMO_REAL=FORBIDDEN`, `COST=R$0`.
