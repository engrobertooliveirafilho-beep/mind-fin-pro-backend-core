# ME-RS-063 — R7 approval lineage reconciliation (2026-11-08)

## Evidence supplied from isolated Windows execution
- Original executor: `D:\\MIND_TEMP\\MIND_POST_R6_ACTIVE\\code\\engineering_pipeline\\post_r6.py`
- Original SHA-256: `58e559debb6181b4a34f857572a3fd1c84f1994def82637ad696106aaecd9d63`
- ME-RS-056: 127,004 records; full source hash/cursor match; SQLite integrity OK.
- ME-RS-060: incremental resume and replay PASS on a three-record sample.
- ME-RS-061: 8/9 approval checks PASS; post-ingestion mismatched approval did not raise.
- ME-RS-062: mismatched late approval left existing record PENDING, no exception; valid approval PASS.
- ME-RS-063: mismatched approval **at ingestion** raised `APPROVAL_LINEAGE_MISMATCH`, transaction left 0 records; clean ingestion 2 PENDING; original files unchanged.
- ME-RS-063 report SHA-256: `dc344cb351c9d5f9c41a1d40eea8164e1a7272271c5870c51354d1f79c399be3`.

## Finding and gate
The original executor enforces lineage on new-record ingestion. Late approvals against an already-persisted PENDING record are silently ignored when lineage differs. Silent ignore preserves safety but is not an explicit fail-closed rejection. **Do not certify approval reconciliation or R4→R8 synchronization.**

## Required minimal correction
1. Recover the exact original executor bytes, verify SHA-256, and compare with GitHub canonical authority before proposing any patch.
2. In the existing-PENDING approval reconciliation path, reject an approval referencing the same `r6_sha256` but a mismatched `r4_sha256` or `r5_sha256` with `APPROVAL_LINEAGE_MISMATCH`, before any UPDATE/COMMIT.
3. Preserve cursor, transaction atomicity, legitimate approval/replay semantics, and the new-ingestion guard.
4. Execute isolated tests for both mismatched-new and mismatched-existing approval, valid approval, replay, crash/rollback, and no mutation of originals.
5. Only then reconcile R8 canonical executor/checkpoint authority and integrate.

## Scope
This commit records the issue and adds a reproducible offline regression harness. It does not claim to patch the original executor or run tests in GitHub CI. No production activation, real orders, cloud spend, or Drive mutation is authorized.
