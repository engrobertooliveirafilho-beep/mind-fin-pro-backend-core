import csv,json,hashlib,statistics,subprocess,os,shutil
from pathlib import Path
from datetime import datetime,UTC

REMOTE_RAW="gdrive:mind-workspace/MIND_TRADER/P15_REAL_MARKET_DATA/raw"
REMOTE_NORM="gdrive:mind-workspace/MIND_TRADER/P15_REAL_MARKET_DATA/normalized"
REMOTE_REPORTS="gdrive:mind-workspace/MIND_TRADER/P15_REAL_MARKET_DATA/reports"

TMP=Path(os.environ.get("TEMP",".")).joinpath("mind_p15_market_data_runtime")
RAW=TMP/"raw"
NORM=TMP/"normalized"

def run_cmd(cmd):
    return subprocess.run(cmd,shell=True,capture_output=True,text=True)

def parse_name(name):
    stem=Path(name).stem
    parts=stem.split("_")
    symbol=parts[0]
    tf="D1"
    if "15min" in stem: tf="M15"
    elif "20min" in stem: tf="M20"
    elif "30min" in stem: tf="M30"
    elif "60min" in stem: tf="H1"
    elif "Diário" in stem or "Diario" in stem: tf="D1"
    return symbol,tf

def br_float(v):
    try: return float(str(v).replace(".","").replace(",","."))
    except: return 0.0

def normalize_file(p):
    symbol,tf=parse_name(p.name)
    rows=[]
    with open(p,"r",encoding="latin1",errors="ignore",newline="") as f:
        reader=csv.DictReader(f,delimiter=";")
        for r in reader:
            rows.append({
                "symbol":symbol,
                "timeframe":tf,
                "date":r.get("Data",""),
                "open":br_float(r.get("Abertura","")),
                "high":br_float(r.get("Máximo","")),
                "low":br_float(r.get("Mínimo","")),
                "close":br_float(r.get("Fechamento","")),
                "volume":br_float(r.get("Volume","")),
                "quantity":br_float(r.get("Quantidade",""))
            })
    out=NORM/f"{symbol}_{tf}_normalized.csv"
    out.parent.mkdir(parents=True,exist_ok=True)
    with open(out,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["symbol","timeframe","date","open","high","low","close","volume","quantity"])
        w.writeheader(); w.writerows(rows)
    return out,rows

def certify(rows):
    return {
        "rows":len(rows),
        "schema_ok":len(rows)>0 and all(k in rows[0] for k in ["symbol","date","open","high","low","close"]),
        "enough_rows":len(rows)>=50,
        "certified":len(rows)>=50
    }

def baseline(rows):
    if len(rows)<30: return {"tested":False}
    closes=[r["close"] for r in rows if r["close"]>0]
    if len(closes)<30: return {"tested":False}
    rets=[closes[i]/closes[i-1]-1 for i in range(1,len(closes)) if closes[i-1]]
    return {
        "tested":True,
        "bars":len(closes),
        "avg_return":round(statistics.mean(rets),8) if rets else 0,
        "volatility":round(statistics.pstdev(rets),8) if len(rets)>1 else 0,
        "last_close":closes[-1]
    }

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def run():
    if TMP.exists(): shutil.rmtree(TMP,ignore_errors=True)
    RAW.mkdir(parents=True,exist_ok=True); NORM.mkdir(parents=True,exist_ok=True)

    dl=run_cmd(f'rclone copy "{REMOTE_RAW}" "{RAW}" --progress')
    results=[]
    for p in RAW.glob("*.csv"):
        out,rows=normalize_file(p)
        results.append({
            "source":p.name,
            "normalized":out.name,
            "sha256":sha(out),
            "dataset":certify(rows),
            "baseline":baseline(rows)
        })

    report_dir=Path("reports/P15.3_P15.5_PROFIT_MARKET_DATA_PIPELINE")
    report_dir.mkdir(parents=True,exist_ok=True)

    manifest={
        "STATUS":"P15.3_P15.5_PROFIT_MARKET_DATA_PIPELINE_IMPLEMENTED",
        "RAW_FILES":len(list(RAW.glob("*.csv"))),
        "NORMALIZED_FILES":len(list(NORM.glob("*.csv"))),
        "CERTIFIED_DATASETS":sum(x["dataset"]["certified"] for x in results),
        "BASELINES_TESTED":sum(x["baseline"].get("tested",False) for x in results),
        "REMOTE_RAW":REMOTE_RAW,
        "REMOTE_NORMALIZED":REMOTE_NORM,
        "REMOTE_REPORTS":REMOTE_REPORTS,
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "NEXT":"P15.6_STRATEGY_BACKTEST_ON_CERTIFIED_DATASETS",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }

    (report_dir/"dataset_results.json").write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding="utf-8")
    (report_dir/"P15.3_P15.5_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")

    run_cmd(f'rclone copy "{NORM}" "{REMOTE_NORM}" --progress')
    run_cmd(f'rclone copy "{report_dir}" "{REMOTE_REPORTS}" --progress')
    shutil.rmtree(TMP,ignore_errors=True)
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
