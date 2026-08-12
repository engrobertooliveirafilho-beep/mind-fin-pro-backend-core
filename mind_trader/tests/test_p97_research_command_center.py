from app.p9_research_command_center.engine import build_dashboard, DASHBOARDS

def test_p97_dashboard_sections():
    d=build_dashboard()
    for x in ["top_genomes","top_dna","top_datasets","top_robustness","top_paper_candidates","top_correlations","uncertainty_alerts"]:
        assert x in d

def test_p97_blocks_real_promotion():
    d=build_dashboard()
    assert d["live"]=="FORBIDDEN"
    assert d["real_broker"]=="DISABLED"
    assert d["promotion_allowed"] is False

def test_p97_manifest_written():
    from pathlib import Path
    build_dashboard()
    assert Path("reports/P9.7_RESEARCH_COMMAND_CENTER/P9.7_manifest.json").exists()
