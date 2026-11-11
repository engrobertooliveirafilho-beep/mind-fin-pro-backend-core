# ET665.R347 — CERTIFICAÇÃO LIMITADA DO RUNTIME OFFLINE (2026-11-11)

Fonte de prova: GitHub Actions run 43031688159, job 130560072942, head 9e46a3c8cc8108c036a2e5388fb2a2738c09c969 (PR #25, draft, base audit/et665-r345-s20-s21-evidence-20261110).

- Job exact-source-offline: completed SUCCESS.
- Verificações git hash-object antes da execução: R341 2022b8b4d0b57bda7ce91557faf3c0118824b34c; R347 6de1cc19718df772c62f0f3fc311e828683838a1; teste R347 de9713f378b887bb4dfa7485469b7e9a5e93afd0. Passaram (shell set -euo pipefail).
- Docker python:3.11-slim, --network none, --read-only, --cap-drop ALL, --security-opt no-new-privileges, volume de código read-only.
- Log: Ran 23 tests in 0.005s; OK; 0 failures.
- Artifact ID 13860909005, name et665-r347-runtime-log, digest sha256:b65495536942d64ea9002faceda22ec60d69a2c25a1c86d0f8e6700d1d4d0562.
- Docker image pulled before offline test: digest sha256:07d4824036af339fa1b6ef769cc99d9c10a141769538b52b3b597c84f7a7b535.

CERTIFIED ONLY: exact-source, synthetic structural causal-gate unit/integration tests. Not certified: original historical S20/S21 records; independent source provenance; walk-forward/OOS/returns; broker runtime; FASE B 16/16; HP19 19/19.

Decision: close the R347 exact-source synthetic runtime sub-gate, retain the original-data sub-gate blocked; no new implementation fronts. Main/production unchanged; PAPER_ONLY; REAL_ORDERS and FTMO_REAL forbidden; R$0.

References: https://github.com/engrobertooliveirafilho-beep/mind-fin-pro-backend-core/actions/runs/43031688159
