# ET665.R25 — Receipt of R24 offline triage

Operator-provided PowerShell output, 2026-11-07; input HEAD `26417fd33f5759b3081820c1976bab21a922a311`.

- Tracked/analyzed Python files: 37,784/37,784.
- `parse_failures=38` (corrects the earlier assistant's erroneous count of 39).
- Priority files: 3,857; semantic review `NOT_CERTIFIED`.
- Scopes: OTHER_REPOSITORY 26,892; QUARANTINE_REVIEW_REQUIRED 7,593; TRADER_MIRROR_CANDIDATE 2,127; HISTORICAL_REVIEW_REQUIRED 672; TRADER_ACTIVE_CANDIDATE 500.
- Kind counts: dynamic 7,989; filesystem 262; mt5 163; network 3,574; process 783; parse failure 38; MT5_TOKEN 41; ORDER_CHECK_TOKEN 5; ORDER_SEND_TOKEN 5; PROCESS_INVOCATION 758; RCLONE_TOKEN 178; SHELL_TRUE_TOKEN 47; URL_TOKEN 25,348.
- Input inventory SHA-256 `c85ca57f7ce4d0365115476bb00029debb40fa24c06fc0b3a01fb71b9dfa2f62`.
- `triage_summary.json` SHA-256 `6408a7e5debe2c34f2b13756192544337d614d4352da1ca93a174addae5e688f`.
- `parse_failures.json` SHA-256 `4afb6ec73411384be3f7371d047d00a283ab5b1323e3eb1490091ea21a96b4c0`.
- `priority_routes.json` SHA-256 `3db6c3c452a37d5ef30d220b8aff14d8ab3aee40f25d4aec951aee3b79437420`.
- Triage path provided by operator: `D:\\MIND_T~1\\SYSTEM~1\\ET665_R24_TRIAGE_20261107_203701`.

The scanner covers tracked Python blobs at the pinned HEAD, not necessarily executable entrypoint reachability, all file types, external dependencies, or untracked sources. Regex token counts are not confirmed calls. Scope classification by path is provisional, not proof of quarantine or lack of reachability.

`PYTHON_TREE_ENUMERATION=PASS`
`R24_TRIAGE=PASS`
`SEMANTIC_ROUTE_REVIEW=NOT_CERTIFIED`
`PHASE_B=BLOCKED`
`REAL_ORDERS=FORBIDDEN`
`FTMO_REAL=FORBIDDEN`
