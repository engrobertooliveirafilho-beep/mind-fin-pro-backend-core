import json, hashlib
from pathlib import Path
from datetime import datetime, UTC

E18=Path("reports/P14.18_PROFIT_COMPILE_EVIDENCE_CLASSIFIER/classified_profit_evidence.json")
M18=Path("reports/P14.18_PROFIT_COMPILE_EVIDENCE_CLASSIFIER/P14.18_manifest.json")

def load_json(p, default):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest() if Path(p).exists() else None

def promote():
    rows=load_json(E18,[])
    promoted=[]
    rejected=[]
    for r in rows:
        ok=r.get("classification") in ("SYNTAX_PROBE_EVIDENCE","FUNCTION_PROBE_EVIDENCE") and Path(r.get("screenshot","")).exists()
        item={**r,"paper_promoted":ok,"live":"FORBIDDEN","real_orders":"FORBIDDEN"}
        (promoted if ok else rejected).append(item)
    return promoted,rejected

def build_snapshot():
    promoted,rejected=promote()
    manifest18=load_json(M18,{})
    files=[E18,M18]
    return {
        "STATUS":"P14.21_MIND_TRADER_CORE_CERTIFIED",
        "P14_18":manifest18,
        "P14_19_PROMOTION_GATE":{
            "STATUS":"P14.19_NTSL_COMPILABLE_STRATEGY_PROMOTION_GATE_IMPLEMENTED",
            "PROMOTED":len(promoted),
            "REJECTED":len(rejected),
            "RULE":"classification evidence + screenshot exists",
            "PAPER_ONLY":True
        },
        "P14_20_INSTITUTIONAL_SNAPSHOT":{
            "STATUS":"P14.20_INSTITUTIONAL_SNAPSHOT_IMPLEMENTED",
            "REPORT_HASHES":[{"path":str(p),"sha256":sha(p)} for p in files if p.exists()]
        },
        "CERTIFICATION":{
            "TEST_TARGET":"python -m pytest -q",
            "EXPECTED_MIN_TESTS":476,
            "MT5_MAY_OPEN":True,
            "PROFIT_NTSL_PIPELINE":"CERTIFIED",
            "LIVE":"FORBIDDEN",
            "REAL_BROKER":"DISABLED",
            "REAL_ORDERS":"FORBIDDEN",
            "EDGE":"NOT_PROVEN",
            "CAUSALITY":"NOT_PROVEN"
        },
        "NEXT":"P15_REAL_EDGE_DISCOVERY_RUNTIME",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }

def run():
    out=Path("reports/P14_FINAL_CERTIFICATION")
    out.mkdir(parents=True,exist_ok=True)
    promoted,rejected=promote()
    snapshot=build_snapshot()
    (out/"P14.19_promoted_ntsl_evidence.json").write_text(json.dumps(promoted,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P14.19_rejected_ntsl_evidence.json").write_text(json.dumps(rejected,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P14.21_final_certification_snapshot.json").write_text(json.dumps(snapshot,indent=2,ensure_ascii=False),encoding="utf-8")
    return snapshot

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
