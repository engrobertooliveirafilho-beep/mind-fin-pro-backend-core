"""Causal, research-only feature derivation for raw MT5 OHLC CSVs."""
from pathlib import Path
import pandas as pd

def build_features(source: str | Path, destination: str | Path) -> dict:
    df = pd.read_csv(source, parse_dates=["time"])
    required = {"time", "open", "high", "low", "close", "spread"}
    missing = sorted(required - set(df.columns))
    if missing: raise ValueError("MISSING_COLUMNS:" + ",".join(missing))
    if not df["time"].is_monotonic_increasing or df["time"].duplicated().any():
        raise ValueError("TIME_ORDER_INVALID")
    close = df["close"].astype(float)
    prev = close.shift(1)
    tr = pd.concat([(df["high"]-df["low"]).abs(), (df["high"]-prev).abs(), (df["low"]-prev).abs()], axis=1).max(axis=1)
    for n in (9,21,55,200): df[f"sma_{n}"] = close.rolling(n,min_periods=n).mean()
    df["atr_14"] = tr.rolling(14,min_periods=14).mean()
    df["atr_pct"] = df["atr_14"] / close
    for fast,slow,label in ((9,21,"trend_9_21"),(21,55,"trend_21_55"),(55,200,"trend_55_200")):
        df[label]="NA"
        df.loc[df[f"sma_{fast}"]>df[f"sma_{slow}"],label]="UP"
        df.loc[df[f"sma_{fast}"]<df[f"sma_{slow}"],label]="DOWN"
    q70=df["atr_pct"].rolling(500,min_periods=100).quantile(.70)
    q30=df["atr_pct"].rolling(500,min_periods=100).quantile(.30)
    df["volatility_state"]="NORMAL"
    df.loc[df["atr_pct"]>q70,"volatility_state"]="HIGH"
    df.loc[df["atr_pct"]<q30,"volatility_state"]="LOW"
    df["spread_state"]="UNKNOWN"
    # Session remains UNKNOWN until source timezone/session mapping is authenticated.
    df["session"]="UNKNOWN"
    cols=["time","open","high","low","close","tick_volume","spread","real_volume","sma_9","sma_21","sma_55","sma_200","atr_14","atr_pct","trend_9_21","trend_21_55","trend_55_200","session","volatility_state","spread_state"]
    df[[c for c in cols if c in df.columns]].to_csv(destination,index=False)
    return {"rows":len(df),"valid_sma200":int(df["sma_200"].notna().sum()),"valid_atr":int(df["atr_14"].notna().sum()),"session":"UNKNOWN_BY_DESIGN"}

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser(); p.add_argument("source"); p.add_argument("destination"); a=p.parse_args()
    print(build_features(a.source,a.destination))
