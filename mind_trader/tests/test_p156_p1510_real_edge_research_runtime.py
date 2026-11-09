import pytest
from app.p156_p1510_real_edge_research_runtime.engine import backtest, walk_forward, monte_carlo, cmd

def test_p156_backtest_runs():
    rows=[{"close":float(i)} for i in range(1,200)]
    r=backtest(rows,5,21)
    assert "profit_factor" in r
    assert "trades" in r

def test_p157_walk_forward_safe():
    rows=[{"close":float(i)} for i in range(1,200)]
    r=walk_forward(rows,5,21)
    assert "approved" in r

def test_p158_monte_carlo_safe():
    r=monte_carlo([0.01,-0.005,0.02,-0.01,0.015,0.005,-0.002,0.01,0.003,0.004])
    assert "approved" in r

def test_p1510_manifest():
    with pytest.raises(PermissionError, match="ET665_RCLONE_COMMAND_NOT_ALLOWLISTED"):
        cmd(["rclone","copy","gdrive:unapproved","/tmp/out","--progress"])
