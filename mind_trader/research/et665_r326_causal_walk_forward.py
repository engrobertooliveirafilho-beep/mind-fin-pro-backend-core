"""ET665 R326 — fail-closed offline empirical walk-forward metrics; no trading."""
import csv
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path

def evaluate_csv(path, *, provenance_verified=False):
    result = {"decision":"BLOCKED","runtime_promotion_allowed":False,
              "real_execution_allowed":False,"issues":[],"edges":{}}
    if provenance_verified is not True:
        result["issues"].append("CAUSAL_PROVENANCE_NOT_VERIFIED")
        return result
    p=Path(path)
    if p.is_symlink() or not p.is_file():
        result["issues"].append("INVALID_SOURCE")
        return result
    try:
        with p.open("r",encoding="utf-8-sig",newline="") as fh:
            reader=csv.DictReader(fh)
            if reader.fieldnames != ["edge_id","timestamp","pnl_r"]:
                result["issues"].append("INVALID_HEADER")
                return result
            trades=defaultdict(list)
            seen=set()
            for i,row in enumerate(reader):
                if i>=100_000 or None in row or None in row.values():
                    result["issues"].append("INVALID_ROWS")
                    return result
                edge=row["edge_id"]
                stamp=datetime.fromisoformat(row["timestamp"].replace("Z","+00:00"))
                pnl=float(row["pnl_r"])
                if not edge or not math.isfinite(pnl) or abs(pnl)>1000:
                    result["issues"].append("INVALID_TRADE")
                    return result
                key=(edge,stamp)
                if key in seen:
                    result["issues"].append("DUPLICATE_EDGE_TIMESTAMP")
                    return result
                seen.add(key)
                trades[edge].append((stamp,pnl))
    except (OSError,ValueError,TypeError,UnicodeError,csv.Error):
        result["issues"].append("UNREADABLE_OR_INVALID_SOURCE")
        return result
    if not trades:
        result["issues"].append("NO_TRADES")
        return result
    for edge,data in trades.items():
        if data!=sorted(data,key=lambda x:x[0]):
            result["issues"].append("NONCHRONOLOGICAL_TRADES")
            return result
        n=len(data)
        if n<30:
            result["edges"][edge]={"decision":"BLOCKED_INSUFFICIENT_SAMPLES","samples":n}
            continue
        windows=[data[n*k//5:n*(k+1)//5] for k in range(5)]
        values=[x for _,x in data]
        wins=[x for x in values if x>0]
        losses=[x for x in values if x<0]
        pf=sum(wins)/abs(sum(losses)) if losses else None
        wr=len(wins)/n*100
        exp=sum(values)/n
        eq=peak=dd=0.0
        for x in values:
            eq+=x
            peak=max(peak,eq)
            dd=max(dd,peak-eq)
        passed=sum(sum(x for _,x in window)>0 for window in windows)
        result["edges"][edge]={"samples":n,"pf":pf,"winrate":wr,"expectancy":exp,
                              "max_dd_r":dd,"positive_windows":passed,
                              "research_gates_pass":bool(pf is not None and pf>=1.5 and wr>=45 and exp>0 and dd<=12 and passed>=4),
                              "decision":"RESEARCH_ONLY_NOT_CERTIFIED"}
    result["issues"].append("INDEPENDENT_OOS_COSTS_AND_CAUSALITY_PENDING")
    return result
