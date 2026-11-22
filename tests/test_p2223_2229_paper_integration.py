import pytest
from app.runtime.p2223_broker_emulator import BrokerEmulator
from app.runtime.p2223_2229_paper_integration import run_paper_pipeline

@pytest.mark.parametrize("cycles", [0, -1, True, 1.5, "3", 1001])
def test_invalid_cycles(cycles):
    with pytest.raises(ValueError, match="P2223_P2229_INVALID_CYCLES"):
        run_paper_pipeline(cycles)

def test_integrated_engines_do_not_place_orders():
    broker = BrokerEmulator()
    result = run_paper_pipeline(3, broker=broker)
    assert result["status"] == "SIMULATION_ONLY_NOT_CERTIFIED"
    assert result["mode"] == "PAPER_ONLY"
    assert result["broker_orders_created"] == 0
    assert result["broker_trades_observed"] == 0
    assert broker.trades == []
    assert len(result["sample"]) == 3
    assert all(set(row) == {"book", "market", "strategies", "crisis", "macro", "ecosystem"} for row in result["sample"])

def test_killed_broker_fails_closed_before_processing():
    broker = BrokerEmulator()
    broker.risk.killed = True
    with pytest.raises(RuntimeError, match="P2223_P2229_RISK_KILLED"):
        run_paper_pipeline(2, broker=broker)
    assert broker.trades == []

def test_wrong_broker_is_rejected():
    with pytest.raises(TypeError, match="P2223_P2229_INVALID_BROKER"):
        run_paper_pipeline(1, broker=object())

def test_broker_remains_unmodified():
    broker = BrokerEmulator()
    before = (broker.risk.equity, broker.risk.peak, broker.risk.day_start_equity)
    run_paper_pipeline(2, broker=broker)
    assert before == (broker.risk.equity, broker.risk.peak, broker.risk.day_start_equity)
