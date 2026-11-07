# ET665.MB.R4 — PAPER session integrity, source audit and test plan

Date: 2026-11-07. Authenticated GitHub source review; no local test execution, MT5, broker, CI, Drive write, deployment or merge.

## Finding
`PaperTradingSessionManager._read_session` formerly returned unvalidated JSON. Corrupt JSON, non-object payloads, missing keys, non-finite values, invalid counters and invalid `risk_amount` could raise exceptions before an explicit PAPER denial. `open_session` could replace a corrupt pre-existing session, destroying the audit boundary.

## Changes
- `3fba5936c325584b71b1179cb0d4105c8923d6bc`: validates persisted session structure and finite numeric limits; converts parse/read failure to invalid session; refuses opening a new session over an existing corrupt file; rejects malformed risk amounts.
- `8a53b1c681ece1c8ab6685e766a83d6f1ba11e3f`: 27 focused offline regression cases (6 corrupt payloads, 12 malformed fields, 8 invalid risks, 1 valid path), prepared but **NOT EXECUTED**.

## Remaining technical risk
- `_read_session` currently returns None for missing and corrupt sessions; the caller `pre_trade_check` denies both. `open_session` distinguishes corrupt pre-existing files and blocks.
- `record_trade_result` still accepts externally supplied `pnl` and performs arithmetic/float conversion without comprehensive validation; must be inspected and tested separately.
- Historical ET665.MB 50/50 PASS does not cover commits R2–R4.
- The 74-reference route inventory and all transitive entrypoints remain not fully certified.

## Gate
`R4_PATCH=STAGED_UNTESTED`
`R4_REGRESSIONS=27_PREPARED_NOT_EXECUTED`
`R2_R3_R4_NEW_TESTS=89_PREPARED_NOT_EXECUTED`
`HISTORICAL_MB=50_OF_50_VERIFIED_PASS`
`INDEPENDENT_REVIEW=WAIVED_BY_OWNER`
`PHASE_B=OPEN`
`REAL_ORDERS=FORBIDDEN`
`FTMO_REAL=FORBIDDEN`
`MAIN_MERGE=BLOCKED`
