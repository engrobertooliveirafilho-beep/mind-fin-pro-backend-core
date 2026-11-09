# ET665.R246 — P15.25 runtime integrity negative regressions

Date: 2026-11-08. Parent: ET665.R245 / draft PR #18, initial HEAD `98dc8ad1d633011ab3e36d63982ed0243f9d1711`.

## Authenticated source verification

- PR #18 was open and draft (5 commits), and PR #17 was open/draft.
- `main` remained `1b5916fbdc8c90173061315400abb92f3bbbb13a`, with `protected=false`.
- PR-triggered workflow runs at the inspected R245 HEAD: 0; commit statuses: 0.
- R244 mocks `Path.write_text` so it does not verify persisted JSON; R245 inspects persisted JSON in four mock-reconstruction scenarios.
- P15.25 currently hard-codes `approved=[]`, `RESEARCH_ONLY` and `INDEPENDENT_APPROVAL=NOT_PROVEN`, but the repository-wide downstream consumer search remains incomplete. `risk_of_ruin` sums unvalidated trade returns.

## Added source-level regression

`mind_trader/tests/security_review/test_et665_r246_p1525_runtime_integrity.py`

1. Forged upstream independent approval and certification alongside 50 profitable synthetic trades must not certify the actual persisted manifest or reconstruction JSON.
2. A malformed synthetic trade return must raise `TypeError` or `ValueError` before creating a certification JSON. This covers one malformed-data path, not a general validation guarantee.

Both tests use a temporary working directory and mocked reconstruction. They do not connect to MT5, a broker, Drive or the network.

## Evidence limits

`TESTS_PUBLISHED_NOT_EXECUTED`. No CI PASS, isolated Docker run, process/network isolation proof, independent sign-off, R113 integration, R60 reconciliation, MT5 certification, or HP19 functionality is claimed.

Run in an approved offline sandbox:

```bash
python -m unittest discover -s mind_trader/tests/security_review -p 'test_et665_r246_p1525_runtime_integrity.py' -v
```

Keep actual stdout/JUnit, environment details and SHA-256 evidence before certification. No merge; no production; `REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0`.
