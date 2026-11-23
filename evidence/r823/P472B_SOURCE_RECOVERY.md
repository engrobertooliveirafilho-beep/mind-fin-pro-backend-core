# R823 — P4.72B original source recovery and historical test reconciliation
Date: 2026-11-22

## Original source recovered from GitHub repository tree
- `app/runtime/staging_v2/execution/tests/test_p472b_capability_recovery_bridge.py`, blob `750bad8faeffbe6ff9a281b5146490aca0cb815f`.
- `app/runtime/staging_v2/memory/_evidence/P4_72B_TOP5_CAPABILITY_BRIDGE_20260618_194507/capability_recovery_bridge.py`, blob `8c20ed03bfe838bfafd94e7fd2eedfe9fc9e5775`.
- `app/runtime/staging_v2/execution/_evidence/P4_72B_TOP5_CAPABILITY_BRIDGE_20260618_194507/p472b_smoke.py`, blob `ebf7550e341413aa72e90d43ea20666ada132631`.

## Original behavior confirmed
The two historical tests explicitly assert `import_ok >= 5` and `with_successful_calls >= 1`. The original P4.72B implementation imports all five modules and invokes memory functions `social_memory_report`, `store_social_memory`, `retrieve_cognitive_memory` or instantiates `RetrievalProvider` and `AdaptiveSocialDialogue`. The `_safe_call` wrapper records `ok=True` when a callable merely returns a coroutine object; it does not await the coroutine or verify completion. This explains the risk evidenced by R822 logs reporting unawaited `memory` and `memory_runtime` coroutines, though the specific coroutine provenance is not established without runtime tracing.

## Security and compatibility
Do NOT execute historical P4.72B tests against the hardened R817 report. Their assertions require precisely the active behavior intentionally blocked in R815–R817. Preserve original staging files read-only and treat them as historical evidence, not live-certified capabilities.
The original smoke script includes a user-identifying WhatsApp number; do not run it or reproduce that identifier in reports.
This recovery supersedes R821–R822's earlier `historical test source unavailable` finding.

## Certification boundary
3/3 original files fetched from GitHub and their blob IDs recorded. No new Python tests executed in R823, no current consumer audit, no active probe, no merge or production mutation.
`R823=3/3_SOURCE_RECOVERED | HISTORICAL_TESTS_RECONCILED | E2E=FALSE | MAIN=INTACT | COST=R$0`
