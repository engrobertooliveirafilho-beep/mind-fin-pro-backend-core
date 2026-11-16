# ET665 — Git blob-exact offline regression — 2026-11-16

Repository: engrobertooliveirafilho-beep/mind-fin-pro-backend-core
Branch: engineering/et665-trader-wiring-failclosed-20261116

- Runtime: `mind_trader/app/engines/core.py`
  - Git blob SHA-1: `88876409137a37d2c304ebd0802f65c5c8dbcbc9`
- Regression: `tests/test_et665_legacy_jsonl_writer_safety.py`
  - Git blob SHA-1: `8587cdb112ad6d29f47705dad23b9679d271756a`
- Method: retrieved published source contents, reconstructed local files, verified each with `git hash-object` against GitHub blob IDs, then executed `python -m unittest discover -s tests -p 'test_et665_legacy_jsonl_writer_safety.py' -v` offline.
- Result: **9 tests, 9 PASS, 0 FAIL**.
- Scope: syntax compilation, FTMO simulation symbol persistence, reject LIVE/unknown/empty symbol, signed PnL, reject NaN/infinite risk.
- No Docker execution claimed; no GitHub Actions execution claimed; no S19/S20/S21 end-to-end certification claimed.
- MAIN intact, no merge, PAPER_ONLY, REAL_ORDERS forbidden, FTMO_REAL forbidden, cost R$0.

Next: connect this certified isolated engine to historical source/writer chain with independently proven symbol lineage. Historical S19/S20 CSVs do not contain symbol; no fabricated backfill permitted.
