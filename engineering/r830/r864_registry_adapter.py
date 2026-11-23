"""Conservative adapter for historical heterogeneous MIND agent registry."""
import re
PAT=re.compile(r'[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\Z')
def adapt(registry):
    blocked={'status':'blocked','executed':0,'e2e_certified':False}
    if type(registry) is not dict or type(registry.get('agents')) is not list or len(registry['agents'])>1000:
        return {**blocked,'reason':'invalid_registry'}
    out=[]; seen=set()
    for a in registry['agents']:
        if type(a) is not dict or type(a.get('id')) is not str or not PAT.fullmatch(a['id']) or a['id'] in seen:
            return {**blocked,'reason':'invalid_agent'}
        seen.add(a['id'])
        steps=a.get('step_ids',[])
        if type(steps) is not list or len(steps)>300 or any(type(s) is not int or s<1 for s in steps):
            return {**blocked,'reason':'invalid_steps'}
        gov=a.get('governance')
        if gov is not None and type(gov) is not dict:
            return {**blocked,'reason':'invalid_governance'}
        if 'auto_run' in a and type(a['auto_run']) is not bool:
            return {**blocked,'reason':'invalid_autorun'}
        flag=gov.get('auto_run') if gov is not None else a.get('auto_run')
        if flag is not None and type(flag) is not bool:
            return {**blocked,'reason':'invalid_autorun'}
        out.append({'id':a['id'],'step_ids':list(steps),'auto_run_recorded':flag,'executed':False})
    return {'status':'planned_only','agents':out,'executed':0,'e2e_certified':False}
