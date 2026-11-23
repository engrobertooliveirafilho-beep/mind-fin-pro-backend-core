"""R844: deterministic offline replacement for historical stub. No runtime imports."""
import re
AGENT_ID='dev.step_planner_agent'
def describe_capabilities():
 return {'id':AGENT_ID,'kind':'step_implementation_planner','mode':'offline_planning_only','runtime_certified':False}
def run_dry(payload=None):
 if not isinstance(payload,dict) or not isinstance(payload.get('approved_steps'),list) or not payload['approved_steps']:
  return {'status':'blocked','reason':'no_approved_steps','agent_id':AGENT_ID}
 steps=payload['approved_steps']
 if len(steps)>100:return {'status':'blocked','reason':'batch_limit','agent_id':AGENT_ID}
 plans=[];seen=set()
 for s in steps:
  if not isinstance(s,dict) or set(s)!={'id','title','approved','source_sha256'}:
   return {'status':'blocked','reason':'invalid_schema','agent_id':AGENT_ID}
  i,t,a,h=s['id'],s['title'],s['approved'],s['source_sha256']
  if not isinstance(i,int) or isinstance(i,bool) or i<=0 or i in seen or not isinstance(t,str) or not t.strip() or len(t)>240 or a is not True or not isinstance(h,str) or not re.fullmatch('[0-9a-f]{64}',h):
   return {'status':'blocked','reason':'unverified','agent_id':AGENT_ID}
  seen.add(i)
  plans.append({'step_id':i,'title':t.strip(),'source_sha256':h,'implementation_path':f'src/revisions/step_{i:04d}.py','test_path':f'tests/test_step_{i:04d}.py','status':'PLAN_ONLY'})
 return {'status':'planned','agent_id':AGENT_ID,'plans':plans,'runtime_certified':False,'integration_authorized':False}
