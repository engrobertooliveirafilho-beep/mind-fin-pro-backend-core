"""P1633: read-only confluence candidates reconciliation; never promote candidates."""
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
from pathlib import Path
MAX_SOURCE_BYTES = 20_000_000
REQUIRED = ('asset','timeframe','specialist_id','family','profile','deployment_score','confluence_score','opportunity_score','pattern_status','decision')
def reconcile(rows):
    if not isinstance(rows,list) or not rows: raise ValueError('missing candidates')
    seen=set();families=set();assets=set();scores=[]
    for row in rows:
        if not isinstance(row,dict) or any(k not in row for k in REQUIRED): raise ValueError('invalid candidate')
        if any(not isinstance(row[k],str) or not row[k].strip() for k in ('asset','timeframe','specialist_id','family','profile')): raise ValueError('invalid identity')
        specialist=row['specialist_id'].strip().casefold()
        if specialist in seen: raise ValueError('duplicate normalized specialist')
        seen.add(specialist);families.add(row['family'].strip().casefold());assets.add(row['asset'].strip().casefold())
        if row['pattern_status']!='MINED_CANDIDATE' or row['decision']!='WATCH_ONLY':raise ValueError('unauthorized historical promotion')
        for k in ('deployment_score','confluence_score','opportunity_score'):
            if isinstance(row[k],bool):raise ValueError('boolean score')
            try:v=Decimal(str(row[k]))
            except (InvalidOperation,ValueError,TypeError,OverflowError) as exc:raise ValueError('invalid score') from exc
            if not v.is_finite() or not 0<=v<=100:raise ValueError('out-of-range score')
        scores.append(Decimal(str(row['opportunity_score'])))
    return {'status':'WATCH_ONLY','candidates':len(rows),'unique_specialists':len(seen),'assets':len(assets),'families':len(families),'max_opportunity_score':str(max(scores)),'historical_performance_verified':False,'promotion_allowed':False,'order_send_allowed':False,'e2e_certified':False}
def reconcile_file(path):
    source=Path(path)
    if not source.is_file() or not 0 < source.stat().st_size <= MAX_SOURCE_BYTES: raise ValueError('missing, empty or oversized source')
    raw=source.read_bytes()
    if not 0 < len(raw) <= MAX_SOURCE_BYTES: raise ValueError('invalid source size')
    def unique_pairs(pairs):
        result={}
        for k,v in pairs:
            if k in result: raise ValueError('duplicate JSON field')
            result[k]=v
        return result
    data=json.loads(raw,object_pairs_hook=unique_pairs,parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON')))
    result=reconcile(data);result['historical_sha256']=sha256(raw).hexdigest();return result
