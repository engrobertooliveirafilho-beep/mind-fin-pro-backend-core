import pytest
from app.p121_200x_autonomous_demo_evidence_factory.engine import run

def test_p121_200_runtime():
    with pytest.raises(RuntimeError, match="ET665_BN_MT5_CONNECTIVITY_DISABLED_PENDING_SECURITY_REVIEW"):
        run()
