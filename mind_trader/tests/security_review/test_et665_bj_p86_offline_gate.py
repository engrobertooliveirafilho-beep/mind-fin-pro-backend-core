"""ET665.BJ: P86 must remain offline and fail closed without MetaTrader5 installed."""
import ast
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
P86 = ROOT / "app/p86_execution_intelligence_domain/engine.py"


def test_p86_contains_no_mt5_import_or_calls():
    tree = ast.parse(P86.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(a.name != "MetaTrader5" for a in node.names)
        if isinstance(node, ast.ImportFrom):
            assert node.module != "MetaTrader5"
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert not (isinstance(node.func.value, ast.Name) and node.func.value.id == "mt5")


def test_p86_snapshot_and_run_fail_closed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    spec = importlib.util.spec_from_file_location("et665_bj_p86", P86)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with pytest.raises(RuntimeError, match="MT5_CONNECTIVITY_DISABLED"):
        module.mt5_snapshot()
    with pytest.raises(RuntimeError, match="MT5_CONNECTIVITY_DISABLED"):
        module.run()
