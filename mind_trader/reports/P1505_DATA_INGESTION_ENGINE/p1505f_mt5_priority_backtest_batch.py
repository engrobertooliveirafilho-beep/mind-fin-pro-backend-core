import json, math
import pandas as pd
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("reports/P1505_DATA_INGESTION_ENGINE")
QUEUE = OUT / "p1505e_auto_backtest_queue.json"
RESULTS = OUT / "p1505f_mt5_priority_backtest_results.json"
REPORT = OUT / "p1505f_mt5_priority_backtest_report.json"

BATCH_LIMIT = 500

def load_json(p, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

def simple_backtest(df, family, params):
    close = df["close"].astype(float)

    if len(close) < 100:
        return None

    returns = close.pct_change().fillna(0)

    if family in ["SMA_CROSS", "EMA_CROSS"]:
        fast, slow = params[0], params[1]
        if family == "SMA_CROSS":
            f = close.rolling(fast).mean()
            s = close.rolling(slow).mean()
        else:
            f = close.ewm(span=fast, adjust=False).mean()
            s = close.ewm(span=slow, adjust=False).mean()
        signal = (f > s).astype(int).shift(1).fillna(0)

    elif family == "RSI_REVERSION":
        period, low, high = params
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(period).mean()
        loss = (-delta.clip(upper=0)).rolling(period).mean()
        rs = gain / loss.replace(0, math.nan)
        rsi = 100 - (100 / (1 + rs))
        signal = (rsi < low).astype(int).shift(1).fillna(0)

    elif family in ["BREAKOUT", "DONCHIAN"]:
        window = params[0]
        high = close.rolling(window).max()
        signal = (close > high.shift(1)).astype(int).shift(1).fillna(0)

    elif family == "ATR_TREND":
        period, mult = params
        ma = close.rolling(period).mean()
        vol = close.pct_change().rolling(period).std()
        signal = (close > ma * (1 + vol * mult)).astype(int).shift(1).fillna(0)

    elif family == "BOLLINGER_REVERSION":
        period, mult = params
        ma = close.rolling(period).mean()
        sd = close.rolling(period).std()
        lower = ma - mult * sd
        signal = (close < lower).astype(int).shift(1).fillna(0)

    else:
        signal = pd.Series(0, index=df.index)

    strat_ret = returns * signal
    trades = int((signal.diff().abs() > 0).sum())

    gains = strat_ret[strat_ret > 0].sum()
    losses = abs(strat_ret[strat_ret < 0].sum())
    pf = float(gains / losses) if losses > 0 else float(gains * 1000)

    equity = (1 + strat_ret).cumprod()
    dd = float(((equity.cummax() - equity) / equity.cummax()).max()) if len(equity) else 0

    score = (pf / (1 + dd)) if trades >= 5 else 0

    return {
        "trades": trades,
        "profit_factor": round(pf, 6),
        "max_drawdown_proxy": round(dd, 6),
        "score": round(score, 6),
        "approved_backtest": bool(pf >= 1.20 and dd <= 0.25 and trades >= 5)
    }

queue = load_json(QUEUE, [])
mt5_jobs = [j for j in queue if j.get("source") == "MT5" and j.get("status") == "QUEUED"]
batch = mt5_jobs[:BATCH_LIMIT]

results = []
approved = 0
errors = 0

for job in batch:
    try:
        df = pd.read_csv(job["dataset"])
        bt = simple_backtest(df, job["family"], job["params"])

        if not bt:
            errors += 1
            results.append({**job, "status": "ERROR", "error": "INSUFFICIENT_DATA"})
            continue

        row = {
            **job,
            **bt,
            "status": "BACKTESTED",
            "REAL_ORDERS": "FORBIDDEN",
            "FTMO_REAL": "FORBIDDEN",
            "MT5_REAL": "FORBIDDEN"
        }

        if bt["approved_backtest"]:
            approved += 1

        results.append(row)

    except Exception as e:
        errors += 1
        results.append({**job, "status": "ERROR", "error": str(e)})

RESULTS.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

report = {
    "STATUS": "P1505F_MT5_PRIORITY_BACKTEST_BATCH_COMPLETED",
    "BATCH_LIMIT": BATCH_LIMIT,
    "JOBS_INPUT": len(batch),
    "BACKTESTED": len([r for r in results if r.get("status") == "BACKTESTED"]),
    "APPROVED_BACKTESTS": approved,
    "ERRORS": errors,
    "RESULTS_FILE": str(RESULTS),
    "NEXT": "P1505G_WALK_FORWARD_MONTE_CARLO_ON_MT5_APPROVED",
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
