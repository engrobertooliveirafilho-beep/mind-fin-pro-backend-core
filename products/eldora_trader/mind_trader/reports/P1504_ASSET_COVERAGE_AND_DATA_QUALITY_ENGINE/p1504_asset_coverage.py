import json, re
from pathlib import Path
from datetime import datetime, UTC
from collections import defaultdict

OUT = Path("reports/P1504_ASSET_COVERAGE_AND_DATA_QUALITY_ENGINE")
OUT.mkdir(parents=True, exist_ok=True)

DATA = Path("data/normalized")

TIMEFRAMES = ["M1","M2","M5","M15","M20","M30","H1","H4","D1","W1","MN1"]

def parse_file(f):
    name = f.stem.replace("_normalized", "")

    if re.match(r"^TEST_", name):
        return name, "TEST", "BLACKLIST"

    m = re.match(r"^MT5_(.+)_(M1|M5|M15|M30|H1|H4|D1)$", name)
    if m:
        return m.group(1), m.group(2), "FOREX_MT5"

    m = re.match(r"^(.+)_(M1|M2|M5|M15|M20|M30|H1|H4|D1|W1|MN1)$", name)
    if m:
        return m.group(1), m.group(2), "MARKET"

    return name, "UNKNOWN", "MARKET"

def classify_asset(asset):
    if asset.startswith("TEST_"):
        return "BLACKLIST_TEST"
    if asset in ["EURUSD","GBPUSD","AUDUSD","USDCAD","USDJPY","XAUUSD"]:
        return "FOREX_OR_METAL"
    if asset in ["WINFUT","WDOFUT","WSPFUT","CADFUT","DOLB11","DOLCC","DOLCV","DOLPT"]:
        return "FUTURES"
    if asset.startswith("DI1") or asset in ["SELIC","IPCA"]:
        return "RATES_MACRO"
    if asset.endswith("11") or asset in ["IFIX"]:
        return "FII_OR_ETF"
    if asset.startswith("BTC") or asset in ["QBTC11","XBIT11","GBTC11","NBIT11","OBTC3","OBTC3F"]:
        return "CRYPTO"
    if asset in ["IBOV","IBRA","IGCX","IGCT","IMOB"]:
        return "INDEX"
    return "EQUITY_OR_OTHER"

files = list(DATA.glob("*.csv"))

assets = defaultdict(lambda: {
    "files": [],
    "timeframes": set(),
    "market_class": None,
    "quality_flags": [],
    "coverage_score": 0,
    "day_trade_ready": False,
    "swing_trade_ready": False
})

blacklist = []
whitelist = []

for f in files:
    asset, tf, source_type = parse_file(f)
    cls = classify_asset(asset)

    assets[asset]["files"].append(f.name)
    assets[asset]["timeframes"].add(tf)
    assets[asset]["market_class"] = cls

    if cls == "BLACKLIST_TEST":
        assets[asset]["quality_flags"].append("TEST_DATASET")
        blacklist.append(asset)

for asset, row in assets.items():
    tfs = row["timeframes"]
    row["timeframes"] = sorted(list(tfs))
    row["dataset_count"] = len(row["files"])

    score = 0
    if "M1" in tfs or "M5" in tfs or "M15" in tfs:
        score += 2
    if "M30" in tfs or "H1" in tfs:
        score += 2
    if "H4" in tfs or "D1" in tfs:
        score += 2
    if len(tfs) >= 4:
        score += 2
    if len(tfs) >= 7:
        score += 2

    row["coverage_score"] = score
    row["day_trade_ready"] = any(x in tfs for x in ["M1","M5","M15","M30"])
    row["swing_trade_ready"] = any(x in tfs for x in ["H1","H4","D1","W1","MN1"])

    if row["market_class"] != "BLACKLIST_TEST" and score >= 2:
        whitelist.append(asset)

asset_rows = []
for asset, row in assets.items():
    asset_rows.append({
        "asset": asset,
        "market_class": row["market_class"],
        "dataset_count": row["dataset_count"],
        "timeframes": row["timeframes"],
        "coverage_score": row["coverage_score"],
        "day_trade_ready": row["day_trade_ready"],
        "swing_trade_ready": row["swing_trade_ready"],
        "quality_flags": sorted(list(set(row["quality_flags"]))),
        "files": row["files"]
    })

asset_rows = sorted(asset_rows, key=lambda x: (x["coverage_score"], x["dataset_count"]), reverse=True)

report = {
    "STATUS": "P1504_ASSET_COVERAGE_AND_DATA_QUALITY_ENGINE_COMPLETED",
    "DATASETS": len(files),
    "ASSETS_UNIQUE": len(asset_rows),
    "TIMEFRAMES_UNIQUE": len(set(tf for r in asset_rows for tf in r["timeframes"])),
    "WHITELIST_ASSETS": len(set(whitelist)),
    "BLACKLIST_ASSETS": len(set(blacklist)),
    "DAY_TRADE_READY_ASSETS": len([r for r in asset_rows if r["day_trade_ready"]]),
    "SWING_TRADE_READY_ASSETS": len([r for r in asset_rows if r["swing_trade_ready"]]),
    "TOP_COVERED_ASSETS": asset_rows[:20],
    "BLACKLIST": sorted(list(set(blacklist))),
    "NEXT": "USE_WHITELIST_FOR_INSTITUTIONAL_BACKTESTS",
    "REAL_ORDERS": "FORBIDDEN",
    "FTMO_REAL": "FORBIDDEN",
    "MT5_REAL": "FORBIDDEN",
    "generated_at": datetime.now(UTC).isoformat()
}

(OUT / "p1504_asset_coverage_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
(OUT / "p1504_assets_full.json").write_text(json.dumps(asset_rows, indent=2, ensure_ascii=False), encoding="utf-8")
(OUT / "p1504_whitelist_assets.json").write_text(json.dumps(sorted(list(set(whitelist))), indent=2, ensure_ascii=False), encoding="utf-8")
(OUT / "p1504_blacklist_assets.json").write_text(json.dumps(sorted(list(set(blacklist))), indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps(report, indent=2, ensure_ascii=False))
