# Institutional wiring — static source discovery safety correction

Date: 2026-11-21
Branch: `engineering/agents-dispatch-fix-20261121`

## Correction
The previous discovery path imported every listed module and called its `health()` callback. Even without calling `run()`, Python module imports and health callbacks can execute arbitrary side effects. The wiring now parses source with Python AST and does not import or invoke the discovered modules.

- Source: `app/runtime/mind_trader_institutional_wiring.py`
- Git blob: `103a3c50b06693cd7a9872a3f286a7153836cb30`
- Test: `tests/test_institutional_wiring_discovery_only.py`
- Git blob: `110d86bb265c9b465e2f9c85e656dc0a0234ec16`
- Commits: `bfaa97285cba622dc58b812813d1b7011a2780e8`, `351b2209850a69c49da3f197e602757823c70f04`
- Tests added/updated: five offline unit cases for AST-only inspection, no import/execution, missing source, invalid Python syntax, invalid payload, and static health status.

## Certification
The code and tests were read back from GitHub after publication. **The five tests have not been executed** in this interaction. No PASS is claimed. GitHub Actions execution was not available through the connected action set in this session.

## Historical source reconciliation
The Drive remediation ledger (2026-10-29) was re-read. Its ET-026 records a historical PAPER/backtest technical-readiness PASS dated 2026-09-14, explicitly not a real FTMO evaluation. ET-019 remains a suspected ExecutionV4 MTM/atomicity defect, not a reproduced bug. Exact ExecutionV4 source and the later final repair/test matrices were not found by the targeted Drive and repository searches performed in this pass; therefore no speculative patch was applied to that engine.

`PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | MAIN=INTACTA | PRODUCTION=INTACTA | E2E_CERTIFIED=FALSE | COST=R$0`
