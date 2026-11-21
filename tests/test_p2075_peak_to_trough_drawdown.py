import pytest
from app.runtime.p2071_2080_realtime_paper_runtime import RuntimeMonitor, PaperPortfolioExecutor

def test_max_drawdown_tracks_intermediate_peak_to_trough():
    monitor = RuntimeMonitor(100000.0)
    for equity in (102000.0, 97000.0, 99500.0):
        monitor.record_equity(equity)
    executor = PaperPortfolioExecutor(99500.0)
    snapshot = monitor.snapshot(executor)
    assert snapshot["drawdown_abs"] == -2500.0
    assert snapshot["max_drawdown_abs"] == 5000.0
    assert snapshot["max_drawdown_pct"] == pytest.approx(5000.0 / 102000.0)

def test_drawdown_is_zero_if_equity_never_falls():
    monitor = RuntimeMonitor(100000.0)
    monitor.record_equity(101000.0)
    executor = PaperPortfolioExecutor(102000.0)
    snapshot = monitor.snapshot(executor)
    assert snapshot["drawdown_abs"] == 0
    assert snapshot["max_drawdown_abs"] == 0
    assert snapshot["max_drawdown_pct"] == 0

def test_negative_pnl_cannot_have_zero_drawdown():
    monitor = RuntimeMonitor(100000.0)
    executor = PaperPortfolioExecutor(99030.6331)
    snapshot = monitor.snapshot(executor)
    assert snapshot["drawdown_abs"] < 0
    assert snapshot["max_drawdown_abs"] > 0
    assert snapshot["max_drawdown_pct"] > 0
