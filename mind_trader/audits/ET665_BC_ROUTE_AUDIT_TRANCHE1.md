# ET665.BC — Route audit, tranche 1 (source-grounded)

Date: 2026-11-06. Inspected ref: `37b363a0316769097a551c787513d2bbb7f08254`. No runtime execution or live order was performed.

## Confirmed
- `app/execution/gateway.py`: mode gate recognizes PAPER/REPLAY/MICRO_SIM, blocks explicit live modes and unknown modes. PAPER broker acceptance requires both `PAPER_ORDER_ACCEPTED` and `fill.filled is True`. Broker call occurs only in PAPER mode after checks.
- `app/execution/paper_broker_adapter.py`: routes to `simulate_fill` and local JSONL; rejects invalid payload, invalid FTMO cost config and failed fill; no direct real broker send in this module.
- `app/execution/safe_broker_adapter.py`: `blocked_send_order` invokes the institutional lock and returns a blocked result.
- `app/security/institutional_live_lock.py`: explicit research allowlist and unknown-action deny; redacts raw payload in lock audit; report-write errors handled as blocked.

## Additional finding
- The PAPER broker ledger stores the full `order` object, although this path is simulated. Classify and sanitize fields before publishing evidence; do not publish unreviewed logs.
- `paper_route_order` accepts a caller-supplied `broker` label and manually supplied cost values when no FTMO config is provided. This is not proof of live routing, but requires contract/entrypoint and cost-model review.
- The historical names `p74_mt5_demo_order_router_dry_run.py` and `p75_mt5_demo_order_execution_controlled.py` were not found at guessed `mind_trader/app/execution/` paths at this ref. Their actual paths must be resolved from the operator's ET665.AY CSV or a verified repository inventory.

## Scope limits and remaining gates
- The operator reported 74 textual execution references in ET665.AY; this document does not claim all 74 are semantically audited. The original `EXECUTION_ROUTES.csv` is required to map every match to exact repository path, line and disposition.
- ET665.BB: operator reported 45/45 PASS and five hashes verified at the exact patch commit; JUnit/log/hash files remain local, not directly inspected or published to GitHub.
- Perform source-to-source route graph, import-time effects and negative network/broker execution tests; publish sanitized artifacts and obtain independent review.

`PHASE_B=OPEN`; `SECURITY_APPROVAL=NOT_GRANTED`; `REAL_ORDERS=FORBIDDEN`; `MAIN=UNCHANGED`.
