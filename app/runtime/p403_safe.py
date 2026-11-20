"""P403/P404 PAPER-only shadow scoring, no broker access."""
import json
import math
from pathlib import Path

BLOCKS={'LIVE':'FORBIDDEN','REAL_BROKER':'DISABLED','REAL_ORDERS':'FORBIDDEN','FTMO_REAL':'FORBIDDEN','MT5_REAL':'FORBIDDEN'}

def score_routes(routes,evidence):
    if not isinstance(routes,list) or not routes or not isinstance(evidence,dict):
        raise ValueError('missing or invalid P403 input')
    if any(evidence.get(k) != v for k,v in BLOCKS.items()):
        raise ValueError('unsafe demo evidence')
    if not isinstance(evidence.get('POSITIONS_TOTAL'),int) or isinstance(evidence['POSITIONS_TOTAL'],bool) or evidence['POSITIONS_TOTAL']<0:
        raise ValueError('invalid position count')
    scored=[]
    seen=set()
    for r in routes:
        if not isinstance(r,dict) or any(r.get(k)!=v for k,v in BLOCKS.items()) or r.get('order_sent') is not False:
            raise ValueError('unsafe shadow route')
        eid=r.get('edge_id'); score=r.get('score')
        if not isinstance(eid,str) or not eid or eid in seen or isinstance(score,bool) or not isinstance(score,(int,float)) or not math.isfinite(score):
            raise ValueError('invalid route identity or score')
        seen.add(eid)
        if not isinstance(r.get('timeframe'),str) or not r['timeframe']:
            raise ValueError('invalid timeframe')
        final=round(score+(0.10 if r['timeframe'] in ('M5','M15','M30','H1') else 0)-(0.05 if r.get('family')=='RSI_REVERSION' else 0),6)
        scored.append({**r,'shadow_score':final,'journal_status':'RECORDED','execution_mode':'SHADOW_ONLY',**BLOCKS})
    return sorted(scored,key=lambda x:(-x['shadow_score'],x['edge_id']))

def run(routes_path,evidence_path,out_path):
    routes=json.loads(Path(routes_path).read_text(encoding='utf-8'))
    evidence=json.loads(Path(evidence_path).read_text(encoding='utf-8'))
    ranked=score_routes(routes,evidence)
    out=Path(out_path);out.mkdir(parents=True,exist_ok=True)
    (out/'p404_shadow_signal_ranked.json').write_text(json.dumps(ranked,indent=2),encoding='utf-8')
    report=dict(STATUS='P403_SHADOW_SCORING_VALIDATED',SHADOW_SIGNALS_SCORED=len(ranked),ORDER_SENT=False,POSITION_CLOSE_SENT=False,**BLOCKS)
    (out/'p403_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report
