# ET665.BV — Internal security continuation (no independent review)

Date: 2026-11-06
Source branch: `audit/et665h-paper-ci-security-review-20261106`
Inspection scope: `mind_trader/app/execution/gateway.py`, `mind_trader/app/p11_evidence_promotion_gate/engine.py`, `mind_trader/tests/security_review/test_et665_br_external_process_gate.py`.
Method: direct source inspection via authenticated GitHub connector; **no tests executed in this step**.

## Verified code properties

1. Gateway accepts only `PAPER`, `REPLAY`, `MICRO_SIM`; known live modes invoke institutional live lock, unknown modes are blocked.
2. PAPER accepted status requires broker decision `PAPER_ORDER_ACCEPTED` and `fill.filled is True`; nonaccepted or unfilled broker results reject.
3. Gateway output marks `production=BLOCKED`, `real_broker_routing=DISABLED`.
4. P11 promotion result explicitly fixes `live_promotion_allowed=False`, `real_broker_allowed=False`, `ftmo_real_allowed=False`.
5. ET665.BR tests cover three external process modules with AST checks and fail-closed runtime entrypoints.

## Newly identified coverage gaps / next tests

- **BV-01:** `submit_order` checks `mode in LIVE_MODE_TO_ACTION` before type validation. An unhashable mode (e.g. list/dict) can raise `TypeError` instead of producing a blocked ledger event. No live-order bypass is established; robustness and audit logging need regression.
- **BV-02:** `trade_dict`, `regime_report`, and `genome` are used with dictionary operations without early shape checks; malformed inputs may raise before writing a rejection ledger event. Confirm behavior and add fail-closed handling with tests.
- **BV-03:** `REPLAY` and `MICRO_SIM` may return `ACCEPT_SIMULATED_ORDER` without PAPER broker fill; clarify simulated acceptance semantics and test they never invoke broker routing.
- **BV-04:** BR test AST check only detects direct `subprocess` import/calls; does not prove absence of all alternate process invocation APIs. Broaden bounded static scan before considering full closure.

## Policy decision

User elected **not** to perform independent review. This is a documented scope decision, **not** a security sign-off. Replace independent-review handoff as a mandatory workflow step with internal code review, reproducible tests, and evidence. No claim of independent certification or approval.

`SECURITY_APPROVAL=NOT_GRANTED`
`PHASE_B=OPEN`
`REAL_ORDERS=FORBIDDEN`
`FTMO_REAL=FORBIDDEN`
`MAIN_MERGE=BLOCKED`
