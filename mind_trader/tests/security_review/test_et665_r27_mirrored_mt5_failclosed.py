"""R27 static regression: mirrored MT5 functions fail closed before any action."""
import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGETS = (
    ("products/eldora_trader/mind_trader/reports/P78_DEMO_ORDER_SEND_SINGLE_CONTROLLED/p78_demo_order_send.py", "run"),
    ("products/eldora_trader/mind_trader/reports/P77_DEMO_ORDER_CHECK_ONLY/p77_order_check_only.py", "run"),
    ("products/eldora_trader/mind_trader/app/p86_execution_intelligence_domain/engine.py", "mt5_snapshot"),
)

def _source(path):
    return subprocess.check_output(["git", "-C", str(ROOT), "show", "HEAD:" + path], timeout=15).decode("utf-8-sig")

def test_r27_mirror_first_statement_is_unconditional_permission_denial():
    for path, func in TARGETS:
        tree = ast.parse(_source(path), filename=path)
        functions = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == func]
        assert len(functions) == 1, path
        first = functions[0].body[0]
        assert isinstance(first, ast.Raise), path
        assert isinstance(first.exc, ast.Call), path
        assert isinstance(first.exc.func, ast.Name) and first.exc.func.id == "PermissionError", path
        assert first.exc.args and isinstance(first.exc.args[0], ast.Constant), path
        assert str(first.exc.args[0].value).startswith("ET665_R27_"), path

def test_r27_no_top_level_mt5_connect_or_send():
    for path, _ in TARGETS:
        tree = ast.parse(_source(path), filename=path)
        for node in tree.body:
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                raise AssertionError("TOP_LEVEL_CALL_REQUIRES_REVIEW:" + path)
