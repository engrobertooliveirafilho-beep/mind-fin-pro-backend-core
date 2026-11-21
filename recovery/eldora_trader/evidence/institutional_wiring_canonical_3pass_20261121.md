# Eldora Trader — Institutional wiring canonical offline regression

Date: 2026-11-21
Python: 3.13.5, offline; no broker, no network.
Command: `PYTHONPATH=. python -m unittest discover -s tests -v`
Result: **3 tests, 3 PASS, 0 FAIL**, elapsed 0.001s.
Log SHA256: `da7d2277aaef31bfd4fa3b90b80e7ee78d23a2541ed5090a4a05c285cc4af642`

**Exact Git blob SHA1 matched**:
- `app/runtime/mind_trader_institutional_wiring.py`: `6dba5ec9778ae4d7a33cfeeea62bde924aeab20b`
- `tests/test_institutional_wiring_discovery_only.py`: `3e67e812df2478cc02a82c259448c4135e2471b2`

SHA256 source: `95760f1c51461beffd81d64ec365c96d3aef162d3097d78e29c5c1a45063e68a`
SHA256 tests: `7dbbde8173bcc7b4b6652efda11a318989d206c71ee7279e9ad5cffcbbadaad5`

Tests verify: imported module.run is not called; invalid payload including falsey values is rejected; import errors fail closed. These are canonical exact-source unit regressions, **not E2E**, no full-module import or production certification.

Code commits: `c387e6d7a06026be6dae4b4b7abf8e8bea9e92e1`, `4d6cb9f45d701e74aa0a3ad70b43aec6cb5843ce`.
Test commits: `aa57e7b74dc131122f781d3e3ef9cd2d31703713`, `dc2f0fb3952c9eeca678f5a12e1b5978333c9c03`.
Next gate: explicitly authorized PAPER execution wiring with contract tests, no historical S20 mutation.

PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | MAIN=INTACTA | E2E_CERTIFIED=FALSE | COST=R$0
