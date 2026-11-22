"""Source-isolated tests: original P2296C has historical import-time I/O."""
import ast
from pathlib import Path
import pytest

SOURCE = Path(__file__).resolve().parents[1] / "app/runtime/p2296c_real_exit_engine.py"

def _functions():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    module = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)], type_ignores=[])
    ns = {}
    exec(compile(module, str(SOURCE), "exec"), ns)
    return ns

def _rows():
    base = {"open": 100, "high": 101, "low": 99, "close": 100, "atr_14": 1,
            "body_pct": 0.8, "spread_state": "NORMAL", "trend_21_55": "UP"}
    rows = [dict(base, time=str(i)) for i in range(40)]
    rows[20]["close"] = 99
    return rows

def test_time_exit_is_reachable():
    trades = _functions()["simulate"](_rows(), "TIME_EXIT")
    assert trades and trades[0]["exit_reason"] == "TIME_EXIT"

@pytest.mark.parametrize("model", ["UNKNOWN", "", None, "FTMO_REAL"])
def test_invalid_exit_models_fail_closed(model):
    with pytest.raises(ValueError, match="P2296C_INVALID_EXIT_MODEL"):
        _functions()["simulate"](_rows(), model)

def test_historical_exit_models_are_distinct():
    simulate = _functions()["simulate"]
    signatures = []
    for model in ("TIME_EXIT", "ATR_TARGET", "RR_2_TO_1"):
        trades = simulate(_rows(), model)
        assert trades
        signatures.append(tuple((t["exit_reason"], t["exit"]) for t in trades))
    assert len(set(signatures)) >= 2
