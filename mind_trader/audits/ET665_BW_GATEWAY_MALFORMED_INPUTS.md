# ET665.BW — Gateway malformed-input fail-closed patch

Date: 2026-11-06
Branch: `audit/et665h-paper-ci-security-review-20261106`
Patch commit: `fcac1bf972e27e9a371bda046c32c8c00f3fb163`
Test commit: `fd76b7701a00492aed0fe89ea4fd8fb55c3a5739`

## Change
- `ExecutionGateway.submit_order` now rejects non-string `mode` values before set/dict membership operations, writes `BLOCKED_INVALID_EXECUTION_MODE_TYPE` to ledger.
- Rejects non-dict `trade_dict`, `regime_report`, or `genome`, writes `BLOCKED_INVALID_ORDER_INPUT_TYPE` to ledger.
- Both cases retain `production=BLOCKED`, `edge_claim=NONE`, and do not log malformed trade payload.
- Adds seven parameterized regression cases under `mind_trader/tests/security_review/test_et665_bw_gateway_malformed_inputs.py`.

## Verification status
Tests are **published but NOT YET EXECUTED**. Previous ET665.BS 55/55 PASS applies to an earlier commit and must not be attributed to the new HEAD.

## Remaining gaps
- Valid dictionary inputs with missing/invalid field values may still raise exceptions. Expand fail-closed validation in a separate bounded patch.
- Prove REPLAY/MICRO_SIM do not route to broker, and cover alternate process APIs.
- Re-run offline test suite, capture JUnit, hashes, and canonical commit evidence.

`PHASE_B=OPEN`
`SECURITY_APPROVAL=NOT_GRANTED`
`REAL_ORDERS=FORBIDDEN`
`FTMO_REAL=FORBIDDEN`
