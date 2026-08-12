from app.p22_38x_ftmo_robust_research_expansion.engine import run, dataset_inventory, p22_universal_dataset_edge_discovery, p38_autonomous_research_os

def test_p22_38_dataset_inventory():
    ds=dataset_inventory()
    assert isinstance(ds,list)

def test_p22_38_hypotheses_are_paper_only():
    h=p22_universal_dataset_edge_discovery([{"dataset":"x","asset":"A","timeframe":"H1"}])
    assert h[0]["status"]=="HYPOTHESIS_ONLY"
    assert h[0]["REAL_ORDERS"]=="FORBIDDEN"

def test_p38_autonomous_research_os_blocks_live():
    r=p38_autonomous_research_os()
    assert r["LIVE"]=="FORBIDDEN"
    assert r["rule"]=="ALL_SOURCES_HYPOTHESIS_ONLY"

def test_p22_38_master_runtime():
    r=run()
    assert r["STATUS"]=="P22_38X_FTMO_ROBUST_RESEARCH_EXPANSION_IMPLEMENTED"
    assert r["MODULES_IMPLEMENTED"]==17
    assert r["FTMO_STATUS"]=="PAPER_SIMULATION_ONLY"
    assert r["REAL_ORDERS"]=="FORBIDDEN"
