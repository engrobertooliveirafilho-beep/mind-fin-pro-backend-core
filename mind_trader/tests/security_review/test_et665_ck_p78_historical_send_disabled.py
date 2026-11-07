"""Offline regression for the historical P78 MT5 order-send entrypoint."""
import importlib.util
from pathlib import Path
import sys

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "reports" / "P78_DEMO_ORDER_SEND_SINGLE_CONTROLLED" / "p78_demo_order_send.py"


@pytest.mark.parametrize("symbol,lot", [
    ("EURUSD", 0.01),
    ("XAUUSD", 100),
    ("", -1),
])
def test_p78_never_connects_to_mt5_or_sends_orders(tmp_path, monkeypatch, symbol, lot):
    monkeypatch.chdir(tmp_path)
    class ForbiddenMT5:
        def __getattr__(self, key):
            raise AssertionError("MT5_ACCESS_FORBIDDEN:" + key)
    monkeypatch.setitem(sys.modules, "MetaTrader5", ForbiddenMT5())
    spec = importlib.util.spec_from_file_location("et665_ck_p78", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.run(symbol=symbol, lot=lot)
    assert result["STATUS"] == "P78_BLOCKED_INSTITUTIONAL"
    assert result["ORDER_SENT"] is False
    assert result["REAL_ORDERS"] == "FORBIDDEN"
    assert result["FTMO_REAL"] == "FORBIDDEN"
    assert (tmp_path / "reports/P78_DEMO_ORDER_SEND_SINGLE_CONTROLLED/p78_report.json").exists()


def test_p78_has_no_mt5_import_or_order_send():
    import ast
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    assert not any(
        isinstance(node, (ast.Import, ast.ImportFrom)) and
        ("MetaTrader5" in ast.unparse(node))
        for node in ast.walk(tree)
    )
    assert not any(
        isinstance(node, ast.Attribute) and node.attr in ("order_send", "order_check", "initialize")
        for node in ast.walk(tree)
    )
