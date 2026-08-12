from app.main import app

def test_usde_run_file_route_registered():
    paths = [r.path for r in app.routes]
    assert "/usde/run-file" in paths
