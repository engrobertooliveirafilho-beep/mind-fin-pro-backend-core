# Agent contract V4 — corrected and tested (2026-11-21)

- Original Drive source `app/meta/agents_unified_runtime.py`: file `1IsM5-lotyUzmYQg8Ibvsy7VFz1xkr2E-`; original finance agent `domain.economics_finance_markets`: file `1NWZNHcOxAvhVvS3RFNDvhWQeG4KLqdFx` (stub, `not_implemented`).
- Fixed existing V4 implementation, not a new validator: require `mode=dry_run` and reject broker_order, submit_order, withdraw_funds.
- Executed `python -m unittest -v test_agent_contract_v4` in isolated local Python: **22 tests PASS, 0 FAIL**.
- SHA256 code: `55f8b3058a0d928e8d711100df853cf8119ea71988555698fc8e9a2a526a750f`; tests: `f2e193888cff8a6e71f311e74e83e66c9d5292606f66044d0f62223170e3e843`; test log: `fe1bdf609e101b7041e4f7f3bea4d193d7569dc894f91876315a5f67e447df4e`.
- Local git blob hashes match GitHub content SHA: code `0babe921d4c31b488f49e22d4f00c1292b07cd33`, tests `46d61fe2698dd546caf15a703162de60ab590bf3`.
- Scope: contract unit tests only. No original agent functional test, no runtime integration, no E2E certification.
- `MAIN=INTACTA | PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | COST=R$0 | E2E_CERTIFIED=FALSE`
