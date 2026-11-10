# MC-R292 — Distributed and research engine audit
Date: 2026-11-10

## New original Drive sources recovered
- Step450 distributed agents: Drive file ID `1CKl3VQEU_FbNP1etA0o2eIx5-3P1psSr`.
- Step452 research agent: Drive file ID `1dAvIGw9wvY11NnoQ64LPDeSO7uYlDFfI`.
- Readable source snapshots preserved under `audits/hp19/r292/` for deterministic review.

## Verified source defects / limitations
- Step450 selects one maximum-score cluster per agent and sends every logical shard to that same cluster. It does not distribute load across clusters. Duplicate agent IDs also collapse in the intermediate dictionary; no unique-ID validation is visible in the recovered source.
- Step452 routes every mode (`web_stub`, `internal`, `hybrid`) through `_make_stub_results`; outputs use `stub://research` and synthetic text. It is not a real research engine and must not be presented as sourced research.

## Tests
- 4/4 local static AST contract assertions PASS against equivalent source patterns.
- Added repeatable unittest AST suite `test_recovered_engine_static_contracts.py` (4 tests) alongside preserved source snapshots. Exact GitHub checkout/CI execution has not yet been observed; therefore remote suite status remains PENDING.
- No production engine changed. No authority mapping proves these snapshots are the active canonical runtime modules.

## Next
Recover canonical router/engine authority, compare hashes and existing implementations; implement fair capacity/latency-aware placement and reject duplicate IDs only after contract approval; research engine must fail closed for unavailable real sources rather than synthesize citations/results. Then execute exact checkout tests and offline integration.

Master Ledger append still HTTP 403 (previous verified). This report remains GitHub-only pending sync. R4 untouched; main/production untouched; REAL_ORDERS/FTMO_REAL forbidden; cost R$0. HP19 and global certification remain BLOCKED.
