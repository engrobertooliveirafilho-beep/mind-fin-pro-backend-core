from app.p147_genome_evolution_engine.engine import mutate_params, make_code, run

def test_p147_mutations_exist():
    assert len(mutate_params({})) >= 5

def test_p147_code_has_orders_blocked_by_policy_not_code():
    c=make_code(9,21)
    assert "BuyAtMarket" in c
    assert "SellShortAtMarket" in c

def test_p147_manifest():
    m=run()
    assert m["STATUS"]=="P14.7_GENOME_EVOLUTION_ENGINE_IMPLEMENTED"
    assert m["REAL_ORDERS"]=="FORBIDDEN"
    assert m["EXPORT_READY"] is True
