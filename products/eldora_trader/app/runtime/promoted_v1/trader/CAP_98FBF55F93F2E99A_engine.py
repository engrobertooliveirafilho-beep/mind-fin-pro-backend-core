import json
from pathlib import Path
from datetime import datetime, UTC
from app.p11_edge_evidence_engine.engine import evaluate_edge_evidence
from app.p11_causality_evidence_firewall.engine import evaluate_causality_claim, REQUIRED_CAUSALITY_TESTS

def evaluate_paper_promotion(candidate):
    edge=evaluate_edge_evidence(candidate.get("edge_candidate",{}))
    causality=evaluate_causality_claim(candidate.get("causality_claim",{}))
    paper_allowed=edge["paper_edge_evidence"] is True and causality["causality_proven"] is True
    return {
        "candidate_id":candidate.get("candidate_id","unknown"),
        "edge":edge,
        "causality":causality,
        "paper_promotion_allowed":paper_allowed,
        "live_promotion_allowed":False,
        "real_broker_allowed":False,
        "ftmo_real_allowed":False,
        "status":"PAPER_PROMOTION_ALLOWED_RESEARCH_ONLY" if paper_allowed else "PROMOTION_BLOCKED_INSUFFICIENT_EVIDENCE",
        "evaluated_at":datetime.now(UTC).isoformat()
    }

def run():
    out=Path("reports/P11.2_EVIDENCE_PROMOTION_GATE")
    out.mkdir(parents=True,exist_ok=True)
    candidate={
        "candidate_id":"sample",
        "edge_candidate":{
            "candidate_id":"edge_sample",
            "datasets":[{"asset":"WIN","period":"2024"},{"asset":"WIN","period":"2025"},{"asset":"WDO","period":"2026"}],
            "walk_forward_results":[True,True,True],
            "monte_carlo_results":[True,True,True],
            "robustness_score":0.9,
            "out_of_sample_score":0.8
        },
        "causality_claim":{"claim_id":"causal_sample","tests":{t:True for t in REQUIRED_CAUSALITY_TESTS}}
    }
    evaluation=evaluate_paper_promotion(candidate)
    manifest={
        "STATUS":"P11.2_EVIDENCE_PROMOTION_GATE_IMPLEMENTED",
        "SAMPLE_STATUS":evaluation["status"],
        "PAPER_PROMOTION_ALLOWED":evaluation["paper_promotion_allowed"],
        "LIVE_PROMOTION_ALLOWED":False,
        "REAL_BROKER_ALLOWED":False,
        "FTMO_REAL_ALLOWED":False,
        "EXPORT_READY":True
    }
    (out/"P11.2_sample_promotion_gate.json").write_text(json.dumps(evaluation,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P11.2_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
