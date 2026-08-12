from app.p9_continuous_research_runtime.engine import run_cycle, STEPS

def test_p96_cycle_has_required_steps():
    c=run_cycle("TEST_CYCLE")
    for s in ["new_data_scan","dataset_quality_gate","massive_backtest_grid","monte_carlo","robustness_committee","paper_candidate_ranking"]:
        assert s in c["steps"]

def test_p96_runtime_blocks_live_and_broker():
    c=run_cycle("TEST_LOCK")
    assert c["live"]=="FORBIDDEN"
    assert c["real_broker"]=="DISABLED"
    assert c["promotion_allowed"] is False

def test_p96_manifest_written():
    from pathlib import Path
    run_cycle("TEST_REPORT")
    assert Path("reports/P9.6_CONTINUOUS_RESEARCH_RUNTIME/P9.6_manifest.json").exists()
