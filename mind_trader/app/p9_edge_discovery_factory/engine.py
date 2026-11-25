import json
from pathlib import Path
from app.p9_massive_backtest_grid.engine import run as run_grid

MIN_RULES = {
    "profit_factor": 1.25, "sharpe": 0.50, "sortino": 0.75,
    "max_drawdown": 0.25, "risk_of_ruin": 0.30, "stability": 0.60,
    "regime_robustness": 0.50, "cross_asset_robustness": 0.50,
    "cross_period_robustness": 0.50
}

def evaluate_candidate(candidate):
    # Metric thresholds are not evidence. Until provenance verification exists,
    # no candidate can enter the PAPER queue, even if caller-supplied metrics look strong.
    return {
        "genome_id": candidate.get("genome_id") if isinstance(candidate, dict) else None,
        "checks": {},
        "evidence_score": None,
        "paper_candidate": False,
        "edge_proven": False,
        "causality_proven": False,
        "promotion_allowed": False,
        "reason": "VERIFIABLE_BACKTEST_PROVENANCE_GATE_NOT_IMPLEMENTED"
    }

def run():
    out = Path("reports/P9.5_EDGE_DISCOVERY_FACTORY")
    out.mkdir(parents=True, exist_ok=True)
    grid_manifest = run_grid(3000, 300)
    ranked_path = Path("reports/P9.3_MASSIVE_BACKTEST_GRID/P9.3_top_ranked_candidates.json")
    candidates = json.loads(ranked_path.read_text(encoding="utf-8")) if ranked_path.exists() else []
    evaluations = [evaluate_candidate(c) for c in candidates]
    paper = []
    (out / "P9.5_candidate_evaluations.json").write_text(
        json.dumps(evaluations, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (out / "P9.5_paper_candidates.json").write_text("[]", encoding="utf-8")
    manifest = {
        "STATUS": "P9.5_BLOCKED_VERIFIABLE_BACKTEST_PROVENANCE_MISSING",
        "CANDIDATES_ANALYZED": len(evaluations),
        "PAPER_CANDIDATES": 0,
        "UPSTREAM_P9_3_STATUS": grid_manifest["STATUS"],
        "EDGE": "NOT_PROVEN",
        "CAUSALITY": "NOT_PROVEN",
        "LIVE": "FORBIDDEN",
        "REAL_BROKER": "DISABLED",
        "PROMOTION_ALLOWED": False,
        "BLOCKING_GATE": "REAL_BACKTEST_AND_DATASET_LINEAGE_VERIFIER_REQUIRED",
        "EXPORT_READY": False
    }
    (out / "P9.5_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return manifest

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
