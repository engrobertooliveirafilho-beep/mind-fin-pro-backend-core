from app.eldora.core.tenant_engine import resolve_tenant
from app.eldora.core.auth_context import build_auth_context
from app.eldora.core.rbac import has_permission
from app.eldora.core.policy_engine import evaluate_policy

def test_tenant_default():
    assert resolve_tenant()["tenant_id"] == "default"

def test_auth_context_guest():
    ctx = build_auth_context()
    assert ctx["role"] == "guest"
    assert ctx["authenticated"] is False

def test_rbac_admin():
    assert has_permission("admin", "apply_schema") is True

def test_policy_guest_denied_admin_action():
    result = evaluate_policy("guest", "apply_schema")
    assert result["allowed"] is False

def test_policy_user_runtime_allowed():
    result = evaluate_policy("user", "use_runtime")
    assert result["allowed"] is True
