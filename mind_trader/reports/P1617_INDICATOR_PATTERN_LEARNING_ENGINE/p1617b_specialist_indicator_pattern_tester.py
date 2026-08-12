import json
import pandas as pd
from pathlib import Path
from datetime import datetime, UTC

SPECIALISTS = Path("reports/P1610_SPECIALIST_LIBRARY/specialist_library.json")
FEATURES = Path("data/features")
OUT = Path("reports/P1617_INDICATOR_PATTERN_LEARNING_ENGINE")
REPORT = OUT / "p1617b_specialist_indicator_pattern_report.json"
DETAIL = OUT / "p1617b_specialist_indicator_pattern_detail.json"

def load(p, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

specialists = load(SPECIALISTS, [])

def feature_file(asset, tf):
    return FEATURES / f"{asset}_{tf}_features.csv"

def safe_float(x):
    try:
        return float(x)
    except Exception:
        return 0.0

patterns = []

for s in specialists:
    asset = s.get("asset")
    tf = s.get("timeframe")
    f = feature_file(asset, tf)

    if not f.exists():
        continue

    try:
        df = pd.read_csv(f)

        if len(df) < 100:
            continue

        candidates = []

        rules = [
            ("RSI_OVERSOLD", df["rsi_14"] < 30),
            ("RSI_OVERBOUGHT", df["rsi_14"] > 70),
            ("EMA_BULL", df["ema_21"] > df["ema_55"]),
            ("EMA_BEAR", df["ema_21"] < df["ema_55"]),
            ("BB_LOWER_ZONE", df["bb_position"] < 0.20),
            ("BB_UPPER_ZONE", df["bb_position"] > 0.80),
            ("DONCHIAN_LOW_ZONE", df["donchian_position"] < 0.20),
            ("DONCHIAN_HIGH_ZONE", df["donchian_position"] > 0.80),
            ("MACD_BULL", df["macd"] > df["macd_signal"]),
            ("MACD_BEAR", df["macd"] < df["macd_signal"]),
            ("FIBO_382_500", df["fibo_zone"] == "382_500"),
            ("FIBO_500_618", df["fibo_zone"] == "500_618"),
            ("LONG_WICK_REJECTION", df["trigger_long_wick_rejection"] == 1),
            ("BULLISH_ENGULFING", df["trigger_bullish_engulfing"] == 1),
            ("TREND_UP", df["trend_proxy"] == "TREND_UP"),
            ("TREND_DOWN", df["trend_proxy"] == "TREND_DOWN"),
            ("HIGH_VOL", df["volatility_proxy"] == "HIGH_VOL"),
            ("LOW_VOL", df["volatility_proxy"] == "LOW_VOL"),
        ]

        for name, mask in rules:
            count = int(mask.fillna(False).sum())
            coverage = count / len(df)

            if count < 10:
                continue

            score = (
                safe_float(s.get("deployment_score")) * 0.40 +
                safe_float(s.get("payoff_ratio_real")) * 2.00 +
                safe_float(s.get("profit_factor_real")) * 0.75 +
                safe_float(s.get("expectancy_per_trade_real")) * 100 +
                coverage * 5
            )

            candidates.append({
                "pattern": name,
                "matches": count,
                "coverage": round(coverage, 6),
                "pattern_score": round(score, 6)
            })

        candidates = sorted(candidates, key=lambda x: x["pattern_score"], reverse=True)

        patterns.append({
            "specialist_id": s.get("specialist_id"),
            "edge_id": s.get("edge_id"),
            "asset": asset,
            "timeframe": tf,
            "family": s.get("family"),
            "profile": s.get("profile"),
            "base_deployment_score": s.get("deployment_score"),
            "payoff_ratio_real": s.get("payoff_ratio_real"),
            "expectancy_per_trade_real": s.get("expectancy_per_trade_real"),
            "profit_factor_real": s.get("profit_factor_real"),
            "best_patterns": candidates[:10],
            "status": "PATTERN_TESTED",
            "ORDER_SENT": False,
            "REAL_ORDERS": "FORBIDDEN",
            "FTMO_REAL": "FORBIDDEN",
            "MT5_REAL": "FORBIDDEN"
        })

    except Exception as e:
        patterns.append({
            "specialist_id": s.get("specialist_id"),
            "asset": asset,
            "timeframe": tf,
            "status": "ERROR",
            "error": str(e)
        })

patterns = sorted(
    patterns,
    key=lambda x: (x.get("best_patterns") or [{"pattern_score":0}])[0].get("pattern_score",0),
    reverse=True
)

report = {
    "STATUS": "P1617B_SPECIALIST_INDICATOR_PATTERN_TESTER_COMPLETED",
    "SPECIALISTS_INPUT": len(specialists),
    "SPECIALISTS_TESTED": len([p for p in patterns if p.get("status") == "PATTERN_TESTED"]),
    "ERRORS": len([p for p in patterns if p.get("status") == "ERROR"]),
    "TOP10_PATTERN_SPECIALISTS": patterns[:10],
    "NEXT": "P1618_MARKET_STRUCTURE_ENGINE",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

DETAIL.write_text(json.dumps(patterns, indent=2, ensure_ascii=False), encoding="utf-8")
REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "STATUS": report["STATUS"],
    "SPECIALISTS_INPUT": report["SPECIALISTS_INPUT"],
    "SPECIALISTS_TESTED": report["SPECIALISTS_TESTED"],
    "ERRORS": report["ERRORS"],
    "NEXT": report["NEXT"]
}, indent=2, ensure_ascii=False))
