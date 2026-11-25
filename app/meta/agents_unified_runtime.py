from importlib import import_module

_NAMES = '''business_strategy_cashflow_agent cognition_os_kernel_agent core_high_governance_council core_safety_compliance_hub core_system_supervisor creative_sora_marketing_director creative_video_scenarios_agent domain_economics_finance_markets domain_facebook_media_buyer_engine domain_instagram_brand_engine domain_napoleon_hill_engine domain_psychology_mindset domain_social_recommendation_kernel domain_tiktok_growth_engine domain_youtube_longform_engine meta_autonomous_evolution_agent meta_global_agent_mapper meta_mind_archives_agent_mapper mission_autonomous_docking_agent mission_autonomous_navigation_agent mission_deep_space_exploration_agent mission_eva_support_agent mission_fault_detection_recovery_agent mission_launch_sequencer_agent mission_life_support_integrity_agent mission_mission_control_agent mission_orbital_simulation_agent mission_radiation_shield_agent mission_space_weather_agent mission_telemetry_observability_agent world_metaverse_orchestrator dev_step_planner_agent dev_code_blueprint_agent dev_test_guardian_agent dev_refactor_assistant_agent dev_impl_squad_coordinator sec_sentinel sec_gatekeeper sec_cipher_guard sec_echo_shield sec_atlas_backup_commander sec_vaultmind sec_overwatch perf_query_optimizer perf_api_latency_guardian perf_cache_strategist perf_load_balancer_ai perf_code_profiler_engine cog_ecosystem_balancer cog_modularity_enforcer cog_robustness_engine cog_autonomous_maturity_meter'''.split()
_MODULES = {name.replace('_', '.', 1): 'app.agents.' + name for name in _NAMES}

def run_agent(agent_id: str, payload=None):
    def reject(reason):
        return {'agent_id': agent_id, 'status': 'blocked', 'error': reason}
    if not isinstance(agent_id, str) or agent_id not in _MODULES:
        return reject('UNKNOWN_AGENT')
    if payload is not None and not isinstance(payload, dict):
        return reject('INVALID_PAYLOAD')
    try:
        module = import_module(_MODULES[agent_id])
        if module.describe_capabilities().get('id') != agent_id:
            return reject('IDENTITY_MISMATCH')
        result = module.run_dry(payload)
        if not isinstance(result, dict) or result.get('agent_id') != agent_id:
            return reject('INVALID_RESULT')
        if result.get('mode') == 'stub' or result.get('status') == 'not_implemented':
            return reject('NOT_IMPLEMENTED')
        return result
    except Exception:
        return reject('EXECUTION_ERROR')
