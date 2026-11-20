"""Read-only P601 allocation reconciler; rejects excess aggregate risk."""
import json,math
from decimal import Decimal
from pathlib import Path
BLOCKS={'LIVE':'FORBIDDEN','REAL_BROKER':'DISABLED','REAL_ORDERS':'FORBIDDEN','FTMO_REAL':'FORBIDDEN','MT5_REAL':'FORBIDDEN'}
CAPS={'edge':Decimal('0.0025'),'asset':Decimal('0.004'),'timeframe':Decimal('0.005'),'family':Decimal('0.005')}
def audit(rows,report):
    if not isinstance(rows,list) or not rows or not isinstance(report,dict):raise ValueError('invalid input')
    if any(report.get(k)!=v for k,v in BLOCKS.items()) or report.get('ORDER_SENT') is not False:raise ValueError('unsafe report')
    groups={k:{} for k in CAPS};seen=set();total=Decimal(0)
    for r in rows:
        if not isinstance(r,dict) or any(r.get(k)!=v for k,v in BLOCKS.items()) or r.get('order_sent') is not False:raise ValueError('unsafe row')
        eid=r.get('edge_id');status=r.get('allocation_status');v=r.get('risk_pct')
        if not isinstance(eid,str) or not eid or eid in seen or status not in ('ALLOCATED_SIMULATED','BLOCKED_BY_CAP') or isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0:raise ValueError('invalid allocation')
        seen.add(eid);risk=Decimal(str(v))
        if (status=='BLOCKED_BY_CAP') != (risk==0):raise ValueError('status-risk mismatch')
        for k in CAPS:
            name=eid if k=='edge' else r.get(k)
            if not isinstance(name,str) or not name:raise ValueError('invalid group')
            groups[k][name]=groups[k].get(name,Decimal(0))+risk
        total+=risk
    violations=[(k,n,str(v),str(CAPS[k])) for k,g in groups.items() for n,v in g.items() if v>CAPS[k]]
    if total!=Decimal(str(report.get('TOTAL_ALLOCATED_RISK_PCT'))):raise ValueError('report mismatch')
    return {'status':'REJECTED_CAP' if violations else 'PASS','violations':violations,'total_risk':str(total),'order_sent':False}
def run(allocation,report):return audit(json.loads(Path(allocation).read_text()),json.loads(Path(report).read_text()))
