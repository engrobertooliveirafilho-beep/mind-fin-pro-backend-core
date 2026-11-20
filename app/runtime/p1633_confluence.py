"""P1633: read-only confluence candidates reconciliation; never promote candidates."""
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
from pathlib import Path
REQUIRED = ('asset','timeframe','specialist_id','family','profile','deployment_score','confluence_score','opportunity_score','pattern_status','decision')
def reconcile(rows):
    if not isinstance(rows,list) or not rows: raise ValueError('missing candidates')
    seen=set();families=set();assets=set();scores=[]
    for row in rows:
        if not isinstance(row,dict) or any(k not in row for k in REQUIRED): raise ValueError('invalid candidate')
        if any(not isinstance(row[k],str) or not row[k].strip() for k in ('asset','timeframe','specialist_id','family','profile')): raise ValueError('invalid identity')
        if row['specialist_id'] in seen: raise ValueError('duplicate specialist')
        seen.add(row['specialist_id']);families.add(row['family']);assets.add(row['asset'])
        if row['pattern_status']!='MINED_CANDIDATE' or row['decision']!='WATCH_ONLY':raise ValueError('unauthorized historical promotion')
        for k in ('deployment_score','confluence_score','opportunity_score'):
            if isinstance(row[k],bool):raise ValueError('boolean score')
            try:v=Decimal(str(row[k]))
            except (InvalidOperation,ValueError,TypeError) as exc:raise ValueError('invalid score') from exc
            if not v.is_finite() or not 0<=v<=100:raise ValueError('out-of-range score')
        scores.append(Decimal(str(row['opportunity_score'])))
    return {'status':'WATCH_ONLY','candidates':len(rows),'unique_specialists':len(seen),'assets':len(assets),'families':len(families),'max_opportunity_score':str(max(scores)),'historical_performance_verified':False,'promotion_allowed':False,'order_send_allowed':False,'e2e_certified':False}
def reconcile_file(path):
    raw=Path(path).read_bytes();result=reconcile(json.loads(raw));result['historical_sha256']=sha256(raw).hexdigest();return result
