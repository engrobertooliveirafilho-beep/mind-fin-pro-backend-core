# P2614 audit and Monte Carlo hardening — 2026-11-21

Repository: `engrobertooliveirafilho-beep/mind-fin-pro-backend-core`
Branch: `engineering/p2614-replay-failclosed-20261120`
Base revision: `0104a8b19b7845bbe32f5b71aad97986a4575e09`

## Recovered lineage
Drive folder `p2614_real_fill_replay` contains six replay modules: loader, features, execution, replay, audit and montecarlo, plus package initializer. Six Drive folder copies were found; five nonempty copies expose the same seven filenames, byte sizes and modification timestamps. The repository branch already contains P2614 chronology and fail-closed changes, so this patch extends the existing branch instead of rebuilding the engine.

## Corrections
- `audit.py`: malformed records, missing fields, boolean/negative/unhashable bar indices, invalid edge IDs, non-finite/overflow numeric values, duplicate trades and unsafe real-execution flags now return explicit failures rather than incidental exceptions.
- `montecarlo.py`: validates capital, risk, run count and trade records; rejects NaN/Infinity/overflow and invalid runs; handles empty samples; bounds percentile indices.

## Tests
Local deterministic regression harness: `PYTHONPATH=. pytest -q` → **30 passed**.
Coverage: existing P2614 chronology, no-overlap, PAPER-only, invalid risk parameters, unknown strategy/direction and cost/index gates; plus 13 audit/Monte Carlo hardening cases.
The local harness was assembled from the recovered branch logic and these revisions; it is unit evidence, not an independent clean checkout run. It is NOT a historical GER40 replay, market-data certification, FTMO certification, or end-to-end runtime certification.

GitHub Actions has no P2614-specific test workflow on this branch. The only listed workflows are `build-runpod-worker.yml` and `r338-drive-recovery.yml`; the latter is a Drive recovery workflow, not a P2614 test suite. No CI PASS is claimed.

## Remaining replay limitations
- `execution.py` still estimates R from next-bar open to a fixed-hold close and clamps R to preset bounds; it does not simulate intrabar stop/target fills.
- `montecarlo.py` still permutes the observed trade sequence; it is not bootstrap resampling or parameter/slippage stress.
- `loader.py` silently skips malformed rows and does not certify unique, strictly increasing timestamps or timezone/session normalization.

These remain blocked from runtime promotion until corrected and replayed against the canonical GER40 dataset.

`PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | MAIN=INTACTA | PRODUCTION=INTACTA | E2E_CERTIFIED=FALSE | COST=R$0`
