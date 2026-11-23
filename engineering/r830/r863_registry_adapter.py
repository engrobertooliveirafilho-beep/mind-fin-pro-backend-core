"""Convert historical rich registry into strict offline plans; never run agents."""
import re
PAT=re.compile(r'[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\Z')
def adapt(registry, *, paper_only=True):
    blocked={'status':'blocked','executed':0,'e2e_certified':False}
    if paper_only is not True or type(registry) is not dict or type(registry.get('agents')) is not list:
        return {**blocked,'reason':'invalid_input'}
    agents=registry['agents']
    if len(agents)>1000:return {**blocked,'reason':'limit'}
    out=[]; seen=set()
    for a in agents:
        if type(a) is not dict:return {**blocked,'reason':'invalid_agent'}
        i=a.get('id'); g=a.get('governance'); steps=a.get('step_ids',[])
        if type(i) is not str or not PAT.fullmatch(i) or i in seen:return {**blocked,'reason':'invalid_id'}
        if type(g) is not dict or type(g.get('auto_run')) is not bool:return {**blocked,'reason':'invalid_governance'}
        if type(steps) is not list or len(steps)>300 or any(type(s) is not int or s<1 for s in steps):return {**blocked,'reason':'invalid_steps'}
        seen.add(i)
        out.append({'id':i,'auto_run_requested':g['auto_run'],'step_ids':list(steps),'executed':False})
    return {'status':'planned_only','agents':out,'executed':0,'e2e_certified':False}
