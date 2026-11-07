# ET665.I — Verified transitive import closure (source inspection only)

## Gateway dependency chain
- `app/execution/gateway.py` → `app/engines/core.py`, `app/engines/regime_detection.py`, `app/validation/adversarial_ai.py`, `app/risk/ftmo_ruleset.py`, `app/execution/paper_session.py`, `app/execution/paper_broker_adapter.py`, `app/security/institutional_live_lock.py`
- `app/engines/regime_detection.py` → `app/backtest/market_core.py`
- `app/execution/paper_broker_adapter.py` → `app/execution/safe_broker_adapter.py`, `app/execution/paper_fill_model.py`, `app/risk/ftmo_ruleset.py`
- `app/execution/safe_broker_adapter.py` → `app/security/institutional_live_lock.py`
- `app/execution/paper_session.py` → `app/risk/ftmo_ruleset.py`

All above files were fetched and inspected on `audit/et651-paper-execution-chain-20261105`. Their visible top-level imports use Python standard library or the listed local modules. `pytest` remains a test-runner dependency. This is a **source-level dependency closure for this entrypoint only**, not a verified environment lockfile, a repository-wide dependency audit, or proof of import-time safety.

## Proven functional defect from source review
`ExecutionGateway.submit_order` sets `ACCEPT_SIMULATED_ORDER` whenever its upstream checks pass, regardless of the subsequent `paper_route_order` decision. The new negative regression `test_et665_i_gateway_broker_rejection.py` mocks the broker rejection and asserts fail-closed. It is **NOT RUN** and expected to fail against the inspected implementation.

## Gate
- SOURCE_DEPENDENCY_CLOSURE=REVIEWED_FOR_GATEWAY_ENTRYPOINT
- IMPORT_SIDE_EFFECTS=NOT_EXECUTION_VERIFIED
- PYTEST_RUNTIME=UNAVAILABLE
- REGRESSION_TEST=STAGED_NOT_EXECUTED
- SECURITY_APPROVAL=PENDING
- PHASE_B=OPEN
- REAL_ORDERS=FORBIDDEN
