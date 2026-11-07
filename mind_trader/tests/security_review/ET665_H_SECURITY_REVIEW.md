# ET665.H — Security review gate (not approved)

Status: **REVIEW_REQUIRED**. Do not dispatch, merge, or enable the workflow.

## Scope
Historical test modules: P846, P847, P848, P849, P895, P896, P897, P898, P899.
Canonical package: `mind_trader`. Existing runtime is not certified.

## Current evidence
- ET665.D: nine files inventoried; zero matches in limited static pattern scan.
- ET665.E: 16 files copied and hash matched locally; transitive imports unresolved.
- ET665.G: Docker engine unavailable; no pytest run.
- GitHub source inspection: gateway depends on engines/core, engines/regime_detection, validation/adversarial_ai; regime_detection imports backtest/market_core.
- Gateway risk: reports ACCEPT_SIMULATED_ORDER when pre-route checks pass without asserting broker PAPER decision == PAPER_ORDER_ACCEPTED.
- FTMO default costs: spread/slippage/commission are zero, not representative of live costs.

## Mandatory security review before enabling
1. Establish complete transitive import graph, including import-time side effects.
2. Confirm no real broker/network route, credentials, environment secrets, privileged mounts, or external callbacks.
3. Provide an offline execution environment (not a network-enabled GitHub-hosted runner) with verified Python and pytest artifacts and no dependency download.
4. Pin all runtime dependencies and runner image by immutable digest; verify provenance and zero-cost entitlement.
5. Ensure repository is read-only, artifacts written only to a scratch directory, and no external access.
6. Add negative regression: if PAPER broker rejects/fill fails, gateway must never report accepted.
7. Test missing/invalid FTMO config, positive nonzero transaction costs, session risk and live lock.
8. Compare SHA-256 against canonical source and retain test output/JUnit, hashes, environment manifest.
9. Review workflow permissions, event triggers and untrusted input exposure.

## Decision
CI_EXECUTION=NOT_STARTED
PHASE_B=OPEN
REAL_ORDERS=FORBIDDEN
MERGE=BLOCKED
