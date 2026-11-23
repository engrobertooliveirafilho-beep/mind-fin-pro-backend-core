# R815 — Capability recovery probe fail-closed
Date: 2026-11-22
Target: engrobertooliveirafilho-beep/mind-fin-pro-backend-core, main base, isolated branch engineering/r815-safe-capability-probe-20261122.
Historical R809-R814 corrections and HP19 recovery are preserved, not repeated.
Original main file app/runtime/capability_recovery_bridge.py blob SHA 75086cfbd78064001f9bd6cd83245d14ceb65dd0.
Finding: capability_recovery_report() imports TOP5 modules, invokes discovered synchronous functions, and instantiates classes by default; this is an active execution probe, not passive inspection.
Change in original file on isolated branch: default execute_probes=False returns a static inventory without imports or calls; only literal True enters the legacy active probe. Explicit opt-in remains potentially side-effectful and must not be used in production without further isolation.
Regression tests added in tests/test_r815_capability_probe_safe.py. GitHub publication and source reread verified. Static source assertions were executed through the connected GitHub read; Python test execution is not yet evidenced. No runtime/E2E certification claimed.
No main mutation, merge, deployment, API purchase, or production calls.
MAIN=INTACT | STATIC_GATE=VERIFIED | PYTHON_TESTS=NOT_EXECUTED | E2E=FALSE | COST=R$0
