# ET665.R201 — Operator-approved Docker image identity (2026-11-08)

R200 pinned execution to the inspected local image ID, but any locally available image matching the mutable tag could still be used without independent authorization. R201 requires `ET665_EXPECTED_IMAGE_ID=sha256:<64 lowercase hex>` and rejects missing/malformed IDs before evidence creation. After resolving the local tag, the script rejects any mismatch between the actual image ID and the separately approved expected ID.

The expected image ID must come from an independent, trusted image approval process, not merely from copying the output of `docker image inspect` in the same run. SHA matching proves identity equality, not safety of the image contents.

This is a source-only patch published to draft PR #17. No Docker execution, pytest approval, merge or production mutation. R60 Drive/GitHub reconciliation and HP19 executor certification remain open.

`R201=PATCH_PUBLISHED | DOCKER_TESTS=NOT_EXECUTED | PHASE_B=OPEN | MAIN=UNCHANGED | PRODUCTION=UNTOUCHED | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0`
