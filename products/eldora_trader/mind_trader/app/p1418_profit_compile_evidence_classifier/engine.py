import json
from pathlib import Path
from datetime import datetime, UTC

P1416=Path("reports/P14.16_IMPORT_AUTORUN_RECONCILIATION/P14.16_reconciliation_snapshot.json")

def load_snapshot():
    if not P1416.exists():
        return {}
    return json.loads(P1416.read_text(encoding="utf-8"))

def classify_row(row):
    sid=row.get("strategy_id","")
    screenshot=row.get("screenshot","")
    file=row.get("file","")
    if screenshot and Path(screenshot).exists():
        if sid.startswith("p1416p_"):
            return "FUNCTION_PROBE_EVIDENCE"
        if sid.startswith("p1416i_"):
            return "SYNTAX_PROBE_EVIDENCE"
        return "SCREENSHOT_EVIDENCE"
    if screenshot:
        return "SCREENSHOT_REFERENCED_MISSING"
    if file:
        return "FILE_ONLY_NO_SCREENSHOT"
    return "UNKNOWN"

def classify_all():
    snap=load_snapshot()
    rows=snap.get("AUTORUN_RESULTS",[])
    out=[]
    for r in rows:
        out.append({
            **r,
            "classification":classify_row(r),
            "live":"FORBIDDEN",
            "real_orders":"FORBIDDEN"
        })
    return out

def summary(rows):
    s={}
    for r in rows:
        c=r["classification"]
        s[c]=s.get(c,0)+1
    return s

def run():
    out=Path("reports/P14.18_PROFIT_COMPILE_EVIDENCE_CLASSIFIER")
    out.mkdir(parents=True,exist_ok=True)
    rows=classify_all()
    manifest={
        "STATUS":"P14.18_PROFIT_COMPILE_EVIDENCE_CLASSIFIER_IMPLEMENTED",
        "ROWS_CLASSIFIED":len(rows),
        "SUMMARY":summary(rows),
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "NEXT":"P14.19_NTSL_COMPILABLE_STRATEGY_PROMOTION_GATE",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"classified_profit_evidence.json").write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P14.18_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
