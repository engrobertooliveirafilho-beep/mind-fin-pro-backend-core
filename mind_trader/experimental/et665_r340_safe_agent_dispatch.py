"""ET665.R340 — safe explicit agent dispatch, isolated candidate.

Does not enable real orders, external I/O, or automatically certify agents.
Missing modules and error/stub responses fail closed.
"""
from importlib import import_module
from typing import Any

# Explicitly authorized names only; runtime import is deferred until called.
# Historical Drive source: file 1IsM5-lotyUzmYQg8Ibvsy7VFz1xkr2E-
AGENT_MODULES = (
    "business_strategy_cashflow_agent",
    "cognition_os_kernel_agent",
    "core_high_governance_council",
    "core_safety_compliance_hub",
    "core_system_supervisor",
    "creative_sora_marketing_director",
    "creative_video_scenarios_agent",
    "domain_economics_finance_markets",
    "domain_facebook_media_buyer_engine",
    "domain_instagram_brand_engine",
    "domain_napoleon_hill_engine",
    "domain_psychology_mindset",
    "domain_social_recommendation_kernel",
    "domain_tiktok_growth_engine",
    "domain_youtube_longform_engine",
    "meta_autonomous_evolution_agent",
    "meta_global_agent_mapper",
    "meta_mind_archives_agent_mapper",
    "mission_autonomous_docking_agent",
)
# These are 19 *candidate* names from a historical 51-import dispatcher,
# NOT verified HP19 membership or certification.

def run_agent(agent_id: str, payload: Any = None) -> dict:
    if not isinstance(agent_id, str) or agent_id not in AGENT_MODULES:
        raise ValueError("unauthorized or unknown agent_id")
    module = import_module("app.agents." + agent_id)
    runner = getattr(module, "run_dry", None)
    if not callable(runner):
        raise RuntimeError("missing concrete run_dry implementation")
    result = runner(payload)
    if not isinstance(result, dict):
        raise RuntimeError("invalid agent result type")
    if any(key in result for key in ("error", "not_implemented", "stub")):
        raise RuntimeError("agent returned error or placeholder")
    if result.get("status") in ("error", "stub", "not_implemented") or result.get("mode") == "stub":
        raise RuntimeError("agent returned failure or placeholder")
    if not result:
        raise RuntimeError("agent returned empty result")
    # Identity is mandatory: a different agent must never impersonate the requested one.
    claimed = result.get("agent_id")
    if not isinstance(claimed, str) or claimed.replace(".", "_") != agent_id:
        raise RuntimeError("agent identity mismatch or missing")
    if result.get("status") != "processed":
        raise RuntimeError("agent has not proved processing")
    if result.get("real_orders") != "FORBIDDEN" or result.get("promotion_authorized") is not False:
        raise RuntimeError("agent result lacks safety assertions")
    return result
