# R250 — dependency and implementation conflict audit — 2026-11-10

Recovered from Google Drive:
- `app/agents/multi_agent.py` (1yIsu8fSRLwPPd5LG2kPedmkJ4uweOFWz), 4,971 chars, defines MultiAgentConfig, MultiAgentRole, MultiAgentMessage, and a **second MultiAgentSystem implementation**. This implementation validates returned role for each handler and raises ValueError on mismatch.
- `app/agents/multi_agent_system.py` (1xP69doHnxAIzWN3-x1KEFWl2EyyCycaI), 4,171 chars, imports MultiAgentConfig from `multi_agent`, defines its own MultiAgentSystem and calls four handlers without checking returned roles. **Duplicate class/contract, inconsistent validation**. Canonical authority not established; do not merge blindly.
- `app/mind/agent_profiles.py` (1yoLZonvmIs4U3AS5Vkr3E0qDZhKUsALP), 6,779 chars, in-memory profile registry, implements resolve_profile_for_context.
- `app/mind/orchestrator.py` (1Sr4FECfyV7M8dEDbW3lC6qJZBtRNla73), 5,669 chars, implements build_plan and optional imports from app.search.universal_search, app.creative.creative_os/creative_insights and app.mind.graph_memory. Missing optional modules are silently set None; therefore planning may degrade without an explicit error. Does not itself execute tools.
- `app/mind/agent_router.py` (14-_xB3jXW_SaDum5QQdnxrvYwtKGj0fU), 2,506 chars, depends on both agent_profiles and orchestrator. Both direct dependencies now located in Drive; their full transitive imports and runtime behavior remain unverified.
- `app/cognition/multi_agent_coop/engine.py` (1mGNPTQlT6R_xia0NwHFcTh7C1FehYS0h), 2,343 chars, explicitly declares engine='multi_agent_coop_stub' and emits hypothetical tool messages; exclude from functional certification.

Decision: reuse existing classes only after choosing authoritative version and testing role mismatch, max_rounds and optional-dependency degradation. This audit is source inspection, not execution evidence. HP19 remains 0/19 certified. No production, merge, scheduler or real orders.
