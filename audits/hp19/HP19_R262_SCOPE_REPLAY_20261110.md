# R262 — canonical scope and persistent replay prevention

Executed offline on 2026-11-10: `cd /mnt/data/HP19_R262 && python -m unittest -v test_scope_replay_gate` → **24/24 PASS** (0.145s). Note: 8 new test methods plus 16 inherited R260 test invocations; no claim of 24 independent scenarios.

Added strict allowlist of 19 `agent_`-prefixed HP19 contract IDs, signed manifest inspection, SQLite durable `run_id` uniqueness and envelope-digest uniqueness, atomic transaction. Invalid signature and tampered source do not consume a run. Returned result remains `certified=False`.

Limitations: trusted runner is still a test fixture; no independent institutional authority, trusted challenge/clock, or behavioral proof. SQLite path and database durability need hardening before any deployment. No production/main changes, no real orders, no scheduler. HP19=0/19.
