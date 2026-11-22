"""P2305 FTMO digital twin: risk limits are not performance certification."""
from decimal import Decimal, InvalidOperation

def _number(value):
    if isinstance(value, bool):
        raise ValueError("P2305_INVALID_NUMBER")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("P2305_INVALID_NUMBER") from None
    if not result.is_finite() or result < 0:
        raise ValueError("P2305_INVALID_NUMBER")
    return result

def reconcile_twin(summary, state, rules):
    if not isinstance(summary, dict) or not isinstance(state, dict) or not isinstance(rules, dict):
        raise ValueError("P2305_INVALID_INPUT")
    for source in (summary, state):
        if source.get("mode") != "PAPER_ONLY" or source.get("real_orders") != "FORBIDDEN" or source.get("ftmo_real") != "FORBIDDEN":
            raise ValueError("P2305_UNSAFE_MODE")
    if summary.get("ftmo_twin_status") != "FTMO_TWIN_PASS" or state.get("status") != "FTMO_TWIN_PASS":
        raise ValueError("P2305_INVALID_STATUS")
    if rules.get("risk_block_only") != "TRUE" or rules.get("real_orders") != "FORBIDDEN" or rules.get("ftmo_real") != "FORBIDDEN":
        raise ValueError("P2305_UNSAFE_RULES")
    expected = {"daily_loss_limit_pct":"1.0", "total_loss_limit_pct":"5.0",
                "max_trades_day":"6", "max_trades_edge_day":"2",
                "max_exposure_lots":"0.01", "default_lot":"0.01"}
    for k, v in expected.items():
        if _number(rules.get(k)) != Decimal(v):
            raise ValueError("P2305_RULE_MISMATCH")
    consumed = _number(summary.get("trades_consumed"))
    if consumed != _number(state.get("trades_consumed")) or consumed != 0:
        raise ValueError("P2305_CONSUMPTION_UNVERIFIED")
    if _number(summary.get("trades_day")) != _number(state.get("trades_day")):
        raise ValueError("P2305_COUNT_MISMATCH")
    if _number(summary.get("daily_loss_pct")) > _number(rules["daily_loss_limit_pct"]) or _number(summary.get("total_loss_pct")) > _number(rules["total_loss_limit_pct"]):
        raise ValueError("P2305_RISK_LIMIT")
    return {"status":"RISK_CONFIGURATION_ONLY", "historical_twin_pass":True,
            "consumed_trades":0, "performance_certified":False,
            "ftmo_challenge_certified":False, "real_orders":"FORBIDDEN",
            "e2e_certified":False}
