import json, hashlib, time
from pathlib import Path

ASSET_UNIVERSE = {
    "brazil_futures": ["WIN","WDO","IND","DOL"],
    "forex": ["EURUSD","GBPUSD","USDJPY"],
    "commodities": ["XAUUSD"],
    "indices": ["SP500","NASDAQ"],
    "crypto": ["BTCUSD","ETHUSD"],
    "brazil_stocks": ["PETR4","VALE3","ITUB4","BBDC4","BBAS3","ABEV3","WEGE3","B3SA3","RENT3","PRIO3","SUZB3","ELET3","JBSS3","RAIL3","MGLU3"],
    "international_stocks": ["AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA","NFLX","AMD","INTC","JPM","BAC","KO","PEP","WMT","COST","DIS","NKE","XOM","CVX"]
}

TIMEFRAMES = ["TICK","M1","M5","M15","M30","H1","H4","D1"]
SOURCES = ["MT5_CSV","PROFIT_CSV","GENERIC_OHLCV_CSV","TICK_DATA"]

def dataset_id(asset, timeframe, source):
    raw=f"{asset}:{timeframe}:{source}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

def build_catalog():
    records=[]
    for group, assets in ASSET_UNIVERSE.items():
        for asset in assets:
            for tf in TIMEFRAMES:
                for source in SOURCES:
                    records.append({
                        "dataset_id": dataset_id(asset,tf,source),
                        "asset_group": group,
                        "asset": asset,
                        "timeframe": tf,
                        "source": source,
                        "status": "REGISTERED_PENDING_DATA",
                        "quality_gate": "REQUIRED",
                        "lineage": "REQUIRED",
                        "certification": "BLOCKED_UNTIL_REAL_DATA",
                        "live_allowed": False,
                        "real_broker_allowed": False
                    })
    return records

def run():
    out=Path("reports/P9.1_DATA_EXPANSION_ENGINE")
    out.mkdir(parents=True, exist_ok=True)
    catalog=build_catalog()
    lineage=[{
        "dataset_id": r["dataset_id"],
        "source": r["source"],
        "asset": r["asset"],
        "timeframe": r["timeframe"],
        "origin": "EXTERNAL_FILE_REQUIRED",
        "hash_required": True,
        "audit_required": True
    } for r in catalog]
    quality=[{
        "dataset_id": r["dataset_id"],
        "required_checks": ["schema","timestamp_order","duplicates","missing_values","ohlcv_consistency","volume_validity","spread_costs_when_available"],
        "status": "PENDING_REAL_FILE"
    } for r in catalog]
    snapshot={
        "P9.1_STATE_SNAPSHOT":{
            "STATUS":"P9.1_DATA_EXPANSION_ENGINE_REGISTERED",
            "TOTAL_DATASET_SLOTS":len(catalog),
            "ASSET_UNIVERSE":ASSET_UNIVERSE,
            "TIMEFRAMES":TIMEFRAMES,
            "SOURCES":SOURCES,
            "LIVE":"FORBIDDEN",
            "PRODUCTION":"BLOCKED",
            "REAL_BROKER":"DISABLED",
            "EDGE":"NONE",
            "CAUSALITY":"NOT_PROVEN",
            "NEXT":"INGEST_REAL_MT5_PROFIT_CSV_FILES",
            "EXPORT_READY":True
        }
    }
    (out/"dataset_catalog.json").write_text(json.dumps(catalog,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"dataset_lineage.json").write_text(json.dumps(lineage,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"dataset_quality_gate.json").write_text(json.dumps(quality,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P9.1_STATE_SNAPSHOT.json").write_text(json.dumps(snapshot,indent=2,ensure_ascii=False),encoding="utf-8")
    return snapshot

if __name__ == "__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
