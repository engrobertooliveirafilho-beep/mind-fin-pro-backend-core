# ET665.R203 — Bounded offline Docker execution (2026-11-08)

Authenticated inspection of the R202 shell runner showed no wall-clock limit around `docker run`. A hung test process could block completion and delay evidence finalization indefinitely.

R203 requires the host `timeout` utility and wraps the existing offline Docker command with `timeout --signal=TERM --kill-after=15s 15m`. Timeout exit status is recorded by the existing evidence mechanism and prevents any success/certification message. Docker remains `--network=none`, read-only, `--pull=never`, and uses the separately approved image ID.

**Limitations:** timeout applies to the Docker client process; it does not independently prove daemon/container cleanup if the daemon is unresponsive. An operator must inspect for residual containers and review the original logs. This is a published source patch; the offline Docker suite was not executed here. R60 reconciliation and HP19 remain open.

`R203=PATCH_PUBLISHED | DOCKER_TESTS=NOT_EXECUTED | PHASE_B=OPEN | MAIN=UNCHANGED | PRODUCTION=UNTOUCHED | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0`
