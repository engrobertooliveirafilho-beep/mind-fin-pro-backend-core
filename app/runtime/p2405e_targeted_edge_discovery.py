
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
        "runtime_allowed":False,
        "real_execution_allowed":False,
        "purpose":"offline_targeted_edge_discovery",
    }

def candidate_allowed_for_runtime(candidate):
    return False
