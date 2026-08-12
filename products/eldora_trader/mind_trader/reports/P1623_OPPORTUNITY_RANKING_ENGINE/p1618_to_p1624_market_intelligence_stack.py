import json
import pandas as pd
from pathlib import Path
from datetime import datetime, UTC
from collections import defaultdict

FEATURES = Path("data/features")
SPECIALISTS = Path("reports/P1610_SPECIALIST_LIBRARY/specialist_library.json")

OUT1618 = Path("reports/P1618_MARKET_STRUCTURE_ENGINE")
OUT1619 = Path("reports/P1619_CANDLE_TRIGGER_ENGINE")
OUT1620 = Path("reports/P1620_CONFLUENCE_ENGINE")
OUT1621 = Path("reports/P1621_ASSET_INTELLIGENCE_LIBRARY")
OUT1622 = Path("reports/P1622_SPECIALIST_KNOWLEDGE_BASE")
OUT1623 = Path("reports/P1623_OPPORTUNITY_RANKING_ENGINE")
OUT1624 = Path("reports/P1624_SEASONALITY_ENGINE")

for p in [OUT1618,OUT1619,OUT1620,OUT1621,OUT1622,OUT1623,OUT1624]:
    p.mkdir(parents=True, exist_ok=True)

def load_json(p, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

specialists = load_json(SPECIALISTS, [])

structure_rows = []
candle_rows = []
confluence_rows = []
seasonality_rows = []

for f in FEATURES.glob("*_features.csv"):
    try:
        df = pd.read_csv(f)
        if len(df) < 100:
            continue

        df["time"] = pd.to_datetime(df["time"], errors="coerce", dayfirst=True)
        df = df.dropna(subset=["time","open","high","low","close"]).reset_index(drop=True)

        name = f.stem.replace("_features","")
        parts = name.split("_")
        asset = parts[0]
        timeframe = parts[1] if len(parts) > 1 else "UNKNOWN"

        df["swing_high"] = df["high"].rolling(5, center=True).max() == df["high"]
        df["swing_low"] = df["low"].rolling(5, center=True).min() == df["low"]

        df["prev_swing_high"] = df["high"].where(df["swing_high"]).ffill().shift(1)
        df["prev_swing_low"] = df["low"].where(df["swing_low"]).ffill().shift(1)

        df["bos_bull"] = (df["close"] > df["prev_swing_high"]).astype(int)
        df["bos_bear"] = (df["close"] < df["prev_swing_low"]).astype(int)

        df["liquidity_sweep_high"] = ((df["high"] > df["prev_swing_high"]) & (df["close"] < df["prev_swing_high"])).astype(int)
        df["liquidity_sweep_low"] = ((df["low"] < df["prev_swing_low"]) & (df["close"] > df["prev_swing_low"])).astype(int)

        df["structure_trend"] = "RANGE"
        df.loc[df["ema_21"] > df["ema_55"], "structure_trend"] = "TREND_UP"
        df.loc[df["ema_21"] < df["ema_55"], "structure_trend"] = "TREND_DOWN"

        mid = (df["donchian_high_20"] + df["donchian_low_20"]) / 2
        df["premium_discount_zone"] = "MID"
        df.loc[df["close"] > mid, "premium_discount_zone"] = "PREMIUM"
        df.loc[df["close"] < mid, "premium_discount_zone"] = "DISCOUNT"

        body = (df["close"] - df["open"]).abs()
        rng = (df["high"] - df["low"]).replace(0, pd.NA)
        upper = df["high"] - df[["open","close"]].max(axis=1)
        lower = df[["open","close"]].min(axis=1) - df["low"]

        df["candle_doji"] = ((body / rng) < 0.15).astype(int)
        df["candle_hammer"] = ((lower / rng > 0.55) & (upper / rng < 0.25)).astype(int)
        df["candle_shooting_star"] = ((upper / rng > 0.55) & (lower / rng < 0.25)).astype(int)
        df["candle_bullish_engulfing"] = (
            (df["close"] > df["open"]) &
            (df["close"].shift(1) < df["open"].shift(1)) &
            (df["close"] > df["open"].shift(1)) &
            (df["open"] < df["close"].shift(1))
        ).astype(int)
        df["candle_bearish_engulfing"] = (
            (df["close"] < df["open"]) &
            (df["close"].shift(1) > df["open"].shift(1)) &
            (df["close"] < df["open"].shift(1)) &
            (df["open"] > df["close"].shift(1))
        ).astype(int)
        df["inside_bar"] = ((df["high"] < df["high"].shift(1)) & (df["low"] > df["low"].shift(1))).astype(int)
        df["outside_bar"] = ((df["high"] > df["high"].shift(1)) & (df["low"] < df["low"].shift(1))).astype(int)

        df["hour"] = df["time"].dt.hour
        df["day_of_week"] = df["time"].dt.day_name()
        df["month"] = df["time"].dt.month

        df["session"] = "OTHER"
        df.loc[df["hour"].between(0,7), "session"] = "ASIA"
        df.loc[df["hour"].between(8,12), "session"] = "LONDON"
        df.loc[df["hour"].between(13,17), "session"] = "NEW_YORK"
        df.loc[df["hour"].between(18,23), "session"] = "POST_NY"

        latest = df.iloc[-1]

        structure_score = 0
        structure_score += 20 if latest.get("bos_bull",0) or latest.get("bos_bear",0) else 0
        structure_score += 15 if latest.get("liquidity_sweep_high",0) or latest.get("liquidity_sweep_low",0) else 0
        structure_score += 10 if latest.get("structure_trend") in ["TREND_UP","TREND_DOWN"] else 0

        candle_score = 0
        candle_score += 20 if latest.get("candle_bullish_engulfing",0) or latest.get("candle_bearish_engulfing",0) else 0
        candle_score += 15 if latest.get("candle_hammer",0) or latest.get("candle_shooting_star",0) else 0
        candle_score += 10 if latest.get("inside_bar",0) or latest.get("outside_bar",0) else 0

        indicator_score = 0
        indicator_score += 10 if latest.get("rsi_14",50) < 30 or latest.get("rsi_14",50) > 70 else 0
        indicator_score += 10 if latest.get("bb_position",0.5) < 0.2 or latest.get("bb_position",0.5) > 0.8 else 0
        indicator_score += 10 if latest.get("macd",0) > latest.get("macd_signal",0) else 0
        indicator_score += 10 if latest.get("fibo_zone") in ["382_500","500_618"] else 0

        confluence_score = min(100, structure_score + candle_score + indicator_score)

        structure_rows.append({
            "asset":asset,"timeframe":timeframe,
            "structure_trend":latest.get("structure_trend"),
            "bos_bull":int(latest.get("bos_bull",0)),
            "bos_bear":int(latest.get("bos_bear",0)),
            "liquidity_sweep_high":int(latest.get("liquidity_sweep_high",0)),
            "liquidity_sweep_low":int(latest.get("liquidity_sweep_low",0)),
            "premium_discount_zone":latest.get("premium_discount_zone"),
            "structure_score":structure_score
        })

        candle_rows.append({
            "asset":asset,"timeframe":timeframe,
            "doji":int(latest.get("candle_doji",0)),
            "hammer":int(latest.get("candle_hammer",0)),
            "shooting_star":int(latest.get("candle_shooting_star",0)),
            "bullish_engulfing":int(latest.get("candle_bullish_engulfing",0)),
            "bearish_engulfing":int(latest.get("candle_bearish_engulfing",0)),
            "inside_bar":int(latest.get("inside_bar",0)),
            "outside_bar":int(latest.get("outside_bar",0)),
            "candle_score":candle_score
        })

        confluence_rows.append({
            "asset":asset,"timeframe":timeframe,
            "structure_score":structure_score,
            "candle_score":candle_score,
            "indicator_score":indicator_score,
            "confluence_score":confluence_score,
            "session":latest.get("session"),
            "hour":int(latest.get("hour")),
            "day_of_week":latest.get("day_of_week"),
            "month":int(latest.get("month")),
            "REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","MT5_REAL":"FORBIDDEN"
        })

        seasonality_rows.append({
            "asset":asset,"timeframe":timeframe,
            "latest_session":latest.get("session"),
            "latest_hour":int(latest.get("hour")),
            "latest_day_of_week":latest.get("day_of_week"),
            "latest_month":int(latest.get("month"))
        })

    except Exception as e:
        structure_rows.append({"file":str(f),"status":"ERROR","error":str(e)})

asset_intel = defaultdict(lambda: {
    "asset":None,"specialists":0,"best_score":0,"best_payoff":0,
    "profiles":defaultdict(int),"families":defaultdict(int),"timeframes":defaultdict(int)
})

specialist_kb = []

for s in specialists:
    asset = s.get("asset")
    a = asset_intel[asset]
    a["asset"] = asset
    a["specialists"] += 1
    a["best_score"] = max(a["best_score"], float(s.get("deployment_score") or 0))
    a["best_payoff"] = max(a["best_payoff"], float(s.get("payoff_ratio_real") or 0))
    a["profiles"][s.get("profile")] += 1
    a["families"][s.get("family")] += 1
    a["timeframes"][s.get("timeframe")] += 1

    specialist_kb.append({
        "specialist_id":s.get("specialist_id"),
        "asset":asset,
        "timeframe":s.get("timeframe"),
        "family":s.get("family"),
        "profile":s.get("profile"),
        "regime_tags":s.get("regime_tags"),
        "payoff_ratio_real":s.get("payoff_ratio_real"),
        "expectancy_per_trade_real":s.get("expectancy_per_trade_real"),
        "profit_factor_real":s.get("profit_factor_real"),
        "avg_holding_bars":s.get("avg_holding_bars"),
        "best_entry_hour":s.get("best_entry_hour"),
        "knowledge_status":"SPECIALIST_KB_REGISTERED"
    })

asset_library = []
for asset, a in asset_intel.items():
    asset_library.append({
        "asset":asset,
        "specialists":a["specialists"],
        "best_score":a["best_score"],
        "best_payoff":a["best_payoff"],
        "profiles":dict(a["profiles"]),
        "families":dict(a["families"]),
        "timeframes":dict(a["timeframes"]),
        "asset_status":"ASSET_INTELLIGENCE_READY"
    })

opportunities = []
conf_map = {(c["asset"],c["timeframe"]):c for c in confluence_rows if "asset" in c}

for s in specialists:
    key = (s.get("asset"),s.get("timeframe"))
    c = conf_map.get(key)
    if not c:
        continue

    opportunity_score = (
        float(s.get("deployment_score") or 0) * 0.55 +
        float(c.get("confluence_score") or 0) * 0.45
    )

    opportunities.append({
        "asset":s.get("asset"),
        "timeframe":s.get("timeframe"),
        "specialist_id":s.get("specialist_id"),
        "family":s.get("family"),
        "profile":s.get("profile"),
        "deployment_score":s.get("deployment_score"),
        "confluence_score":c.get("confluence_score"),
        "opportunity_score":round(opportunity_score,6),
        "session":c.get("session"),
        "hour":c.get("hour"),
        "decision":"WATCH_ONLY" if opportunity_score < 85 else "ELITE_CANDIDATE",
        "ORDER_SENT":False,
        "REAL_ORDERS":"FORBIDDEN",
        "FTMO_REAL":"FORBIDDEN",
        "MT5_REAL":"FORBIDDEN"
    })

opportunities = sorted(opportunities, key=lambda x:x["opportunity_score"], reverse=True)

(OUT1618/"market_structure_snapshot.json").write_text(json.dumps(structure_rows,indent=2,ensure_ascii=False),encoding="utf-8")
(OUT1619/"candle_trigger_snapshot.json").write_text(json.dumps(candle_rows,indent=2,ensure_ascii=False),encoding="utf-8")
(OUT1620/"confluence_snapshot.json").write_text(json.dumps(confluence_rows,indent=2,ensure_ascii=False),encoding="utf-8")
(OUT1621/"asset_intelligence_library.json").write_text(json.dumps(asset_library,indent=2,ensure_ascii=False),encoding="utf-8")
(OUT1622/"specialist_knowledge_base.json").write_text(json.dumps(specialist_kb,indent=2,ensure_ascii=False),encoding="utf-8")
(OUT1623/"opportunity_ranking.json").write_text(json.dumps(opportunities,indent=2,ensure_ascii=False),encoding="utf-8")
(OUT1624/"seasonality_snapshot.json").write_text(json.dumps(seasonality_rows,indent=2,ensure_ascii=False),encoding="utf-8")

master = {
    "STATUS":"P1618_TO_P1624_MARKET_INTELLIGENCE_STACK_COMPLETED",
    "MARKET_STRUCTURE_ROWS":len(structure_rows),
    "CANDLE_TRIGGER_ROWS":len(candle_rows),
    "CONFLUENCE_ROWS":len(confluence_rows),
    "ASSETS_IN_LIBRARY":len(asset_library),
    "SPECIALISTS_IN_KB":len(specialist_kb),
    "OPPORTUNITIES_RANKED":len(opportunities),
    "TOP5_OPPORTUNITIES":opportunities[:5],
    "NEXT":"P1625_MULTI_TIMEFRAME_CONFIRMATION_AND_REGIME_SELECTOR",
    "ORDER_SENT":False,
    "REAL_ORDERS":"FORBIDDEN",
    "FTMO_REAL":"FORBIDDEN",
    "MT5_REAL":"FORBIDDEN",
    "generated_at":datetime.now(UTC).isoformat()
}

Path("reports/P1623_OPPORTUNITY_RANKING_ENGINE/p1623_master_market_intelligence_report.json").write_text(json.dumps(master,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps(master,indent=2,ensure_ascii=False))
