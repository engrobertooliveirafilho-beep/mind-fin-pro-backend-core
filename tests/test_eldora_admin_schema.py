from fastapi.testclient import TestClient
from app.main import app

def test_eldora_admin_schema_forbidden_without_token():
    client = TestClient(app)
    r = client.post("/eldora/admin/apply-schema")
    assert r.status_code == 403
