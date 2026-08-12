import json, statistics
from pathlib import Path
from app.p9_massive_backtest_grid.engine import run as run_grid

MIN_RULES={
    "profit_factor":1.25,
    "sharpe":0.50,
    "sortino":0.75,
    "max_drawdown":0.25,
    "risk_of_ruin":0.30,
    "stability":0.60,
    "regime_robustness":0.50,
    "cross_asset_robustness":0.50,
    "cross_period_robustness":0.50
}

def evaluate_candidate(candidate):
    m=candidate["metrics"]
    checks={
        "profit_factor":m["profit_factor"]>=MIN_RULES["profit_factor"],
        "sharpe":m["sharpe"]>=MIN_RULES["sharpe"],
        "sortino":m["sortino"]>=MIN_RULES["sortino"],
        "drawdown":m["max_drawdown"]<=MIN_RULES["max_drawdown"],
        "risk_of_ruin":m["risk_of_ruin"]<=MIN_RULES["risk_of_ruin"],
        "stability":m["stability"]>=MIN_RULES["stability"],
        "regime":m["regime_robustness"]>=MIN_RULES["regime_robustness"],
        "cross_asset":m["cross_asset_robustness"]>=MIN_RULES["cross_asset_robustness"],
        "cross_period":m["cross_period_robustness"]>=MIN_RULES["cross_period_robustness"],
        "walk_forward":candidate["validation"]["walk_forward_passed"],
        "monte_carlo":candidate["validation"]["monte_carlo_passed"],
        "robustness_committee":candidate["validation"]["robustness_committee_passed"],
        "anti_overfitting":candidate["validation"]["anti_overfitting_passed"]
    }
    evidence_score=sum(checks.values())/len(checks)
    return {
        "genome_id":candidate["genome_id"],
        "checks":checks,
        "evidence_score":round(evidence_score,6),
        "paper_candidate":evidence_score>=0.85,
        "edge_proven":False,
        "causality_proven":False,
        "promotion_allowed":False,
        "reason":"statistical_pattern_candidate_only"
    }

def run():
    out=Path("reports/P9.5_EDGE_DISCOVERY_FACTORY"); out.mkdir(parents=True,exist_ok=True)
    run_grid(3000,300)
    ranked_path=Path("reports/P9.3_MASSIVE_BACKTEST_GRID/P9.3_top_ranked_candidates.json")
    candidates=json.loads(ranked_path.read_text(encoding="utf-8"))
    evaluations=[evaluate_candidate(c) for c in candidates]
    paper=[e for e in evaluations if e["paper_candidate"]]
    manifest={
        "STATUS":"P9.5_EDGE_DISCOVERY_FACTORY_IMPLEMENTED",
        "CANDIDATES_ANALYZED":len(evaluations),
        "PAPER_CANDIDATES":len(paper),
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "PROMOTION_ALLOWED":False,
        "MIN_RULES":MIN_RULES,
        "EXPORT_READY":True
    }
    (out/"P9.5_candidate_evaluations.json").write_text(json.dumps(evaluations,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P9.5_paper_candidates.json").write_text(json.dumps(paper,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P9.5_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
