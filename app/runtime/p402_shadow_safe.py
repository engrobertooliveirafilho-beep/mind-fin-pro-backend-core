"""Fail-closed, PAPER-only P402 shadow routing; no broker or order dispatch."""
import json
import math
from pathlib import Path

BLOCKS={'LIVE':'FORBIDDEN','REAL_BROKER':'DISABLED','REAL_ORDERS':'FORBIDDEN','FTMO_REAL':'FORBIDDEN','MT5_REAL':'FORBIDDEN'}

def load_json(path):
    p=Path(path)
    if not p.is_file():
        raise FileNotFoundError(f'required P402 input missing: {p.name}')
    return json.loads(p.read_text(encoding='utf-8'))

def route_shadow(edges,positions):
    if not isinstance(edges,list) or not edges or not isinstance(positions,list):
        raise ValueError('invalid or empty P402 inputs')
    active=set()
    for p in positions:
        if not isinstance(p,dict) or not isinstance(p.get('symbol'),str) or not p['symbol'].strip():
            raise ValueError('invalid position')
        active.add(p['symbol'])
    routes=[]
    seen=set()
    for i,e in enumerate(edges):
        if not isinstance(e,dict):
            raise ValueError('invalid edge')
        eid=e.get('job_id')
        asset=e.get('asset')
        tf=e.get('timeframe') or e.get('target_timeframe')
        score=e.get('institutional_score')
        if not isinstance(eid,str) or not eid.strip() or eid in seen or not isinstance(asset,str) or not asset.strip() or not isinstance(tf,str) or not tf.strip() or isinstance(score,bool) or not isinstance(score,(int,float)) or not math.isfinite(score):
            raise ValueError('invalid edge identity, timeframe or score')
        if any(k in e and e[k]!=v for k,v in BLOCKS.items()):
            raise ValueError('unsafe historical edge')
        seen.add(eid)
        occupied=asset in active
        routes.append(dict(rank=i+1,edge_id=eid,asset=asset,timeframe=tf,family=e.get('family'),score=score,shadow_action='SHADOW_MONITOR_EXISTING_POSITION' if occupied else 'SHADOW_WATCH',reason='ASSET_ALREADY_OPEN' if occupied else 'NO_EXECUTION_SHADOW_MODE',order_sent=False,**BLOCKS))
    return routes

def run(source,positions,output):
    routes=route_shadow(load_json(source),load_json(positions))
    report=dict(STATUS='P402_SHADOW_VALIDATED',SHADOW_ROUTES=len(routes),ORDER_SENT=False,POSITION_CLOSE_SENT=False,**BLOCKS)
    out=Path(output)
    out.mkdir(parents=True,exist_ok=True)
    (out/'p402_shadow_routes.json').write_text(json.dumps(routes,indent=2),encoding='utf-8')
    (out/'p402_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report
