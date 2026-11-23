# R816 — Disable unsafe active capability probes

Date: 2026-11-22

## Baseline reconciliation
- R815 branch already changed the default report to passive, but `execute_probes=True` still imported modules, invoked arbitrary synchronous functions, and instantiated classes.
- Historical HP19 recovery R812, isolated R811/R814 contracts, and STEP inventories were not repeated.
- Current accessible source: `engrobertooliveirafilho-beep/mind-fin-pro-backend-core`; the separate `mind-fin-pro-org/mind-platform` could not be accessed via connected GitHub API.

## Change on isolated branch
- Updated original `app/runtime/capability_recovery_bridge.py` so `capability_recovery_report()` never performs active probes, even if `execute_probes=True`.
- Explicitly reports `mode=declared_only`, `active_probe_allowed=False`, `functionally_certified=0`, and `certification=not_tested` per module.
- Preserved legacy helper function definitions for compatibility, but these helpers themselves remain capable of active imports/calls if invoked directly; their direct call sites need a separate audit.
- Updated the prior R815 test that previously expected explicit active opt-in.
- Added a separately tested, import-free passive implementation and tests in `src/revisions/r816/`.

## Evidence
- Local isolated Python pytest: **10/10 PASS** in 0.04 s.
- Isolated local source SHA-256: `37ad20cc54c6f32fc8a4aed28116ffeb5ecf84f0032cf01bdb60626b71fce9b4`.
- Isolated local tests SHA-256: `1023bd1241c94033fa8718934f91db9a13fe9c6ecdf02df16b8cd7e7246a99c8`.
- Published GitHub files read back: **4/4**.
- Static integration checks on original source and test update: **6/6 PASS**.
- **Not claimed:** integrated Python regression, production E2E, deploy, HP19 functional certification.

## State
`R816=ISOLATED_TESTS_10/10_PASS | INTEGRATED_STATIC_6/6_PASS | INTEGRATED_PYTHON_PENDING | MAIN_INTACT | COST_R$0`
