import math

def _finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(float(value))
    except (OverflowError, TypeError, ValueError):
        return False

def audit_trades(trades):
    errors = []
    if not isinstance(trades, (list, tuple)):
        return {"errors": ["INVALID_TRADES_COLLECTION"], "passed": False, "error_count": 1}

    seen = set()
    required = ("signal_i", "entry_i", "exit_i", "edge_id", "capital_before", "capital_after", "pnl_usd", "r", "real_execution_allowed")
    for index, trade in enumerate(trades):
        if not isinstance(trade, dict):
            errors.append(f"INVALID_TRADE_RECORD:{index}")
            continue
        missing = [key for key in required if key not in trade]
        if missing:
            errors.append(f"MISSING_FIELDS:{index}:{','.join(missing)}")
            continue

        signal_i, entry_i, exit_i = trade["signal_i"], trade["entry_i"], trade["exit_i"]
        indices = (signal_i, entry_i, exit_i)
        valid_indices = all(type(value) is int and value >= 0 for value in indices)
        if not valid_indices:
            errors.append(f"INVALID_BAR_INDEX:{index}")
        elif entry_i <= signal_i:
            errors.append("LOOKAHEAD_OR_SAME_BAR_ENTRY")
        elif exit_i <= entry_i:
            errors.append("INVALID_EXIT_ORDER")

        edge_id = trade["edge_id"]
        if not isinstance(edge_id, str) or not edge_id.strip():
            errors.append(f"INVALID_EDGE_ID:{index}")
        elif valid_indices:
            key = (edge_id, entry_i, exit_i)
            if key in seen:
                errors.append("DUPLICATE_TRADE")
            seen.add(key)

        if trade.get("real_execution_allowed") is not False:
            errors.append("REAL_EXEC_FLAG_NOT_FALSE")

        for field in ("capital_before", "capital_after", "pnl_usd", "r"):
            if not _finite_number(trade[field]):
                errors.append(f"INVALID_NUMERIC:{index}:{field}")
        for field in ("capital_before", "capital_after"):
            value = trade[field]
            if _finite_number(value) and value <= 0:
                errors.append("NEGATIVE_OR_ZERO_CAPITAL")

    return {"errors": errors, "passed": len(errors) == 0, "error_count": len(errors)}
