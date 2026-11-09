"""R308 PAPER session behavioral regressions; no network or broker access."""
import json

from mind_trader.app.execution import paper_session as module


def _manager(tmp_path, monkeypatch, pnl=0.0, config_hash="trusted"):
    monkeypatch.setattr(module, "load_ftmo_config", lambda _: (
        {"max_daily_loss": 100.0}, {"valid": True, "hash": "trusted"}
    ))
    manager = module.PaperTradingSessionManager(
        str(tmp_path / "session.json"),
        str(tmp_path / "events.jsonl"),
        str(tmp_path / "rules.json"),
    )
    (tmp_path / "session.json").write_text(json.dumps({
        "session_id": "paper-test", "status": "OPEN", "trades": 0,
        "max_daily_trades": 10, "daily_pnl": pnl, "max_daily_loss": 100.0,
        "loss_streak": 0, "ftmo_config_hash": config_hash,
    }), encoding="utf-8")
    return manager


def test_r308_matching_config_and_positive_pnl_do_not_consume_loss_limit(tmp_path, monkeypatch):
    manager = _manager(tmp_path, monkeypatch, pnl=80.0)
    result = manager.pre_trade_check(50.0)
    assert result["allowed"] is True
    assert result["decision"] == "ALLOW_PAPER_TRADE"


def test_r308_realized_losses_consume_daily_limit(tmp_path, monkeypatch):
    manager = _manager(tmp_path, monkeypatch, pnl=-80.0)
    result = manager.pre_trade_check(30.0)
    assert result["allowed"] is False
    assert result["decision"] == "BLOCK_DAILY_LOSS_LIMIT"


def test_r308_changed_config_hash_blocks_before_trade(tmp_path, monkeypatch):
    manager = _manager(tmp_path, monkeypatch, config_hash="stale")
    result = manager.pre_trade_check(10.0)
    assert result["allowed"] is False
    assert result["decision"] == "BLOCK_PAPER_SESSION_FTMO_CONFIG_DRIFT"


def test_r308_invalid_config_blocks_before_trade(tmp_path, monkeypatch):
    manager = _manager(tmp_path, monkeypatch)
    monkeypatch.setattr(module, "load_ftmo_config", lambda _: (None, {"valid": False}))
    result = manager.pre_trade_check(10.0)
    assert result["allowed"] is False
    assert result["decision"] == "BLOCK_PAPER_SESSION_FTMO_CONFIG_DRIFT"
