import json
from pathlib import Path
from datetime import datetime, UTC

REQUIRED_CAUSALITY_TESTS=[
    "temporal_precedence",
    "placebo_test",
    "regime_invariance",
    "confounder_check",
    "cross_asset_replication",
    "out_of_sample_replication"
]

def evaluate_causality_claim(claim):
    tests=claim.get("tests",{})
    checks={t: tests.get(t) is True for t in REQUIRED_CAUSALITY_TESTS}
    score=sum(checks.values())/len(checks)
    return {
        "claim_id":claim.get("claim_id","unknown"),
        "checks":checks,
        "causality_score":round(score,6),
        "causality_proven":score==1.0,
        "live_allowed":False,
        "real_broker_allowed":False,
        "promotion_allowed":False,
        "status":"CAUSALITY_EVIDENCE_ACCEPTED_PAPER_ONLY" if score==1.0 else "CAUSALITY_NOT_PROVEN",
        "evaluated_at":datetime.now(UTC).isoformat()
    }

def firewall(candidate):
    result=evaluate_causality_claim(candidate.get("causality_claim",{}))
    candidate["causality_firewall"]=result
    candidate["promotion_allowed"]=False
    candidate["live_allowed"]=False
    candidate["real_broker_allowed"]=False
    return candidate

def run():
    out=Path("reports/P11.1_CAUSALITY_EVIDENCE_FIREWALL")
    out.mkdir(parents=True,exist_ok=True)
    sample={"claim_id":"sample","tests":{t:True for t in REQUIRED_CAUSALITY_TESTS}}
    evaluation=evaluate_causality_claim(sample)
    manifest={
        "STATUS":"P11.1_CAUSALITY_EVIDENCE_FIREWALL_IMPLEMENTED",
        "REQUIRED_TESTS":REQUIRED_CAUSALITY_TESTS,
        "SAMPLE_STATUS":evaluation["status"],
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "PROMOTION_ALLOWED":False,
        "EXPORT_READY":True
    }
    (out/"P11.1_sample_causality_evaluation.json").write_text(json.dumps(evaluation,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P11.1_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
