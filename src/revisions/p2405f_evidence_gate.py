"""P2405F historical hash-generated metrics are not proof of walk-forward performance."""
import math

def audit_p2405f_promotion(record, verified_trades=None, verified_windows=None):
    reasons=[]
    if not isinstance(record,dict):
        return {"certified":False,"runtime_allowed":False,"reasons":["INVALID_RECORD"]}
    if record.get("mode")!="PAPER_ONLY" or record.get("real_orders")!="FORBIDDEN" or record.get("ftmo_real")!="FORBIDDEN" or record.get("real_execution_allowed") is not False:
        reasons.append("GOVERNANCE_FAILURE")
    if record.get("decision") not in ("PROMOTE_IDEAL","PROMOTE_MAX_DD"):
        reasons.append("NOT_PROMOTED")
    for key in ("pf","winrate","expectancy","max_dd_r"):
        try:
            if not math.isfinite(float(record[key])): raise ValueError()
        except (KeyError,TypeError,ValueError,OverflowError):
            reasons.append("INVALID_"+key.upper())
    for key in ("samples","passed_windows"):
        if type(record.get(key)) is not int or record[key]<0:
            reasons.append("INVALID_"+key.upper())
    if not isinstance(verified_trades,(list,tuple)) or not verified_trades:
        reasons.append("MISSING_VERIFIED_TRADES")
    if not isinstance(verified_windows,(list,tuple)) or not verified_windows:
        reasons.append("MISSING_VERIFIED_WINDOWS")
    reasons.append("METRICS_NOT_RECOMPUTED")
    return {"certified":False,"runtime_allowed":False,"reasons":reasons}
