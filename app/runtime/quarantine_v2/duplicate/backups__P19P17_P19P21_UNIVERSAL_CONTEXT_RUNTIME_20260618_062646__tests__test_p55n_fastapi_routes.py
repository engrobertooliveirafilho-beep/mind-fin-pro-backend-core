from app.mind.p5_5n_fastapi_routes import run_p55n_healthcheck
from app.mind.p5_5n_fastapi_routes.routes import router

def test_p55n_healthcheck():
    h = run_p55n_healthcheck()
    assert h["status"] == "P5.5N_READY"
    assert "/p55/bulls/ranking" in h["routes"]

def test_router_prefix():
    assert router.prefix == "/p55/bulls"
