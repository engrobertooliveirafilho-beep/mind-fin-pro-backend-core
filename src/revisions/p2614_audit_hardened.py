"""P2614 trade audit: offline, fail-closed, PAPER-only."""
import math


def audit_trades(trades):
    errors = []
    seen = set()
    for index, trade in enumerate(trades):
        if not isinstance(trade, dict):
            errors.append(f"{index}:INVALID_TRADE_RECORD")
            continue
        required = ("signal_i", "entry_i", "exit_i", "edge_id", "capital_after", "r")
        if any(key not in trade for key in required):
            errors.append(f"{index}:MISSING_REQUIRED_FIELD")
            continue
        signal, entry, exit_ = (trade[k] for k in ("signal_i", "entry_i", "exit_i"))
        if any(type(v) is not int or v < 0 for v in (signal, entry, exit_)):
            errors.append(f"{index}:INVALID_BAR_INDEX")
            continue
        if entry <= signal:
            errors.append(f"{index}:LOOKAHEAD_OR_SAME_BAR_ENTRY")
        if exit_ <= entry:
            errors.append(f"{index}:INVALID_EXIT_ORDER")
        if not isinstance(trade["edge_id"], str) or not trade["edge_id"].strip():
            errors.append(f"{index}:INVALID_EDGE_ID")
            continue
        key = (trade["edge_id"], entry, exit_)
        if key in seen:
            errors.append(f"{index}:DUPLICATE_TRADE")
        seen.add(key)
        if trade.get("real_execution_allowed") is not False:
            errors.append(f"{index}:REAL_EXEC_FLAG_NOT_FALSE")
        for field in ("capital_after", "r"):
            try:
                value = float(trade[field])
                if not math.isfinite(value) or (field == "capital_after" and value <= 0):
                    errors.append(f"{index}:INVALID_{field.upper()}")
            except (TypeError, ValueError, OverflowError):
                errors.append(f"{index}:INVALID_{field.upper()}")
    return {"errors": errors, "passed": not errors, "error_count": len(errors)}
