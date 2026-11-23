"""R865: reconcile real historical registry without granting runtime authority."""
from r864_registry_adapter import adapt

def reconcile(registry):
    result=adapt(registry)
    if result['status']!='planned_only':return result
    agents=result['agents']
    steps=set()
    for agent in agents:steps.update(agent['step_ids'])
    return {'status':'reconciled_offline','agent_count':len(agents),
            'unique_step_count':len(steps),
            'autorun_requests':sum(a['auto_run_recorded'] is True for a in agents),
            'agents_without_steps':sum(not a['step_ids'] for a in agents),
            'executed':0,'e2e_certified':False,
            'execution_authorized':False}
