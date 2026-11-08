# ET665.R187 — Offline execution harness, evidence pending (2026-11-08)

## Verified
PR #14 draft at head `6276f1ca6504cc106fe7f1d9c34a2a9b0789d2bf`; authenticated GitHub workflow lookup returned zero PR-triggered runs for this commit. No test pass evidence from CI.

## Deliverable
`mind_trader/scripts/et665_r187_offline_regressions.sh` is a manually invoked, fail-closed Docker harness for R180/R182/R183/R184/R186. It refuses to pull images, requires an existing locally prepared `et665-pytest-offline:py312` image with pytest already installed, runs with `--network=none`, read-only root and repository, no capabilities, no-new-privileges, CPU/memory/pid limits, and captures JUnit, logs, exit status, SHA-256 and image/commit identity under ignored local evidence folder.

## Execution requirements and limits
- NOT EXECUTED by this publication. No Docker daemon, image or pytest runtime verified here.
- The script assumes a local Git checkout and POSIX Bash; Windows PowerShell users need an approved compatible shell or separately reviewed equivalent.
- This is an operator-run harness, not independent proof of network/process isolation. Docker security settings need runtime inspection and review.
- The R186 test set comprises 6 test functions. Existing R180/R182/R183/R184 test counts are as previously authored, not independently executed.
- Do not put broker credentials, MT5 or production mounts in the container. Do not enable real orders.
- R188 remains blocked on original R60 manifests, hash reconciliation, independent review, and technical main branch protection.

`R187=HARNESS_PUBLISHED | TESTS=NOT_EXECUTED | PHASE_B=OPEN | MAIN=UNCHANGED | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0`
