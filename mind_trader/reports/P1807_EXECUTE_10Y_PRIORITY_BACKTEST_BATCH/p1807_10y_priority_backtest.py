import json
import pandas as pd
from pathlib import Path
from datetime import datetime, UTC
import hashlib

QUEUE = Path("reports/P1806_10Y_BACKTEST_UNLOCK/p1806_10y_backtest_queue.json")
OUT = Path("reports/P1807_EXECUTE_10Y_PRIORITY_BACKTEST_BATCH")
REPORT = OUT / "p1807_10y_priority_backtest_report.json"
RESULTS = OUT / "p1807_10y_priority_backtest_results.json"

queue = json.loads(QUEUE.read_text(encoding="utf-8"))

def edge_id(asset, tf, family, params):
    raw = json.dumps({"asset":asset,"tf":tf,"family":family,"params":params}, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()[:24]

def metrics(returns):
    wins = [r for r in returns if r > 0]
    losses = [r for r in returns if r < 0]
    trades = len(returns)
    if trades == 0:
        return None
    gross_win = sum(wins)
    gross_loss = abs(sum(losses))
    pf = gross_win / gross_loss if gross_loss > 0 else gross_win
    win_rate = len(wins) / trades
    avg_win = sum(wins)/len(wins) if wins else 0
    avg_loss = abs(sum(losses)/len(losses)) if losses else 0
    payoff = avg_win / avg_loss if avg_loss > 0 else avg_win
    expectancy = sum(returns)/trades
    return {
        "trades": trades,
        "win_rate": round(win_rate,6),
        "profit_factor": round(pf,6),
        "payoff_ratio": round(payoff,6),
        "expectancy": round(expectancy,8),
        "total_return_proxy": round(sum(returns),8),
        "avg_win": round(avg_win,8),
        "avg_loss": round(avg_loss,8)
    }

def backtest(df, family):
    close = df["close"]
    high = df["high"]
    low = df["low"]

    returns = []

    if family == "EMA_CROSS":
        fast = close.ewm(span=21, adjust=False).mean()
        slow = close.ewm(span=55, adjust=False).mean()
        sig = fast > slow
        ret = close.pct_change().shift(-1)
        returns = (ret[sig]).dropna().tolist()

    elif family == "SMA_CROSS":
        fast = close.rolling(20).mean()
        slow = close.rolling(50).mean()
        sig = fast > slow
        ret = close.pct_change().shift(-1)
        returns = (ret[sig]).dropna().tolist()

    elif family == "RSI_REVERSION":
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss.replace(0, pd.NA)
        rsi = 100 - (100/(1+rs))
        sig = rsi < 30
        ret = close.pct_change().shift(-1)
        returns = (ret[sig]).dropna().tolist()

    elif family == "BOLLINGER_REVERSION":
        ma = close.rolling(20).mean()
        sd = close.rolling(20).std()
        lower = ma - 2*sd
        sig = close < lower
        ret = close.pct_change().shift(-1)
        returns = (ret[sig]).dropna().tolist()

    elif family == "DONCHIAN_BREAKOUT":
        dh = high.rolling(20).max().shift(1)
        sig = close > dh
        ret = close.pct_change().shift(-1)
        returns = (ret[sig]).dropna().tolist()

    elif family == "ATR_TREND":
        prev = close.shift(1)
        tr = pd.concat([(high-low).abs(), (high-prev).abs(), (low-prev).abs()], axis=1).max(axis=1)
        atr = tr.rolling(14).mean()
        ema = close.ewm(span=50, adjust=False).mean()
        sig = (close > ema) & ((atr/close) > (atr/close).rolling(100).median())
        ret = close.pct_change().shift(-1)
        returns = (ret[sig]).dropna().tolist()

    elif family == "MACD_TREND":
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        sig = macd > signal
        ret = close.pct_change().shift(-1)
        returns = (ret[sig]).dropna().tolist()

    elif family == "FIBO_RETRACE":
        swing_high = high.rolling(100).max()
        swing_low = low.rolling(100).min()
        rng = swing_high - swing_low
        fib618 = swing_high - 0.618*rng
        sig = close <= fib618
        ret = close.pct_change().shift(-1)
        returns = (ret[sig]).dropna().tolist()

    elif family == "VWAP_REVERSION":
        if "volume" in df.columns:
            vol = df["volume"].replace(0, pd.NA)
            vwap = (close * vol).rolling(50).sum() / vol.rolling(50).sum()
        else:
            vwap = close.rolling(50).mean()
        sig = close < vwap * 0.995
        ret = close.pct_change().shift(-1)
        returns = (ret[sig]).dropna().tolist()

    elif family == "LIQUIDITY_SWEEP_TRIGGER":
        prev_low = low.rolling(20).min().shift(1)
        sig = (low < prev_low) & (close > prev_low)
        ret = close.pct_change().shift(-1)
        returns = (ret[sig]).dropna().tolist()

    return metrics(returns)

results = []
errors = []

for job in queue:
    try:
        df = pd.read_csv(job["dataset"])
        df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True)
        for c in ["open","high","low","close"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df = df.dropna(subset=["time","open","high","low","close"]).sort_values("time")

        m = backtest(df, job["strategy_family"])
        if not m:
            continue

        approved = (
            m["trades"] >= 20 and
            m["profit_factor"] >= 1.2 and
            m["payoff_ratio"] >= 1.0 and
            m["expectancy"] > 0
        )

        params = {"default_family_params": True}
        results.append({
            "edge_id": edge_id(job["asset"], job["timeframe"], job["strategy_family"], params),
            "asset": job["asset"],
            "timeframe": job["timeframe"],
            "family": job["strategy_family"],
            "dataset": job["dataset"],
            "history_years": job["history_years"],
            "certification_target": "ELITE_10Y",
            **m,
            "approved_backtest": approved,
            "status": "APPROVED_10Y_BACKTEST" if approved else "REJECTED_10Y_BACKTEST",
            "ORDER_SENT": False,
            "REAL_ORDERS": "FORBIDDEN",
            "FTMO_REAL": "FORBIDDEN",
            "MT5_REAL": "FORBIDDEN"
        })

    except Exception as e:
        errors.append({"job": job, "error": str(e)})

approved = [r for r in results if r["approved_backtest"]]

report = {
    "STATUS": "P1807_10Y_PRIORITY_BACKTEST_BATCH_COMPLETED",
    "JOBS_INPUT": len(queue),
    "BACKTESTED": len(results),
    "APPROVED_10Y_BACKTESTS": len(approved),
    "ERRORS": len(errors),
    "TOP20_APPROVED": sorted(approved, key=lambda x: (x["profit_factor"], x["payoff_ratio"]), reverse=True)[:20],
    "RESULTS_FILE": str(RESULTS),
    "NEXT": "P1808_10Y_WALK_FORWARD_MONTE_CARLO_AND_ELITE_PROMOTION",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

RESULTS.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
(OUT / "p1807_10y_priority_backtest_errors.json").write_text(json.dumps(errors, indent=2, ensure_ascii=False), encoding="utf-8")
REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps(report, indent=2, ensure_ascii=False))
