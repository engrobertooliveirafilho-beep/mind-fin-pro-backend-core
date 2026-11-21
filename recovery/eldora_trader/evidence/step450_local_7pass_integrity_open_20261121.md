# STEP450 — offline behavioral regression, 2026-11-21

Original Drive `1CKl3VQEU_FbNP1etA0o2eIx5-3P1psSr`. Canonical GitHub `app/cognition/distributed_agents_step450/engine.py`.

**Executed:** `PYTHONPATH=. python -m unittest discover -s tests -v` → **7/7 PASS**; 0 failures. Log SHA256 `6bb7e6d2fe013732aa678a7a889d80427c70181a2bb5b5e05068309a3897c20f`.

**Integrity caveat — not exact-source certified:** local test file blob `e346cd7ea77615c853d3b79d0fe5aaface7c5c70` matches published GitHub test file. Local engine reconstruction blob `eb1d14db51de81b092da7ed5004b2e54259f9be3` **does not match** published canonical engine blob `f50ba18ae7c0764a5d6c9a91f1ea440dfe6c0f17`. The tests validate local equivalent behavior only; canonical exact-byte certification remains OPEN.

Seven cases: assignments, max fanout, duplicate cluster ID, duplicate agent ID, empty clusters, infinite latency, UTC metadata. No full main application boot, HTTP integration, broker or E2E certification. No live orders.

`PAPER_ONLY=TRUE | MAIN=INTACTA | REAL_ORDERS=FORBIDDEN | E2E_CERTIFIED=FALSE | COST=R$0`
