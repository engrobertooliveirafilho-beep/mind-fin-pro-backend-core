"""P2301: audit historical spread/slippage evidence, fail closed on PF scale mismatch."""
from decimal import Decimal, InvalidOperation

def _decimal(value):
    if isinstance(value, bool):
        raise ValueError("P2301_INVALID_NUMBER")
    try:
        n = Decimal(str(value).replace(",", "."))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("P2301_INVALID_NUMBER") from None
    if not n.is_finite() or n < 0:
        raise ValueError("P2301_INVALID_NUMBER")
    return n

def reconcile_stress(rows, expected_p10):
    if not isinstance(rows, (list, tuple)) or len(rows) != 36:
        raise ValueError("P2301_INVALID_SCENARIO_COUNT")
    if not isinstance(expected_p10, dict) or len(expected_p10) != 4:
        raise ValueError("P2301_MISSING_BASELINE")
    groups = {}
    scale_errors = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("P2301_INVALID_ROW")
        key = (row.get("family"), row.get("confirmation"))
        if key not in expected_p10 or row.get("symbol") != "GER40" or row.get("timeframe") != "H1" or row.get("exit_model") != "TIME_EXIT" or row.get("mode") != "PAPER_ONLY" or row.get("real_orders") != "FORBIDDEN":
            raise ValueError("P2301_UNSAFE_ROW")
        base = _decimal(row.get("base_pf_p10"))
        reference = _decimal(expected_p10[key])
        penalty = _decimal(row.get("total_penalty"))
        adjusted = _decimal(row.get("adjusted_pf"))
        if abs((base - penalty) - adjusted) > Decimal("0.0001"):
            raise ValueError("P2301_ARITHMETIC_MISMATCH")
        if abs(base - reference) > Decimal("0.0001"):
            scale_errors.append({"strategy": key, "historical_base": str(base), "expected_base": str(reference)})
        groups.setdefault(key, set()).add(row.get("scenario"))
    if any(len(v) != 9 for v in groups.values()) or len(groups) != 4:
        raise ValueError("P2301_INCOMPLETE_SCENARIOS")
    return {"status": "HISTORICAL_PF_SCALE_MISMATCH" if scale_errors else "BASELINE_RECONCILED_REPLAY_REQUIRED",
            "scenarios": 36, "affected_rows": len(scale_errors),
            "historical_passes_certified": 0, "promotion_allowed": False,
            "trade_level_cost_replay_required": True, "e2e_certified": False}
