# P2614 audit and Monte Carlo hardening — 2026-11-21

Repository: `engrobertooliveirafilho-beep/mind-fin-pro-backend-core`
Branch: `engineering/p2614-replay-failclosed-20261120`
Base revision: `0104a8b19b7845bbe32f5b71aad97986a4575e09`

## Recovered lineage
Drive folder `p2614_real_fill_replay` contains the six-module replay package: loader, features, execution, replay, audit, montecarlo, plus package initializer. The same seven-file package appears in multiple Drive folders with matching file sizes and modification timestamps. The repository branch already contains the P2614 chronology and fail-closed changes, so this patch extends that branch rather than rebuilding the engine.

## Corrections
- `audit.py`: malformed/non-dict records, missing fields, boolean/negative indices, invalid edge IDs, non-finite numbers, duplicate trades and unsafe real-execution flags now return explicit failures rather than raising incidental KeyError/TypeError.
- `montecarlo.py`: validates capital, risk, run count and trade records; rejects NaN/Infinity and invalid runs; handles empty samples; bounds percentile indices.

## Tests
Executed locally against the recovered branch replay/execution code and the updated audit/Monte Carlo modules:
`PYTHONPATH=. pytest -q` → **27 passed**.
Coverage: existing chronology, no-overlap, PAPER-only, invalid risk parameters, unknown strategy/direction and cost/index gates; plus 10 new audit/Monte Carlo hardening cases.
This is isolated unit/regression evidence using deterministic test fixtures. It is NOT a historical GER40 replay, market-data certification, FTMO certification, or end-to-end runtime certification.

GitHub Actions for the base branch had failed in workflow `.github/workflows/r338-drive-recovery.yml`; that workflow failure is separate from this local pytest result. No CI PASS is claimed.

`PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | MAIN=INTACTA | PRODUCTION=INTACTA | E2E_CERTIFIED=FALSE | COST=R$0`
