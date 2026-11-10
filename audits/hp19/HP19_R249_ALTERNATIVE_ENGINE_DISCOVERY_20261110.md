# R249 — alternative implementation search (2026-11-10)

## Historical variants compared
Drive exact-name variants of `app/agents/sec_sentinel.py`: IDs `1B4RdoylWbUMmpUmk1JGzylu0Yh-gtaEW`, `14Y84AtJLAWIVeKP_uxwlRQpxovcr9Qs-`, `1bdB6bODhImWheAh1NIv6YuU07baZNcj8`. All three source texts 816 characters, identical on inspection, all `run_dry` -> `status=not_implemented`, `mode=stub`. No functional alternative found in this sample. Other HP19 variants not yet compared.

## Existing operational logic outside HP19
- `app/agents/multi_agent_system.py`, Drive `1xP69doHnxAIzWN3-x1KEFWl2EyyCycaI`: deterministic multi-round dispatch of injected orchestrator/researcher/toolmaster/summarizer handlers; depends on `app.agents.multi_agent.MultiAgentConfig` and caller-provided handlers. Real orchestration logic exists, but handler implementations and isolation not verified; **not HP19 functional evidence**.
- `app/mind/agent_router.py`, Drive `14-_xB3jXW_SaDum5QQdnxrvYwtKGj0fU`: resolves profiles and builds plans via `app.mind.agent_profiles.resolve_profile_for_context` and `app.mind.orchestrator.plan_as_dict`. Dependencies unverified; not a replacement for HP19.
- `app/modules/meta_agent_supervisor/supervisor.py`, Drive `1h_JbGlIQ8GjN40t1XyGR-ihKeg9sEBrE`: concrete deterministic priority/health/load/capability scoring; only selects agents, does not execute tasks. `build_default_supervisor` uses three hard-coded demo agents, not canonical HP19 IDs. No deployment permitted.

## Decision
Reuse existing orchestration and scoring code only after offline isolated dependency tests; no duplicate motors, no HP19 certification, no scheduler/production/main activation. Next verify full dependencies and alternate source revisions, hash exact bytes and test deterministic behavior with non-network offline inputs.
