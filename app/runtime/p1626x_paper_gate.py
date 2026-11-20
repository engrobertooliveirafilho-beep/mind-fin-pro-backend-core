"""Read-only P1626X PAPER research gate; does not infer correlations or execute orders."""
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from pathlib import Path
import json

def validate(edges):
    if not isinstance(edges,list) or not edges:
        raise ValueError('P1625 source missing or empty')
    seen=set(); scores=[]
    for edge in edges:
        if not isinstance(edge,dict):raise ValueError('invalid edge')
        eid=edge.get('edge_id')
        if not isinstance(eid,str) or not eid or eid in seen:raise ValueError('invalid/duplicate edge_id')
        seen.add(eid)
        values={}
        for key in ('profit_factor','max_drawdown','decay_revalidation_score'):
            raw=edge.get(key)
            if isinstance(raw,bool) or raw is None:raise ValueError('missing/boolean metric')
            try: v=Decimal(str(raw))
            except (InvalidOperation,ValueError,TypeError) as exc:raise ValueError('invalid metric') from exc
            if not v.is_finite():raise ValueError('nonfinite metric')
            values[key]=v
        pf,dd,decay=(values[k] for k in ('profit_factor','max_drawdown','decay_revalidation_score'))
        if pf<0 or not 0<=dd<=1 or not 0<=decay<=1:raise ValueError('out-of-range metric')
        scores.append({'edge_id':eid,'research_allocation_score':str(max(Decimal('0.01'),pf*(1-dd)*(1-decay)))})
    return {'status':'P1626X_PAPER_RESEARCH_RECONCILED','edges':len(seen),'scores':scores,
            'correlation_estimated':False,'allocation_authorized':False,
            'promotion_allowed':False,'order_send_allowed':False,'e2e_certified':False}

def validate_file(path):
    raw=Path(path).read_bytes()
    result=validate(json.loads(raw))
    result['source_sha256']=sha256(raw).hexdigest()
    return result
