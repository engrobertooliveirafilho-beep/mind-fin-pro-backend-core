import os
import pytest
from fastapi import HTTPException
from app.eldora.core.jwt_auth import create_token, verify_token
from app.eldora.core.auth_context import build_auth_context
from app.eldora.security.service import require_admin_token
from app.api.eldora_auth import token, session_get
from app.api.eldora_security import tenant

@pytest.fixture(autouse=True)
def jwt_secret(monkeypatch):
    monkeypatch.setenv("ELDORA_JWT_SECRET", "test-secret-for-isolated-tests-only-0123456789")

def test_valid_and_expired_jwt():
    assert verify_token(create_token("u1","t1","user"))["valid"]
    assert not verify_token(create_token("u1","t1","user",ttl_seconds=1).rsplit(".",1)[0] + ".invalid")["valid"]

def test_missing_secret_fails_closed(monkeypatch):
    monkeypatch.delenv("ELDORA_JWT_SECRET", raising=False)
    with pytest.raises(RuntimeError):
        create_token("u1","t1","user")

def test_admin_requires_signed_admin_claim():
    assert not require_admin_token("any-string-with-length")
    assert not require_admin_token(create_token("u1","t1","user"))
    assert require_admin_token(create_token("u1","t1","admin"))

def test_context_ignores_untrusted_parameters():
    assert not build_auth_context("admin","other","admin")["authenticated"]
    ctx = build_auth_context("fake","other","admin",token=create_token("u1","t1","user"))
    assert (ctx["user_id"],ctx["tenant_id"],ctx["role"]) == ("u1","t1","user")

@pytest.mark.asyncio
async def test_token_minting_disabled():
    with pytest.raises(HTTPException) as exc:
        await token()
    assert exc.value.status_code == 403

@pytest.mark.asyncio
async def test_cross_tenant_session_blocked():
    with pytest.raises(HTTPException) as exc:
        await session_get("u1","t2",authorization="Bearer "+create_token("u1","t1","user"))
    assert exc.value.status_code == 403

@pytest.mark.asyncio
async def test_cross_tenant_security_blocked():
    with pytest.raises(HTTPException) as exc:
        await tenant("t2",authorization="Bearer "+create_token("u1","t1","user"))
    assert exc.value.status_code == 403
