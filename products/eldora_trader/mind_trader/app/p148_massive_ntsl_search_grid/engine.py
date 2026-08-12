import json, hashlib
from pathlib import Path
from datetime import datetime, UTC

ASSETS=["WIN","WDO","PETR4","VALE3"]
TIMEFRAMES=["M1","M5","M15"]
FAST=[5,8,9,12,14,20]
SLOW=[21,26,34,50,72,100]

def code(fast,slow):
    return f"""input
  fastPeriod({fast});
  slowPeriod({slow});

var
  fastMA, slowMA : Float;

begin
  fastMA := MediaExp(fastPeriod, Close);
  slowMA := MediaExp(slowPeriod, Close);

  if (fastMA > slowMA) and (fastMA[1] <= slowMA[1]) then
    BuyAtMarket;

  if (fastMA < slowMA) and (fastMA[1] >= slowMA[1]) then
    SellShortAtMarket;
end;"""

def generate():
    base=Path("strategies/ntsl_massive_grid")
    base.mkdir(parents=True,exist_ok=True)
    rows=[]
    for asset in ASSETS:
        for tf in TIMEFRAMES:
            for f in FAST:
                for s in SLOW:
                    if f>=s:
                        continue
                    sid=hashlib.sha256(f"{asset}:{tf}:{f}:{s}".encode()).hexdigest()[:16]
                    folder=base/sid
                    folder.mkdir(parents=True,exist_ok=True)
                    (folder/"code.nts").write_text(code(f,s),encoding="utf-8")
                    meta={
                        "strategy_id":sid,
                        "family":"ema_cross_grid",
                        "asset":asset,
                        "timeframe":tf,
                        "fast":f,
                        "slow":s,
                        "requires_profit_backtest":True,
                        "live":"FORBIDDEN",
                        "real_orders":"FORBIDDEN"
                    }
                    (folder/"metadata.json").write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding="utf-8")
                    rows.append(meta)
    return rows

def run():
    out=Path("reports/P14.8_MASSIVE_NTSL_SEARCH_GRID")
    out.mkdir(parents=True,exist_ok=True)
    rows=generate()
    manifest={
        "STATUS":"P14.8_MASSIVE_NTSL_SEARCH_GRID_IMPLEMENTED",
        "STRATEGIES_CREATED":len(rows),
        "ASSETS":ASSETS,
        "TIMEFRAMES":TIMEFRAMES,
        "FAMILY":"ema_cross_grid",
        "PAPER_ONLY":True,
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"massive_ntsl_grid_catalog.json").write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P14.8_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
