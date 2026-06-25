
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

def runtime_allowed():
    return False

def hard_gate(metrics):
    return (
        metrics.get("edge_count",0) >= 5 and
        metrics.get("pf",0) >= 1.5 and
        metrics.get("winrate",0) >= 45 and
        metrics.get("expectancy",0) > 0 and
        metrics.get("max_dd_r",999) <= 12 and
        metrics.get("max_redundancy",999) < 0.75
    )

def safety_contract():
    return {
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "real_execution_allowed":False,
        "runtime_allowed":False,
        "purpose":"repaired_offline_edge_pool_optimization",
    }
