import json, re
from pathlib import Path
from datetime import datetime, UTC

NTS_DIR=Path("profit_import_package")
RESULTS_DIR=Path("reports")

FUNCTIONS=[
 "BuyAtMarket","SellShortAtMarket","ClosePosition",
 "IsBought","IsSold","HasPosition",
 "Media","MediaExp","MME","MMA","RSI","MACD"
]

def read_nts_files():
    rows=[]
    for f in NTS_DIR.glob("*.nts"):
        txt=f.read_text(encoding="utf-8",errors="ignore")
        found=[fn for fn in FUNCTIONS if re.search(r"\b"+re.escape(fn)+r"\b",txt)]
        rows.append({"file":str(f),"strategy_id":f.stem,"functions":found})
    return rows

def screenshot_evidence():
    evidence={}
    for p in RESULTS_DIR.rglob("*.png"):
        sid=p.stem
        evidence.setdefault(sid,[]).append(str(p))
    return evidence

def build_matrix():
    files=read_nts_files()
    evidence=screenshot_evidence()
    matrix=[]
    for fn in FUNCTIONS:
        used=[x for x in files if fn in x["functions"]]
        with_evidence=[x for x in used if x["strategy_id"] in evidence]
        matrix.append({
            "function":fn,
            "used_in_files":len(used),
            "screenshot_evidence":len(with_evidence),
            "status":"EVIDENCE_FOUND" if with_evidence else ("USED_NO_SCREENSHOT" if used else "NOT_USED"),
            "live":"FORBIDDEN",
            "real_orders":"FORBIDDEN"
        })
    return matrix

def run():
    out=Path("reports/P14.17_NTSL_FUNCTION_COMPATIBILITY_MATRIX")
    out.mkdir(parents=True,exist_ok=True)
    matrix=build_matrix()
    manifest={
        "STATUS":"P14.17_NTSL_FUNCTION_COMPATIBILITY_MATRIX_IMPLEMENTED",
        "FUNCTIONS_TRACKED":len(FUNCTIONS),
        "FUNCTIONS_WITH_EVIDENCE":sum(x["status"]=="EVIDENCE_FOUND" for x in matrix),
        "FUNCTIONS_USED_NO_SCREENSHOT":sum(x["status"]=="USED_NO_SCREENSHOT" for x in matrix),
        "NTS_FILES_SCANNED":len(read_nts_files()),
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "NEXT":"P14.18_PROFIT_COMPILE_EVIDENCE_CLASSIFIER",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"ntsl_function_matrix.json").write_text(json.dumps(matrix,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P14.17_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
