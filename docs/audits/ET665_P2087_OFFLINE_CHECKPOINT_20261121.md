# ET665 P2087 — isolated offline checkpoint regression

Date: 2026-11-21. Original GitHub source: `app/runtime/p2081_2090_realtime_portfolio_governance.py`, branch `engineering/et665-realdna-reconciliation-20261121`.
Fix commit: `576dac8e594f2a7a5ff749e5d48949ed9185337b` (POSIX directory fsync after atomic rename).

## Executed evidence
Local `python -m pytest -q /mnt/data/et665_p2087_offline/test_checkpoint.py`: **5 passed in 0.05s**.
- Isolated checkpoint write/read; idempotent rerun; conflicting historical checkpoint; symlink directory; non-finite JSON rejection.
- `test_checkpoint.py` SHA256 `670c5a86f3b74fd64614106c08341f5799d7483c4f7d3a6b8538aa1b3e62b2be`
- `pytest.log` SHA256 `bd5201fad773316bbfda2cfee7833ff2d8db356db81550c537f47ba44de0ed2d`

## Certification boundary
The test module **reproduces the checkpoint algorithm** from the GitHub source in a local isolated harness. It is **not** a test import of the original GitHub module, not an end-to-end restart, and does not establish production readiness. No live feed, brokers, real orders, paid API or main branch changes.

`PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | E2E_CERTIFIED=FALSE | COST=R$0`
