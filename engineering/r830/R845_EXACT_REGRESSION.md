# R845 — Exact published regression and source lineage
2026-11-22. The exact bytes of `engineering/r830/r844_step_planner.py` and `engineering/r830/test_r844_step_planner.py` were reconstructed in an isolated local workspace and compared against GitHub readback blob IDs:
- `r844_step_planner.py`: `a430ccf8c6254d7dafb2330a912116a29c9ae2ed` (match).
- `test_r844_step_planner.py`: `903d366984145d1cdc74ce68c6c2516e94c2a5e0` (match).
- Executed `python -m unittest -v test_r844_step_planner.py`: **16 tests, 16 PASS, 0 failures**. This certifies offline behavioral contract only; no consumer E2E.
- Original Drive `app/agents/dev/step_planner_agent.py` recovered from four historical file IDs: `16ekkPZHcuyGyDdJYHOIjNWIduJa7QDP5`, `1h7lokNx1G60cetjbg1ax7CyWk5pjCX3h`, `1BT2t7mBTK7XSSXnkAz9OqpdQsSbOzDn4`, `1eHIA9cRjOh6LFnJntSbeS4lNmar-8Mky`. All four returned **identical source text** (930 characters), with `run_dry` returning `not_implemented`/`stub`. Four archive copies are not four different implementations.
- R844 is an isolated replacement, **not integrated into the original agent runtime**; its SHA-256 input is only format-checked, not bound to independently recovered bytes. Promotion remains blocked until source-byte attestation and consumer integration are tested.
- R841–R843 STEPs and HP19 reconciliation preserved, no reimplementation or promotion.
MAIN unchanged, Drive original unchanged, no production execution, no paid services.
