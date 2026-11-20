"""P1629 historical Trade DNA fail-closed audit; read-only."""
from decimal import Decimal,InvalidOperation
def audit(rows):
    if not isinstance(rows,list) or not rows:raise ValueError('missing DNA')
    seen=set();missing_p90=0
    for r in rows:
        if not isinstance(r,dict):raise ValueError('invalid record')
        sid=r.get('specialist_id');eid=r.get('edge_id')
        if not isinstance(sid,str) or not sid or sid in seen or not isinstance(eid,str) or not eid or eid not in sid:raise ValueError('identity conflict')
        seen.add(sid)
        if r.get('dna_status')!='TRADE_DNA_REGISTERED':raise ValueError('unregistered DNA')
        if not isinstance(r.get('regime_tags'),list) or not all(isinstance(t,str) and t for t in r['regime_tags']):raise ValueError('invalid regimes')
        if type(r.get('best_entry_hour')) is not int or not 0<=r['best_entry_hour']<=23:raise ValueError('invalid hour')
        for k in ('payoff_ratio_real','expectancy_per_trade_real','profit_factor_real','avg_holding_bars','avg_R','max_R','p90_R'):
            if k=='p90_R' and r.get(k) is None:
                missing_p90+=1
                continue
            try:v=Decimal(str(r[k]))
            except (KeyError,ValueError,TypeError,InvalidOperation) as exc:raise ValueError('invalid metric') from exc
            if not v.is_finite():raise ValueError('nonfinite metric')
        if Decimal(str(r['avg_holding_bars']))<0 or Decimal(str(r['profit_factor_real']))<0:raise ValueError('negative metrics')
    return {'status':'P1629_HISTORICAL_DNA_RECONCILED','records':len(seen),'missing_p90_R':missing_p90,'statistics_complete':missing_p90==0,'order_send_allowed':False,'promotion_allowed':False,'e2e_certified':False}
