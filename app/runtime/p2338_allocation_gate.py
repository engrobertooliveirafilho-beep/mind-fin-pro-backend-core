"""P2338 PAPER-only capital allocation simulation gate.

No broker/API calls and no capital movement. Missing statistical policy blocks allocation.
"""
from decimal import Decimal, InvalidOperation

def simulate_allocation(*, ranking, rebalance, policy, capital):
    if not all(isinstance(x,dict) for x in (ranking,rebalance,policy)):
        raise ValueError("P2338_INVALID_INPUT")
    if ranking.get("mode")!="PAPER_ONLY" or ranking.get("real_orders")!="FORBIDDEN" or ranking.get("ftmo_real")!="FORBIDDEN":
        raise ValueError("P2338_UNSAFE_MODE")
    if rebalance.get("gate_decision")!="NO_REBALANCE":
        raise ValueError("P2338_REBALANCE_GATE_MISMATCH")
    if ranking.get("rankable_symbols")!="0" or ranking.get("total_trades")!="1":
        raise ValueError("P2338_RANKING_EVIDENCE_MISMATCH")
    if policy.get("authority")!="APPROVED_POLICY_ARTIFACT" or not isinstance(policy.get("min_closed_trades_per_symbol"),int) or policy["min_closed_trades_per_symbol"]<=0:
        return {"status":"BLOCKED_MISSING_APPROVED_SAMPLE_POLICY","allocation":{},"capital_allocated":0,"orders_authorized":0}
    if not isinstance(capital,str):
        raise ValueError("P2338_CAPITAL_MUST_BE_STRING")
    try:
        amount=Decimal(capital)
    except InvalidOperation:
        raise ValueError("P2338_INVALID_CAPITAL") from None
    if not amount.is_finite() or amount<=0:
        raise ValueError("P2338_INVALID_CAPITAL")
    # Current evidence: one trade, zero rankable symbols. No allocation possible.
    if int(ranking["total_trades"]) < policy["min_closed_trades_per_symbol"] or int(ranking["rankable_symbols"]) == 0:
        return {"status":"BLOCKED_INSUFFICIENT_FORWARD_SAMPLE","allocation":{},"capital_allocated":0,"orders_authorized":0}
    return {"status":"BLOCKED_NO_APPROVED_ALLOCATION_MODEL","allocation":{},"capital_allocated":0,"orders_authorized":0}
