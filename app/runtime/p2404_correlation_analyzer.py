"""P2404 offline edge-correlation and anti-redundancy engine.

Pure analysis only. Historical alignment semantics are preserved: absent edge
observations are zero-filled on the union timestamp grid, while Jaccard overlap
is reported separately so sparse co-occurrence is visible.
"""
from __future__ import annotations
from collections.abc import Mapping
from itertools import combinations
from math import isfinite, sqrt
from typing import Any

MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

class CorrelationInputError(ValueError):
    """Source series or metrics are malformed or unsafe."""

def safety_contract() -> dict[str, Any]:
    return {"mode":MODE,"real_orders":REAL_ORDERS,"ftmo_real":FTMO_REAL,
            "real_execution_allowed":False,"runtime_allowed":False,
            "purpose":"offline_edge_correlation_and_anti_redundancy"}

def runtime_allowed() -> bool:
    return False

def _number(value: Any, field: str) -> float:
    if isinstance(value,bool):
        raise CorrelationInputError(f"{field}: boolean is not numeric evidence")
    try:
        result=float(value)
    except (TypeError,ValueError,OverflowError) as exc:
        raise CorrelationInputError(f"{field}: finite numeric value required") from exc
    if not isfinite(result):
        raise CorrelationInputError(f"{field}: finite numeric value required")
    return result

def _validate_series(rows: Any) -> tuple[dict[str,dict[str,float]],list[str]]:
    if not isinstance(rows,(list,tuple)) or not rows:
        raise CorrelationInputError("rows: non-empty list required")
    edge_ts={}
    for index,row in enumerate(rows):
        if not isinstance(row,Mapping):
            raise CorrelationInputError(f"row[{index}]: mapping required")
        missing=[key for key in ("edge_id","timestamp","pnl_r") if key not in row]
        if missing:
            raise CorrelationInputError(f"row[{index}]: missing fields {','.join(missing)}")
        edge_id,timestamp=row["edge_id"],row["timestamp"]
        if not isinstance(edge_id,str) or not edge_id.strip():
            raise CorrelationInputError(f"row[{index}]: invalid edge_id")
        if not isinstance(timestamp,str) or not timestamp.strip():
            raise CorrelationInputError(f"row[{index}]: invalid timestamp")
        if row.get("mode",MODE)!=MODE or row.get("real_orders",REAL_ORDERS)!=REAL_ORDERS:
            raise CorrelationInputError(f"row[{index}]: PAPER safety contract mismatch")
        real_flag=row.get("real_execution_allowed",False)
        if row.get("ftmo_real",FTMO_REAL)!=FTMO_REAL or real_flag not in (False,"False","false",0):
            raise CorrelationInputError(f"row[{index}]: real execution authority detected")
        values=edge_ts.setdefault(edge_id,{})
        if timestamp in values:
            raise CorrelationInputError(f"duplicate edge/timestamp: {edge_id}/{timestamp}")
        values[timestamp]=_number(row["pnl_r"],f"row[{index}].pnl_r")
    if len(edge_ts)<2:
        raise CorrelationInputError("at least two distinct edge series are required")
    all_timestamps=sorted({stamp for series in edge_ts.values() for stamp in series})
    if len(all_timestamps)<3:
        raise CorrelationInputError("at least three distinct timestamps are required")
    return edge_ts,all_timestamps

def pearson(a:list[float],b:list[float])->float:
    if len(a)!=len(b) or len(a)<3:
        raise CorrelationInputError("Pearson requires equal series with at least three values")
    mean_a,mean_b=sum(a)/len(a),sum(b)/len(b)
    da=[x-mean_a for x in a]; db=[y-mean_b for y in b]
    var_a,var_b=sum(x*x for x in da),sum(y*y for y in db)
    if var_a<=0 or var_b<=0:
        return 0.0
    return sum(x*y for x,y in zip(da,db))/sqrt(var_a*var_b)

def rankdata(values:list[float])->list[float]:
    pairs=sorted((value,index) for index,value in enumerate(values))
    ranks=[0.0]*len(values); index=0
    while index<len(pairs):
        end=index
        while end+1<len(pairs) and pairs[end+1][0]==pairs[index][0]:
            end+=1
        average_rank=(index+end+2)/2
        for position in range(index,end+1):
            ranks[pairs[position][1]]=average_rank
        index=end+1
    return ranks

def spearman(a:list[float],b:list[float])->float:
    return pearson(rankdata(a),rankdata(b))

def overlap(edge_a:Mapping[str,float],edge_b:Mapping[str,float])->float:
    a,b=set(edge_a),set(edge_b); union=a|b
    return len(a&b)/len(union) if union else 0.0

def drawdown_flags(values:list[float])->list[float]:
    equity=0.0; peak=0.0; flags=[]
    for value in values:
        equity+=value; peak=max(peak,equity)
        flags.append(1.0 if peak-equity>0 else 0.0)
    return flags

