"""ET665 R434: offline fail-closed PAPER directional consensus. No broker imports."""
import math
from datetime import datetime, timezone

def decide(context, votes, policy, now=None):
    blocked = lambda reason: {"allowed": False, "route": "OBSERVE_ONLY", "reason": reason, "real_execution_allowed": False}
    if not isinstance(context, dict) or not isinstance(policy, dict) or not isinstance(votes, list): return blocked("INVALID_INPUT")
    if any(policy.get(k) != v for k,v in (("mode","PAPER_ONLY"),("real_orders","FORBIDDEN"),("ftmo_real","FORBIDDEN"),("real_execution_allowed",False))): return blocked("SAFETY_LOCK_FAILED")
    if context.get("symbol") != policy.get("allowed_symbol") or context.get("timeframe") not in policy.get("allowed_timeframes",[]): return blocked("SYMBOL_OR_TIMEFRAME_INVALID")
    if context.get("session") not in policy.get("allowed_sessions",[]) or context.get("regime") not in policy.get("allowed_regimes",[]): return blocked("SESSION_OR_REGIME_INVALID")
    if context.get("direction") not in ("BUY_PAPER","SELL_PAPER"): return blocked("DIRECTION_INVALID")
    try:
        now=now or datetime.now(timezone.utc)
        stamp=datetime.fromisoformat(context["timestamp"].replace("Z","+00:00"))
        if stamp.tzinfo is None or not 0 <= (now-stamp).total_seconds() <= 300: return blocked("STALE_CONTEXT")
        quorum=int(policy["min_context_matches"]); min_weight=float(policy["min_weight_sum"]); min_confidence=float(policy["min_confidence"])
        if quorum<2 or not 0<min_weight<=1 or not 0<min_confidence<=1: return blocked("INVALID_POLICY")
        ids=set();total=0.0
        for vote in votes:
            if not isinstance(vote,dict) or not isinstance(vote.get("edge_id"),str) or not vote["edge_id"] or vote["edge_id"] in ids: return blocked("INVALID_OR_DUPLICATE_VOTE")
            ids.add(vote["edge_id"])
            if vote.get("direction")!=context["direction"] or vote.get("symbol")!=context["symbol"] or vote.get("timeframe")!=context["timeframe"]: return blocked("CONTRADICTORY_VOTE")
            weight=float(vote["weight"])
            if not math.isfinite(weight) or not 0<weight<=1: return blocked("INVALID_WEIGHT")
            vt=datetime.fromisoformat(vote["timestamp"].replace("Z","+00:00"))
            if vt.tzinfo is None or not 0 <= (now-vt).total_seconds() <= 300: return blocked("STALE_VOTE")
            total+=weight
        if len(votes)<quorum or total<min_weight or total<min_confidence or total>1.000001: return blocked("CONSENSUS_NOT_REACHED")
    except (ValueError,TypeError,KeyError,OverflowError): return blocked("INVALID_EVIDENCE")
    return {"allowed":True,"route":"PAPER_SIGNAL_CANDIDATE","reason":"DIRECTIONAL_CONSENSUS","votes":len(votes),"confidence":round(total,6),"real_execution_allowed":False}
