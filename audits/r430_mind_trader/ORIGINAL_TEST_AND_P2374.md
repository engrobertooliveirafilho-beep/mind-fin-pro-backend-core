# R430 — Original test and P2373–P2374 audit

2026-10-31. Read-only Drive provenance and isolated local execution.

- Historical original source: Drive ID 1Z4_Laor3FtgviDpNENNKl_dvjbslEUN2; GitHub recovery/r429_mind_original/agent_longterm_memory.py, blob SHA 6a72091b7d2e1d1c5c362da8ad74262066a9c5ab.
- Historical original test: Drive ID 1KBzCTiKhqD3ihnWftppMhkvsO7ai_kGF; GitHub recovery/r429_mind_original/test_agent_longterm_memory.py, blob SHA 127e8b2f095976e34133ff59f1a4b6ce9b02b795.
- Original source SHA256 local: e9ab54a34cf651fd356326ec9de737258654ec28a23542c8991c2c58c0931179. Test SHA256: edff92ecd38675ebaae1063cdc5313a00d9c2aef878f7ba53fa4de8bfa142435.
- Execution: original test content and import path run with original source in isolated app/ package, PYTHONPATH=., python -m pytest -q tests/test_agent_longterm_memory.py => 1 passed in 0.02s. No modified test logic.
- Current-code comparison: app/agent_longterm_memory.py returned GitHub 404 on audit/r318-ftmo-evidence. This does not prove absence on all branches or equivalent functionality elsewhere. No merge or integration authorized.
- Limit: memory is in-process, non-durable; no restart/rollback guarantee.
- P2373 historical log Drive 1KbkyvnjJOq4r6-hTMZBomqh6G68KxyF_: 5000 candidates tested, 52 observed, 4948 rejected, 0 promoted.
- P2374 historical log Drive 1tyY3YwwapQ3bd8vZ_zVAMK6zxVR37qeI: 52 observed candidates walk-forward tested, 52 rejected, 0 observed, 0 promoted. A second log Drive 15KRjEUNkhQuJRIouuT6zDb6QZiENUge1 shows same counts with a distinct historical output directory.
- Executors and their tests not yet recovered or run. No OOS/cost independent certification. PAPER_ONLY; REAL_ORDERS FORBIDDEN; FTMO_READY FALSE.
