import importlib
import pytest

MODULES = (
    "app.runtime.p2091_2100_realtime_intelligence_layer",
    "app.runtime.p2101_2110_autonomous_paper_operations",
    "app.runtime.p2111_2120_maximum_technical_capacity",
)

@pytest.mark.parametrize("module_name", MODULES)
def test_unsafe_live_mode_is_not_silently_rewritten(module_name, monkeypatch):
    mod = importlib.import_module(module_name)
    monkeypatch.setenv("REAL_ORDERS", "ALLOWED")
    with pytest.raises(RuntimeError, match="REAL_ORDERS_LOCK_BREACH"):
        mod.assert_no_financial_execution()
    assert __import__("os").environ["REAL_ORDERS"] == "ALLOWED"

@pytest.mark.parametrize("module_name", MODULES)
def test_missing_locks_can_be_initialized_to_paper_only(module_name, monkeypatch):
    mod = importlib.import_module(module_name)
    for key in mod.ABSOLUTE_LOCKS:
        monkeypatch.delenv(key, raising=False)
    mod.assert_no_financial_execution()
    for key, value in mod.ABSOLUTE_LOCKS.items():
        assert __import__("os").environ[key] == value
