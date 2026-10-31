from datetime import datetime, timezone
from typing import Dict, Any
from app.agents.business_strategy_cashflow_agent import run_dry, describe_capabilities
from app.agents.cognition_os_kernel_agent import run_dry, describe_capabilities
from app.agents.core_high_governance_council import run_dry, describe_capabilities
from app.agents.core_safety_compliance_hub import run_dry, describe_capabilities
from app.agents.core_system_supervisor import run_dry, describe_capabilities
from app.agents.creative_sora_marketing_director import run_dry, describe_capabilities
from app.agents.creative_video_scenarios_agent import run_dry, describe_capabilities
from app.agents.domain_economics_finance_markets import run_dry, describe_capabilities
from app.agents.domain_facebook_media_buyer_engine import run_dry, describe_capabilities
from app.agents.domain_instagram_brand_engine import run_dry, describe_capabilities
from app.agents.domain_napoleon_hill_engine import run_dry, describe_capabilities
from app.agents.domain_psychology_mindset import run_dry, describe_capabilities
from app.agents.domain_social_recommendation_kernel import run_dry, describe_capabilities
from app.agents.domain_tiktok_growth_engine import run_dry, describe_capabilities
from app.agents.domain_youtube_longform_engine import run_dry, describe_capabilities
from app.agents.meta_autonomous_evolution_agent import run_dry, describe_capabilities
from app.agents.meta_global_agent_mapper import run_dry, describe_capabilities
from app.agents.meta_mind_archives_agent_mapper import run_dry, describe_capabilities
from app.agents.mission_autonomous_docking_agent import run_dry, describe_capabilities
from app.agents.mission_autonomous_navigation_agent import run_dry, describe_capabilities
from app.agents.mission_deep_space_exploration_agent import run_dry, describe_capabilities
from app.agents.mission_eva_support_agent import run_dry, describe_capabilities
from app.agents.mission_fault_detection_recovery_agent import run_dry, describe_capabilities
from app.agents.mission_launch_sequencer_agent import run_dry, describe_capabilities
from app.agents.mission_life_support_integrity_agent import run_dry, describe_capabilities
from app.agents.mission_mission_control_agent import run_dry, describe_capabilities
from app.agents.mission_orbital_simulation_agent import run_dry, describe_capabilities
from app.agents.mission_radiation_shield_agent import run_dry, describe_capabilities
from app.agents.mission_space_weather_agent import run_dry, describe_capabilities
from app.agents.mission_telemetry_observability_agent import run_dry, describe_capabilities
from app.agents.world_metaverse_orchestrator import run_dry, describe_capabilities
from app.agents.dev_step_planner_agent import run_dry, describe_capabilities
from app.agents.dev_code_blueprint_agent import run_dry, describe_capabilities
from app.agents.dev_test_guardian_agent import run_dry, describe_capabilities
from app.agents.dev_refactor_assistant_agent import run_dry, describe_capabilities
from app.agents.dev_impl_squad_coordinator import run_dry, describe_capabilities
from app.agents.sec_sentinel import run_dry, describe_capabilities
from app.agents.sec_gatekeeper import run_dry, describe_capabilities
from app.agents.sec_cipher_guard import run_dry, describe_capabilities
from app.agents.sec_echo_shield import run_dry, describe_capabilities
from app.agents.sec_atlas_backup_commander import run_dry, describe_capabilities
from app.agents.sec_vaultmind import run_dry, describe_capabilities
from app.agents.sec_overwatch import run_dry, describe_capabilities
from app.agents.perf_query_optimizer import run_dry, describe_capabilities
from app.agents.perf_api_latency_guardian import run_dry, describe_capabilities
from app.agents.perf_cache_strategist import run_dry, describe_capabilities
from app.agents.perf_load_balancer_ai import run_dry, describe_capabilities
from app.agents.perf_code_profiler_engine import run_dry, describe_capabilities
from app.agents.cog_ecosystem_balancer import run_dry, describe_capabilities
from app.agents.cog_modularity_enforcer import run_dry, describe_capabilities
from app.agents.cog_robustness_engine import run_dry, describe_capabilities
from app.agents.cog_autonomous_maturity_meter import run_dry, describe_capabilities

def run_agent(agent_id: str, payload=None) -> Dict[str, Any]:
    # dynamic dispatch
    try:
        mod = agent_id.replace('.', '_')
        fn = globals().get('run_dry')
        return fn(payload)
    except Exception as e:
        return {'agent_id': agent_id, 'error': str(e)}