def _validate_stats(stats_rows:Any,edge_ids:set[str])->dict[str,dict[str,float]]:
    if stats_rows is None:
        return {}
    if not isinstance(stats_rows,(list,tuple)):
        raise CorrelationInputError("stats_rows: list required")
    stats={}
    for index,row in enumerate(stats_rows):
        if not isinstance(row,Mapping):
            raise CorrelationInputError(f"stats[{index}]: mapping required")
        edge_id=row.get("edge_id")
        if not isinstance(edge_id,str) or edge_id not in edge_ids:
            raise CorrelationInputError(f"stats[{index}]: unknown edge_id")
        if edge_id in stats:
            raise CorrelationInputError(f"stats[{index}]: duplicate edge_id")
        stats[edge_id]={key:_number(row.get(key),f"stats[{index}].{key}")
                        for key in ("pf","winrate","expectancy","net_r","max_dd_r","trades")}
    return stats

def analyze_correlation(rows:Any,stats_rows:Any=None,*,threshold:float=0.75)->dict[str,Any]:
    """Measure Pearson, Spearman, timestamp overlap and drawdown synchronization.

    Correlation uses the historical union-grid convention (no-trade timestamp=0).
    Pairwise overlap is separately reported and participates in redundancy scoring.
    The result is research-only and never grants runtime permission.
    """
    threshold_value=_number(threshold,"threshold")
    if not 0.0<=threshold_value<=1.0:
        raise CorrelationInputError("threshold must be within 0..1")
    edge_ts,all_timestamps=_validate_series(rows)
    edge_ids=sorted(edge_ts)
    aligned={edge_id:[edge_ts[edge_id].get(stamp,0.0) for stamp in all_timestamps] for edge_id in edge_ids}
    dd_map={edge_id:drawdown_flags(aligned[edge_id]) for edge_id in edge_ids}
    pairs=[]; pair_lookup={}
    for edge_a,edge_b in combinations(edge_ids,2):
        a,b=aligned[edge_a],aligned[edge_b]
        p=pearson(a,b); sp=spearman(a,b); ov=overlap(edge_ts[edge_a],edge_ts[edge_b])
        dd_sync=pearson(dd_map[edge_a],dd_map[edge_b])
        redundancy=max(abs(p),abs(sp),ov,abs(dd_sync))
        pair_lookup[frozenset((edge_a,edge_b))]=redundancy
        pairs.append({"edge_a":edge_a,"edge_b":edge_b,"pearson":round(p,6),
                      "spearman":round(sp,6),"overlap":round(ov,6),
                      "drawdown_sync":round(dd_sync,6),"redundancy_score":round(redundancy,6),
                      "redundant":redundancy>=threshold_value,"mode":MODE,
                      "real_orders":REAL_ORDERS,"ftmo_real":FTMO_REAL,
                      "real_execution_allowed":False})
    stats=_validate_stats(stats_rows,set(edge_ids))
    quality={}
    for edge_id in edge_ids:
        st=stats.get(edge_id)
        if st is None:
            continue
        quality[edge_id]=round(min(st["pf"]/2.5,1)*30
            +min(st["winrate"]/65,1)*15
            +min(max(st["expectancy"],0)/0.30,1)*25
            +min(st["trades"]/220,1)*10
            +max(0,20-min(st["max_dd_r"]/6,1)*20),6)
    selected=[]
    if stats:
        for edge_id in sorted(quality,key=lambda key:-quality[key]):
            if all(pair_lookup.get(frozenset((edge_id,chosen)),0.0)<threshold_value for chosen in selected):
                selected.append(edge_id)
    selected_rows=[]
    for edge_id in selected:
        selected_rows.append({"edge_id":edge_id,"quality_score":quality[edge_id],**stats[edge_id],
            "selection_status":"ANTI_REDUNDANCY_SELECTED","mode":MODE,
            "real_orders":REAL_ORDERS,"ftmo_real":FTMO_REAL,"real_execution_allowed":False})
    redundant_pairs=sum(pair["redundant"] for pair in pairs)
    avg_abs_pearson=round(sum(abs(pair["pearson"]) for pair in pairs)/len(pairs),6) if pairs else 0.0
    max_redundancy=round(max((pair["redundancy_score"] for pair in pairs),default=0.0),6)
    return {"mission":"P2404_CORRELATION_ANALYZER","mode":MODE,"real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,"edges_input":len(edge_ids),"timestamps":len(all_timestamps),
        "pairwise_tests":len(pairs),"redundant_pairs":redundant_pairs,
        "avg_abs_pearson":avg_abs_pearson,"max_redundancy":max_redundancy,
        "anti_redundancy_selected":len(selected),"selected_edges":selected,
        "pairwise":pairs,"selected_pool":selected_rows,"correlation_calculated":True,
        "runtime_promotion_allowed":False,"runtime_allowed":False,"real_execution_allowed":False,
        "certification":"OFFLINE_ANALYSIS_ONLY"}
