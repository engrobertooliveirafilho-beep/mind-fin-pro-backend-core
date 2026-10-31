# R382 — Historical MIND agent executor recovery (2026-10-31)

## Sources actually read in Google Drive
- `app/meta/agents_unified_runtime.py` historical text IDs 1IsM5-lotyUzmYQg8Ibvsy7VFz1xkr2E-, 1l6pRGOHJj2ZqnUDjlcFktDrfxafWBnQm, 1yJ5zEY0kekQSS8NjzetlGH6nKyq3HwPk (4587 characters each).
- `app/meta/agents_runtime.py` IDs 10WByay5ageFVa7fDPGsF4s-6mg2DDTxT, 1jaU9tnrShrPNJ-PYboNq45aupQqriQQS (2238 chars).
- `app/mind/agent_runtime.py` IDs 1HZxNtW1pPvPoMXrdNL3wyo9RAoVfBkB9, 1659n9FT32403OLBTXQLwgG42TlnvvSWl (9035 chars).
- `app/mind/mind_talk_runtime_adapter.py` IDs 1bd2p99EMqRxiVZh6aWbjPjrEmyhNncen, 1YA__l-MTcNfwb_h3W8jPpW6_aVhJilYc (1130 chars).
- Original `tests/test_agents_runtime.py` ID 1yoapMPUH-kQNBz9OsA5-dq_EEeh0e7L7.

## Original defects, directly grounded in source
1. `agents_unified_runtime.run_agent`: computes `mod = agent_id.replace('.', '_')` but never uses it. It resolves `globals().get('run_dry')` even though 50+ imports repeatedly shadow the same symbol; no dispatch map, so cannot prove requested agent executes. Catches all exceptions and returns an error dictionary.
2. `agents_runtime.py`: generates `registry_scan_minimal` proposal placeholders with None-valued fields; auto-starts a scheduler at module import and silently swallows failures. Not evidence of autonomous evolution.
3. `agent_runtime.py`: missing agent router falls back to `chat_llm` stub; `_exec_chat_llm` returns `status=stub` with `ok=True`; `_exec_creative_os` returns `status=noop` with `ok=True`. This is false-positive operational success.
4. `mind_talk_runtime_adapter.py`: invokes `run_agent_turn_as_dict(payload)` positionally, while callee declares keyword-only parameters `prompt, user_id, org_id, plan`; this raises TypeError when executed.

## Hash authority and tests
The four logical sources and duplicates were read through Drive connector, but no independent historical SHA-256 baseline was found in these reads. Text character counts are NOT byte counts or hashes. Historical source content is recovered for inspection, but byte-for-byte provenance and actual isolated execution have NOT been certified. Do not integrate unverified modules or rewrite original code in place.

## Fail-closed plan
- Copy original bytes to quarantine with independently verified SHA-256.
- Execute static AST and isolated regression tests that reproduce bad dispatch, false-success stubs and keyword-only adapter mismatch; compare duplicate variants.
- Fix dispatch with explicit agent_id-to-module registry; mark stub/noop as unsuccessful; repair adapter signature and add negative tests.
- Publish tested patch only after GitHub Actions run and logs PASS. Keep historical originals immutable.
