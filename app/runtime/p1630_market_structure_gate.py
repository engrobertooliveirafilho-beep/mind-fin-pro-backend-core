"""P1630 historical market structure count-library read-only reconciliation."""
import hashlib
import json
from pathlib import Path

def audit(counts):
    if not isinstance(counts, dict) or not counts:
        raise ValueError('missing market structure library')
    total=0
    for key,value in counts.items():
        if not isinstance(key,str) or not key.strip() or type(value) is not int or value < 0:
            raise ValueError('invalid market structure count')
        total+=value
    return {'status':'P1630_HISTORICAL_COUNTS_RECONCILED','patterns':len(counts),'observations':total,'signals_validated':False,'order_send_allowed':False,'promotion_allowed':False,'e2e_certified':False}

def audit_file(path):
    raw=Path(path).read_bytes()
    def pairs_unique(pairs):
        obj={}
        for key,value in pairs:
            if key in obj:raise ValueError('duplicate pattern')
            obj[key]=value
        return obj
    data=json.loads(raw,object_pairs_hook=pairs_unique,parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite JSON')))
    report=audit(data)
    report['source_sha256']=hashlib.sha256(raw).hexdigest()
    return report
