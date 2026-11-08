# ET665.R190 — Pinned offline execution preflight (2026-11-08)

R189 harness inspection identified two residual preflight gaps: a checkout HEAD was recorded but not checked against an approved immutable SHA; an externally selected Docker context/host could be used before any isolation evidence existed. R190 hardens the existing PR #17 rather than opening another dependent PR.

Changes: resolve repository root physically, require an absolute evidence path, require `ET665_EXPECTED_HEAD` to be an explicit 40-character SHA equal to the local checkout HEAD, and reject `DOCKER_HOST`/`DOCKER_CONTEXT` overrides before contacting Docker. This does **not** attest the default Docker daemon is local; operator must verify context and host independently.

Invocation contract (only on approved offline Docker host, after review): `ET665_EXPECTED_HEAD=<reviewed-full-SHA> bash mind_trader/scripts/et665_r187_offline_regressions.sh`. Replace the placeholder with the exact approved SHA; never guess it. Local prebuilt image and evidence directory prerequisites remain mandatory.

Status: SOURCE PATCH PUBLISHED, NOT EXECUTED. Docker isolation, regression pass/fail, R60 Drive manifests and main branch protection are not certified. No production changes or real orders.
