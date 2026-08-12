import json
from pathlib import Path
from datetime import datetime, UTC

DATA_ROOT="data"

ASSET_GROUPS={
    "BR":["WIN","WDO","IND","DOL","PETR4","VALE3","ITUB4","BBDC4","BBAS3","WEGE3","BOVA11"],
    "US":["AAPL","MSFT","NVDA","AMZN","META","GOOGL","TSLA","SPY","QQQ","DIA"],
    "FOREX":["EURUSD","GBPUSD","USDJPY","AUDUSD","USDCAD"],
    "COMMODITIES":["XAUUSD","XAGUSD","WTI","BRENT","NATGAS"],
    "CRYPTO":["BTCUSD","ETHUSD","SOLUSD","BNBUSD"]
}

def scan():
    files=list(Path(DATA_ROOT).rglob("*.csv"))
    names=[f.name.upper() for f in files]
    result={"datasets":len(files),"groups":{}}

    for group,assets in ASSET_GROUPS.items():
        covered=sum(1 for asset in assets if any(asset in n for n in names))
        result["groups"][group]={
            "assets":len(assets),
            "covered":covered,
            "coverage_ratio":round(covered/len(assets),4)
        }

    return result

def run():
    summary=scan()
    report={
        "STATUS":"P13.6_DATASET_COVERAGE_GROWTH_IMPLEMENTED",
        "SUMMARY":summary,
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    out=Path("reports/P13.6_DATASET_COVERAGE_GROWTH")
    out.mkdir(parents=True,exist_ok=True)
    (out/"coverage_growth.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
