# ET665.R200 — Immutable Docker image execution (2026-11-08)

Authenticated inspection found a runtime integrity gap in the R187–R199 offline harness: the script inspected the local image tag but ran the mutable tag later. The image could change between inspection and execution, and an image-supplied ENTRYPOINT could intercept the intended pytest command.

R200 resolves the image to its local sha256 image ID, validates the 64-hex format, records that ID and executes the same immutable image ID with an explicit `--entrypoint python`. It still uses `--pull=never`, no network, read-only repository, and restrictive Docker settings.

**Limitations:** A local image ID is not an independent trust attestation. The approved image must still be reviewed; the host Docker daemon, offline isolation, test outcomes and evidence chain require independent validation. No Docker execution occurred in this turn. The GitHub CI query for preceding head `9f0561d1049e63c5ada876fac6fc2ba1e2d4f327` returned no PR workflow runs or combined statuses.

`R200=PATCH_PUBLISHED | DOCKER_TESTS=NOT_EXECUTED | PHASE_B=OPEN | MAIN=UNCHANGED | PRODUCTION=UNTOUCHED | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0`
