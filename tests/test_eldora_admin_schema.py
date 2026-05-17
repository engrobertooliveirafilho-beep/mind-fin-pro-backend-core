from fastapi.testclient import TestClient
from app.main import app

def test_admin_schema_hidden_by_default():
    client = TestClient(app)
    r = client.post("/eldora/admin/apply-schema")
    assert r.status_code == 404
