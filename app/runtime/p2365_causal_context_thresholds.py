"""Causal P2365 feature thresholds; no in-sample promotion authority."""
from __future__ import annotations
import pandas as pd


def causal_context_thresholds(df: pd.DataFrame, *, warmup: int = 200) -> pd.DataFrame:
    required = {"time", "close", "high", "low"}
    if not isinstance(df, pd.DataFrame) or not required.issubset(df.columns):
        raise ValueError("missing OHLC/time columns")
    if df.empty or df["time"].isna().any() or not df["time"].is_monotonic_increasing or df["time"].duplicated().any():
        raise ValueError("chronology invalid")
    result = df.copy()
    try:
        result["time"] = pd.to_datetime(result["time"], errors="raise", utc=True)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("invalid timestamp") from exc
    if result["time"].isna().any() or not result["time"].is_monotonic_increasing or result["time"].duplicated().any():
        raise ValueError("chronology invalid after timestamp parsing")
    for col in ("close", "high", "low"):
        result[col] = pd.to_numeric(result[col], errors="raise")
        if result[col].isna().any() or not result[col].map(lambda v: pd.notna(v) and abs(v) != float("inf")).all():
            raise ValueError("nonfinite OHLC")
    if (result["close"] <= 0).any() or (result["high"] < result["low"]).any() or (result["high"] < result["close"]).any() or (result["low"] > result["close"]).any():
        raise ValueError("invalid OHLC geometry")
    returns = result["close"].pct_change(fill_method=None)
    volatility = returns.rolling(20).std()
    result["vol_q30"] = volatility.expanding(min_periods=warmup).quantile(0.30).shift(1)
    result["vol_q70"] = volatility.expanding(min_periods=warmup).quantile(0.70).shift(1)
    result["price_median"] = result["close"].expanding(min_periods=warmup).median().shift(1)
    result["promotion_allowed"] = False
    return result
