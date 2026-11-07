# ET665.MB.R17 — Residual route source reconciliation after 253/253 PASS

Date: 2026-11-07. Authenticated GitHub source inspection of branch `audit/et665h-paper-ci-security-review-20261106`, after R16. This is a targeted reconciliation, not an exhaustive inventory. No code was executed, no broker connected, and no historical Drive content modified.

## Current-source findings

| Route | Prior concern | Current source evidence | Classification |
|---|---|---|---|
| `mind_trader/app/p1621e_real_video_fetch_loop/engine.py` | `yt-dlp` subprocess and external video network | Both `fetch_metadata` and `run` immediately raise `ET665_BR_EXTERNAL_EXECUTION_DISABLED_PENDING_SECURITY_REVIEW`. | **BLOCKED_BY_SOURCE**; reachable caller/import audit outstanding |
| `mind_trader/app/p1622_autonomous_daily_research_cron/engine.py` | Arbitrary module subprocess pipeline | `run_module` and `run` immediately raise the same ET665_BR guard; PIPELINE is only a declaration. | **BLOCKED_BY_SOURCE**; alternative invocations outstanding |
| `mind_trader/app/p75_mt5_demo_order_execution_controlled/engine.py` | `sent_to_mt5_demo` misleading claimed send | `EXECUTION_ARMED=False`, `sent_to_mt5_demo=False` unconditionally; `permission_granted` separate, no transport in this file. | **SIMULATION_ONLY_SOURCE**; dependencies not fully audited |
| `mind_trader/app/p86_execution_intelligence_domain/engine.py` | `mt5.initialize` / terminal and account reads | `mt5_snapshot()` raises `ET665_BJ_MT5_CONNECTIVITY_DISABLED_PENDING_SECURITY_REVIEW` before any MT5 call; `run()` calls it before writing module reports. | **BLOCKED_BY_SOURCE**; other MT5 routes not covered |
| `mind_trader/app/validation/promotion_authority.py` | Unknown target accepted as PAPER promotion | `ALLOWED_TARGETS=frozenset({"PAPER"})`; non-string/unknown target rejected before validation result. | **PAPER_ALLOWLIST_SOURCE**; full caller validation outstanding |
| `mind_trader/app/p1621f_transcript_download_strategy_extraction/engine.py` | `yt-dlp` and unverified transcript evidence | R1 audit reports ET665_BR guard; **not re-fetched in this R17 pass**. | **PRIOR_REVIEW_ONLY**; verify exact current blob |

## Residual risk and gates

- Source-level hard stops are valuable but do **not** certify all reachable paths, import side effects, dynamic invocation, other subprocess APIs, MT5 access routes, or transitive dependencies.
- The historical inventory of 74 textual route occurrences is not a complete semantic execution graph. Do not claim 74/74 reviewed or global route coverage.
- The 253/253 regression suite and independent evidence ZIP integrity PASS remain valid **for tested commit** `d7bf41752d86ffef59cd18d5a93583d35f94dba0`. This document-only commit is not part of that test run.
- No security certification and no Phase B release.

`FOCUSED_REGRESSIONS=PASS`
`ARTIFACT_INTEGRITY=PASS`
`RESIDUAL_INVENTORY=PARTIAL_NOT_CERTIFIED`
`SECURITY_APPROVAL=NOT_GRANTED`
`PHASE_B=BLOCKED`
`REAL_ORDERS=FORBIDDEN`
`FTMO_REAL=FORBIDDEN`
`MAIN_MERGE=BLOCKED`
