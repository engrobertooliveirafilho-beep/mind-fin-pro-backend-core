"""R46 offline static checks; historical MT5 entrypoints must fail closed."""
import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TARGETS = (
    "reports/P77_DEMO_ORDER_CHECK_ONLY/p77_order_check_only.py",
    "reports/P79_DEMO_ORDER_AUDIT_POSITION_MONITOR/p79_monitor.py",
)


def source(path):
    return subprocess.check_output(["git", "-C", str(ROOT), "show", "HEAD:" + path], timeout=20).decode("utf-8-sig")


def test_r46_mt5_entrypoints_are_terminal_free_and_fail_closed():
    for suffix in TARGETS:
        for prefix in ("mind_trader/", "products/eldora_trader/mind_trader/"):
            path = prefix + suffix
            text = source(path)
            tree = ast.parse(text, filename=path)
            assert "MetaTrader5" not in text, path
            assert not any(isinstance(n, ast.Attribute) and n.attr in
                           ("initialize", "order_send", "order_check", "positions_get")
                           for n in ast.walk(tree)), path
            runs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run"]
            assert len(runs) == 1, path
            assert len(runs[0].body) == 1, path
            first = runs[0].body[0]
            assert isinstance(first, ast.Raise), path
            assert isinstance(first.exc, ast.Call) and isinstance(first.exc.func, ast.Name), path
            assert first.exc.func.id == "PermissionError", path
