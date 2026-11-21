# P2614 isolated replay regression — 2026-11-21

Repository: `engrobertooliveirafilho-beep/mind-fin-pro-backend-core`
Branch: `engineering/p2614-replay-failclosed-20261120`

## Drive recovery
Recovered the P2614 package from Drive: loader, features, execution, replay, audit, Monte Carlo and package initializer. Also recovered the P2400/P2404/P2405C/P2405E source lineage and their regression tests. Historical certificates remain historical; no claim of current end-to-end replay is made.

## Corrections
- Audit rejects malformed records, invalid indices, unsafe real flags, non-finite numbers, duplicate trades, PnL/equity inconsistencies and broken capital chains.
- Monte Carlo changed from permutation-only to seeded bootstrap sampling with replacement. Permutation-only sampling did not vary the observed R distribution; in a multiplicative model, shuffled final equity is order-invariant, making prior final-equity percentiles misleading.
- Existing execution remains a fixed-horizon close proxy, not intrabar stop/target fill simulation. It is explicitly NOT certified as a real-fill engine.
- Loader still needs strict row rejection, duplicate/monotonic timestamp validation and timezone/session normalization.
- P2405C best configuration was blocked: PF 1.414763 and max DD 21.982572R, below PF 1.5 and above hard DD 18R.

## CI evidence
Dedicated GitHub Actions workflow run: `44930224203`, commit `efbd9b92a29583a881629ba33ff0fee2e3bb21df`.
Result: **38 tests passed**, workflow conclusion `success`.
This run covered P2614 chronology/fail-closed/audit/Monte Carlo and Trader.1.001 static exporter safety tests. P2923 was added in a later commit; workflow run `44930924216` passed **48/48 tests**, including P2923 block-bootstrap/regime gates.

`PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | MAIN=INTACTA | PRODUCTION=INTACTA | E2E_CERTIFIED=FALSE | COST=R$0`
