"""ET665.CM.5: structural guard tests; never import or run MT5 entrypoints."""
import ast
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
FUNCTION_GUARDS = [
    ("app/p138_platform_connectors/engine.py", "mt5_probe"),
    ("app/p139_mt5_historical_data_puller/engine.py", "pull"),
    ("reports/P77_DEMO_ORDER_CHECK_ONLY/p77_order_check_only.py", "run"),
    ("reports/P1505_DATA_INGESTION_ENGINE/p1505b_mt5_harvester.py", "run"),
    ("reports/P76A_MT5_CONNECTION_AUDIT/p76a_mt5_connection_audit.py", "run"),
    ("reports/P76A2_MT5_DEMO_VALIDATION_FIX/p76a2_demo_validation_fix.py", "run"),
    ("reports/P76B_MT5_DEMO_ENVIRONMENT_CERTIFICATION/p76b_certify_environment.py", "run"),
]
TOP_LEVEL_GUARDS = [
    "reports/P1804_REAL_MT5_HISTORY_DOWNLOAD_PROBE/p1804_real_mt5_history_download_probe.py",
    "reports/P1805_SYMBOL_DISCOVERY_AND_10Y_NORMALIZATION/p1805_symbol_discovery_10y_normalization.py",
]

def _guarded(node):
    return (isinstance(node, ast.Raise)
        and isinstance(node.exc, ast.Call)
        and isinstance(node.exc.func, ast.Name)
        and node.exc.func.id == "PermissionError"
        and node.exc.args
        and isinstance(node.exc.args[0], ast.Constant)
        and node.exc.args[0].value == "ET665_MT5_UNCERTIFIED_ENTRYPOINT_BLOCKED")

@pytest.mark.parametrize("path,function", FUNCTION_GUARDS)
def test_mt5_function_blocked_before_connection(path, function):
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == function)
    assert _guarded(node.body[0])

@pytest.mark.parametrize("path", TOP_LEVEL_GUARDS)
def test_mt5_top_level_blocked_before_import(path):
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    body = list(tree.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        body.pop(0)  # A module docstring is metadata, not an executable statement.
    assert body and _guarded(body[0])
    assert not any(isinstance(n, (ast.Import, ast.ImportFrom)) and any(a.name == "MetaTrader5" for a in n.names) for n in ast.walk(tree))
