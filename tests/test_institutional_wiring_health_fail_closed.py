"""Health must be side-effect free and must not imply E2E certification."""
import ast
from pathlib import Path


def test_health_never_calls_runtime_or_imports_modules(monkeypatch):
    from app.runtime import mind_trader_institutional_wiring as wiring

    def forbidden(*args, **kwargs):
        raise AssertionError("health triggered runtime execution")

    monkeypatch.setattr(wiring, "run_institutional_wiring", forbidden)
    monkeypatch.setattr(wiring.importlib, "import_module", forbidden)
    result = wiring.health()
    assert result["status"] == "NOT_CERTIFIED"
    assert result["runs_ok"] is None
    assert result["reason"] == "RUNTIME_EVIDENCE_NOT_VERIFIED"


def test_wiring_summary_does_not_claim_operational():
    from app.runtime import mind_trader_institutional_wiring as wiring

    # Inspect function source without invoking external modules.
    source = Path(wiring.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
              and n.name == "run_institutional_wiring")
    status_values = [
        node.value for node in ast.walk(fn)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        and node.value in ("operational", "NOT_CERTIFIED")
    ]
    assert "NOT_CERTIFIED" in status_values
    assert "operational" not in status_values
