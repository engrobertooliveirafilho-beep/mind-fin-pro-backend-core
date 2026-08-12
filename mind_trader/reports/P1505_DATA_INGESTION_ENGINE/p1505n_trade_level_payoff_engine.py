import json, math
import pandas as pd
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("reports/P1505_DATA_INGESTION_ENGINE")
SRC1 = OUT / "p1505h_mt5_promoted_edge_pool.json"
SRC2 = OUT / "p1505l_remaining_mt5_mc_results.json"

TRADES_OUT = OUT / "p1505n_trade_level_trades.json"
EDGES_OUT = OUT / "p1505n_edge_trade_metrics.json"
BEST_OUT = OUT / "p1505n_best_edge_by_asset.json"
REPORT = OUT / "p1505n_trade_level_payoff_report.json"

def load(p):
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

def signal_series(df, family, params):
    close = df["close"].astype(float)

    if family in ["SMA_CROSS", "EMA_CROSS"]:
        fast, slow = params[0], params[1]
        f = close.rolling(fast).mean() if family == "SMA_CROSS" else close.ewm(span=fast, adjust=False).mean()
        s = close.rolling(slow).mean() if family == "SMA_CROSS" else close.ewm(span=slow, adjust=False).mean()
        return (f > s).astype(int)

    if family == "RSI_REVERSION":
        period, low, high = params
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(period).mean()
        loss = (-delta.clip(upper=0)).rolling(period).mean()
        rs = gain / loss.replace(0, math.nan)
        rsi = 100 - (100 / (1 + rs))
        return (rsi < low).astype(int)

    if family in ["BREAKOUT", "DONCHIAN"]:
        window = params[0]
        high = close.rolling(window).max()
        return (close > high.shift(1)).astype(int)

    if family == "ATR_TREND":
        period, mult = params
        ma = close.rolling(period).mean()
        vol = close.pct_change().rolling(period).std()
        return (close > ma * (1 + vol * mult)).astype(int)

    if family == "BOLLINGER_REVERSION":
        period, mult = params
        ma = close.rolling(period).mean()
        sd = close.rolling(period).std()
        lower = ma - mult * sd
        return (close < lower).astype(int)

    return pd.Series(0, index=df.index)

def extract_trades(edge):
    dataset = edge.get("dataset")
    if not dataset or not Path(dataset).exists():
        return []

    df = pd.read_csv(dataset)
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df = df.dropna(subset=["time","open","high","low","close"]).reset_index(drop=True)

    sig = signal_series(df, edge.get("family"), edge.get("params")).fillna(0).astype(int)

    trades = []
    in_trade = False
    entry_i = None

    for i in range(1, len(df)):
        prev = sig.iloc[i-1]
        cur = sig.iloc[i]

        if not in_trade and prev == 0 and cur == 1:
            in_trade = True
            entry_i = i
            continue

        if in_trade and prev == 1 and cur == 0:
            exit_i = i
            entry_price = float(df.loc[entry_i, "close"])
            exit_price = float(df.loc[exit_i, "close"])
            pnl_pct = (exit_price / entry_price) - 1.0

            window = df.loc[entry_i:exit_i]
            mae = ((window["low"].astype(float).min() / entry_price) - 1.0)
            mfe = ((window["high"].astype(float).max() / entry_price) - 1.0)

            trades.append({
                "edge_id": edge.get("edge_id") or edge.get("job_id"),
                "asset": edge.get("asset"),
                "timeframe": edge.get("timeframe"),
                "family": edge.get("family"),
                "params": edge.get("params"),
                "entry_time": str(df.loc[entry_i, "time"]),
                "exit_time": str(df.loc[exit_i, "time"]),
                "entry_hour": int(df.loc[entry_i, "time"].hour),
                "exit_hour": int(df.loc[exit_i, "time"].hour),
                "entry_price": entry_price,
                "exit_price": exit_price,
                "side": "LONG",
                "pnl_pct": round(pnl_pct, 8),
                "win_loss": "WIN" if pnl_pct > 0 else "LOSS",
                "holding_bars": int(exit_i - entry_i),
                "mae_pct": round(float(mae), 8),
                "mfe_pct": round(float(mfe), 8),
                "REAL_ORDERS": "FORBIDDEN",
                "FTMO_REAL": "FORBIDDEN",
                "MT5_REAL": "FORBIDDEN"
            })

            in_trade = False
            entry_i = None

    return trades

