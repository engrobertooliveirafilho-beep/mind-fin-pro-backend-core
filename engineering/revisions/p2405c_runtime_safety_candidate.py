"""P2405C PAPER-only fail-closed hard gate. Isolated candidate; no runtime promotion."""
import math
MODE = "PAPER_ONLY"
REAL_ORDERS = "FORBIDDEN"
FTMO_REAL = "FORBIDDEN"

def runtime_allowed():
    return False

def hard_gate(metrics):
    if not isinstance(metrics, dict):
        return False
    values = {}
    for key in ("pf", "winrate", "expectancy", "max_dd_r", "edge_count"):
        value = metrics.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False
        try:
            if not math.isfinite(value):
                return False
        except (TypeError, ValueError, OverflowError):
            return False
        values[key] = value
    return (values["pf"] >= 1.5 and 45 <= values["winrate"] <= 100
            and values["expectancy"] > 0 and 0 <= values["max_dd_r"] <= 18
            and isinstance(values["edge_count"], int)
            and values["edge_count"] >= 5)

def safety_contract():
    return {"mode": MODE, "real_orders": REAL_ORDERS, "ftmo_real": FTMO_REAL,
            "runtime_allowed": False, "real_execution_allowed": False,
            "purpose": "offline_portfolio_risk_engine"}
