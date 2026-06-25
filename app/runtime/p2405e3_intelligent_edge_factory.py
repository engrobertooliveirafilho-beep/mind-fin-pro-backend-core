
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

FAMILIES=[
    "ATR","VOLATILITY","MOMENTUM","REVERSAL","BREAKOUT","FALSE_BREAKOUT",
    "LIQUIDITY","VWAP","EMA","SMA","RSI","ADX","BOLLINGER","TIME",
    "WEEKDAY","MULTITIMEFRAME","TREND","RANGE","CANDLE","MICROSTRUCTURE"
]

def runtime_allowed():
    return False

def candidate_allowed_for_runtime(candidate):
    return False

def safety_contract():
    return {
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "runtime_allowed":False,
        "real_execution_allowed":False,
        "purpose":"offline_intelligent_edge_factory",
        "families":FAMILIES,
    }
