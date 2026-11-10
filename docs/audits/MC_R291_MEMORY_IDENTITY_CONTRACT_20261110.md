# MC-R291 — Drive engine memory identity contract
Date: 2026-11-10

Directly inspected original Drive hierarchical planner source (ID 13sUVaHTSPHLPHr2A2_fPoVs8yDkrCBsu): `request.memory_key or f"hp-{abs(hash(request.goal)) % 10_000}"`. Python randomized string hashes vary between process seeds, so generated identifiers are not stable across restarts. Proposed fix: deterministic `sha256(goal.encode('utf-8')).hexdigest()[:16]` prefix; this is **not applied** to the original engine because authoritative runtime path is unverified.

Drive cooperation engine source (ID 1mGNPTQlT6R_xia0NwHFcTh7C1FehYS0h) self-identifies `multi_agent_coop_stub`. Not suitable for HP19 functional certification.

GitHub default branch code search for exact engine names and `memory_key`: no results (not proof of repository-wide absence).

Isolated proof-of-concept tests: 3/3 PASS in local Python unittest. Tests do not execute exact recovered engine source or certify integration. GitHub path: `audits/hp19/r291/test_recovered_engine_contract_poc.py`. Require exact-source tests and authority reconciliation before applying changes.

Drive Master Ledger write remains HTTP 403 from R289. No main/production changes; no real orders; R$0. Global certification BLOCKED.
