"""P701 supervisor interlock: no ACTIVE shadow supervision on invalid P601 risk."""
from decimal import Decimal
from .p601_risk_gate import audit, BLOCKS

def supervise(allocations, report, historical_supervised):
    result=audit(allocations,report)
    if not isinstance(historical_supervised,list):raise ValueError('invalid supervision')
    active={r['edge_id']:r for r in allocations if r.get('allocation_status')=='ALLOCATED_SIMULATED'}
    seen=set();output=[]
    for row in historical_supervised:
        if not isinstance(row,dict) or any(row.get(k)!=v for k,v in BLOCKS.items()):
            raise ValueError('unsafe supervision')
        eid=row.get('edge_id')
        if not isinstance(eid,str) or eid not in active or eid in seen or row.get('shadow_only') is not True or row.get('execution_allowed') is not False:
            raise ValueError('invalid supervision identity or mode')
        if Decimal(str(row.get('risk_pct'))) != Decimal(str(active[eid]['risk_pct'])):
            raise ValueError('risk mismatch')
        seen.add(eid)
        output.append({**row,'health':'RED' if result['status']!='PASS' else row.get('health'),'supervisor_status':'BLOCKED_RISK' if result['status']!='PASS' else 'ACTIVE','execution_allowed':False,**BLOCKS})
    if seen!=set(active):raise ValueError('missing supervised allocation')
    return {'risk_audit':result,'supervised':output,'operationally_certified':False}
