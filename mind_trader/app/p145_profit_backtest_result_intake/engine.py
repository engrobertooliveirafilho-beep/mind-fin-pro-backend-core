import json, csv
from pathlib import Path
from datetime import datetime, UTC

WATCH_DIR=Path("data/incoming/profit_backtests")
REQUIRED_COLUMNS={"strategy_id","asset","timeframe","profit_factor","drawdown","winrate","trades"}

def inspect_result_file(path):
    p=Path(path)
    with open(p,newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        cols={c.strip().lower() for c in (reader.fieldnames or [])}
        rows=list(reader)
    missing=sorted(REQUIRED_COLUMNS-cols)
    valid=not missing and len(rows)>0
    return {
        "file":str(p),
        "rows":len(rows),
        "columns":sorted(cols),
        "missing":missing,
        "valid":valid
    }

def scan_results():
    WATCH_DIR.mkdir(parents=True,exist_ok=True)
    return [inspect_result_file(p) for p in WATCH_DIR.glob("*.csv")]

def run():
    out=Path("reports/P14.5_PROFIT_BACKTEST_RESULT_INTAKE")
    out.mkdir(parents=True,exist_ok=True)
    results=scan_results()
    manifest={
        "STATUS":"P14.5_PROFIT_BACKTEST_RESULT_INTAKE_IMPLEMENTED",
        "WATCH_DIR":str(WATCH_DIR),
        "FILES_FOUND":len(results),
        "FILES_VALID":sum(x["valid"] for x in results),
        "REQUIRED_COLUMNS":sorted(REQUIRED_COLUMNS),
        "PAPER_ONLY":True,
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"profit_backtest_result_scan.json").write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P14.5_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
