import json
import hashlib
import pandas as pd
from pathlib import Path
from datetime import datetime, UTC

BASE = Path("reports/P1871_TO_P1875_DNA_EXTRACTION_FACTORY")
DNA_DIR = Path("data/lake/dna")
FEATURE_DIR = Path("data/lake/feature_store")
FEATURES_DIR = Path("data/lake/features")

MC = Path("reports/P1809B_MONTE_CARLO_10000_TRADE_SEQUENCE/p1809b_monte_carlo_10000_report.json")

def load_json(p, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

mc = load_json(MC, {})
elite_edges = mc.get("APPROVED_EDGES", [])

DATASET_MAP = {
    ("XAUUSD", "D1"): "data/normalized_10y/MT5_XAUUSD_D1_10Y_normalized.csv",
    ("USDJPY", "D1"): "data/normalized_10y/MT5_USDJPY_D1_10Y_normalized.csv"
}

def trade_id(edge_id, t):
    raw = f"{edge_id}|{str(t)}"
    return hashlib.md5(raw.encode()).hexdigest()[:24]

def session_from_hour(h):
    if 0 <= h < 7:
        return "ASIA"
    if 7 <= h < 12:
        return "LONDON"
    if 12 <= h < 17:
        return "NY"
    if 17 <= h < 21:
        return "NY_CLOSE"
    return "OFF_HOURS"

def add_features(df):
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True)
    df = df.dropna(subset=["time","open","high","low","close"]).sort_values("time").reset_index(drop=True)

    for c in ["open","high","low","close"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    if "volume" not in df.columns:
        df["volume"] = 0
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0)

    df["return_next"] = df["close"].pct_change().shift(-1)
    df["body_pct"] = ((df["close"] - df["open"]).abs() / df["open"]).fillna(0)
    df["range_pct"] = ((df["high"] - df["low"]) / df["open"]).fillna(0)
    df["upper_wick_pct"] = ((df["high"] - df[["open","close"]].max(axis=1)) / df["open"]).fillna(0)
    df["lower_wick_pct"] = ((df[["open","close"]].min(axis=1) - df["low"]) / df["open"]).fillna(0)
    df["close_position"] = ((df["close"] - df["low"]) / (df["high"] - df["low"]).replace(0, pd.NA)).fillna(0.5)

    prev_close = df["close"].shift(1)
    tr = pd.concat([
        (df["high"] - df["low"]).abs(),
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs()
    ], axis=1).max(axis=1)

    df["atr14"] = tr.rolling(14).mean()
    df["atr_pct"] = (df["atr14"] / df["close"]).fillna(0)
    df["atr_slope"] = df["atr14"].pct_change().fillna(0)
    df["atr_percentile_252"] = df["atr_pct"].rolling(252).rank(pct=True).fillna(0.5)

    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, pd.NA)
    df["rsi14"] = (100 - (100 / (1 + rs))).fillna(50)
    df["rsi_slope"] = df["rsi14"].diff().fillna(0)

    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["ema200"] = df["close"].ewm(span=200, adjust=False).mean()
    df["ema20_50_state"] = (df["ema20"] > df["ema50"]).astype(int)
    df["ema50_200_state"] = (df["ema50"] > df["ema200"]).astype(int)

    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]

    up_move = df["high"].diff()
    down_move = -df["low"].diff()
    plus_dm = ((up_move > down_move) & (up_move > 0)) * up_move
    minus_dm = ((down_move > up_move) & (down_move > 0)) * down_move
    atr = tr.rolling(14).mean().replace(0, pd.NA)
    plus_di = 100 * plus_dm.rolling(14).mean() / atr
    minus_di = 100 * minus_dm.rolling(14).mean() / atr
    dx = ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, pd.NA)) * 100
    df["adx14"] = dx.rolling(14).mean().fillna(0)

    ma20 = df["close"].rolling(20).mean()
    sd20 = df["close"].rolling(20).std()
    df["bb_width"] = ((4 * sd20) / ma20).fillna(0)

    df["donchian_high_20"] = df["high"].rolling(20).max().shift(1)
    df["donchian_low_20"] = df["low"].rolling(20).min().shift(1)

    df["prev_low_sweep"] = ((df["low"] < df["donchian_low_20"]) & (df["close"] > df["donchian_low_20"])).astype(int)
    df["prev_high_sweep"] = ((df["high"] > df["donchian_high_20"]) & (df["close"] < df["donchian_high_20"])).astype(int)
    df["breakout_up"] = (df["close"] > df["donchian_high_20"]).astype(int)
    df["breakout_down"] = (df["close"] < df["donchian_low_20"]).astype(int)

    df["trend_regime"] = "RANGE"
    df.loc[(df["ema20"] > df["ema50"]) & (df["ema50"] > df["ema200"]), "trend_regime"] = "TREND_UP"
    df.loc[(df["ema20"] < df["ema50"]) & (df["ema50"] < df["ema200"]), "trend_regime"] = "TREND_DOWN"

    df["volatility_regime"] = "NORMAL_VOL"
    df.loc[df["atr_percentile_252"] >= 0.75, "volatility_regime"] = "HIGH_VOL"
    df.loc[df["atr_percentile_252"] <= 0.25, "volatility_regime"] = "LOW_VOL"

    df["market_physics_energy"] = (
        df["atr_percentile_252"].fillna(0.5) * 40 +
        df["adx14"].fillna(0) * 0.6 +
        df["bb_width"].rank(pct=True).fillna(0.5) * 30
    ).clip(0, 100)

    df["market_entropy_proxy"] = (1 - df["close_position"].sub(0.5).abs() * 2).clip(0, 1)

    df["hour"] = df["time"].dt.hour
    df["weekday"] = df["time"].dt.day_name()
    df["weekday_num"] = df["time"].dt.weekday
    df["month"] = df["time"].dt.month
    df["session"] = df["hour"].apply(session_from_hour)

    return df

