from app.p203_400x_massive_research_evolution_factory.engine import run

def test_p203_400_runtime():
    r=run(max_jobs=1000)
    assert r["STATUS"]=="P203_400X_MASSIVE_RESEARCH_EVOLUTION_FACTORY_IMPLEMENTED"
    assert r["MODULES_IMPLEMENTED"]==198
    assert r["REAL_ORDERS"]=="FORBIDDEN"
    assert r["FTMO_REAL"]=="FORBIDDEN"
