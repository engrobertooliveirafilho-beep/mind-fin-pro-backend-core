from app.main import app

def test_science_route_registered():
    routes=[r.path for r in app.routes]
    assert "/usde/science/run" in routes
