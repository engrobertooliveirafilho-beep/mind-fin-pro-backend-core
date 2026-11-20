"""P1625 read-only PAPER portfolio adapter; rejects malformed historical inputs."""
from decimal import Decimal, InvalidOperation

BLOCKS={'LIVE':'FORBIDDEN','REAL_BROKER':'DISABLED','REAL_ORDERS':'FORBIDDEN','FTMO_REAL':'FORBIDDEN','CAUSALITY':'NOT_PROVEN'}

def allocate(edges):
    if not isinstance(edges,list) or not edges:
        raise ValueError('missing active edges')
    scored=[];seen=set()
    for edge in edges:
        if not isinstance(edge,dict): raise ValueError('invalid edge')
        eid=edge.get('edge_id')
        if not isinstance(eid,str) or not eid or eid in seen:raise ValueError('duplicate or invalid edge id')
        seen.add(eid)
        vals=[]
        for key in ('profit_factor','max_drawdown','decay_revalidation_score'):
            raw=edge.get(key)
            if raw is None or isinstance(raw,bool):raise ValueError('missing or boolean metric')
            try: value=Decimal(str(raw))
            except (InvalidOperation,TypeError,ValueError) as exc:raise ValueError('invalid metric') from exc
            if not value.is_finite():raise ValueError('nonfinite metric')
            vals.append(value)
        pf,dd,decay=vals
        if pf<0 or not 0<=dd<=1 or not 0<=decay<=1:raise ValueError('metric outside domain')
        score=max(Decimal('0.01'),pf*(1-dd)*(1-decay))
        scored.append((edge,score))
    total=sum((score for _,score in scored),Decimal(0))
    return [{**edge,'portfolio_score':float(score),'paper_weight':float(score/total),**BLOCKS} for edge,score in scored]
