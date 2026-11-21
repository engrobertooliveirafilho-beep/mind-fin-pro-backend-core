"""P2365 causal DE40 M5 context research. No trading or promotion."""
from __future__ import annotations
import pandas as pd
from app.runtime.p2365_causal_context_thresholds import causal_context_thresholds


def train_de40_contexts(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    df = causal_context_thresholds(frame)
    df["ma50"] = df["close"].rolling(50).mean()
    df["ma200"] = df["close"].rolling(200).mean()
    delta = df["ma50"] - df["ma200"]
    band = df["price_median"] * 0.0005
    df["regime"] = "WARMUP"
    ready = delta.notna() & band.notna()
    df.loc[ready & (delta.abs() < band), "regime"] = "RANGE"
    df.loc[ready & (delta >= band), "regime"] = "UPTREND"
    df.loc[ready & (delta <= -band), "regime"] = "DOWNTREND"
    vol = df["close"].pct_change(fill_method=None).rolling(20).std()
    df["volatility"] = "UNKNOWN_VOL"
    valid = df["vol_q30"].notna() & df["vol_q70"].notna() & vol.notna()
    df.loc[valid, "volatility"] = "NORMAL_VOL"
    df.loc[valid & (vol >= df["vol_q70"]), "volatility"] = "HIGH_VOL"
    df.loc[valid & (vol <= df["vol_q30"]), "volatility"] = "LOW_VOL"
    hours = pd.to_datetime(df["time"]).dt.hour
    df["session"] = "OFF_HOURS"
    for name, low, high in (("LONDON_OPEN", 7, 10), ("LONDON_MID", 10, 13),
                            ("NY_OVERLAP", 13, 16), ("NY_LATE", 16, 20)):
        df.loc[(hours >= low) & (hours < high), "session"] = name
    df["structure"] = "NEUTRAL"
    df.loc[df["close"] > df["high"].rolling(20).max().shift(1), "structure"] = "BREAKOUT_UP"
    df.loc[df["close"] < df["low"].rolling(20).min().shift(1), "structure"] = "BREAKOUT_DOWN"
    df["context"] = df["regime"] + "|" + df["volatility"] + "|" + df["session"] + "|" + df["structure"]
    df["future_move"] = df["close"].shift(-12) - df["close"]
    rows = []
    for name, group in df.loc[ready & valid & df["future_move"].notna()].groupby("context"):
        if len(group) < 100:
            continue
        move = group["future_move"]
        buy = round(100 * (move > 0).mean(), 2)
        sell = round(100 * (move < 0).mean(), 2)
        best = max(buy, sell)
        avg = float(move.mean())
        avg_abs = float(move.abs().mean())
        score = round(min(100, min(40, max(0, best - 50) * 2) +
                          min(30, abs(avg) / max(avg_abs, 1e-9) * 30) +
                          min(20, len(group) / 5000) + (10 if "BREAKOUT" in name else 0)), 2)
        rows.append(dict(context=name, samples=len(group), best_side="BUY" if buy >= sell else "SELL",
                         long_win_rate=buy, short_win_rate=sell, best_win_rate=best,
                         avg_future_move=round(avg, 4), avg_abs_move=round(avg_abs, 4),
                         score=score, decision="OBSERVE" if score >= 45 else "REJECT",
                         timeframe="M5", symbol="DE40", mode="PAPER_ONLY"))
    rank = pd.DataFrame(rows, columns=["context","samples","best_side","long_win_rate",
        "short_win_rate","best_win_rate","avg_future_move","avg_abs_move","score",
        "decision","timeframe","symbol","mode"])
    rank = rank.sort_values(["score","best_win_rate","samples"], ascending=False)
    summary = dict(mission="P2365_DE40_CONTEXT_RANKING_AND_EXPECTANCY", source_rows=len(df),
                   contexts_ranked=len(rank), promoted_contexts=0,
                   certification="PENDING_INDEPENDENT_OOS_VALIDATION", mode="PAPER_ONLY",
                   real_orders="FORBIDDEN", ftmo_real="FORBIDDEN")
    return rank, summary
