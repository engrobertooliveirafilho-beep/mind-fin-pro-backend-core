# MC-R294 — Hardening dispatch and research output validation
Date: 2026-11-10

## Changes
- Scheduler rejects NaN/infinite latency or weight, booleans masquerading as numeric values, and roles outside the Step450 contract. Deterministic capacity/latency-aware placement retained.
- Research adapter now invokes an explicitly configured provider and validates every result: non-empty title/snippet/source and HTTPS source URL. Stub URLs, missing provenance, empty query and provider exceptions fail closed; no synthetic fallback.
- These remain isolated modules; canonical Step450/452 runtime routers are not modified or wired.

## Tests
11/11 Python unittest PASS locally against exact source text mirrored from this branch: deterministic/capacity bounds, NaN latency, bool weight, invalid role, insufficient capacity, no provider, stub URL, missing provenance, provider exception, HTTPS result and empty query. Runtime: Python unittest; 0.001s.
- GitHub readback and CI status are separate gates; no remote CI PASS claimed.

## Outstanding
- HTTPS syntax alone does not prove source authenticity, relevance or that a provider actually fetched the page. Provider adapter still needs trusted connector implementation, allowlisted provenance and retrieval evidence.
- Need exact repository checkout CI and endpoint contract tests before runtime integration.
- Drive Master Ledger append still HTTP 403; report is GitHub-only pending synchronization.

No merge, deployment, main or production changes. R4 untouched. REAL_ORDERS/FTMO_REAL forbidden. Cost R$0. HP19/global certification BLOCKED.
