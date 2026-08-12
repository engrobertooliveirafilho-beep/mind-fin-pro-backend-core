import json, statistics
from pathlib import Path
from datetime import datetime, UTC

def walk_forward_authority(windows):
    if len(windows)<3:
        return {"decision":"WALK_FORWARD_INSUFFICIENT_WINDOWS","passed":False,"production":"BLOCKED","edge_claim":"NONE"}
    expectancies=[float(w.get("expectancy",0)) for w in windows]
    pfs=[float(w.get("profit_factor",0)) for w in windows]
    positive=sum(1 for x in expectancies if x>0)
    avg_exp=statistics.mean(expectancies)
    min_pf=min(pfs)
    consistency=positive/len(windows)
    passed=avg_exp>0 and min_pf>1.05 and consistency>=0.67
    return {
        "authority":"P8.81_WALK_FORWARD_AUTHORITY",
        "windows":len(windows),
        "avg_expectancy":avg_exp,
        "min_profit_factor":min_pf,
        "positive_window_ratio":consistency,
        "passed":passed,
        "decision":"WALK_FORWARD_PASS_RESEARCH_ONLY" if passed else "WALK_FORWARD_REJECT_OR_RETEST",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }

def save_walk_forward_authority(report,path="mind_trader/reports/P8.81_walk_forward_authority.json"):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return path
