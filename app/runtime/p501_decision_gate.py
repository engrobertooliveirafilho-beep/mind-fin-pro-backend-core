"""Historical P501 shadow classification; classifications never authorize execution."""
import json
import math
from pathlib import Path

BLOCKS = {'LIVE':'FORBIDDEN','REAL_BROKER':'DISABLED','REAL_ORDERS':'FORBIDDEN','FTMO_REAL':'FORBIDDEN','MT5_REAL':'FORBIDDEN'}

def classify(ranked):
    if not isinstance(ranked,list) or not ranked:
        raise ValueError('missing ranked shadow signals')
    output=[];seen=set()
    for row in ranked:
        if not isinstance(row,dict) or any(row.get(k)!=v for k,v in BLOCKS.items()):
            raise ValueError('unsafe shadow signal')
        eid=row.get('edge_id'); score=row.get('shadow_score')
        if not isinstance(eid,str) or not eid or eid in seen or isinstance(score,bool) or not isinstance(score,(int,float)) or not math.isfinite(score):
            raise ValueError('invalid shadow signal')
        if row.get('execution_mode')!='SHADOW_ONLY' or row.get('order_sent') is not False:
            raise ValueError('non-shadow execution mode')
        seen.add(eid)
        decision='HIGH_PRIORITY_DEMO' if score>=3 else 'DEMO_CANDIDATE' if score>=2 else 'WATCHLIST'
        output.append({**row,'decision':decision,'position_close_sent':False,**BLOCKS})
    return output

def run(ranked_path,out_path):
    rows=classify(json.loads(Path(ranked_path).read_text(encoding='utf-8')))
    out=Path(out_path);out.mkdir(parents=True,exist_ok=True)
    (out/'p501_shadow_decisions.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    return {'INPUT_SIGNALS':len(rows),'DEMO_CANDIDATES':sum(r['decision']!='WATCHLIST' for r in rows),'WATCHLIST':sum(r['decision']=='WATCHLIST' for r in rows),'ORDER_SENT':False,**BLOCKS}
