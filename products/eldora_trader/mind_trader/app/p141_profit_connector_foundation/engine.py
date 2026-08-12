import json
from pathlib import Path
from datetime import datetime, UTC

WATCH_DIR=Path("data/incoming/profit/watch")

SUPPORTED_ASSETS=[
 "WIN","WDO","IND","DOL",
 "PETR4","VALE3","ITUB4","BBDC4","BBAS3","WEGE3","BOVA11"
]

def discover_exports():
    files=list(WATCH_DIR.glob("*.csv"))
    discovered=[]
    for f in files:
        upper=f.name.upper()
        asset=None
        for a in SUPPORTED_ASSETS:
            if a in upper:
                asset=a
                break
        discovered.append({
            "file":str(f),
            "asset":asset,
            "recognized":asset is not None
        })
    return discovered

def run():
    WATCH_DIR.mkdir(parents=True,exist_ok=True)

    exports=discover_exports()

    manifest={
        "STATUS":"P14.1_PROFIT_CONNECTOR_FOUNDATION_IMPLEMENTED",
        "WATCH_DIRECTORY":str(WATCH_DIR),
        "SUPPORTED_ASSETS":SUPPORTED_ASSETS,
        "FILES_FOUND":len(exports),
        "FILES_RECOGNIZED":sum(x["recognized"] for x in exports),
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }

    out=Path("reports/P14.1_PROFIT_CONNECTOR_FOUNDATION")
    out.mkdir(parents=True,exist_ok=True)

    (out/"profit_exports_discovered.json").write_text(
        json.dumps(exports,indent=2,ensure_ascii=False),
        encoding="utf-8"
    )

    (out/"P14.1_manifest.json").write_text(
        json.dumps(manifest,indent=2,ensure_ascii=False),
        encoding="utf-8"
    )

    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