def signal_mask(df, family):
    if family == "LIQUIDITY_SWEEP_TRIGGER":
        return df["prev_low_sweep"] == 1

    if family == "RSI_REVERSION":
        return df["rsi14"] < 30

    return pd.Series(False, index=df.index)

all_trades = []
feature_exports = []

for edge in elite_edges:
    asset = edge.get("asset")
    timeframe = edge.get("timeframe")
    family = edge.get("family")
    edge_id = edge.get("edge_id")

    dataset = DATASET_MAP.get((asset, timeframe))
    if not dataset or not Path(dataset).exists():
        continue

    df = pd.read_csv(dataset)
    df = add_features(df)

    features_file = FEATURES_DIR / f"{asset}_{timeframe}_features.csv"
    df.to_csv(features_file, index=False)
    feature_exports.append(str(features_file))

    mask = signal_mask(df, family)
    sig = df.loc[mask].copy()

    for idx, row in sig.iterrows():
        if idx + 1 >= len(df):
            continue

        future = df.iloc[idx+1:min(idx+11, len(df))]
        ret = row.get("return_next")
        if pd.isna(ret):
            continue

        mfe = (future["high"].max() - row["close"]) / row["close"] if len(future) else 0
        mae = (future["low"].min() - row["close"]) / row["close"] if len(future) else 0

        outcome = "WIN" if ret > 0 else "LOSS"
        dna = {
            "trade_id": trade_id(edge_id, row["time"]),
            "edge_id": edge_id,
            "asset": asset,
            "timeframe": timeframe,
            "family": family,
            "entry_time": str(row["time"]),
            "exit_time_proxy": str(df.iloc[idx+1]["time"]),
            "weekday": row["weekday"],
            "weekday_num": int(row["weekday_num"]),
            "month": int(row["month"]),
            "hour": int(row["hour"]),
            "session": row["session"],
            "return_1bar": float(ret),
            "outcome": outcome,
            "mfe_10bar_proxy": float(mfe),
            "mae_10bar_proxy": float(mae),
            "bars_held_proxy": 1,
            "body_pct": float(row["body_pct"]),
            "range_pct": float(row["range_pct"]),
            "upper_wick_pct": float(row["upper_wick_pct"]),
            "lower_wick_pct": float(row["lower_wick_pct"]),
            "close_position": float(row["close_position"]),
            "atr_pct": float(row["atr_pct"]),
            "atr_slope": float(row["atr_slope"]),
            "atr_percentile_252": float(row["atr_percentile_252"]),
            "rsi14": float(row["rsi14"]),
            "rsi_slope": float(row["rsi_slope"]),
            "adx14": float(row["adx14"]),
            "macd": float(row["macd"]),
            "macd_hist": float(row["macd_hist"]),
            "ema20_50_state": int(row["ema20_50_state"]),
            "ema50_200_state": int(row["ema50_200_state"]),
            "bb_width": float(row["bb_width"]),
            "prev_low_sweep": int(row["prev_low_sweep"]),
            "prev_high_sweep": int(row["prev_high_sweep"]),
            "breakout_up": int(row["breakout_up"]),
            "breakout_down": int(row["breakout_down"]),
            "trend_regime": row["trend_regime"],
            "volatility_regime": row["volatility_regime"],
            "market_physics_energy": float(row["market_physics_energy"]),
            "market_entropy_proxy": float(row["market_entropy_proxy"]),
            "trigger": "LIQUIDITY_SWEEP" if family == "LIQUIDITY_SWEEP_TRIGGER" else "RSI_REVERSION",
            "structure": "SWEEP" if row["prev_low_sweep"] == 1 else "STAT_REVERSION",
            "mtf_context_proxy": f"{row['trend_regime']}_{row['volatility_regime']}",
            "ORDER_SENT": False,
            "REAL_ORDERS": "FORBIDDEN",
            "FTMO_REAL": "FORBIDDEN",
            "MT5_REAL": "FORBIDDEN"
        }

        all_trades.append(dna)

