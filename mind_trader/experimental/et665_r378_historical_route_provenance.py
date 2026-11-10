"""ET665.R378 — compare route IDs with the candidate dispatcher.

The Drive artifact contains historical route declarations, not official HP19
contracts. This check establishes identity correspondence only.
"""
from mind_trader.experimental.et665_r340_safe_agent_dispatch import AGENT_MODULES
from mind_trader.experimental.et665_r377_e2e_phase_b_report import run

HISTORICAL_ROUTE_SOURCE = "1i1yj4qab7-NPay3tvK-xl7Fh7-3_o_lJ"
HISTORICAL_FIRST_19 = (
    "business.strategy_cashflow_agent", "cognition.os_kernel_agent",
    "core.high_governance_council", "core.safety_compliance_hub",
    "core.system_supervisor", "creative.sora_marketing_director",
    "creative.video_scenarios_agent", "domain.economics_finance_markets",
    "domain.facebook_media_buyer_engine", "domain.instagram_brand_engine",
    "domain.napoleon_hill_engine", "domain.psychology_mindset",
    "domain.social_recommendation_kernel", "domain.tiktok_growth_engine",
    "domain.youtube_longform_engine", "meta.autonomous_evolution_agent",
    "meta.global_agent_mapper", "meta.mind_archives_agent_mapper",
    "mission.autonomous_docking_agent",
)

def _canonical(value):
    return value.replace("_", ".") if isinstance(value, str) else value

def audit():
    expected = HISTORICAL_FIRST_19
    if len(expected) != 19 or len(set(expected)) != 19:
        raise RuntimeError("historical route inventory is not 19 unique IDs")
    if tuple(_canonical(x) for x in AGENT_MODULES) != expected:
        raise RuntimeError("candidate dispatcher differs from historical route inventory")
    report = run()
    actual = [_canonical(x["agent_id"]) for x in report["candidate_outputs"]]
    if actual != list(expected):
        raise RuntimeError("executed candidate identities differ from historical routes")
    return {
        "status": "HISTORICAL_ROUTE_IDENTITY_MATCH",
        "matched_candidates": 19,
        "historical_source_drive_id": HISTORICAL_ROUTE_SOURCE,
        "historical_source_type": "route_declarations_not_runtime_contracts",
        "official_hp19_membership_verified": False,
        "official_hp19_certified": 0,
        "phase_b_certified": 0,
        "real_orders": "FORBIDDEN",
        "production_modified": False,
    }
