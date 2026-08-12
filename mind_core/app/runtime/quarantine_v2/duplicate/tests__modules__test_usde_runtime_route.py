from app.main import app

def test_usde_runtime_route_registered():
    routes=[r.path for r in app.routes]
    assert "/usde/runtime/status" in routes
