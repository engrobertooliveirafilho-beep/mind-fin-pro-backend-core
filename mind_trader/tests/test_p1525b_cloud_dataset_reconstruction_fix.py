import pytest
from app.p1525b_cloud_dataset_reconstruction_fix.engine import metrics, corr, cmd

def test_p1525b_metrics():
    m=metrics([{"return":0.1},{"return":-0.02},{"return":0.03}],[1,1.1,1.078,1.11])
    assert "profit_factor" in m

def test_p1525b_corr():
    assert corr([1,2,3],[1,2,3]) >= 0.99

def test_p1525b_manifest():
    with pytest.raises(PermissionError, match="ET665_RCLONE_COMMAND_NOT_ALLOWLISTED"):
        cmd(["rclone","copy","gdrive:unapproved","/tmp/out","--progress"])
