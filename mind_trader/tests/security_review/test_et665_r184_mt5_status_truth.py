"""ET665 R184: structural non-execution regression. No engines imported or run."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "app"


def source(relative):
    return (ROOT / relative / "engine.py").read_text(encoding="utf-8")


def test_p121_snapshot_is_unconditionally_disabled():
    code = source("p121_200x_autonomous_demo_evidence_factory")
    tree = ast.parse(code)
    snap = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "snapshot")
    assert any(isinstance(n, ast.Raise) for n in snap.body)
    run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run")
    first = run.body[0]
    assert isinstance(first, ast.Assign)
    assert isinstance(first.value, ast.Call)
    assert isinstance(first.value.func, ast.Name) and first.value.func.id == "snapshot"


def test_p121_no_false_certification():
    code = source("p121_200x_autonomous_demo_evidence_factory")
    assert '"MODULES_CERTIFIED":0' in code
    assert '"status":"UNVERIFIED"' in code
    assert '"STATUS":"BLOCKED_PENDING_MT5_SECURITY_REVIEW"' in code


def test_p93_no_false_certification():
    code = source("p93_120x_extended_demo_ftmo_readiness_runtime")
    assert '"MODULES_CERTIFIED":0' in code
    assert '"status":"UNVERIFIED"' in code
    assert '"FINAL_CERTIFICATION_LAYER":"UNVERIFIED"' in code
    assert '"FTMO_RELEASE":release' in code
    assert 'release="BLOCKED_PENDING_30_90_DAY_DEMO_EVIDENCE"' in code


def test_r184_keeps_order_prohibitions():
    for module in ("p121_200x_autonomous_demo_evidence_factory", "p93_120x_extended_demo_ftmo_readiness_runtime"):
        code = source(module)
        assert '"REAL_ORDERS":"FORBIDDEN"' in code
        assert '"FTMO_REAL":"FORBIDDEN"' in code
        assert '"MT5_REAL":"FORBIDDEN"' in code
        assert "order_send(" not in code
