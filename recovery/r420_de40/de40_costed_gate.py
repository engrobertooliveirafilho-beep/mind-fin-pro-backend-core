"""R420 independent DE40 source validation and costed causal PAPER replay.
Not an original strategy; spread unit and execution venue must be verified.
"""
import csv,hashlib,math
from datetime import datetime
from pathlib import Path

def replay(path,expected_sha256,*,point_size=None,slippage_points=None,ftmo_rules=None):
    fail=lambda why:{'status':'BLOCKED','reason':why,'promotion_authorized':False,'ftmo_certified':False}
    if not isinstance(expected_sha256,str) or len(expected_sha256)!=64 or any(x not in '0123456789abcdefABCDEF' for x in expected_sha256):return fail('HASH_REQUIRED')
    if hashlib.sha256(Path(path).read_bytes()).hexdigest().lower()!=expected_sha256.lower():return fail('HASH_MISMATCH')
    if point_size is None or slippage_points is None or ftmo_rules is None:return fail('COST_AND_FTMO_CONTRACT_REQUIRED')
    if not all(isinstance(x,(float,int)) and math.isfinite(x) and x>=0 for x in (point_size,slippage_points)) or point_size==0:return fail('INVALID_COST_CONTRACT')
    rows=[]
    try:
        with open(path,newline='',encoding='utf-8-sig') as f:
            rd=csv.DictReader(f,delimiter=';')
            if not {'time','open','high','low','close','spread','symbol','timeframe'}.issubset(rd.fieldnames or []):return fail('SCHEMA')
            for x in rd:
                t=datetime.strptime(x['time'],'%Y.%m.%d %H:%M:%S')
                o,h,l,c,s=[float(x[k]) for k in ('open','high','low','close','spread')]
                if x['symbol']!='DE40' or not all(map(math.isfinite,(o,h,l,c,s))) or min(o,h,l,c)<=0 or l>min(o,c) or h<max(o,c) or s<0:return fail('BAD_CANDLE')
                if rows and t<=rows[-1][0]:return fail('NON_MONOTONIC')
                rows.append((t,c,s,x['timeframe']))
    except (ValueError,KeyError,TypeError,UnicodeError):return fail('PARSE')
    if len(rows)<30 or len({r[3] for r in rows})!=1:return fail('INSUFFICIENT')
    split=int(len(rows)*.7);gross=[];net=[]
    for i in range(split,len(rows)-1):
        prev,cur,nxt=rows[i-1][1],rows[i][1],rows[i+1][1]
        direction=(cur>prev)-(cur<prev)
        if not direction:continue
        g=direction*(nxt-cur)/cur
        cost=(rows[i][2]*point_size+2*slippage_points)/cur
        gross.append(g);net.append(g-cost)
    if not net:return fail('NO_SIGNALS')
    return {'status':'PAPER_COSTED_UNCERTIFIED','timeframe':rows[0][3],'signals':len(net),'gross_mean':sum(gross)/len(gross),'net_mean':sum(net)/len(net),'point_size_assumed':point_size,'slippage_points_assumed':slippage_points,'ftmo_rule_parameters':ftmo_rules,'timezone':'UNSPECIFIED','original_engine':False,'promotion_authorized':False,'ftmo_certified':False}
