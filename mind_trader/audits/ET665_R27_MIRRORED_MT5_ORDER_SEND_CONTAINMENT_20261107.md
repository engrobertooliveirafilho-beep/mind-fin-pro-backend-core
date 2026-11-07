# ET665.R27 — Confirmed mirrored MT5 bypass and source-level containment

Date: 2026-11-07. Inspected source directly through authenticated GitHub connector on the isolated audit branch.

## Confirmed divergence
- Canonical `mind_trader/reports/P78_DEMO_ORDER_SEND_SINGLE_CONTROLLED/p78_demo_order_send.py` does not import MT5 and only emits a blocked report.
- Mirror `products/eldora_trader/mind_trader/reports/P78_DEMO_ORDER_SEND_SINGLE_CONTROLLED/p78_demo_order_send.py` imported MT5, initialized the terminal and contained an executable `mt5.order_send(request)` after a DEMO/server check. This is a **potential order-transmission path**, not evidence of an actual order or demonstrated reachability in production.
- Canonical P77 has an unconditional first-statement PermissionError, while mirror P77 lacked it and performed `mt5.initialize` and `mt5.order_check`.
- Canonical P86 `mt5_snapshot` raises before terminal access, while mirror P86 lacked this guard and called `mt5.initialize`/position APIs.

## Containment published
- Mirror P78 `run` now immediately raises `PermissionError("ET665_R27_MIRRORED_MT5_ORDER_SEND_FORBIDDEN")` — commit `571921bb334fd4877b83525e99232cc9c7a5e2c3`.
- Mirror P77 `run` now immediately raises `PermissionError("ET665_R27_MIRRORED_MT5_ORDER_CHECK_FORBIDDEN")` — commit `07cbb0ba384813ceb3fdf4a994208f052b86ce97`.
- Mirror P86 `mt5_snapshot` now immediately raises `PermissionError("ET665_R27_MIRRORED_MT5_CONNECTIVITY_FORBIDDEN")` — commit `e7eb490c419fe64fafbb546043d869dcf7ccf46e`.
- Static regression `mind_trader/tests/security_review/test_et665_r27_mirrored_mt5_failclosed.py`, corrected Git root in commit `df2b1e20bb5caaba2fb1d48431b30f2d208dc59d`. **NOT YET EXECUTED**.

The original unsafe statements remain unreachable inside these functions, but this does not prove absence of other entrypoints, dynamic loading or other mirrored copies. No main merge, live orders or MT5 connection authorized.

`CONFIRMED_MIRROR_GAP=YES`
`R27_SOURCE_CONTAINMENT=PATCHED_NOT_TESTED`
`R27_REGRESSIONS=PENDING`
`SEMANTIC_ROUTE_REVIEW=INCOMPLETE`
`PHASE_B=BLOCKED`
`REAL_ORDERS=FORBIDDEN`
`FTMO_REAL=FORBIDDEN`
