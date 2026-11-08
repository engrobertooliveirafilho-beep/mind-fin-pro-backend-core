# ET665.R186 — Dependency gates and isolated regression consolidation (2026-11-08)

## Authority and scope
Based on authenticated GitHub inspection of draft PRs #10–#13 and direct source reads from the R185 head `c67254469136349423eb68c1674f66231a38a8c7`. Repository-wide inventory remains partial (truncated tree). No approval for execution, release, merge or real orders.

## Implemented in isolated branch
1. P13.8: MT5 admission denial occurs before report creation; Profit/FTMO CSV probes no longer create incoming folders.
2. P13.9: `run()` delegates directly to the existing unconditional MT5 denial before report creation. Standalone `write_csv()` remains an untrusted helper and is not certified.
3. P13.10: distinguishes minimum schema/row count from authenticity; `certified=False`, `provenance_verified=False`, `chronology_verified=False`, `canonical_manifest_reconciled=False`, and source `UNVERIFIED`. Manifest reports zero certified until independent evidence exists.
4. P15.15: disables promotion of `dataset.certified` from prior reports; queue stays empty pending independent canonical hash/manifest verification.
5. Six focused R186 regression cases added; NOT EXECUTED at publication. Independent execution must collect JUnit, stdout/stderr, code SHA-256 and observed network/process isolation.

## Dependency matrix
| Gate | Evidence | State |
|---|---|---|
| R180 dataset path safeguards | 24 scenarios authored | NOT_EXECUTED |
| R182 subprocess allowlist | 12 scenarios authored | NOT_EXECUTED |
| R183 pipeline subprocess allowlist | 12 scenarios authored | NOT_EXECUTED |
| R184 structural status checks | 4 scenarios authored | NOT_EXECUTED |
| R186 pre-side-effect admission and provenance | 6 scenarios authored | NOT_EXECUTED |
| R60 original Drive manifest reconciliation | Original authoritative manifests unavailable | BLOCKED |
| OS/network isolation | No independent offline evidence | BLOCKED |
| Main branch technical protection | R185 reports protected=false | GOVERNANCE_RISK |
| Independent review and Fase B certification | Not completed | BLOCKED |

## Required offline execution
Run `python -m pytest -q mind_trader/tests/security_review/test_et665_r186_dependency_gates.py` in pre-approved offline Docker sandbox with network disabled and no production credentials. Then execute existing R180/R182/R183/R184 suites under the same isolation, collecting reproducible logs. No tests were executed by this publication.

## Non-claims
Fail-closed guards are source-level controls, not proof of global isolation. P13.10's file SHA alone is not a verified provenance manifest. R186 is a proposed review change only; upstream callers and compatibility remain to be checked. No real MT5 account or broker should be used for tests.

`R186=PROPOSED | PHASE_B=OPEN | TESTS=NOT_EXECUTED | MAIN=UNCHANGED | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0.00`
