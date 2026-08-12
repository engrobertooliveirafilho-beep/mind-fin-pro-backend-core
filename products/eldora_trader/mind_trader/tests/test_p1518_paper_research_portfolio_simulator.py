from app.p1518_paper_research_portfolio_simulator.engine import edge_metrics, proxy_corr, portfolio_metrics, run

def test_p1518_edge_metrics_blocks_orders():
    e={"symbol":"X","timeframe":"H1","strategy":"sma_cross","fast":5,"slow":55,"total_return":0.2,"profit_factor":2,"trades":40,"winrate":45}
    m=edge_metrics(e)
    assert m["real_orders"]=="FORBIDDEN"

def test_p1518_proxy_corr():
    a={"timeframe":"H1","strategy":"sma","regime":"trend","symbol":"A"}
    b={"timeframe":"H1","strategy":"sma","regime":"trend","symbol":"B"}
    assert proxy_corr(a,b)>0

def test_p1518_manifest():
    m=run()
    assert m["STATUS"]=="P15.18_PAPER_RESEARCH_PORTFOLIO_SIMULATOR_IMPLEMENTED"
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True
