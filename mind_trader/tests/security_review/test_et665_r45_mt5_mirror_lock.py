"""ET665.R45 offline checks: never import MT5 or execute historical engines."""
import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def source(path):
    return subprocess.check_output(["git", "-C", str(ROOT), "show", "HEAD:" + path], timeout=20).decode("utf-8-sig")


def test_p78_mirror_has_no_mt5_transport():
    path = "mind_trader/reports/P78_DEMO_ORDER_SEND_SINGLE_CONTROLLED/p78_demo_order_send.py"
    main = source(path)
    mirror = source("products/eldora_trader/" + path)
    ast.parse(main)
    tree = ast.parse(mirror)
    run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run")
    assert isinstance(run.body[0], ast.Raise)
    assert isinstance(run.body[0].exc, ast.Call)
    assert isinstance(run.body[0].exc.func, ast.Name) and run.body[0].exc.func.id == "PermissionError"
    assert not any(isinstance(n, (ast.Import, ast.ImportFrom)) and
                   ("MetaTrader5" in ast.unparse(n)) for n in ast.walk(tree))
    assert not any(isinstance(n, ast.Attribute) and n.attr in ("order_send", "order_check", "initialize") for n in ast.walk(tree))
    assert '"ORDER_SENT": False' in mirror
    assert "P78_BLOCKED_INSTITUTIONAL" in mirror


def test_p75_mirror_cannot_claim_order_sent():
    path = "mind_trader/app/p75_mt5_demo_order_execution_controlled/engine.py"
    main = source(path)
    mirror = source("products/eldora_trader/" + path)
    assert main == mirror
    ast.parse(mirror)
    assert '"sent_to_mt5_demo":False' in mirror
    assert "DEMO_PERMISSION_ONLY_NOT_SENT" in mirror
    assert "EXECUTION_ARMED=False" in mirror


def test_p77_p79_are_still_fail_closed():
    for suffix in ("reports/P77_DEMO_ORDER_CHECK_ONLY/p77_order_check_only.py",
                   "reports/P79_DEMO_ORDER_AUDIT_POSITION_MONITOR/p79_monitor.py"):
        for prefix in ("mind_trader/", "products/eldora_trader/mind_trader/"):
            tree = ast.parse(source(prefix + suffix))
            run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run")
            assert isinstance(run.body[0], ast.Raise), prefix + suffix
