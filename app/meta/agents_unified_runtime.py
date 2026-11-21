"""Recovered 52-agent dispatcher; historical ID contract, fail-closed dry-run only."""
from importlib import import_module

AGENT_IDS = frozenset(['business.strategy_cashflow_agent','cognition.os_kernel_agent','core.high_governance_council','core.safety_compliance_hub','core.system_supervisor','creative.sora_marketing_director','creative.video_scenarios_agent','domain.economics_finance_markets','domain.facebook_media_buyer_engine','domain.instagram_brand_engine','domain.napoleon_hill_engine','domain.psychology_mindset','domain.social_recommendation_kernel','domain.tiktok_growth_engine','domain.youtube_longform_engine','meta.autonomous_evolution_agent','meta.global_agent_mapper','meta.mind_archives_agent_mapper','mission.autonomous_docking_agent','mission.autonomous_navigation_agent','mission.deep_space_exploration_agent','mission.eva_support_agent','mission.fault_detection_recovery_agent','mission.launch_sequencer_agent','mission.life_support_integrity_agent','mission.mission_control_agent','mission.orbital_simulation_agent','mission.radiation_shield_agent','mission.space_weather_agent','mission.telemetry_observability_agent','world.metaverse_orchestrator','dev.step_planner_agent','dev.code_blueprint_agent','dev.test_guardian_agent','dev.refactor_assistant_agent','dev.impl_squad_coordinator','sec.sentinel','sec.gatekeeper','sec.cipher_guard','sec.echo_shield','sec.atlas_backup_commander','sec.vaultmind','sec.overwatch','perf.query_optimizer','perf.api_latency_guardian','perf.cache_strategist','perf.load_balancer_ai','perf.code_profiler_engine','cog.ecosystem_balancer','cog.modularity_enforcer','cog.robustness_engine','cog.autonomous_maturity_meter'])
DENIED = frozenset(('real_orders','live_trading','execute_trade','gpu_provision','ftmo_real','place_order','send_order','submit_order','withdraw_funds'))

class AgentDispatchError(ValueError):
    pass

def _validate(value, seen=None, depth=0):
    if seen is None: seen=set()
    if depth > 16: raise AgentDispatchError('payload too deep')
    if type(value) in (dict,list,tuple):
        ident=id(value)
        if ident in seen: raise AgentDispatchError('cyclic payload')
        seen.add(ident)
        try:
            if type(value) is dict:
                for k,v in value.items():
                    if type(k) is not str or k.casefold() in DENIED: raise AgentDispatchError('forbidden key')
                    _validate(v,seen,depth+1)
            else:
                for v in value: _validate(v,seen,depth+1)
        finally: seen.remove(ident)
    elif type(value) not in (str,int,float,bool,type(None)):
        raise AgentDispatchError('unsupported payload type')

def run_agent(agent_id, payload=None, *, loader=None):
    if type(agent_id) is not str or agent_id not in AGENT_IDS:
        raise AgentDispatchError('agent not registered')
    if payload is None: payload={}
    if type(payload) is not dict: raise AgentDispatchError('payload must be dict')
    _validate(payload)
    module_name='app.agents.'+agent_id.replace('.','_',1)
    try:
        module=(loader or import_module)(module_name)
        fn=getattr(module,'run_dry',None)
        if not callable(fn): raise AgentDispatchError('run_dry missing')
        result=fn(dict(payload))
    except AgentDispatchError: raise
    except Exception as exc: raise AgentDispatchError('agent unavailable') from exc
    if (type(result) is not dict or result.get('agent_id') != agent_id or
        result.get('status') != 'ok' or result.get('mode') != 'dry_run' or 'error' in result):
        raise AgentDispatchError('agent not functionally validated')
    _validate(result)
    return result
