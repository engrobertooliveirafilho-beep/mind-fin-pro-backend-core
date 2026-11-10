# R251 — source preservation and reproducibility

Recovered five original source files from Google Drive and published them verbatim under `audits/hp19/r251_sources/` on an isolated GitHub branch (not imported by production):

| Original path | Drive source ID | GitHub audit path |
|---|---|---|
| app/agents/multi_agent.py | 1yIsu8fSRLwPPd5LG2kPedmkJ4uweOFWz | audits/hp19/r251_sources/app/agents/multi_agent.py |
| app/agents/multi_agent_system.py | 1xP69doHnxAIzWN3-x1KEFWl2EyyCycaI | audits/hp19/r251_sources/app/agents/multi_agent_system.py |
| app/mind/agent_profiles.py | 1yoLZonvmIs4U3AS5Vkr3E0qDZhKUsALP | audits/hp19/r251_sources/app/mind/agent_profiles.py |
| app/mind/orchestrator.py | 1Sr4FECfyV7M8dEDbW3lC6qJZBtRNla73 | audits/hp19/r251_sources/app/mind/orchestrator.py |
| app/mind/agent_router.py | 14-_xB3jXW_SaDum5QQdnxrvYwtKGj0fU | audits/hp19/r251_sources/app/mind/agent_router.py |

These are archived sources for inspection and future offline tests, **not a functional integration**. Local runtime could not download raw GitHub due to DNS/network isolation; no actual behavioral tests were executed in R251. R250 finding stands: duplicate MultiAgentSystem, different role validation. Canonical implementation undecided; fail closed. HP19=0/19 certified. No production/main modifications, scheduler or orders.
