from app.p9_massive_backtest_grid.engine import run, evaluate_genome
from app.p9_genome_explosion_engine.engine import generate_genomes

def test_p93_does_not_fabricate_performance_metrics():
    result = evaluate_genome(generate_genomes(1)[0])
    assert result["metrics"] is None
    assert result["research_score"] is None
    assert result["status"] == "BLOCKED_REAL_BACKTEST_ENGINE_NOT_CONNECTED"
    assert result["validation"]["walk_forward"] == "NOT_RUN"
    assert result["validation"]["monte_carlo"] == "NOT_RUN"
    assert result["promotion_allowed"] is False

def test_p93_run_is_blocked_without_real_backtest_engine():
    manifest = run(10, 5)
    assert manifest["STATUS"] == "P9.3_BLOCKED_REAL_BACKTEST_ENGINE_NOT_CONNECTED"
    assert manifest["BACKTESTS_EXECUTED"] == 0
    assert manifest["TOP_EXPORTED"] == 0
    assert manifest["PROMOTION_ALLOWED"] is False
    assert manifest["EXPORT_READY"] is False

def test_p93_ranked_output_is_empty_until_backtests_exist():
    import json
    from pathlib import Path
    run(10, 5)
    path = Path("reports/P9.3_MASSIVE_BACKTEST_GRID/P9.3_top_ranked_candidates.json")
    assert json.loads(path.read_text(encoding="utf-8")) == []
