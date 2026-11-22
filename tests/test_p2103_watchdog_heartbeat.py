import pytest
from app.runtime.p2101_2110_autonomous_paper_operations import Watchdog

@pytest.mark.parametrize("heartbeat", ["alive", None, True, -1, 0, {}, []])
def test_p2103_watchdog_rejects_malformed_heartbeat(heartbeat):
    result = Watchdog().evaluate({"heartbeat": heartbeat, "runtime_status": "RUNNING"})
    assert result.status == "FAIL"
    assert result.payload["heartbeat_present"] is False

def test_p2103_watchdog_accepts_valid_heartbeat():
    result = Watchdog().evaluate({"heartbeat": 123, "runtime_status": "RUNNING"})
    assert result.status == "PASS"
