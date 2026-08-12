import json, hashlib
from pathlib import Path
from datetime import datetime, UTC

ASSETS=[
 {"symbol":"WIN","exchange":"B3","country":"BR","asset_class":"futures","currency":"BRL","sector":"index"},
 {"symbol":"WDO","exchange":"B3","country":"BR","asset_class":"futures","currency":"BRL","sector":"fx"},
 {"symbol":"PETR4","exchange":"B3","country":"BR","asset_class":"stock","currency":"BRL","sector":"energy"},
 {"symbol":"VALE3","exchange":"B3","country":"BR","asset_class":"stock","currency":"BRL","sector":"materials"},
 {"symbol":"ITUB4","exchange":"B3","country":"BR","asset_class":"stock","currency":"BRL","sector":"financials"},
 {"symbol":"AAPL","exchange":"NASDAQ","country":"US","asset_class":"stock","currency":"USD","sector":"technology"},
 {"symbol":"MSFT","exchange":"NASDAQ","country":"US","asset_class":"stock","currency":"USD","sector":"technology"},
 {"symbol":"NVDA","exchange":"NASDAQ","country":"US","asset_class":"stock","currency":"USD","sector":"semiconductors"},
 {"symbol":"SPY","exchange":"NYSEARCA","country":"US","asset_class":"etf","currency":"USD","sector":"index"},
 {"symbol":"QQQ","exchange":"NASDAQ","country":"US","asset_class":"etf","currency":"USD","sector":"index"},
 {"symbol":"EURUSD","exchange":"FX","country":"GLOBAL","asset_class":"forex","currency":"USD","sector":"majors"},
 {"symbol":"GBPUSD","exchange":"FX","country":"GLOBAL","asset_class":"forex","currency":"USD","sector":"majors"},
 {"symbol":"USDJPY","exchange":"FX","country":"GLOBAL","asset_class":"forex","currency":"JPY","sector":"majors"},
 {"symbol":"XAUUSD","exchange":"COMEX/OTC","country":"GLOBAL","asset_class":"commodity","currency":"USD","sector":"metals"},
 {"symbol":"WTI","exchange":"NYMEX","country":"US","asset_class":"commodity","currency":"USD","sector":"energy"},
 {"symbol":"BTCUSD","exchange":"CRYPTO","country":"GLOBAL","asset_class":"crypto","currency":"USD","sector":"digital_asset"},
 {"symbol":"ETHUSD","exchange":"CRYPTO","country":"GLOBAL","asset_class":"crypto","currency":"USD","sector":"digital_asset"}
]

def asset_id(a):
    return hashlib.sha256(f"{a['symbol']}:{a['exchange']}:{a['asset_class']}".encode()).hexdigest()[:18]

def build_registry():
    out=[]
    for a in ASSETS:
        r=dict(a)
        r["asset_id"]=asset_id(a)
        r["active"]=True
        r["tradable"]=False
        r["research_only"]=True
        r["data_sources_required"]=["MT5_CSV","PROFIT_CSV","GENERIC_OHLCV_CSV","TICK_CSV"]
        r["dataset_count"]=0
        r["certified_dataset_count"]=0
        r["live"]="FORBIDDEN"
        r["real_broker"]="DISABLED"
        out.append(r)
    return out

def coverage(registry):
    classes={}
    countries={}
    for r in registry:
        classes[r["asset_class"]]=classes.get(r["asset_class"],0)+1
        countries[r["country"]]=countries.get(r["country"],0)+1
    return {"total_assets":len(registry),"by_asset_class":classes,"by_country":countries,"certified_dataset_count":sum(r["certified_dataset_count"] for r in registry)}

def run():
    out=Path("reports/P11.3_GLOBAL_MARKET_REGISTRY")
    out.mkdir(parents=True,exist_ok=True)
    registry=build_registry()
    cov=coverage(registry)
    manifest={
        "STATUS":"P11.3_GLOBAL_MARKET_REGISTRY_IMPLEMENTED",
        "TOTAL_ASSETS":len(registry),
        "COVERAGE":cov,
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "FTMO_REAL":"FORBIDDEN",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"global_market_registry.json").write_text(json.dumps(registry,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"coverage_report.json").write_text(json.dumps(cov,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P11.3_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
