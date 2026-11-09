"""ET665.R48: offline static regression for uncertified MT5 entrypoints."""
import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TARGETS = {
    "reports/DAILY_DEMO_EVIDENCE_COLLECTION/collect_daily_demo_evidence.py": "run",
    "reports/P1505_DATA_INGESTION_ENGINE/p1505b_mt5_harvester.py": "run",
    "reports/P76A2_MT5_DEMO_VALIDATION_FIX/p76a2_demo_validation_fix.py": "run",
    "reports/P76A_MT5_CONNECTION_AUDIT/p76a_mt5_connection_audit.py": "run",
    "reports/P76B_MT5_DEMO_ENVIRONMENT_CERTIFICATION/p76b_certify_environment.py": "run",
    "reports/P77B_DEMO_ORDER_CHECK_FILLING_MODE_FIX/p77b_filling_check.py": "check",
    "app/p138_platform_connectors/engine.py": "mt5_probe",
    "app/p139_mt5_historical_data_puller/engine.py": "pull",
}


def test_r48_no_mt5_import_or_terminal_calls_in_remediated_sources():
    for suffix, fn in TARGETS.items():
        path = "mind_trader/" + suffix
        source = subprocess.check_output(["git", "-C", str(ROOT), "show", "HEAD:" + path], timeout=20).decode("utf-8-sig")
        tree = ast.parse(source)
        assert "MetaTrader5" not in source, path
        assert not any(isinstance(n, ast.Attribute) and n.attr in ("order_send", "order_check", "initialize", "positions_get") for n in ast.walk(tree)), path
        functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == fn]
        assert len(functions) == 1, path
        first = functions[0].body[0]
        assert isinstance(first, ast.Raise), path
        assert isinstance(first.exc, ast.Call) and isinstance(first.exc.func, ast.Name) and first.exc.func.id == "PermissionError", path
