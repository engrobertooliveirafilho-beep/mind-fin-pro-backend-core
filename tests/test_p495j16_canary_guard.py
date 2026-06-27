import os
from app.api import whatsapp


def test_canary_off_by_default(monkeypatch):
    monkeypatch.delenv("MIND_ENABLE_CONVERSATION_RECOVERY_CANARY", raising=False)
    assert whatsapp._p495j16_recovery_canary_enabled("x") is False


def test_canary_allowlist(monkeypatch):
    monkeypatch.setenv("MIND_ENABLE_CONVERSATION_RECOVERY_CANARY", "1")
    monkeypatch.setenv("MIND_CONVERSATION_RECOVERY_ALLOWLIST", "user123")
    assert whatsapp._p495j16_recovery_canary_enabled("user123") is True


def test_apply_recovery_enabled(monkeypatch):
    monkeypatch.setenv("MIND_ENABLE_CONVERSATION_RECOVERY_CANARY", "1")
    monkeypatch.setenv("MIND_CONVERSATION_RECOVERY_ALLOWLIST", "user123")
    result = whatsapp._p495j16_apply_recovery_if_enabled("qual seu nome", "user123", "teste", {})
    assert result["enabled"] is True
    assert result["signal"]["intent"] == "identity"
