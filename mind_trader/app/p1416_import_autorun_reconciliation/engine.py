import csv, json
from pathlib import Path
from datetime import datetime, UTC

TOOLS=Path("tools")
IMPORT=Path("profit_import_package")
REPORTS=Path("reports")

def list_files(path, pattern):
    return [str(p) for p in path.rglob(pattern)] if path.exists() else []

def read_autorun_results():
    rows=[]
    for f in REPORTS.rglob("results.csv"):
        try:
            with open(f,newline="",encoding="utf-8-sig") as fh:
                for r in csv.DictReader(fh):
                    r["source_file"]=str(f)
                    rows.append(r)
        except Exception as e:
            rows.append({"source_file":str(f),"error":str(e)})
    return rows

def run():
    out=Path("reports/P14.16_IMPORT_AUTORUN_RECONCILIATION")
    out.mkdir(parents=True,exist_ok=True)

    tools=list_files(TOOLS,"*.ps1")
    nts=list_files(IMPORT,"*.nts")
    screenshots=list_files(REPORTS,"*.png")
    results=read_autorun_results()

    snapshot={
        "STATUS":"P14.16_IMPORT_AUTORUN_RECONCILIATION_IMPLEMENTED",
        "TOOLS_PS1":len(tools),
        "NTS_IMPORT_FILES":len(nts),
        "AUTORUN_RESULT_ROWS":len(results),
        "SCREENSHOTS_FOUND":len(screenshots),
        "TOOLS":tools,
        "NTS_FILES":nts,
        "AUTORUN_RESULTS":results,
        "SCREENSHOTS":screenshots,
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "NEXT":"P14.17_NTSL_FUNCTION_COMPATIBILITY_MATRIX",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }

    (out/"P14.16_reconciliation_snapshot.json").write_text(json.dumps(snapshot,indent=2,ensure_ascii=False),encoding="utf-8")
    return snapshot

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
