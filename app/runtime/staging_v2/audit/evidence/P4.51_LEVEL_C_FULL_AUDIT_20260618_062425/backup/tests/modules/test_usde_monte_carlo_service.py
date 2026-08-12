from app.modules.usde_core.monte_carlo_service import MonteCarloService

def test_monte_carlo_service():
    r=MonteCarloService().run(
        list(range(1,26)),
        15,
        100
    )

    assert r["status"]=="COMPLETED"
    assert r["trials"]==100
