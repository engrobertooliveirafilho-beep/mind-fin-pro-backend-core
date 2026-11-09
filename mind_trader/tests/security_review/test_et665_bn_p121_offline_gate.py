"""ET665.BN — offline security regression for P121-200."""
import ast
import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "app/p121_200x_autonomous_demo_evidence_factory/engine.py"

def test_p121_no_metatrader_import_or_calls():
    tree = ast.parse(TARGET.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(alias.name != "MetaTrader5" for alias in node.names)
        if isinstance(node, ast.ImportFrom):
            assert node.module != "MetaTrader5"
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert not (isinstance(node.func.value, ast.Name) and node.func.value.id == "mt5")

def test_p121_snapshot_and_run_fail_closed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    spec = importlib.util.spec_from_file_location("et665_bn_p121", TARGET)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with pytest.raises(RuntimeError, match="MT5_CONNECTIVITY_DISABLED"):
        module.snapshot()
    with pytest.raises(RuntimeError, match="MT5_CONNECTIVITY_DISABLED"):
        module.run()
