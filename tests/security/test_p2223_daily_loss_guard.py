"""P2223 simulated daily loss guard: isolated, deterministic, no broker connections."""
import importlib.util
from pathlib import Path

MODULE = Path(__file__).resolve().parents[2] / "app/runtime/p2223_broker_emulator.py"
spec = importlib.util.spec_from_file_location("p2223_isolated", MODULE)
p2223 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p2223)

def test_daily_loss_boundary_blocks():
    risk = p2223.RiskEngine()
    assert risk.check(-2999) == "OK"
    assert risk.check(-1) == "KILLED"
    assert risk.check(10000) == "KILLED"

def test_reset_day_preserves_peak():
    risk = p2223.RiskEngine()
    risk.check(-3000)
    peak = risk.peak
    risk.reset_day()
    assert risk.peak == peak
    assert risk.day_start_equity == risk.equity
    assert risk.check(-100) == "OK"

def test_total_drawdown_still_blocks():
    risk = p2223.RiskEngine()
    risk.daily_loss_limit = 1.0
    assert risk.check(-5000) == "KILLED"

def test_paper_only_simulator_contract():
    result = p2223.run_simulation(cycles=0)
    assert result["mode"] == "BROKER_EMULATOR_SIMULATION_ONLY"
    assert result["total_trades"] == 0
