from app.p17x_causality_research_runtime.engine import run, causal_score

def test_p17x_causal_score():
    e={"profit_factor":3,"max_drawdown":0.05,"decay_revalidation_score":0.1,"walk_forward_status":"WALK_FORWARD_APPROVED","monte_carlo_status":"MONTE_CARLO_APPROVED"}
    assert causal_score(e) > 0.5

def test_p17x_run_blocks_live():
    r=run()
    assert r["STATUS"]=="P17X_CAUSALITY_RESEARCH_RUNTIME_IMPLEMENTED"
    assert r["REAL_ORDERS"]=="FORBIDDEN"
    assert r["LIVE"]=="FORBIDDEN"
