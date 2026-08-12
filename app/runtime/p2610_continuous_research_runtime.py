
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
        "purpose":"continuous_offline_edge_research"
    }

def next_cycle():
    return {
        "route":"OFFLINE_RESEARCH_ONLY",
        "real_execution_allowed":False,
        "next_required":"NEW_DATASET_OR_NEXT_RESEARCH_BATCH"
    }
