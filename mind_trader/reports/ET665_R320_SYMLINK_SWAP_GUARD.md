# ET665.R320 — CSV symlink swap guard (2026-11-10)

- Branch: `audit/et665-r317-csv-guard-regressions` (no merge).
- Fix: `mind_trader/research/et665_r315_immutable_csv_snapshot.py` uses `os.open(..., O_NOFOLLOW)` and `os.fstat()` regular-file check on the opened descriptor. The verified byte snapshot is used for hash and parsing.
- Regression: `tests/test_et665_r320_symlink_swap.py` checks replacement of validated source path by symlink immediately before open and ordinary pinned CSV acceptance.
- Local equivalent isolated implementation tested on Python 3.13: **2/2 PASS**. This was a manually reconstructed equivalent module and tests, **not** the actual repository checkout and **not** Docker.
- Remaining: run actual R315/R317/R320 tests in existing offline Docker image; inspect Windows fallback where O_NOFOLLOW is unavailable; full R314–R320 integration and security isolation.
- Google Docs master ledger append failed HTTP 403 PERMISSION_DENIED; no write claimed. This is a permissions error, not evidence that a paid Google subscription is required.
- `PHASE_B=OPEN`; `CERTIFIED_FRONTS=0/16`; `HP19=0/19`; `PAPER_ONLY`; `REAL_ORDERS=FORBIDDEN`; `FTMO_REAL=FORBIDDEN`; `COST=R$0`.
