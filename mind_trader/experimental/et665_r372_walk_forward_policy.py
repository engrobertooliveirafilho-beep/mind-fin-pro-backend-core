"""ET665.R372 P2405F walk-forward historical policy gate.

Source: P2405E3 policy from Drive (2026-06-25). No promotion or broker access.
This is a policy checker, NOT a historical strategy certification.
"""
from decimal import Decimal, InvalidOperation
from app.agents._et665_r356_common import digest

POLICY={"pf":"1.5","winrate":"45","expectancy":"0","max_dd_r":"12",
        "passed_windows":4,"total_windows":5,"min_samples":30,
        "correlation_check_required":True}

def decimal(value):
    if isinstance(value,bool) or not isinstance(value,(str,int)):
        raise ValueError("invalid metric type")
    try: v=Decimal(str(value))
    except (InvalidOperation,ValueError) as exc: raise ValueError("invalid metric") from exc
    if not v.is_finite():raise ValueError("nonfinite metric")
    return v

def evaluate(windows,correlation_checked):
    if not isinstance(windows,list) or len(windows)!=5:
        raise ValueError("exactly five walk-forward windows required")
    if type(correlation_checked) is not bool:
        raise ValueError("correlation check must be explicit")
    ids=set();checks=[]
    for row in windows:
        if not isinstance(row,dict) or set(row)!={"window_id","samples","pf","winrate","expectancy","max_dd_r"}:
            raise ValueError("invalid window schema")
        wid=row["window_id"]
        if not isinstance(wid,str) or not wid or wid in ids:raise ValueError("invalid window identity")
        ids.add(wid)
        samples=row["samples"]
        if type(samples) is not int or samples<0:raise ValueError("invalid samples")
        pf=decimal(row["pf"]);wr=decimal(row["winrate"]);ex=decimal(row["expectancy"]);dd=decimal(row["max_dd_r"])
        if pf<0 or wr<0 or wr>100 or dd<0:raise ValueError("invalid metric range")
        passed=(samples>=30 and pf>=Decimal("1.5") and wr>=Decimal("45")
                and ex>0 and dd<=Decimal("12"))
        checks.append({"window_id":wid,"pass":passed})
    count=sum(c["pass"] for c in checks)
    eligible=count>=4 and correlation_checked
    result={"schema":"ET665.R372.v1","policy_origin":"P2405E3_DRIVE",
            "windows":checks,"passed_windows":count,"required_windows":4,
            "correlation_checked":correlation_checked,
            "research_gate":"PASS" if eligible else "BLOCKED",
            "historical_fills_verified":False,"strategy_promotion_authorized":False,
            "phase_b_certified":False,"real_orders":"FORBIDDEN"}
    result["evidence_sha256"]=digest(result)
    return result
