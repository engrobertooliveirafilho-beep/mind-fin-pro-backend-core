"""P2297 isolated behavior: no dataset, broker, or historical evidence writes."""
import ast
from pathlib import Path
import pytest

SOURCE = Path(__file__).resolve().parents[1] / "app/runtime/p2297_real_exit_segment_wf.py"

def _functions():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    ns = {}
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)], type_ignores=[]), str(SOURCE), "exec"), ns)
    return ns

def _q(**overrides):
    return dict({"exit_model": "TIME_EXIT", "family": "VWAP_REVERSION", "confirmation": "MTF_REQUIRED"}, **overrides)

def test_import_safe():
    import importlib.util
    spec = importlib.util.spec_from_file_location("p2297_isolated", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert callable(module.main)

@pytest.mark.parametrize("exit_model", ["UNKNOWN", None, "FTMO_REAL"])
def test_invalid_exit_model(exit_model):
    q = _q()
    q["exit_model"] = exit_model
    with pytest.raises(ValueError, match="P2297_INVALID_EXIT_MODEL"):
        _functions()["run"]([], q)

@pytest.mark.parametrize("field,value,code", [
    ("family", "UNKNOWN", "P2297_INVALID_FAMILY"),
    ("confirmation", "UNKNOWN", "P2297_INVALID_CONFIRMATION"),
])
def test_invalid_strategy_gates(field, value, code):
    q = _q()
    q[field] = value
    with pytest.raises(ValueError, match=code):
        _functions()["run"]([], q)

def test_empty_rows_cannot_be_approved():
    result = _functions()["run"]([], _q())
    assert result["trades"] == 0 and result["pf"] == 0
