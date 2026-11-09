import ast
from pathlib import Path

APP = Path(__file__).resolve().parents[2] / "app"

def source(name):
    return (APP / name / "engine.py").read_text(encoding="utf-8")

def test_p86_blocks_before_mkdir():
    tree = ast.parse(source("p86_execution_intelligence_domain"))
    run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run")
    first = run.body[0]
    assert isinstance(first, ast.Assign)
    assert isinstance(first.value, ast.Call)
    assert isinstance(first.value.func, ast.Name)
    assert first.value.func.id == "mt5_snapshot"

def test_p16_disables_unverified_promotion():
    tree = ast.parse(source("p16_autonomous_research_runtime"))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "edge_revalidation_engine")
    matches = [
        n for n in ast.walk(fn)
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "approved" for t in n.targets)
    ]
    assert len(matches) == 1
    assert isinstance(matches[0].value, ast.Constant)
    assert matches[0].value.value is False

def test_no_real_order_execution():
    for name in ("p86_execution_intelligence_domain", "p16_autonomous_research_runtime"):
        text = source(name)
        assert '"REAL_ORDERS":"FORBIDDEN"' in text
        assert '"FTMO_REAL":"FORBIDDEN"' in text
        assert "order_send(" not in text