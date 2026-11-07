# ET665.MB.R9 — Adversarial context fail-closed hardening and consolidated suite update

Data: 2026-11-07. Source inspection and GitHub publication only. No pytest, CI, MT5, broker, live execution, Drive write or main merge.

## Finding
`AdversarialValidationEngine` forwarded caller-provided mappings directly to four review agents. Malformed mapping types and non-finite numeric fields could raise exceptions or produce unreliable review outcomes (including arithmetic/division paths). The four agents now validate context types and finite numeric fields before analysis; invalid context produces a deterministic veto.

## Patch and regressions
- Patch commit: `0582fa167502ae4cbc5be8e00a0387a3a0641a2f`.
- Regression commit: `0ab742f4e00c52f27ceb21f735a3974a62c0941e`.
- 10 parameterized malformed-context cases prepared; **NOT EXECUTED**.

## Consolidated runner
- Commit: `d7f527d9f7c3a61f03777c692f74447195569b0c`.
- Runner: `mind_trader/security/et665_mb_r8_consolidated_runner.py`.
- Includes original 50 MB cases, R2 (20), R3 (42), R4 (27), R5 (14), R6 (54), R7 (7), R9 (10): **224 expected tests**.
- Exact count required; nonzero exit, missing JUnit, failures, errors, skips, or absent per-engine P15 cases cause BLOCKED.
- The prior 50/50 ZIP was verified on its earlier commit only. The 224-test consolidated suite is **not yet executed**.
- Runner does not itself enforce OS-level network isolation; run only in the existing isolated offline workspace, without broker credentials.

## Decision
`R9_PATCH=PUBLISHED_UNTESTED`
`R9_TESTS=10_PREPARED_NOT_RUN`
`CONSOLIDATED_EXPECTED=224`
`CONSOLIDATED_EXECUTION=PENDING`
`PHASE_B=OPEN`
`INDEPENDENT_REVIEW=WAIVED_BY_OWNER`
`REAL_ORDERS=FORBIDDEN`
`FTMO_REAL=FORBIDDEN`
`MAIN_MERGE=BLOCKED`