trade_df = pd.DataFrame(all_trades)

trade_dna_file = DNA_DIR / "p1871_trade_dna.csv"
winner_file = DNA_DIR / "p1872_winner_dna.csv"
loser_file = DNA_DIR / "p1873_loser_dna.csv"
cluster_file = DNA_DIR / "p1874_dna_clusters.json"
pattern_file = DNA_DIR / "p1875_pattern_genome.json"

if len(trade_df):
    trade_df.to_csv(trade_dna_file, index=False)

    winners = trade_df[trade_df["outcome"] == "WIN"].copy()
    losers = trade_df[trade_df["outcome"] == "LOSS"].copy()

    winners.to_csv(winner_file, index=False)
    losers.to_csv(loser_file, index=False)

    clusters = []
    group_cols = ["asset","family","session","trend_regime","volatility_regime","trigger"]

    for keys, g in trade_df.groupby(group_cols):
        returns = g["return_1bar"].astype(float)
        wins = g[g["outcome"] == "WIN"]
        losses = g[g["outcome"] == "LOSS"]

        gross_win = wins["return_1bar"].sum() if len(wins) else 0
        gross_loss = abs(losses["return_1bar"].sum()) if len(losses) else 0
        pf = gross_win / gross_loss if gross_loss > 0 else gross_win

        clusters.append({
            "cluster_id": hashlib.md5(str(keys).encode()).hexdigest()[:16],
            "asset": keys[0],
            "family": keys[1],
            "session": keys[2],
            "trend_regime": keys[3],
            "volatility_regime": keys[4],
            "trigger": keys[5],
            "trades": int(len(g)),
            "win_rate": round(len(wins) / len(g), 6),
            "profit_factor_proxy": round(float(pf), 6),
            "avg_return": round(float(returns.mean()), 8),
            "median_return": round(float(returns.median()), 8),
            "avg_mfe_10bar": round(float(g["mfe_10bar_proxy"].mean()), 8),
            "avg_mae_10bar": round(float(g["mae_10bar_proxy"].mean()), 8),
            "status": "CLUSTER_CANDIDATE"
        })

    clusters = sorted(clusters, key=lambda x: (x["profit_factor_proxy"], x["win_rate"], x["trades"]), reverse=True)
    cluster_file.write_text(json.dumps(clusters, indent=2, ensure_ascii=False), encoding="utf-8")

    pattern_genome = []
    for c in clusters[:50]:
        pattern_genome.append({
            "pattern_id": c["cluster_id"],
            "asset": c["asset"],
            "family": c["family"],
            "genome": {
                "session": c["session"],
                "trend_regime": c["trend_regime"],
                "volatility_regime": c["volatility_regime"],
                "trigger": c["trigger"]
            },
            "evidence": {
                "trades": c["trades"],
                "win_rate": c["win_rate"],
                "profit_factor_proxy": c["profit_factor_proxy"],
                "avg_return": c["avg_return"]
            },
            "mutation_seeds": [
                "add_session_filter",
                "add_volatility_filter",
                "add_trend_filter",
                "add_mtf_filter",
                "add_structure_filter"
            ]
        })

    pattern_file.write_text(json.dumps(pattern_genome, indent=2, ensure_ascii=False), encoding="utf-8")

else:
    trade_dna_file.write_text("", encoding="utf-8")
    winner_file.write_text("", encoding="utf-8")
    loser_file.write_text("", encoding="utf-8")
    cluster_file.write_text("[]", encoding="utf-8")
    pattern_file.write_text("[]", encoding="utf-8")

report = {
    "STATUS": "P1871_TO_P1875_DNA_EXTRACTION_FACTORY_COMPLETED",
    "P1871_TRADE_DNA_ROWS": int(len(trade_df)),
    "P1872_WINNER_DNA_ROWS": int((trade_df["outcome"] == "WIN").sum()) if len(trade_df) else 0,
    "P1873_LOSER_DNA_ROWS": int((trade_df["outcome"] == "LOSS").sum()) if len(trade_df) else 0,
    "P1874_DNA_CLUSTERS": len(json.loads(cluster_file.read_text(encoding="utf-8"))),
    "P1875_PATTERN_GENOMES": len(json.loads(pattern_file.read_text(encoding="utf-8"))),
    "FEATURE_EXPORTS": feature_exports,
    "OUTPUTS": {
        "trade_dna": str(trade_dna_file),
        "winner_dna": str(winner_file),
        "loser_dna": str(loser_file),
        "clusters": str(cluster_file),
        "pattern_genome": str(pattern_file)
    },
    "NEXT": "P1876_TO_P1880_SPECIALIST_EVOLUTION_FACTORY",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

(BASE / "p1871_to_p1875_dna_extraction_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
