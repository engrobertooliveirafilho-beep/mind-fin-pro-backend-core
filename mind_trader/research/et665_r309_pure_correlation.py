"""ET665.R309: pure, offline P2404 correlation calculations.
No file, network, broker, runtime, or import side effects. Historical inputs remain quarantined.
"""
import math
from collections import defaultdict
from itertools import combinations

def _pearson(a,b):
    if len(a)!=len(b) or len(a)<3:
        return None
    if any(not isinstance(x,(int,float)) or isinstance(x,bool) or not math.isfinite(x) for x in (*a,*b)):
        return None
    ma=sum(a)/len(a); mb=sum(b)/len(b)
    da=[x-ma for x in a]; db=[y-mb for y in b]
    va=sum(x*x for x in da); vb=sum(y*y for y in db)
    if va<=0 or vb<=0:
        return None
    return sum(x*y for x,y in zip(da,db))/math.sqrt(va*vb)

def _ranks(values):
    ordered=sorted(range(len(values)),key=lambda i:values[i])
    result=[0.0]*len(values)
    pos=0
    while pos<len(values):
        end=pos
        while end+1<len(values) and values[ordered[end+1]]==values[ordered[pos]]:
            end+=1
        rank=(pos+end+2)/2
        for j in range(pos,end+1):
            result[ordered[j]]=rank
        pos=end+1
    return result

def analyze_paper_series(rows):
    """Rows: edge_id, timestamp, pnl_r. Reject duplicates/nonfinite/invalid data.
    Returns statistics only; never promotion or certification.
    """
    data=defaultdict(dict)
    issues=[]
    try:
        for row in rows:
            if not isinstance(row,dict):
                raise ValueError("MALFORMED_ROW")
            eid=row.get("edge_id"); ts=row.get("timestamp"); val=row.get("pnl_r")
            if not isinstance(eid,str) or not eid.strip() or not isinstance(ts,str) or not ts.strip():
                raise ValueError("INVALID_KEYS")
            if isinstance(val,bool) or not isinstance(val,(int,float)) or not math.isfinite(val):
                raise ValueError("INVALID_PNL")
            if ts in data[eid]:
                raise ValueError("DUPLICATE_EDGE_TIMESTAMP")
            data[eid][ts]=float(val)
        if len(data)<2:
            raise ValueError("INSUFFICIENT_EDGES")
        stamps=sorted({ts for values in data.values() for ts in values})
        if len(stamps)<3:
            raise ValueError("INSUFFICIENT_TIMESTAMPS")
        pairs=[]
        for e1,e2 in combinations(sorted(data),2):
            a=[data[e1].get(t,0.0) for t in stamps]
            b=[data[e2].get(t,0.0) for t in stamps]
            p=_pearson(a,b)
            s=_pearson(_ranks(a),_ranks(b))
            overlap=len(set(data[e1])&set(data[e2]))/len(set(data[e1])|set(data[e2]))
            pairs.append({"edge_a":e1,"edge_b":e2,"pearson":p,"spearman":s,"overlap":overlap})
    except (ValueError,TypeError,OverflowError) as exc:
        issues.append(str(exc))
        pairs=[]
    return {"issues":issues,"pairs":pairs,"analysis_valid":not issues,
            "causal_signal_verified":False,"correlation_certified":False,
            "runtime_promotion_allowed":False,"status":"QUARANTINE"}
