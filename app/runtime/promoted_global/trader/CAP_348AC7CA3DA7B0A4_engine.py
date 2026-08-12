import json, hashlib
from pathlib import Path
from datetime import datetime, UTC

SOURCES=[
 {"source_id":"MT5_CSV","type":"csv","markets":["forex","commodities","indices","crypto","stocks"],"requires_manual_export":True,"trust_level":"HIGH_IF_BROKER_HISTORY"},
 {"source_id":"PROFIT_CSV","type":"csv","markets":["brazil_futures","brazil_stocks"],"requires_manual_export":True,"trust_level":"HIGH_IF_PLATFORM_HISTORY"},
 {"source_id":"GENERIC_OHLCV_CSV","type":"csv","markets":["all"],"requires_manual_export":True,"trust_level":"MEDIUM_REQUIRES_VALIDATION"},
 {"source_id":"TICK_CSV","type":"csv","markets":["futures","forex","crypto"],"requires_manual_export":True,"trust_level":"HIGH_IF_TICK_COMPLETE"}
]

TARGET_ASSETS=["WIN","WDO","IND","DOL","PETR4","VALE3","ITUB4","BBDC4","BBAS3","WEGE3","BOVA11","SPY","QQQ","DIA","AAPL","MSFT","NVDA","AMZN","META","GOOGL","TSLA","EURUSD","GBPUSD","USDJPY","AUDUSD","USDCAD","XAUUSD","XAGUSD","WTI","BRENT","NATGAS","BTCUSD","ETHUSD","SOLUSD","BNBUSD"]
TIMEFRAMES=["TICK","M1","M5","M15","M30","H1","H4","D1"]

def registry_id(source, asset, timeframe):
    return hashlib.sha256(f"{source}:{asset}:{timeframe}".encode()).hexdigest()[:18]

def build_registry():
    rows=[]
    for src in SOURCES:
        for asset in TARGET_ASSETS:
            for tf in TIMEFRAMES:
                rows.append({
                    "registry_id":registry_id(src["source_id"],asset,tf),
                    "source_id":src["source_id"],
                    "asset":asset,
                    "timeframe":tf,
                    "source_type":src["type"],
                    "trust_level":src["trust_level"],
                    "requires_manual_export":src["requires_manual_export"],
                    "status":"REGISTERED_PENDING_FILE",
                    "certification_required":True,
                    "lineage_required":True,
                    "live":"FORBIDDEN",
                    "real_broker":"DISABLED"
                })
    return rows

def run():
    out=Path("reports/P13.1_DATA_SOURCE_REGISTRY")
    out.mkdir(parents=True,exist_ok=True)
    registry=build_registry()
    manifest={
        "STATUS":"P13.1_DATA_SOURCE_REGISTRY_IMPLEMENTED",
        "TOTAL_SOURCE_SLOTS":len(registry),
        "SOURCES":SOURCES,
        "ASSETS":TARGET_ASSETS,
        "TIMEFRAMES":TIMEFRAMES,
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"data_source_registry.json").write_text(json.dumps(registry,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P13.1_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
