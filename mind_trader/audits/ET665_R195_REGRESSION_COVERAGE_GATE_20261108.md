# ET665.R195 — Regression coverage evidence gate (2026-11-08)

Authenticated inspection of the R194 runner identified a remaining false-positive path: a valid passing JUnit report from an unrelated test could satisfy the prior XML/count checks. R195 requires JUnit testcase names/classnames to include identifiers for all five requested modules: R180, R182, R183, R184 and R186.

This is a basic coverage-consistency check, **not** an attestation that the cases actually ran, nor proof of the origin of the XML. JUnit attributes can be forged. Approval still requires independent review of Docker runtime logs, source hashes, image identity and offline isolation.

Source change published to existing draft PR #17; no repository pytest or Docker tests executed, no merge, no production changes. R60 reconciliation and HP19 certification remain pending.

`R195=SOURCE_PATCH_PUBLISHED | DOCKER_TESTS=NOT_EXECUTED | PHASE_B=OPEN | MAIN=UNCHANGED | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0`
