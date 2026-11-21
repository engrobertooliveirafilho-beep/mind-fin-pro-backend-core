# FTMO P2131–P2150 — Offline reproduction, 2026-11-21

Result: 8/8 PASS, 0 FAIL (Python unittest, offline, no network).

**Scope:** Local hand-reconstructed behavioral subset of the GitHub module and equivalent tests; **not byte-identical canonical source**. This does not certify the original module, the canonical test suite, or PAPER E2E.

Command: `PYTHONPATH=. python -m unittest discover -s tests -v`

Local log: `/mnt/data/ftmo_validation/results.log`
Log SHA-256: `f4a5f8b9de1b156455e61d132096c4a65cce9454f8ecbb7f0fbdf6d63be9d8a7`

Canonical branch source SHA (Git blob): `6583fd3b78942481922b435e473c770907d8ca24`
Canonical branch tests SHA (Git blob): `d6641b40d642e9600e97b5135b91f985bd00be03`

Remaining gate: execute canonical source and tests byte-for-byte; integrate original PAPER runtime; certify behavioral FTMO limits; no real trading.

PAPER_ONLY=TRUE | FTMO_REAL=FORBIDDEN | MAIN=INTACTA | E2E_CERTIFIED=FALSE | COST=R$0
