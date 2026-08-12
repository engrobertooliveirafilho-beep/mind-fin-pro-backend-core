import json
import pandas as pd
from pathlib import Path
from datetime import datetime, UTC

SRC = Path("reports/P1808_10Y_WALK_FORWARD_MONTE_CARLO/p1808_10y_elite_promoted_edges.json")
OUT = Path("reports/P1809A_REAL_WALK_FORWARD_ENGINE")
REPORT = OUT / "p1809a_real_walk_forward_report.json"
DETAIL = OUT / "p1809a_real_walk_forward_detail.json"

edges = json.loads(SRC.read_text(encoding="utf-8"))

def metrics(returns):
    wins = [r for r in returns if r > 0]
    losses = [r for r in returns if r < 0]
    trades = len(returns)

    if trades == 0:
        return {
            "trades": 0,
            "win_rate": 0,
            "profit_factor": 0,
            "payoff_ratio": 0,
            "expectancy": 0,
            "total_return_proxy": 0
        }

    gross_win = sum(wins)
    gross_loss = abs(sum(losses))
    pf = gross_win / gross_loss if gross_loss > 0 else gross_win
    wr = len(wins) / trades
    avg_win = sum(wins) / len(wins) if wins else 0
    avg_loss = abs(sum(losses) / len(losses)) if losses else 0
    payoff = avg_win / avg_loss if avg_loss > 0 else avg_win
    exp = sum(returns) / trades

    return {
        "trades": trades,
        "win_rate": round(wr, 6),
        "profit_factor": round(pf, 6),
        "payoff_ratio": round(payoff, 6),
        "expectancy": round(exp, 8),
        "total_return_proxy": round(sum(returns), 8)
    }

def signal_returns(df, family):
    close = df["close"]
    high = df["high"]
    low = df["low"]

    ret = close.pct_change().shift(-1)
    sig = pd.Series(False, index=df.index)

    if family == "EMA_CROSS":
        sig = close.ewm(span=21, adjust=False).mean() > close.ewm(span=55, adjust=False).mean()

    elif family == "SMA_CROSS":
        sig = close.rolling(20).mean() > close.rolling(50).mean()

    elif family == "RSI_REVERSION":
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss.replace(0, pd.NA)
        rsi = 100 - (100 / (1 + rs))
        sig = rsi < 30

    elif family == "BOLLINGER_REVERSION":
        ma = close.rolling(20).mean()
        sd = close.rolling(20).std()
        sig = close < (ma - 2 * sd)

    elif family in ["DONCHIAN_BREAKOUT", "DONCHIAN"]:
        sig = close > high.rolling(20).max().shift(1)

    elif family == "LIQUIDITY_SWEEP_TRIGGER":
        prev_low = low.rolling(20).min().shift(1)
        sig = (low < prev_low) & (close > prev_low)

    elif family == "ATR_TREND":
        prev = close.shift(1)
        tr = pd.concat([(high-low).abs(), (high-prev).abs(), (low-prev).abs()], axis=1).max(axis=1)
        atr = tr.rolling(14).mean()
        ema = close.ewm(span=50, adjust=False).mean()
        sig = (close > ema) & ((atr / close) > (atr / close).rolling(100).median())

    elif family == "MACD_TREND":
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        macd_signal = macd.ewm(span=9, adjust=False).mean()
        sig = macd > macd_signal

    elif family == "FIBO_RETRACE":
        swing_high = high.rolling(100).max()
        swing_low = low.rolling(100).min()
        fib618 = swing_high - 0.618 * (swing_high - swing_low)
        sig = close <= fib618

    elif family == "VWAP_REVERSION":
        if "volume" in df.columns:
            vol = df["volume"].replace(0, pd.NA)
            vwap = (close * vol).rolling(50).sum() / vol.rolling(50).sum()
        else:
            vwap = close.rolling(50).mean()
        sig = close < vwap * 0.995

    out = pd.DataFrame({
        "time": df["time"],
        "return": ret.where(sig)
    }).dropna()

    return out

walk = []

for e in edges:
    df = pd.read_csv(e["dataset"])
    df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True)

    for c in ["open", "high", "low", "close"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna(subset=["time", "open", "high", "low", "close"]).sort_values("time").reset_index(drop=True)

    sr = signal_returns(df, e["family"])
    sr["year"] = sr["time"].dt.year

    yearly = []
    for y in sorted(sr["year"].unique().tolist()):
        returns = sr.loc[sr["year"] == y, "return"].tolist()
        m = metrics(returns)
        yearly.append({
            "year": int(y),
            **m,
            "positive_year": m["total_return_proxy"] > 0
        })

    positive_years = len([x for x in yearly if x["positive_year"]])
    tested_years = len(yearly)
    negative_years = tested_years - positive_years

    years_with_min_trades = len([x for x in yearly if x["trades"] >= 5])
    yearly_consistency = positive_years / tested_years if tested_years else 0

    worst_year = min(yearly, key=lambda x: x["total_return_proxy"]) if yearly else None
    best_year = max(yearly, key=lambda x: x["total_return_proxy"]) if yearly else None

    real_wf_pass = (
        tested_years >= 8 and
        yearly_consistency >= 0.60 and
        years_with_min_trades >= 5 and
        (worst_year is None or worst_year["total_return_proxy"] > -0.08)
    )

    walk.append({
        "edge_id": e["edge_id"],
        "asset": e["asset"],
        "timeframe": e["timeframe"],
        "family": e["family"],
        "dataset": e["dataset"],
        "tested_years": tested_years,
        "positive_years": positive_years,
        "negative_years": negative_years,
        "years_with_min_trades": years_with_min_trades,
        "yearly_consistency": round(yearly_consistency, 6),
        "best_year": best_year,
        "worst_year": worst_year,
        "yearly_real": yearly,
        "real_walk_forward_pass": real_wf_pass,
        "status": "REAL_WF_APPROVED" if real_wf_pass else "REAL_WF_REJECTED",
        "previous_elite_status": e.get("elite_status"),
        "ORDER_SENT": False,
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    })

approved = [x for x in walk if x["real_walk_forward_pass"]]

report = {
    "STATUS": "P1809A_REAL_WALK_FORWARD_COMPLETED",
    "EDGES_INPUT": len(edges),
    "EDGES_TESTED": len(walk),
    "REAL_WF_APPROVED": len(approved),
    "REAL_WF_REJECTED": len(walk) - len(approved),
    "APPROVED_EDGES": approved,
    "NEXT": "P1809B_MONTE_CARLO_10000_TRADE_SEQUENCE",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

DETAIL.write_text(json.dumps(walk, indent=2, ensure_ascii=False), encoding="utf-8")
REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps(report, indent=2, ensure_ascii=False))
