from app.mind.p5_5x_genetic_graph_builder import run_p55x_healthcheck

def test_p55x_healthcheck():
    assert run_p55x_healthcheck()["status"]=="P5.5X_READY"
