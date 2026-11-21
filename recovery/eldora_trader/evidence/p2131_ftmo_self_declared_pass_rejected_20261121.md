# P2131–P2150 — self-declared PASS evidence regression (2026-11-21)

- Test command: `cd /mnt/data/ftmo_validation && PYTHONPATH=. python -m unittest discover -s tests -v`
- Environment: Python 3.13, local offline.
- Result: 9 tests, 9 PASS, 0 FAIL.
- Log: `/mnt/data/ftmo_validation/results_9.log`
- Log SHA-256: `4e4821d94ab6f4182f0d483b1315a096ab9701df2447e693fe976bdb167d5705`
- Scope: **reconstructed local behavioral subset**, not exact canonical GitHub files. No canonical-suite PASS claimed.
- New adversarial scenario: six dependency JSONs each self-report PASS plus six audit Markdown files; integrity, metrics, framework and evidence-chain gates remain UNVERIFIED, readiness NOT_CERTIFIED.
- Source commit: `27beb5b270e8984a5f3b79ecc33e03a7d2118a2c`.
- Test commit: `980cae88d03903df79852ccb5ec719bfa7cfbb0d`.
- Pending: byte-exact canonical tests, actual behavior of PAPER engine, independent evidence manifests, full E2E.

PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | E2E_CERTIFIED=FALSE | COST=R$0
