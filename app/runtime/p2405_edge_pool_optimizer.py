
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

def runtime_allowed():
    return False

def safety_contract():
    return {
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "real_execution_allowed":False,
        "runtime_allowed":False,
        "purpose":"offline_edge_pool_optimization",
    }
