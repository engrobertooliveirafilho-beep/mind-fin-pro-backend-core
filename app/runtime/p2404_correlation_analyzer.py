"""P2404: causal synchronized daily realized-return correlation."""
from datetime import datetime
from math import sqrt

MODE="PAPER_ONLY"; REAL_ORDERS="FORBIDDEN"; FTMO_REAL="FORBIDDEN"

def _day(value):
    return datetime.fromisoformat(str(value).replace("Z","+00:00")).date().isoformat()

def daily_returns(closed_ledger,calendar_days,initial_equity=10000.0):
    days=sorted(set(str(d) for d in calendar_days))
    if not days: raise ValueError("Calendar required for synchronized returns")
    pnl_by_edge={}
    for r in closed_ledger:
        if r.get("mode")!="PAPER_ONLY" or r.get("real_orders")!="FORBIDDEN" or r.get("ftmo_real")!="FORBIDDEN":
            raise ValueError("Safety contract failed")
        edge=r["edge_id"]; day=_day(r["exit_time"])
        if day not in days: raise ValueError("Ledger exit day missing from synchronized market calendar")
        by_day=pnl_by_edge.setdefault(edge,{})
        by_day[day]=by_day.get(day,0.0)+float(r["pnl_cash"])
    result={}
    for edge,by_day in pnl_by_edge.items():
        equity=float(initial_equity); series={}
        for day in days:
            pnl=by_day.get(day,0.0); series[day]=pnl/equity if equity else 0.0; equity+=pnl
        result[edge]=series
    return result

def pearson(a,b,min_observations=20):
    pairs=[(float(x),float(y)) for x,y in zip(a,b) if x is not None and y is not None]
    if len(pairs)<min_observations: return None
    ax=[x for x,y in pairs]; by=[y for x,y in pairs]
    ma=sum(ax)/len(ax); mb=sum(by)/len(by)
    da=[x-ma for x in ax]; db=[y-mb for y in by]
    va=sum(x*x for x in da); vb=sum(y*y for y in db)
    if va==0 or vb==0: return None
    return sum(x*y for x,y in zip(da,db))/sqrt(va*vb)

def correlation_matrix(series,min_observations=20):
    edges=sorted(series); matrix={e:{} for e in edges}; pairs=[]
    for a in edges:
        for b in edges:
            if a==b: matrix[a][b]=1.0
            elif b in matrix[a]: matrix[a][b]=matrix[b][a]
            else:
                days=sorted(set(series[a])&set(series[b]))
                corr=pearson([series[a][d] for d in days],[series[b][d] for d in days],min_observations)
                matrix[a][b]=corr
                if a<b: pairs.append({"edge_a":a,"edge_b":b,"observations":len(days),"pearson":corr})
    return matrix,pairs

def safety_contract():
    return {"mode":MODE,"real_orders":REAL_ORDERS,"ftmo_real":FTMO_REAL,
            "runtime_allowed":False,"real_execution_allowed":False}