edges = load(SRC1) + [r for r in load(SRC2) if r.get("promoted_edge") is True]

all_trades = []
edge_metrics = []

for edge in edges:
    trades = extract_trades(edge)
    all_trades.extend(trades)

    wins = [t["pnl_pct"] for t in trades if t["pnl_pct"] > 0]
    losses = [abs(t["pnl_pct"]) for t in trades if t["pnl_pct"] < 0]

    total = len(trades)
    win_rate = len(wins) / total if total else 0
    loss_rate = len(losses) / total if total else 0
    avg_win = sum(wins) / len(wins) if wins else 0
    avg_loss = sum(losses) / len(losses) if losses else 0
    payoff = avg_win / avg_loss if avg_loss else 0
    expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
    profit_factor = sum(wins) / sum(losses) if sum(losses) else 0
    avg_duration = sum(t["holding_bars"] for t in trades) / total if total else 0

    by_hour = {}
    for t in trades:
        h = t["entry_hour"]
        by_hour.setdefault(h, {"trades":0, "wins":0, "pnl":0})
        by_hour[h]["trades"] += 1
        by_hour[h]["wins"] += 1 if t["pnl_pct"] > 0 else 0
        by_hour[h]["pnl"] += t["pnl_pct"]

    best_hour = None
    if by_hour:
        best_hour = sorted(
            by_hour.items(),
            key=lambda x: (x[1]["pnl"], x[1]["wins"] / max(x[1]["trades"],1)),
            reverse=True
        )[0][0]

    score = profit_factor * payoff * max(expectancy, 0) / (1 + abs(avg_loss))

    edge_metrics.append({
        "edge_id": edge.get("edge_id") or edge.get("job_id"),
        "asset": edge.get("asset"),
        "timeframe": edge.get("timeframe"),
        "family": edge.get("family"),
        "params": edge.get("params"),
        "trades": total,
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": round(win_rate, 6),
        "avg_win_pct": round(avg_win, 8),
        "avg_loss_pct": round(avg_loss, 8),
        "payoff_ratio_real": round(payoff, 6),
        "expectancy_per_trade_real": round(expectancy, 8),
        "profit_factor_real": round(profit_factor, 6),
        "avg_holding_bars": round(avg_duration, 2),
        "best_entry_hour": best_hour,
        "best_entry_hour_stats": by_hour.get(best_hour) if best_hour is not None else None,
        "institutional_score_v2": round(score, 8),
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    })

best_by_asset = {}
for m in edge_metrics:
    a = m["asset"]
    if a not in best_by_asset or m["institutional_score_v2"] > best_by_asset[a]["institutional_score_v2"]:
        best_by_asset[a] = m

TRADES_OUT.write_text(json.dumps(all_trades, indent=2, ensure_ascii=False), encoding="utf-8")
EDGES_OUT.write_text(json.dumps(edge_metrics, indent=2, ensure_ascii=False), encoding="utf-8")
BEST_OUT.write_text(json.dumps(best_by_asset, indent=2, ensure_ascii=False), encoding="utf-8")

report = {
    "STATUS": "P1505N_TRADE_LEVEL_PAYOFF_BACKTEST_ENGINE_COMPLETED",
    "EDGES_INPUT": len(edges),
    "EDGES_ANALYZED": len(edge_metrics),
    "TRADES_EXTRACTED": len(all_trades),
    "ASSETS_WITH_BEST_EDGE": len(best_by_asset),
    "BEST_EDGE_BY_ASSET": best_by_asset,
    "OUTPUT_TRADES": str(TRADES_OUT),
    "OUTPUT_EDGE_METRICS": str(EDGES_OUT),
    "OUTPUT_BEST_BY_ASSET": str(BEST_OUT),
    "NEXT": "P1505O_EDGE_RANKING_V2",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({
    "STATUS": report["STATUS"],
    "EDGES_ANALYZED": report["EDGES_ANALYZED"],
    "TRADES_EXTRACTED": report["TRADES_EXTRACTED"],
    "ASSETS_WITH_BEST_EDGE": report["ASSETS_WITH_BEST_EDGE"],
    "NEXT": report["NEXT"],
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN"
}, indent=2, ensure_ascii=False))
