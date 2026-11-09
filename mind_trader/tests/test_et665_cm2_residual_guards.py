"""ET665.CM.2 — isolated regression: no rclone/MT5 binaries needed."""
import ast
import subprocess
import importlib.util
from pathlib import Path
from unittest.mock import patch, Mock
import pytest

ROOT = Path(__file__).resolve().parents[1]
P15 = [
    "app/p1516_multi_family_combo_backtest_executor/engine.py",
    "app/p1525b_cloud_dataset_reconstruction_fix/engine.py",
    "app/p153_p155_profit_market_data_pipeline/engine.py",
    "app/p156_p1510_real_edge_research_runtime/engine.py",
]
MT5 = [
    ("reports/P77B_DEMO_ORDER_CHECK_FILLING_MODE_FIX/p77b_filling_check.py", "check"),
    ("reports/P79_DEMO_ORDER_AUDIT_POSITION_MONITOR/p79_monitor.py", "run"),
]

def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

@pytest.mark.parametrize("path", P15)
def test_rclone_read_only_and_exit_failure(path):
    mod = _load(path, "et665_" + path.replace("/", "_"))
    command = getattr(mod, "run_cmd", None) or getattr(mod, "cmd")
    # Arbitrary remote reads and all remote writes must fail before subprocess execution.
    with patch.object(mod.subprocess, "run") as runner:
        with pytest.raises(PermissionError, match="NOT_ALLOWLISTED"):
            command('rclone copy "gdrive:test/raw" "/tmp/et665_read" --progress')
        with pytest.raises(PermissionError):
            command('rclone copy "/tmp/et665_write" "gdrive:test/reports" --progress')
        runner.assert_not_called()

@pytest.mark.parametrize("path", P15)
def test_no_shell_true_and_safe_cleanup(path):
    source = (ROOT / path).read_text(encoding="utf-8")
    tree = ast.parse(source)
    assert not any(isinstance(n, ast.keyword) and n.arg == "shell" and isinstance(n.value, ast.Constant) and n.value.value is True for n in ast.walk(tree))
    mod = _load(path, "et665_safe_" + path.replace("/", "_"))
    with patch.object(mod, "TMP", Path("/")), pytest.raises(PermissionError, match="UNSAFE_TEMP"):
        mod.safe_cleanup()

@pytest.mark.parametrize("path,entrypoint", MT5)
def test_mt5_uncertified_entrypoint_is_blocked(path, entrypoint):
    source = (ROOT / path).read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == entrypoint)
    first = function.body[0]
    assert isinstance(first, ast.Raise)
    assert isinstance(first.exc, ast.Call)
    assert isinstance(first.exc.func, ast.Name) and first.exc.func.id == "PermissionError"
