# ET665.R191 — Host isolation preflight hardening (2026-11-08)

Source review of the R190 harness identified three residual admission risks: Docker could run through a nonlocal default context, a host root account could map to container root, and untracked source-tree files were not included in the clean-checkout gate.

Patch on existing PR #17:
1. Reject host UID 0.
2. Require Docker context endpoint exactly `unix:///var/run/docker.sock` before inspecting images. Other legitimate local setups intentionally fail closed pending separate review.
3. Reject any tracked or untracked changes in the checkout before running tests.

The Docker socket check is a configuration check, not cryptographic proof of local daemon identity. No Docker run or pytest execution has occurred. Do not mark PASS or certify R60/R186 or Fase B without offline runtime evidence and independent review.

`R191=SOURCE_PATCH_PUBLISHED | TESTS=NOT_EXECUTED | PHASE_B=OPEN | MAIN=UNCHANGED | PRODUCTION=UNTOUCHED | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0`
