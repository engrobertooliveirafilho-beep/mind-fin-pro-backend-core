import pytest
from app.runtime.p2101_2110_autonomous_paper_operations import (
    assert_no_financial_execution, Supervisor, ABSOLUTE_LOCKS
)

def test_paper_lock_rejects_explicit_real_order_mode(monkeypatch):
    monkeypatch.setenv("REAL_ORDERS", "ALLOWED")
    with pytest.raises(RuntimeError, match="REAL_ORDERS_LOCK_BREACH"):
        assert_no_financial_execution()
    assert __import__("os").environ["REAL_ORDERS"] == "ALLOWED"

def test_paper_lock_accepts_valid_environment(monkeypatch):
    for k, v in ABSOLUTE_LOCKS.items():
        monkeypatch.setenv(k, v)
    assert_no_financial_execution() is None

def test_supervisor_fails_closed_on_missing_dependencies():
    d = Supervisor().evaluate({})
    assert d.status == "FAIL"

def test_supervisor_rejects_partial_pass():
    d = Supervisor().evaluate({"p2071": {"status": "PASS"}, "p2081": {"status": "PASS"}})
    assert d.status == "FAIL"

def test_supervisor_accepts_complete_pass_declarations():
    d = Supervisor().evaluate({k: {"status": "PASS"} for k in ("p2071", "p2081", "p2091")})
    assert d.status == "PASS"
