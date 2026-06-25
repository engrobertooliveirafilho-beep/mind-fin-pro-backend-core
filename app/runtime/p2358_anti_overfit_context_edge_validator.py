from __future__ import annotations

def anti_overfit_validate(edge: dict) -> dict:
    symbols_tested = int(edge.get("symbols_tested", 0))
    years_tested = int(edge.get("years_tested", 0))
    regimes_tested = int(edge.get("regimes_tested", 0))
    oos_pf = float(edge.get("out_of_sample_profit_factor", 0))
    oos_payoff = float(edge.get("out_of_sample_payoff", 0))
    oos_expectancy = float(edge.get("out_of_sample_expectancy", 0))
    dd = float(edge.get("max_drawdown", 100))
    parameter_sensitivity = float(edge.get("parameter_sensitivity", 100))

    passed = (
        symbols_tested >= 3 and
        years_tested >= 3 and
        regimes_tested >= 3 and
        oos_pf >= 1.5 and
        oos_payoff >= 3.0 and
        oos_expectancy > 0 and
        dd <= 10 and
        parameter_sensitivity <= 35
    )

    failures = []
    if symbols_tested < 3: failures.append("LOW_SYMBOL_DIVERSITY")
    if years_tested < 3: failures.append("LOW_YEAR_COVERAGE")
    if regimes_tested < 3: failures.append("LOW_REGIME_COVERAGE")
    if oos_pf < 1.5: failures.append("LOW_OOS_PROFIT_FACTOR")
    if oos_payoff < 3.0: failures.append("PAYOFF_BELOW_3_TO_1")
    if oos_expectancy <= 0: failures.append("NEGATIVE_OOS_EXPECTANCY")
    if dd > 10: failures.append("DRAWDOWN_TOO_HIGH")
    if parameter_sensitivity > 35: failures.append("PARAMETER_OVERFITTING_RISK")

    return {
        "edge_id": edge.get("edge_id", "UNKNOWN"),
        "context_edge": edge.get("context_edge", "UNKNOWN"),
        "anti_overfit_passed": passed,
        "decision": "PROMOTE" if passed else "REJECT_OR_KEEP_IN_OBSERVATION",
        "failures": failures,
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }

def health() -> dict:
    return {
        "status": "OK",
        "engine": "P2358_ANTI_OVERFIT_CONTEXT_EDGE_VALIDATOR",
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }
