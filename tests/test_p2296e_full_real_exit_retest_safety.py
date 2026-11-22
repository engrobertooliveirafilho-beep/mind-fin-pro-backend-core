"""P2296E: source-isolated safety regressions; no datasets or broker access."""
import ast
from pathlib import Path
import pytest

SOURCE = Path(__file__).resolve().parents[1] / "app/runtime/p2296e_full_real_exit_retest.py"

def _functions():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    functions = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)], type_ignores=[])
    ns = {}
    exec(compile(functions, str(SOURCE), "exec"), ns)
    return ns

def test_import_safe_main_guard():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    assert any(isinstance(n, ast.FunctionDef) and n.name == "main" for n in tree.body)
    assert not any(isinstance(n, ast.For) for n in tree.body)

@pytest.mark.parametrize("model", ["TIME_EXIT", "ATR_TARGET", "RR_2_TO_1"])
def test_known_models_return_no_trades_for_empty_rows(model):
    fn = _functions()["simulate"]
    q = {"exit_model": model, "family": "VWAP_REVERSAL", "confirmation": "SESSION_REQUIRED"}
    assert fn([], q) == []

def test_metrics_insufficient_trades():
    assert _functions()["metrics"]([1.0, -1.0]) is None
