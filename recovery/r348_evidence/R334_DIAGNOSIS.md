# R348 — R334 recovery root-cause and safe correction proposal

Date: 2026-10-31. Branch: audit/r318-ftmo-evidence.

## Verified
- Existing workflow `.github/workflows/r334-drive-recovery.yml` references `recovery/r328_drive_zip/recovery_queue.jsonl` in both preflight and execution.
- GitHub contents API returned 404 for that path on the audit branch.
- `recovery/r328_drive_zip/queue_p0.jsonl` exists and lists ten P0 records, with `sha256_expected=null` for each.
- R334 Actions run 41231699285 has conclusion failure and no job records exposed by the jobs API. Thus the missing queue is a *code/configuration defect*, but is NOT conclusively the cause of the jobless Actions failure.
- R343 Actions run 41231592718, job 124626761543: 9/9 regression tests PASS.
- Historical P2363C seven dataset paths were identified in baseline sheet rows 1850-1856; bytes not yet recovered.

## Minimal patch (NOT APPLIED)
Change both workflow references from `recovery/r328_drive_zip/recovery_queue.jsonl` to `recovery/r328_drive_zip/queue_p0.jsonl`. Keep all other controls unchanged; do not weaken token validation or historical authority checks.

## Current gates
Workflow change was blocked by the connector's security controls, so do not claim it was applied.
CI_R343=PASS; R334_RECOVERY=FAILURE; ORIGINAL_DATASETS=0/7; HISTORICAL_SHA=0/7; PROMOTION=BLOCKED; FTMO_READY=FALSE; REAL_ORDERS=FORBIDDEN.
