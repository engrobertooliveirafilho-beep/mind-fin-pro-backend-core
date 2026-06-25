
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"
REQUIRED_SCHEMA=["edge_id","timestamp","signal","pnl_r","entry_time","exit_time","holding_bars"]

def safety_contract():
    return {
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "real_execution_allowed":False,
        "runtime_allowed":False,
        "purpose":"offline_correlation_input",
    }

def validate_row(row):
    return all(k in row for k in REQUIRED_SCHEMA)
