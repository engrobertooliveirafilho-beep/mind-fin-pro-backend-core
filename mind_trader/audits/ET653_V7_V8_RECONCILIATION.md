# ET-653 — V7/V8 Drive ↔ GitHub reconciliation (2026-11-05)
- Drive V7: `certification_gate_v7.py`, `test_certification_gate_v7.py`, SHA-256 manifest, audit. GitHub ET-651 lacked V7; added isolated V7 gate at `mind_trader/ftmo_paper_execution/certification_gate_v7.py`. No broker interface.
- Drive V8: `consolidate_v8.py` is a read-only audit script tied to the historical `eldora_ftmo_v7` folder layout. It is **not** an execution engine. Do not install it as a second runtime or copy its hard-coded paths into the canonical package.
- Existing GitHub ET-651 contains V2/V3/V4/V5/V6 in isolated namespace; reuse rather than create another execution engine.
- Isolated local test: 35 PASS / 0 FAIL (33 recovered tests plus two new E2E scenarios) against Drive-recovered modules, `PYTHONPATH=/mnt/data python -m pytest -q -p no:cacheprovider test_et653_e2e.py test_certification_gate_v7.py test_ftmo_pretrade_v2.py test_portfolio_runtime.py test_execution_v6.py`.
- Published `mind_trader/tests/test_et653_paper_e2e.py` contains four regression scenarios. **Exact published GitHub files were not executed**, so package verification remains pending.
- V8 historical record explicitly says `canonical_integration=NOT_VERIFIED`, `historical_motors=NOT_FULLY_RECONCILED`, `ftmo_release=BLOCKED`.
- Gate V7 may assess evidence but must never be treated as permission for live orders. `PAPER_ONLY`; `real_orders=0`; `main` unchanged.
- Next: execute exact GitHub branch tests, reconcile canonical runtime hashes, run historical out-of-sample and forward DEMO; no FTMO certification claimed.
