"""Fail-closed adapter for historical P1636 research-loop metadata. No execution API."""
import json
from pathlib import Path

STAGES = ('DISCOVER','BACKTEST','VALIDATE','CATALOG_SPECIALIST','CLASSIFY_REGIME','MINE_CONFLUENCE','PROMOTE','QUARANTINE_WEAK_SPECIALISTS')
RESEARCH = STAGES[:6] + STAGES[7:]

def reconcile(loop, portfolio, evolution):
    if not isinstance(loop,dict) or not isinstance(portfolio,dict) or not isinstance(evolution,list) or not evolution:
        raise ValueError('missing/invalid evidence')
    if loop.get('STATUS')!='P1636_SELF_LEARNING_RESEARCH_LOOP_REGISTERED' or loop.get('LOOP')!=list(STAGES):
        raise ValueError('unrecognized loop contract')
    if loop.get('NEXT')!='ADD_P1625_TO_P1636_TO_DAILY_ORCHESTRATOR':
        raise ValueError('unexpected orchestration state')
    for doc in (loop,portfolio):
        if any(doc.get(k)!='FORBIDDEN' for k in ('REAL_ORDERS','FTMO_REAL','MT5_REAL')):
            raise ValueError('unsafe trading flags')
    if portfolio.get('ORDER_SENT') is not False or portfolio.get('DECISION')!='WATCH_ONLY':
        raise ValueError('portfolio not watch-only')
    ids=[row.get('specialist_id') for row in evolution if isinstance(row,dict)]
    if len(ids)!=len(evolution) or any(not isinstance(i,str) or not i for i in ids) or len(ids)!=len(set(ids)):
        raise ValueError('invalid specialists')
    return {'status':'RESEARCH_ONLY_RECONCILED','historical_stages':list(STAGES),
            'permitted_stages':list(RESEARCH),'blocked_stages':['PROMOTE'],
            'specialists':len(ids),'orchestrator_connected':False,
            'order_send_allowed':False,'e2e_certified':False}

def reconcile_files(loop_path,portfolio_path,evolution_path):
    return reconcile(*(json.loads(Path(p).read_text(encoding='utf-8')) for p in (loop_path,portfolio_path,evolution_path)))
