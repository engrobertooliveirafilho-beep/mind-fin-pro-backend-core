
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

def runtime_allowed():
    return False

def hard_gate(metrics):
    return (
        metrics.get("pf",0) >= 1.5 and
        metrics.get("winrate",0) >= 45 and
        metrics.get("expectancy",0) > 0 and
        metrics.get("max_dd_r",999) <= 18 and
        metrics.get("edge_count",0) >= 5
    )

def safety_contract():
    return {
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "runtime_allowed":False,
        "real_execution_allowed":False,
        "purpose":"offline_portfolio_risk_engine",
    }
