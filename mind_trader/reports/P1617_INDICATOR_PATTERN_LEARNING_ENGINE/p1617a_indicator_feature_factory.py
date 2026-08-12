import json
import pandas as pd
from pathlib import Path
from datetime import datetime, UTC

DATA = Path("data/normalized")
FEATURES = Path("data/features")
OUT = Path("reports/P1617_INDICATOR_PATTERN_LEARNING_ENGINE")
REPORT = OUT / "p1617a_indicator_feature_factory_report.json"

FEATURES.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

def rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, pd.NA)
    return 100 - (100 / (1 + rs))

def atr(df, period=14):
    h, l, c = df["high"], df["low"], df["close"]
    prev_c = c.shift(1)
    tr = pd.concat([(h-l).abs(), (h-prev_c).abs(), (l-prev_c).abs()], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def parse_name(f):
    name = f.stem.replace("_normalized","")
    parts = name.split("_")
    if name.startswith("MT5_") and len(parts) >= 3:
        return parts[1], parts[2]
    tf_list = ["M1","M5","M15","M20","M30","H1","H4","D1","W1","MN1"]
    tf = parts[-1] if parts[-1] in tf_list else "UNKNOWN"
    asset = "_".join(parts[:-1]) if tf != "UNKNOWN" else name
    return asset, tf

results = []
created = 0
errors = 0

for f in DATA.glob("*.csv"):
    try:
        df = pd.read_csv(f)
        cols = {c.lower(): c for c in df.columns}

        time_col = cols.get("time") or cols.get("datetime") or cols.get("date") or cols.get("timestamp") or cols.get("data")
        required = ["open","high","low","close"]

        if not time_col or any(c not in cols for c in required):
            results.append({"dataset": str(f), "status": "SKIPPED", "reason": "MISSING_TIME_OR_OHLC"})
            continue

        df = df.rename(columns={
            time_col: "time",
            cols["open"]: "open",
            cols["high"]: "high",
            cols["low"]: "low",
            cols["close"]: "close"
        })

        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        for c in ["open","high","low","close"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        df = df.dropna(subset=["time","open","high","low","close"]).sort_values("time").reset_index(drop=True)

        if len(df) < 100:
            results.append({"dataset": str(f), "status": "SKIPPED", "reason": "TOO_FEW_ROWS", "rows": len(df)})
            continue

        close = df["close"]

        df["sma_20"] = close.rolling(20).mean()
        df["sma_50"] = close.rolling(50).mean()
        df["ema_8"] = close.ewm(span=8, adjust=False).mean()
        df["ema_21"] = close.ewm(span=21, adjust=False).mean()
        df["ema_55"] = close.ewm(span=55, adjust=False).mean()

        df["rsi_14"] = rsi(close, 14)
        df["atr_14"] = atr(df, 14)
        df["atr_pct"] = df["atr_14"] / close

        ma = close.rolling(20).mean()
        sd = close.rolling(20).std()
        df["bb_upper"] = ma + 2 * sd
        df["bb_lower"] = ma - 2 * sd
        df["bb_position"] = (close - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"])

        df["donchian_high_20"] = df["high"].rolling(20).max()
        df["donchian_low_20"] = df["low"].rolling(20).min()
        df["donchian_position"] = (close - df["donchian_low_20"]) / (df["donchian_high_20"] - df["donchian_low_20"])

        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        df["macd"] = ema12 - ema26
        df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()

        swing_high = df["high"].rolling(100).max()
        swing_low = df["low"].rolling(100).min()
        rng = swing_high - swing_low
        df["fibo_382"] = swing_high - 0.382 * rng
        df["fibo_500"] = swing_high - 0.500 * rng
        df["fibo_618"] = swing_high - 0.618 * rng
        df["fibo_zone"] = "NONE"
        df.loc[(close <= df["fibo_382"]) & (close >= df["fibo_500"]), "fibo_zone"] = "382_500"
        df.loc[(close <= df["fibo_500"]) & (close >= df["fibo_618"]), "fibo_zone"] = "500_618"

        body = (df["close"] - df["open"]).abs()
        candle_range = (df["high"] - df["low"]).replace(0, pd.NA)
        upper_wick = df["high"] - df[["open","close"]].max(axis=1)
        lower_wick = df[["open","close"]].min(axis=1) - df["low"]

        df["trigger_long_wick_rejection"] = ((lower_wick / candle_range) > 0.55).astype(int)
        df["trigger_bullish_engulfing"] = (
            (df["close"] > df["open"]) &
            (df["close"].shift(1) < df["open"].shift(1)) &
            (df["close"] > df["open"].shift(1)) &
            (df["open"] < df["close"].shift(1))
        ).astype(int)

        df["trend_proxy"] = "RANGE"
        df.loc[df["ema_21"] > df["ema_55"], "trend_proxy"] = "TREND_UP"
        df.loc[df["ema_21"] < df["ema_55"], "trend_proxy"] = "TREND_DOWN"

        df["volatility_proxy"] = "NORMAL_VOL"
        df.loc[df["atr_pct"] > df["atr_pct"].rolling(100).quantile(0.75), "volatility_proxy"] = "HIGH_VOL"
        df.loc[df["atr_pct"] < df["atr_pct"].rolling(100).quantile(0.25), "volatility_proxy"] = "LOW_VOL"

        asset, tf = parse_name(f)
        out_file = FEATURES / f"{asset}_{tf}_features.csv"
        df.to_csv(out_file, index=False)

        created += 1
        results.append({
            "dataset": str(f),
            "asset": asset,
            "timeframe": tf,
            "rows": len(df),
            "features_file": str(out_file),
            "status": "FEATURES_CREATED"
        })

    except Exception as e:
        errors += 1
        results.append({"dataset": str(f), "status": "ERROR", "error": str(e)})

report = {
    "STATUS": "P1617A_INDICATOR_FEATURE_FACTORY_COMPLETED",
    "DATASETS_INPUT": len(list(DATA.glob("*.csv"))),
    "FEATURE_FILES_CREATED": created,
    "ERRORS": errors,
    "RESULTS_SAMPLE": results[:20],
    "NEXT": "P1617B_SPECIALIST_INDICATOR_PATTERN_TESTER",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

(OUT / "p1617a_indicator_feature_factory_detail.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
