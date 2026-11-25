from app.p9_edge_discovery_factory.engine import evaluate_candidate, run

def test_p95_rejects_unverified_caller_supplied_metrics():
    candidate = {
        "genome_id": "synthetic-fixture",
        "metrics": {
            "profit_factor": 9, "sharpe": 9, "sortino": 9,
            "max_drawdown": 0.01, "risk_of_ruin": 0.01,
            "stability": 1, "regime_robustness": 1,
            "cross_asset_robustness": 1, "cross_period_robustness": 1
        },
        "validation": {
            "walk_forward_passed": True, "monte_carlo_passed": True,
            "robustness_committee_passed": True, "anti_overfitting_passed": True
        }
    }
    result = evaluate_candidate(candidate)
    assert result["paper_candidate"] is False
    assert result["promotion_allowed"] is False
    assert result["reason"] == "VERIFIABLE_BACKTEST_PROVENANCE_GATE_NOT_IMPLEMENTED"

def test_p95_run_keeps_paper_queue_empty():
    import json
    from pathlib import Path
    manifest = run()
    assert manifest["STATUS"] == "P9.5_BLOCKED_VERIFIABLE_BACKTEST_PROVENANCE_MISSING"
    assert manifest["PAPER_CANDIDATES"] == 0
    assert manifest["PROMOTION_ALLOWED"] is False
    path = Path("reports/P9.5_EDGE_DISCOVERY_FACTORY/P9.5_paper_candidates.json")
    assert json.loads(path.read_text(encoding="utf-8")) == []
