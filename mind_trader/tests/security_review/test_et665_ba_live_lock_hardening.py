"""ET665.BA: institutional lock security regressions (offline, PAPER only)."""
import json
from unittest.mock import patch

from mind_trader.app.security.institutional_live_lock import (
    FORBIDDEN_ACTIONS,
    ALLOWED_RESEARCH_ACTIONS,
    institutional_live_lock,
    assert_not_live_action,
)


def test_all_forbidden_actions_fail_closed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for action in FORBIDDEN_ACTIONS:
        result = institutional_live_lock(action, {"token": "DO_NOT_PERSIST", "order": {"symbol": "WIN"}})
        assert result["blocked"] is True
        assert result["decision"] == "FORCE_BLOCK_LIVE_OR_PRODUCTION"
        assert result["production"] == "BLOCKED"
        assert result["live"] == "FORBIDDEN"
        assert result["payload_redacted"] is True
        assert result["audit_persisted"] is True
        data = (tmp_path / "mind_trader/reports/P8.92_institutional_live_lock.json").read_text()
        assert "DO_NOT_PERSIST" not in data
        assert '"order"' not in data


def test_unknown_and_malformed_actions_fail_closed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for action in ("NEW_BROKER_ROUTE", "LIVE", "", None, 123, ["PAPER"]):
        result = institutional_live_lock(action, {"api_key": "DO_NOT_PERSIST"})
        assert result["blocked"] is True
        assert result["decision"] == "BLOCK_UNKNOWN_ACTION"
        assert assert_not_live_action(action)[0] is False


def test_explicit_research_modes_only(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for action in ALLOWED_RESEARCH_ACTIONS:
        result = institutional_live_lock(action)
        assert result["blocked"] is False
        assert result["decision"] == "ALLOW_NON_LIVE_RESEARCH_ACTION"


def test_read_only_audit_failure_does_not_bypass_lock(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with patch("pathlib.Path.write_text", side_effect=PermissionError("read-only")):
        result = institutional_live_lock("BROKER_SEND_ORDER", {"secret": "DO_NOT_PERSIST"})
    assert result["blocked"] is True
    assert result["decision"] == "FORCE_BLOCK_LIVE_OR_PRODUCTION"
    assert result["audit_persisted"] is False


def test_gateway_live_mode_remains_blocked_when_audit_write_fails(tmp_path, monkeypatch):
    from mind_trader.app.execution.gateway import ExecutionGateway
    from mind_trader.app.risk.ftmo_ruleset import save_default_ftmo_config

    monkeypatch.chdir(tmp_path)
    config = tmp_path / "ftmo.json"
    save_default_ftmo_config(str(config))
    gateway = ExecutionGateway(
        str(tmp_path / "execution.jsonl"), str(config),
        str(tmp_path / "session.json"), str(tmp_path / "day.jsonl"),
        str(tmp_path / "broker.jsonl"),
    )
    with patch("pathlib.Path.write_text", side_effect=PermissionError("read-only")):
        result = gateway.submit_order("LIVE", {"symbol": "WIN", "token": "SENSITIVE"}, {}, {})
    assert result["decision"] == "FORCE_BLOCK_LIVE_OR_PRODUCTION"
    assert result["live_lock"]["blocked"] is True
    assert result["live_lock"]["audit_persisted"] is False
