from app.p9_edge_discovery_factory.engine import evaluate_candidate, run

def test_p95_evaluation_never_promotes_real():
    c={
        "genome_id":"x",
        "metrics":{"profit_factor":2,"sharpe":2,"sortino":2,"max_drawdown":0.05,"risk_of_ruin":0.05,"stability":1,"regime_robustness":1,"cross_asset_robustness":1,"cross_period_robustness":1},
        "validation":{"walk_forward_passed":True,"monte_carlo_passed":True,"robustness_committee_passed":True,"anti_overfitting_passed":True}
    }
    e=evaluate_candidate(c)
    assert e["paper_candidate"] is True
    assert e["edge_proven"] is False
    assert e["promotion_allowed"] is False

def test_p95_run_manifest():
    m=run()
    assert m["STATUS"]=="P9.5_EDGE_DISCOVERY_FACTORY_IMPLEMENTED"
    assert m["EDGE"]=="NOT_PROVEN"
    assert m["PROMOTION_ALLOWED"] is False
    assert m["EXPORT_READY"] is True

def test_p95_reports_exist():
    from pathlib import Path
    run()
    assert Path("reports/P9.5_EDGE_DISCOVERY_FACTORY/P9.5_manifest.json").exists()
