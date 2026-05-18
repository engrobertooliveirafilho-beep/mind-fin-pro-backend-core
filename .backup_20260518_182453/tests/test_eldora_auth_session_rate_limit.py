from app.eldora.core.jwt_auth import create_token, verify_token
from app.eldora.core.session_memory import save_session, get_session
from app.eldora.core.rate_limit_engine import check_rate_limit
def test_jwt_create_verify():
    r=verify_token(create_token("roberto","default","admin")); assert r["valid"] is True
def test_session_memory():
    save_session("roberto", data={"x":"y"}); assert get_session("roberto")["data"]["x"]=="y"
def test_rate_limit():
    assert check_rate_limit("roberto", limit=2)["allowed"] is True
