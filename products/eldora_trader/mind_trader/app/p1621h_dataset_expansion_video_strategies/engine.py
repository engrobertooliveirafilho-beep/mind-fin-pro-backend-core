import json
from pathlib import Path
from datetime import datetime, UTC

INP=Path("reports/P16.21G_RULE_NORMALIZATION_AUTO_BACKTEST/p1621g_backtest_queue_results.json")
OUT=Path("reports/P16.21H_DATASET_EXPANSION_VIDEO_STRATEGIES")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","CAUSALITY":"NOT_PROVEN"}

TARGET_ASSETS=["WINFUT","WDOFUT","IBOV","PETR4","VALE3","IFIX","CSAN3","BTC"]
TARGET_TIMEFRAMES=["M5","M15","M30","H1","H4","D1"]

def load():
    return json.loads(INP.read_text(encoding="utf-8")) if INP.exists() else []

def inventory_datasets():
    files=list(Path(".").glob("**/*_normalized.csv"))
    out=[]
    for f in files:
        name=f.name.replace("_normalized.csv","")
        parts=name.split("_")
        if len(parts)>=2:
            out.append({"asset":parts[0],"timeframe":parts[1],"path":str(f)})
    return out

def required_dataset_matrix():
    return [{"asset":a,"timeframe":tf,"required_name":f"{a}_{tf}_normalized.csv"} for a in TARGET_ASSETS for tf in TARGET_TIMEFRAMES]

def gap_analysis():
    inv=inventory_datasets()
    have={(x["asset"],x["timeframe"]) for x in inv}
    req=required_dataset_matrix()
    gaps=[x for x in req if (x["asset"],x["timeframe"]) not in have]
    return inv,req,gaps

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    inv,req,gaps=gap_analysis()
    video_queue=load()
    report={
        "STATUS":"P16.21H_DATASET_EXPANSION_FOR_VIDEO_STRATEGIES_IMPLEMENTED",
        "VIDEO_BACKTEST_QUEUE":len(video_queue),
        "DATASETS_DISCOVERED":len(inv),
        "DATASETS_REQUIRED":len(req),
        "DATASET_GAPS":len(gaps),
        "NEXT":"P16.21I_DATASET_ACQUISITION_AND_VIDEO_BACKTEST_RETRY",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (OUT/"p1621h_dataset_inventory.json").write_text(json.dumps(inv,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1621h_required_dataset_matrix.json").write_text(json.dumps(req,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1621h_dataset_gaps.json").write_text(json.dumps(gaps,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1621h_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
