# ET665.R202 — Preflight before evidence creation (2026-11-08)

Inspection of the authenticated PR #17 runner showed that evidence output was created before the approved image ID and required regression files were checked. A failed preflight could leave an unusable evidence directory and prevent the next attempt because existing evidence directories are rejected.

R202 moves creation of the evidence directory until after both the approved image ID check and the existence checks for the six required regression files. Source hashes and run metadata are then written to the fresh evidence directory.

This is a published source correction, not a verified Docker run or security certification. GitHub workflow query for prior head `b54a0b0e555af98bcfdb9d1c1696d69dc9d659a8` returned zero PR-triggered runs in the queried page. R60 Drive/GitHub reconciliation and HP19 remain pending.

`R202=PATCH_PUBLISHED | TESTS=NOT_EXECUTED | PHASE_B=OPEN | MAIN=UNCHANGED | PRODUCTION=UNTOUCHED | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0`
