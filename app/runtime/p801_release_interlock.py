"""P801 certification interlock: read-only and fail-closed."""
from decimal import Decimal,InvalidOperation
from .p601_risk_gate import audit,BLOCKS

def release_gate(allocations, risk_report, supervised, release):
    if not isinstance(release,dict) or any(release.get(k)!=v for k,v in BLOCKS.items()):
        raise ValueError('unsafe release')
    if release.get('real_ftmo_release_allowed') is not False or release.get('human_release_required') is not True:
        raise ValueError('real release prohibited')
    result=audit(allocations,risk_report)
    if not isinstance(supervised,list):raise ValueError('missing supervisor')
    allocated={r['edge_id']:r for r in allocations if r['allocation_status']=='ALLOCATED_SIMULATED'}
    seen=set()
    for r in supervised:
        if not isinstance(r,dict) or any(r.get(k)!=v for k,v in BLOCKS.items()) or r.get('execution_allowed') is not False or r.get('shadow_only') is not True:
            raise ValueError('unsafe supervisor')
        eid=r.get('edge_id')
        if eid not in allocated or eid in seen:raise ValueError('supervisor mismatch')
        try: risk=Decimal(str(r['risk_pct']))
        except (KeyError,ValueError,InvalidOperation):raise ValueError('invalid risk')
        if not risk.is_finite() or risk!=Decimal(str(allocated[eid]['risk_pct'])):raise ValueError('supervisor risk mismatch')
        seen.add(eid)
    if seen!=set(allocated):raise ValueError('missing supervised edge')
    return {'certification':'BLOCKED_RISK' if result['status']!='PASS' else 'BLOCKED_EVIDENCE',
            'demo_operation_ready':False,'real_ftmo_release_allowed':False,'order_sent':False,
            'e2e_certified':False,'risk_audit':result,**BLOCKS}
