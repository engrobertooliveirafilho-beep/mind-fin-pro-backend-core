import json
from pathlib import Path
from datetime import datetime, UTC
from collections import defaultdict

SRC = Path("reports/P1505_DATA_INGESTION_ENGINE/p1506_ranked_convergence_payoff_edges.json")
OUT = Path("reports/P1610_SPECIALIST_LIBRARY")
SPECIALISTS = OUT / "specialist_library.json"
ASSETS = OUT / "asset_library.json"
REPORT = OUT / "p1610_specialist_asset_library_report.json"

def load(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []

edges = load(SRC)

def profile(tf):
    if tf in ["M1","M5"]:
        return "SCALP_SPECIALIST"
    if tf in ["M15","M30","H1"]:
        return "DAY_TRADE_SPECIALIST"
    if tf in ["H4","D1","W1","MN1"]:
        return "SWING_SPECIALIST"
    return "UNKNOWN_SPECIALIST"

def regime_tags(edge):
    fam = edge.get("family")
    tf = edge.get("timeframe")
    tags = []

    if fam in ["RSI_REVERSION","BOLLINGER_REVERSION"]:
        tags.append("RANGE_REVERSION")
    if fam in ["EMA_CROSS","SMA_CROSS","ATR_TREND"]:
        tags.append("TREND_FOLLOWING")
    if fam in ["BREAKOUT","DONCHIAN"]:
        tags.append("BREAKOUT_VOLATILITY")

    if tf in ["M1","M5"]:
        tags.append("FAST_EXECUTION")
    if tf in ["M15","M30","H1"]:
        tags.append("INTRADAY")
    if tf in ["H4","D1"]:
        tags.append("POSITIONAL")

    return tags

specialists = []
asset_map = defaultdict(lambda: {
    "asset": None,
    "edges": 0,
    "profiles": defaultdict(int),
    "families": defaultdict(int),
    "timeframes": defaultdict(int),
    "best_payoff": 0,
    "best_expectancy": 0,
    "best_deployment_score": 0,
    "specialists": []
})

for e in edges:
    trades = int(e.get("trades") or 0)
    payoff = float(e.get("payoff_ratio_real") or 0)
    exp = float(e.get("expectancy_per_trade_real") or 0)
    score = float(e.get("deployment_score") or 0)

    if trades < 5 or payoff <= 1 or exp <= 0:
        continue

    asset = e.get("asset")
    tf = e.get("timeframe")
    fam = e.get("family")
    prof = profile(tf)

    specialist_id = f"{asset}_{tf}_{fam}_{e.get('edge_id')}"

    specialist = {
        "specialist_id": specialist_id,
        "edge_id": e.get("edge_id"),
        "asset": asset,
        "timeframe": tf,
        "family": fam,
        "params": e.get("params"),
        "profile": prof,
        "regime_tags": regime_tags(e),
        "trades": trades,
        "win_rate": e.get("win_rate"),
        "payoff_ratio_real": payoff,
        "expectancy_per_trade_real": exp,
        "profit_factor_real": e.get("profit_factor_real"),
        "avg_holding_bars": e.get("avg_holding_bars"),
        "best_entry_hour": e.get("best_entry_hour"),
        "deployment_score": score,
        "status": "SPECIALIST_REGISTERED",
        "certification": e.get("certification", "RESEARCH_OR_PROFILE_PENDING"),
        "ORDER_SENT": False,
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    }

    specialists.append(specialist)

    a = asset_map[asset]
    a["asset"] = asset
    a["edges"] += 1
    a["profiles"][prof] += 1
    a["families"][fam] += 1
    a["timeframes"][tf] += 1
    a["best_payoff"] = max(a["best_payoff"], payoff)
    a["best_expectancy"] = max(a["best_expectancy"], exp)
    a["best_deployment_score"] = max(a["best_deployment_score"], score)
    a["specialists"].append(specialist_id)

asset_library = []
for asset, a in asset_map.items():
    asset_library.append({
        "asset": asset,
        "registered_specialists": a["edges"],
        "profiles": dict(a["profiles"]),
        "families": dict(a["families"]),
        "timeframes": dict(a["timeframes"]),
        "best_payoff": a["best_payoff"],
        "best_expectancy": a["best_expectancy"],
        "best_deployment_score": a["best_deployment_score"],
        "specialists": a["specialists"],
        "asset_status": "ASSET_LIBRARY_REGISTERED",
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN"
    })

specialists = sorted(specialists, key=lambda x: x["deployment_score"], reverse=True)
asset_library = sorted(asset_library, key=lambda x: x["registered_specialists"], reverse=True)

SPECIALISTS.write_text(json.dumps(specialists, indent=2, ensure_ascii=False), encoding="utf-8")
ASSETS.write_text(json.dumps(asset_library, indent=2, ensure_ascii=False), encoding="utf-8")

report = {
    "STATUS": "P1610_SPECIALIST_AND_ASSET_LIBRARY_ENGINE_COMPLETED",
    "SPECIALISTS_REGISTERED": len(specialists),
    "ASSETS_REGISTERED": len(asset_library),
    "TOP_SPECIALISTS": specialists[:10],
    "ASSET_LIBRARY_TOP": asset_library[:10],
    "NEXT": "P1611_REGIME_CLASSIFICATION_ENGINE",
    "ORDER_SENT": False,
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({
    "STATUS": report["STATUS"],
    "SPECIALISTS_REGISTERED": report["SPECIALISTS_REGISTERED"],
    "ASSETS_REGISTERED": report["ASSETS_REGISTERED"],
    "NEXT": report["NEXT"]
}, indent=2, ensure_ascii=False))
