"""ET665.R339: fail-closed PAPER result accounting guards."""
import json
from mind_trader.tests.test_p896_gateway_paper_broker_integration import gateway


def test_record_trade_rejects_session_limit_tampering(tmp_path):
    g = gateway(tmp_path)
    path = tmp_path / "session.json"
    original = json.loads(path.read_text(encoding="utf-8"))
    altered = dict(original, max_daily_trades=original["max_daily_trades"] + 1)
    path.write_text(json.dumps(altered), encoding="utf-8")
    result = g.paper.record_trade_result(-100)
    assert result["decision"] == "BLOCK_RECORD_SESSION_LIMIT_TAMPERING"
    assert json.loads(path.read_text(encoding="utf-8")) == altered


def test_record_trade_rejects_ftmo_hash_drift(tmp_path):
    g = gateway(tmp_path)
    path = tmp_path / "session.json"
    original = json.loads(path.read_text(encoding="utf-8"))
    altered = dict(original, ftmo_config_hash="invalid")
    path.write_text(json.dumps(altered), encoding="utf-8")
    result = g.paper.record_trade_result(-100)
    assert result["decision"] == "BLOCK_RECORD_FTMO_CONFIG_DRIFT"
    assert json.loads(path.read_text(encoding="utf-8")) == altered
