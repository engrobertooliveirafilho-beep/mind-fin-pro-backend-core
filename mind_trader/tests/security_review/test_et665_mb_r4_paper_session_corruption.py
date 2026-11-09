"""ET665.MB.R4: corrupt PAPER session must never permit trading."""
import json
import pytest
from mind_trader.app.execution.paper_session import PaperTradingSessionManager
from mind_trader.app.risk.ftmo_ruleset import save_default_ftmo_config

@pytest.fixture
def session(tmp_path):
    config=tmp_path/"ftmo.json"
    save_default_ftmo_config(str(config))
    return PaperTradingSessionManager(str(tmp_path/"session.json"), str(tmp_path/"day.jsonl"), str(config))

@pytest.mark.parametrize("payload", ["{bad", "null", "[]", '"OPEN"', '{}', '{"status":"OPEN"}'])
def test_corrupt_session_denies_pretrade_and_open(session, payload):
    session.session_path.write_text(payload, encoding="utf-8")
    assert session.pre_trade_check(10)["allowed"] is False
    assert session.open_session()["decision"]=="BLOCK_CORRUPT_PAPER_SESSION"

@pytest.mark.parametrize("field,bad", [
    ("trades", -1), ("trades", True), ("trades", "0"),
    ("max_daily_trades", 0), ("max_daily_trades", True),
    ("daily_pnl", float("nan")), ("daily_pnl", float("inf")),
    ("max_daily_loss", -1), ("max_daily_loss", True),
    ("loss_streak", -1), ("status", "UNKNOWN"), ("session_id", ""),
])
def test_malformed_session_fields_fail_closed(session, field, bad):
    assert session.open_session()["decision"]=="SESSION_OPENED"
    data=json.loads(session.session_path.read_text(encoding="utf-8"))
    data[field]=bad
    session.session_path.write_text(json.dumps(data), encoding="utf-8")
    assert session.pre_trade_check(10)["allowed"] is False
    assert session.open_session()["decision"]=="BLOCK_CORRUPT_PAPER_SESSION"

@pytest.mark.parametrize("risk", [None, [], "10", True, 0, -1, float("nan"), float("inf")])
def test_invalid_risk_amount_denied(session, risk):
    assert session.open_session()["decision"]=="SESSION_OPENED"
    assert session.pre_trade_check(risk)["decision"]=="BLOCK_INVALID_RISK_AMOUNT"

def test_valid_session_retains_pretrade_allow(session):
    assert session.open_session()["decision"]=="SESSION_OPENED"
    assert session.pre_trade_check(10)["allowed"] is True
