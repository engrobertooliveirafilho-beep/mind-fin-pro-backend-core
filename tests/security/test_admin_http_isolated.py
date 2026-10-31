"""HTTP auth regression without a real database."""
import importlib.util
import os
import sys
import types
from pathlib import Path
from unittest.mock import patch
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

fake = types.ModuleType("psycopg2")
fake.__path__ = []
fake.extras = types.ModuleType("psycopg2.extras")
fake.extras.RealDictCursor = object
def no_real_db(*args, **kwargs):
    raise AssertionError("REAL_DATABASE_ACCESS_FORBIDDEN")
fake.connect = no_real_db
sys.modules["psycopg2"] = fake
sys.modules["psycopg2.extras"] = fake.extras
source = Path(__file__).resolve().parents[2] / "app/admin/public_runtime.py"
spec = importlib.util.spec_from_file_location("isolated_admin", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
app = FastAPI()
app.include_router(module.router)
client = TestClient(app)

@pytest.mark.parametrize("secret,token", [
    (None, None), (None, "anything"), ("", None), ("", "anything"),
    ("expected", None), ("expected", ""), ("expected", "wrong"),
])
def test_http_403(secret, token):
    env = {} if secret is None else {"ADMIN_ACTIVATION_TOKEN": secret}
    headers = {} if token is None else {"x-admin-token": token}
    with patch.dict(os.environ, env, clear=True):
        response = client.post("/admin/neura/public/activate", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "forbidden"

def test_valid_token_reaches_mock_only(monkeypatch):
    calls = []
    def mock_db():
        calls.append(True)
        raise RuntimeError("MOCK_DB_REACHED")
    monkeypatch.setattr(module, "db", mock_db)
    with patch.dict(os.environ, {"ADMIN_ACTIVATION_TOKEN": "expected"}, clear=True):
        with pytest.raises(RuntimeError, match="MOCK_DB_REACHED"):
            client.post("/admin/neura/public/activate", headers={"x-admin-token": "expected"})
    assert calls == [True]
