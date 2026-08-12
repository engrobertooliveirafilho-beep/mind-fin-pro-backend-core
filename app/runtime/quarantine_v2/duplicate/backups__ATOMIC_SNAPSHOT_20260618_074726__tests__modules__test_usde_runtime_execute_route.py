from app.main import app

def test_runtime_execute_route():
    routes=[r.path for r in app.routes]
    assert "/usde/runtime/execute" in routes
