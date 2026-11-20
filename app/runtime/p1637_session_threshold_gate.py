"""P1637 historical session-threshold validator. Read-only; fail-closed."""
from decimal import Decimal,InvalidOperation,ROUND_HALF_UP
def session(h):
    if type(h) is not int or not 0<=h<=23:raise ValueError('invalid hour')
    return 'ASIA' if h<=6 else 'LONDON_OPEN' if h<=9 else 'LONDON' if h<=12 else 'LONDON_NY_OVERLAP' if h<=16 else 'NEW_YORK' if h<=20 else 'POST_NY'
def score(v):
    if isinstance(v,bool):raise ValueError('boolean score')
    try:x=Decimal(str(v))
    except (ValueError,InvalidOperation,TypeError) as exc:raise ValueError('invalid score') from exc
    if not x.is_finite() or not 0<=x<=100:raise ValueError('score range')
    return x
def reconcile(rows,sessions,report):
    if not isinstance(rows,list) or not rows or not isinstance(sessions,list) or not sessions or not isinstance(report,dict):raise ValueError('missing history')
    ids=set();previous=None;counts={'ELITE_CANDIDATE':0,'DEMO_CANDIDATE':0,'WATCH_HIGH_PRIORITY':0}
    for r in rows:
        if not isinstance(r,dict):raise ValueError('invalid row')
        sid=r.get('specialist_id')
        if not isinstance(sid,str) or not sid or sid in ids:raise ValueError('duplicate identity')
        ids.add(sid)
        s=session(r.get('hour'));bonus=7 if s in ('LONDON_OPEN','LONDON_NY_OVERLAP','NEW_YORK') else 4 if s=='LONDON' else 0
        raw=min(Decimal(100),score(r.get('deployment_score'))*Decimal('.45')+score(r.get('confluence_score'))*Decimal('.45')+bonus)
        rounded=raw.quantize(Decimal('.000001'),rounding=ROUND_HALF_UP)
        decision='ELITE_CANDIDATE' if raw>=90 else 'DEMO_CANDIDATE' if raw>=80 else 'WATCH_HIGH_PRIORITY' if raw>=70 else 'WATCH_ONLY'
        if (r.get('refined_session'),r.get('session_bonus'),score(r.get('refined_opportunity_score')),r.get('refined_decision'))!=(s,bonus,rounded,decision):raise ValueError('refinement mismatch')
        if r.get('decision')!='WATCH_ONLY' or r.get('ORDER_SENT') is not False or any(r.get(k)!='FORBIDDEN' for k in ('REAL_ORDERS','FTMO_REAL','MT5_REAL')):raise ValueError('unsafe state')
        if previous is not None and raw>previous:raise ValueError('unsorted')
        previous=raw
        if decision in counts:counts[decision]+=1
    if report.get('OPPORTUNITIES_REFINED')!=len(rows) or report.get('SESSIONS_REGISTERED')!=len(sessions) or any(report.get(k)!=v for k,v in (({'ELITE_CANDIDATE':'ELITE_CANDIDATES','DEMO_CANDIDATE':'DEMO_CANDIDATES','WATCH_HIGH_PRIORITY':'WATCH_HIGH_PRIORITY'}[key],value) for key,value in counts.items())):raise ValueError('totals mismatch')
    if report.get('TOP10_REFINED')!=rows[:10] or report.get('ORDER_SENT') is not False or any(report.get(k)!='FORBIDDEN' for k in ('REAL_ORDERS','FTMO_REAL','MT5_REAL')):raise ValueError('unsafe report')
    return {'status':'HISTORICAL_RECONCILED','rows':len(rows),'sessions':len(sessions),'promotion_allowed':False,'order_send_allowed':False,'e2e_certified':False}
