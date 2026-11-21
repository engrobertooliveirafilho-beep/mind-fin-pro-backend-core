import pytest
from app.runtime.p2081_2090_realtime_portfolio_governance import assert_no_financial_execution, ABSOLUTE_LOCKS

@pytest.mark.parametrize("key,bad", [
    ("MIND_MODE", "LIVE"),
    ("REAL_ORDERS", "ALLOWED"),
    ("BROKER_EXECUTION", "ENABLED"),
    ("MT5_ORDER_SEND", "ENABLED"),
])
def test_p2081_rejects_unsafe_environment_without_masking(monkeypatch, key, bad):
    for name, expected in ABSOLUTE_LOCKS.items():
        monkeypatch.setenv(name, expected)
    monkeypatch.setenv(key, bad)
    with pytest.raises(RuntimeError, match=f"{key}_LOCK_BREACH"):
        assert_no_financial_execution()
    assert __import__("os").environ[key] == bad

def test_p2081_initializes_missing_paper_locks(monkeypatch):
    for name in ABSOLUTE_LOCKS:
        monkeypatch.delenv(name, raising=False)
    assert_no_financial_execution()
    for name, expected in ABSOLUTE_LOCKS.items():
        assert __import__("os").environ[name] == expected
