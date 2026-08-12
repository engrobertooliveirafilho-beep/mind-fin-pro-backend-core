def audit_trades(trades):
    errors=[]
    seen=set()
    for t in trades:
        if t["entry_i"] <= t["signal_i"]:
            errors.append("LOOKAHEAD_OR_SAME_BAR_ENTRY")
        if t["exit_i"] <= t["entry_i"]:
            errors.append("INVALID_EXIT_ORDER")
        key=(t["edge_id"],t["entry_i"],t["exit_i"])
        if key in seen:
            errors.append("DUPLICATE_TRADE")
        seen.add(key)
        if t.get("real_execution_allowed") is not False:
            errors.append("REAL_EXEC_FLAG_NOT_FALSE")
        if t["capital_after"]<=0:
            errors.append("NEGATIVE_OR_ZERO_CAPITAL")
    return {
        "errors":errors,
        "passed":len(errors)==0,
        "error_count":len(errors)
    }
