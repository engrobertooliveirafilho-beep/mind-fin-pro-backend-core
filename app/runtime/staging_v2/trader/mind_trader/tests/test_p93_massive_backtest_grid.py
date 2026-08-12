from app.p9_massive_backtest_grid.engine import run, evaluate_genome
from app.p9_genome_explosion_engine.engine import generate_genomes

def test_p93_evaluate_genome_blocks_promotion():
    g=generate_genomes(1)[0]
    r=evaluate_genome(g)
    assert r["validation"]["promotion_allowed"] is False
    assert r["edge_proven"] is False
    assert r["causality_proven"] is False

def test_p93_run_grid_manifest():
    m=run(1000,50)
    assert m["STATUS"]=="P9.3_MASSIVE_BACKTEST_GRID_IMPLEMENTED"
    assert m["GENOMES_EVALUATED"]==1000
    assert m["PROMOTION_ALLOWED"] is False
    assert m["EXPORT_READY"] is True

def test_p93_top_report_exists():
    from pathlib import Path
    run(100,10)
    assert Path("reports/P9.3_MASSIVE_BACKTEST_GRID/P9.3_top_ranked_candidates.json").exists()
