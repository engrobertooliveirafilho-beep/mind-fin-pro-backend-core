"""R886 explicit inventory and fail-closed binding for 52 historical agent routes."""
EXPECTED_AGENT_IDS = frozenset({
    "business.strategy_cashflow_agent",
    "cognition.os_kernel_agent",
    "core.high_governance_council",
    "core.safety_compliance_hub",
    "core.system_supervisor",
    "creative.sora_marketing_director",
    "creative.video_scenarios_agent",
    "domain.economics_finance_markets",
    "domain.facebook_media_buyer_engine",
    "domain.instagram_brand_engine",
    "domain.napoleon_hill_engine",
    "domain.psychology_mindset",
    "domain.social_recommendation_kernel",
    "domain.tiktok_growth_engine",
    "domain.youtube_longform_engine",
    "meta.autonomous_evolution_agent",
    "meta.global_agent_mapper",
    "meta.mind_archives_agent_mapper",
    "mission.autonomous_docking_agent",
    "mission.autonomous_navigation_agent",
    "mission.deep_space_exploration_agent",
    "mission.eva_support_agent",
    "mission.fault_detection_recovery_agent",
    "mission.launch_sequencer_agent",
    "mission.life_support_integrity_agent",
    "mission.mission_control_agent",
    "mission.orbital_simulation_agent",
    "mission.radiation_shield_agent",
    "mission.space_weather_agent",
    "mission.telemetry_observability_agent",
    "world.metaverse_orchestrator",
    "dev.step_planner_agent",
    "dev.code_blueprint_agent",
    "dev.test_guardian_agent",
    "dev.refactor_assistant_agent",
    "dev.impl_squad_coordinator",
    "sec.sentinel",
    "sec.gatekeeper",
    "sec.cipher_guard",
    "sec.echo_shield",
    "sec.atlas_backup_commander",
    "sec.vaultmind",
    "sec.overwatch",
    "perf.query_optimizer",
    "perf.api_latency_guardian",
    "perf.cache_strategist",
    "perf.load_balancer_ai",
    "perf.code_profiler_engine",
    "cog.ecosystem_balancer",
    "cog.modularity_enforcer",
    "cog.robustness_engine",
    "cog.autonomous_maturity_meter"
})

class RegistryContractError(ValueError):
    pass

def build_registry(handlers):
    if not isinstance(handlers, dict):
        raise RegistryContractError("handlers_must_be_dict")
    supplied = set(handlers)
    missing = EXPECTED_AGENT_IDS - supplied
    unexpected = supplied - EXPECTED_AGENT_IDS
    if missing:
        raise RegistryContractError("missing_handlers:" + ",".join(sorted(missing)))
    if unexpected:
        raise RegistryContractError("unexpected_handlers:" + ",".join(sorted(unexpected)))
    invalid = sorted(agent_id for agent_id, fn in handlers.items() if not callable(fn))
    if invalid:
        raise RegistryContractError("non_callable_handlers:" + ",".join(invalid))
    return dict(handlers)
