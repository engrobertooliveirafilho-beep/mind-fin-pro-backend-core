"""Isolated institutional health and symbol lineage contract tests."""
import ast
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import pytest

SOURCE = Path(__file__).resolve().parents[2] / "app/runtime/mind_trader_institutional_wiring.py"
spec = importlib.util.spec_from_file_location("isolated_institutional_wiring", SOURCE)
wiring = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wiring)

@pytest.mark.parametrize("module", [
    None,
    SimpleNamespace(health=lambda: {"status": "ERROR"}, run=lambda payload: {"status": "ok"}),
    SimpleNamespace(health=lambda: {"status": "operational"}, run=lambda payload: {"status": "error"}),
    SimpleNamespace(health=lambda: {"status": "operational"}, run=lambda payload: {"error": "bad"}),
    SimpleNamespace(health=lambda: {"status": "operational"}, run=lambda payload: (_ for _ in ()).throw(RuntimeError("failure"))),
])
def test_failure_never_reports_operational(module):
    with patch.object(wiring, "MODULES", ["mock.module"]):
        if module is None:
            with patch.object(wiring.importlib, "import_module", side_effect=ImportError("missing")):
                result = wiring.run_institutional_wiring({})
        else:
            with patch.object(wiring.importlib, "import_module", return_value=module):
                result = wiring.run_institutional_wiring({})
    assert result["status"] == "DEGRADED"
    assert result["real_orders"] == "FORBIDDEN"


def test_healthy_mock_reports_operational():
    module = SimpleNamespace(health=lambda: {"status": "operational"}, run=lambda payload: {"status": "ok"})
    with patch.object(wiring, "MODULES", ["mock.module"]), patch.object(wiring.importlib, "import_module", return_value=module):
        result = wiring.run_institutional_wiring({"symbol": "EURUSD"})
    assert result["status"] == "operational"


def test_symbol_passes_to_mock_run_without_real_orders():
    seen = []
    module = SimpleNamespace(health=lambda: {"status": "operational"}, run=lambda payload: seen.append(dict(payload)) or {"status": "ok"})
    payload = {"symbol": "EURUSD", "mode": "PAPER_ONLY"}
    with patch.object(wiring, "MODULES", ["mock.module"]), patch.object(wiring.importlib, "import_module", return_value=module):
        result = wiring.run_institutional_wiring(payload)
    assert seen == [payload]
    assert result["mode"] == "PAPER_ONLY"
    assert result["real_orders"] == "FORBIDDEN"


def test_no_symbol_invented_for_missing_input():
    seen = []
    module = SimpleNamespace(health=lambda: {"status": "operational"}, run=lambda payload: seen.append(dict(payload)) or {"status": "ok"})
    with patch.object(wiring, "MODULES", ["mock.module"]), patch.object(wiring.importlib, "import_module", return_value=module):
        wiring.run_institutional_wiring({})
    assert seen == [{}]


def test_factory_does_not_mutate_historical_csv():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    imports = [n for n in ast.walk(tree) if isinstance(n, ast.Import)]
    assert all(alias.name not in ("csv", "sqlite3") for n in imports for alias in n.names)
