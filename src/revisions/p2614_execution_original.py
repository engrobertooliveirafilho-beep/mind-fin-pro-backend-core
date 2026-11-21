MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

def edge_hold(edge):
    rm=edge.get("risk_model","")
    tf=edge.get("timeframe","H1")
    if rm=="TIME_STOP": return 4
    if rm=="TRAILING": return 6
    if rm=="PARTIAL_TP": return 8
    if tf=="M5": return 3
    if tf=="M30": return 8
    if tf=="H1": return 12
    return 6

def edge_signal(edge, ft):
    fam=edge.get("family","")
    direction=edge.get("direction","BUY_PAPER")
    if edge.get("session") and edge["session"]!=ft["session"]:
        return False
    if edge.get("regime") and edge["regime"] not in [ft["trend"],ft["regime"],"BALANCE"]:
        return False
    if fam in ["LIQUIDITY","FALSE_BREAKOUT"]:
        return ft["wick_ratio"]>=0.38
    if fam in ["VOLATILITY","ATR"]:
        return ft["atr"]>=ft["atr_med"]
    if fam in ["MOMENTUM","TREND"]:
        return (direction=="BUY_PAPER" and ft["trend"]=="TREND_UP") or (direction=="SELL_PAPER" and ft["trend"]=="TREND_DOWN")
    if fam in ["REVERSAL","RANGE","CLOSE_REVERSAL"]:
        return ft["wick_ratio"]>=0.30 and ft["body_ratio"]<=0.65
    if fam in ["BREAKOUT","OPEN_RANGE"]:
        return ft["body_ratio"]>=0.55 and ft["atr"]>=ft["atr_med"]*0.8
    if fam in ["DD_HEDGE","LOSS_STREAK_BREAKER"]:
        return ft["regime"]=="LOW_VOL" or ft["wick_ratio"]>=0.42
    if fam in ["MICROSTRUCTURE","CANDLE"]:
        return ft["body_ratio"]>=0.45 or ft["wick_ratio"]>=0.45
    return True

def simulate_fill(edge, candles, features, i, spread_r=0.03, slippage_r=0.02, commission_r=0.01):
    hold=edge_hold(edge)
    entry_i=i+1
    exit_i=entry_i+hold
    if exit_i>=len(candles):
        return None
    ft=features.get(i)
    if not ft or not edge_signal(edge,ft):
        return None

    entry=candles[entry_i]
    exitc=candles[exit_i]
    raw=(exitc["close"]-entry["open"])/entry["open"]
    if edge["direction"]=="SELL_PAPER":
        raw=-raw

    atr=max(ft["atr"],entry["open"]*0.0001)
    r=(raw*entry["open"]/atr)-spread_r-slippage_r-commission_r

    if edge.get("risk_model")=="ATR_STOP":
        r=max(-1.2,min(2.4,r))
    elif edge.get("risk_model")=="TRAILING":
        r=max(-1.0,min(3.0,r))
    elif edge.get("risk_model")=="LOSS_GUARD":
        r=max(-0.8,min(2.0,r))
    elif edge.get("risk_model")=="COOLDOWN":
        r=max(-0.9,min(2.1,r))
    else:
        r=max(-1.5,min(2.5,r))

    return {
        "signal_i":i,
        "entry_i":entry_i,
        "exit_i":exit_i,
        "signal_time":candles[i]["time"],
        "entry_time":entry["time"],
        "exit_time":exitc["time"],
        "entry_price":entry["open"],
        "exit_price":exitc["close"],
        "r":r,
        "spread_r":spread_r,
        "slippage_r":slippage_r,
        "commission_r":commission_r,
        "real_execution_allowed":False
    }
