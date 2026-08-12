import json, hashlib
from pathlib import Path
from datetime import datetime, UTC

PROMOTED_PATH=Path("reports/P14.6_STRATEGY_PROMOTION_ENGINE/promoted_paper_strategies.json")

def load_promoted():
    if not PROMOTED_PATH.exists():
        return []
    return json.loads(PROMOTED_PATH.read_text(encoding="utf-8"))

def mutate_params(base):
    return [
        {"fast":8,"slow":20},
        {"fast":9,"slow":21},
        {"fast":10,"slow":25},
        {"fast":12,"slow":30},
        {"fast":14,"slow":34}
    ]

def make_code(fast, slow):
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

def evolve():
    promoted=load_promoted()
    out=[]
    base_dir=Path("strategies/ntsl_evolved")
    base_dir.mkdir(parents=True,exist_ok=True)

    for p in promoted:
        for params in mutate_params(p):
            sid=hashlib.sha256(json.dumps({"base":p,"params":params},sort_keys=True).encode()).hexdigest()[:16]
            folder=base_dir/sid
            folder.mkdir(parents=True,exist_ok=True)
            (folder/"code.nts").write_text(make_code(params["fast"],params["slow"]),encoding="utf-8")
            meta={
                "strategy_id":sid,
                "parent_strategy_id":p.get("strategy_id"),
                "asset":p.get("asset"),
                "timeframe":p.get("timeframe"),
                "mutation":params,
                "requires_profit_backtest":True,
                "live":"FORBIDDEN",
                "real_orders":"FORBIDDEN"
            }
            (folder/"metadata.json").write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding="utf-8")
            out.append(meta)
    return out

def run():
    out_dir=Path("reports/P14.7_GENOME_EVOLUTION_ENGINE")
    out_dir.mkdir(parents=True,exist_ok=True)
    evolved=evolve()
    manifest={
        "STATUS":"P14.7_GENOME_EVOLUTION_ENGINE_IMPLEMENTED",
        "PARENTS":len(load_promoted()),
        "EVOLVED_STRATEGIES":len(evolved),
        "PAPER_ONLY":True,
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out_dir/"evolved_strategy_catalog.json").write_text(json.dumps(evolved,indent=2,ensure_ascii=False),encoding="utf-8")
    (out_dir/"P14.7_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
