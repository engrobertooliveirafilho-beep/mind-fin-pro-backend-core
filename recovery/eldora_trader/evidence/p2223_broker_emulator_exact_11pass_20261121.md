# P2223 exact-source offline regression — 2026-11-21

**RESULT: 11/11 PASS, 0 failures** in Python 3 isolated offline unittest.

- Canonical source: `app/runtime/p2223_broker_emulator.py`, Git blob **`d4741fa834c46dd23107c1496c9ade8d117f93d4`**.
- Canonical tests: `tests/test_p2223_broker_emulator_safety.py`, Git blob **`b2873456d76080bcaa61bb091b0da959d6b09118`**.
- Both local file byte sequences verified using `git hash-object` against GitHub fetch blobs; source uses original CRLF trailing newline.
- Command: `PYTHONPATH=. python -m unittest discover -s tests -p test_p2223_broker_emulator_safety.py -v`.
- Log SHA256: **`457f36520617003747f1136c2e053978b7e017b471f01c1f9aa5fbecccd101db`**.
- Cases: invalid side, zero/NaN/bool volume, sticky drawdown/session kill, no post-kill orders, nonfinite PnL, simulated status, insolvent and overflowed equity.
- Supersedes the prior non-exact-source 9/9 evidence for these two Git blobs only.
- No broker connection, FTMO day-boundary validation, full runtime E2E or profitability certification. MAIN untouched; PAPER only; zero cost.
