# ET665.R370 — P2405/P2614 provenance and integration gate

Source: Drive `DOSSIE_AUDITORIA_PROFUNDA_TRADER_CHAT_P2405_P2614.pdf`, file ID `1pvOfy3eEIXkqyEnAp4UNAz_Y-mN0uht6`, historical source updated 2026-08-04. This document is a narrative audit, **not** the executable P2405 contract.

## Recovered historical sequence
- P2405–P2408: Edge Pool, Risk Engine, Edge Factory, Walk Forward, Ensemble, Router and Paper integration repairs.
- P2409–P2415: historical Paper Stack certification claims.
- P2601–P2610: Edge Research Platform.
- P2611: GER40 laboratory.
- P2612: deterministic replay, USD 100 initial capital.
- P2613: bias hardening.
- P2614: modular replay design with loader.py, features.py, execution.py, replay.py, audit.py and montecarlo.py.
- Explicit prohibition: PAPER_ONLY, REAL_ORDERS=FORBIDDEN, FTMO_REAL=FORBIDDEN.

## Integration boundary
R367–R369 use synthetic fixtures and **do not** establish compatibility with P2405 or P2614. Historical P2405 runnable source, authoritative API contracts, execution evidence, and regression fixtures have not yet been reconciled with the current isolated branch. Never replace existing historical implementation with experimental modules.

## Required next gates
1. Recover exact historical P2405 source paths and SHA256 from Drive/GitHub and authoritative manifest.
2. Verify historical input/output contracts and timestamp conventions, without modifying originals.
3. Adapt historical replay loader to R367 split in an isolated adapter; assert no leakage.
4. Compare historical PAPER fills to simulated R367/R368 results with documented differences.
5. Run offline Docker tests with actual historical fixtures and preserve hashed logs.
6. Reconcile HP19 original roster and advertised contracts independently of 19 cashflow candidates.
7. Obtain independently authenticated approval per each of 16 Phase B fronts.

**Status:** P2405_CONTRACT=NOT_RECOVERED | P2614_SOURCE=NOT_RECONCILED | HP19_OFFICIAL=NOT_CERTIFIED | PHASE_B=NOT_CERTIFIED | MAIN=UNTOUCHED | COST=R$0.
