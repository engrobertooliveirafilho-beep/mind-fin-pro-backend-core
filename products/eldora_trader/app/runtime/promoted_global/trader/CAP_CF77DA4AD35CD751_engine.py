import json, statistics
from pathlib import Path
from datetime import datetime, UTC

EVIDENCE_RULES={
    "min_datasets":3,
    "min_periods":3,
    "min_assets":2,
    "min_walk_forward_pass_rate":0.70,
    "min_monte_carlo_pass_rate":0.70,
    "min_robustness_score":0.75,
    "min_out_of_sample_score":0.65
}

def evaluate_edge_evidence(candidate):
    datasets=candidate.get("datasets",[])
    assets={d.get("asset") for d in datasets}
    periods={d.get("period") for d in datasets}
    wf=candidate.get("walk_forward_results",[])
    mc=candidate.get("monte_carlo_results",[])
    robustness=candidate.get("robustness_score",0)
    oos=candidate.get("out_of_sample_score",0)
    wf_rate=sum(bool(x) for x in wf)/len(wf) if wf else 0
    mc_rate=sum(bool(x) for x in mc)/len(mc) if mc else 0
    checks={
        "min_datasets":len(datasets)>=EVIDENCE_RULES["min_datasets"],
        "min_periods":len(periods)>=EVIDENCE_RULES["min_periods"],
        "min_assets":len(assets)>=EVIDENCE_RULES["min_assets"],
        "walk_forward":wf_rate>=EVIDENCE_RULES["min_walk_forward_pass_rate"],
        "monte_carlo":mc_rate>=EVIDENCE_RULES["min_monte_carlo_pass_rate"],
        "robustness":robustness>=EVIDENCE_RULES["min_robustness_score"],
        "out_of_sample":oos>=EVIDENCE_RULES["min_out_of_sample_score"]
    }
    score=sum(checks.values())/len(checks)
    return {
        "candidate_id":candidate.get("candidate_id","unknown"),
        "checks":checks,
        "evidence_score":round(score,6),
        "paper_edge_evidence":score==1.0,
        "causality_proven":False,
        "live_allowed":False,
        "real_broker_allowed":False,
        "promotion_allowed":False,
        "status":"PAPER_EDGE_EVIDENCE_CANDIDATE" if score==1.0 else "INSUFFICIENT_EVIDENCE",
        "evaluated_at":datetime.now(UTC).isoformat()
    }

def run():
    out=Path("reports/P11_EDGE_EVIDENCE_ENGINE")
    out.mkdir(parents=True,exist_ok=True)
    sample={
        "candidate_id":"SAMPLE_EDGE_CANDIDATE",
        "datasets":[
            {"asset":"WIN","period":"2024"},
            {"asset":"WIN","period":"2025"},
            {"asset":"WDO","period":"2026"}
        ],
        "walk_forward_results":[True,True,True,False],
        "monte_carlo_results":[True,True,True,False],
        "robustness_score":0.80,
        "out_of_sample_score":0.70
    }
    evaluation=evaluate_edge_evidence(sample)
    manifest={
        "STATUS":"P11_EDGE_EVIDENCE_ENGINE_IMPLEMENTED",
        "RULES":EVIDENCE_RULES,
        "SAMPLE_STATUS":evaluation["status"],
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "CAUSALITY":"NOT_PROVEN",
        "PROMOTION_ALLOWED":False,
        "EXPORT_READY":True
    }
    (out/"P11_sample_edge_evaluation.json").write_text(json.dumps(evaluation,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P11_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
