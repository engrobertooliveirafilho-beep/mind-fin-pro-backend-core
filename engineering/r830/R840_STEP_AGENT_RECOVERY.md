# R840 — STEP / AGENT historical recovery
Source of truth: Google Drive; code destination: isolated GitHub branch. No changes to main.
## New concrete discovery
- Historical source `app/agents/dev/step_planner_agent.py` recovered from Drive file `16ekkPZHcuyGyDdJYHOIjNWIduJa7QDP5` (935 bytes).
- Source declares `AGENT_ID=dev.step_planner_agent`, `AGENT_KIND=step_implementation_planner`, `STEP_IDS=[]`; exports `describe_capabilities()` and `run_dry(payload)`.
- Crucial: `run_dry` returns `status=not_implemented` and `mode=stub`. This is a **STUB**, not a functional step planner. Never promote or certify.
- GitHub main lookup `app/agents/dev/step_planner_agent.py`: NOT_FOUND. This is a historical Drive recovery, not verified current GitHub runtime.
- Drive `WAVE1_AGENT_ACTIVATION.txt` file `1mSsP-hn6TqLVH6OIcKs9PuxcC0cxGxRK` references canonical `MIND_AGENT_ACTIVATION_MAP.json` and historical multi-agent inventories.
- Drive `WAVE1_STEP_ENGINE.txt` file `1yGAeaeJvIGMhM0BQ645c5ZfNFFD8woJB` references `MIND_CANON/CORE/MIND_STEPS_MAP.txt`, `MIND_CANON/CORE/mind-platform_CANON_20260223_053928/MIND_STEPS.json` and other step assets.
- Drive `steps_1_520_url.txt` points to a historical signed Supabase object URL with redacted token. It is **not** proof of 520 verified implementations.
## Gate and tests
- R840 `r840_step_gate.py` + `test_r840_step_gate.py`: 16/16 local unittest PASS, offline.
- Corrected R839: empty registries rejected, duplicate identifiers/paths rejected, path traversal rejected, VERIFIED_SOURCE requires SHA-256-formatted evidence.
- Caveat: hash format validation does **not** verify file bytes. Source provenance is not certified by a supplied hash string alone.
- No target imports, no legacy runtime execution, no production changes, no orphan promotion.
Next: recover canonical step map and agent activation map, verify SHA-256 against bytes, identify real implementations and consumers, reject stubs.
