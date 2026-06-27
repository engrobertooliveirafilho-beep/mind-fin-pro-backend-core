import os
from app.api import whatsapp


def test_p495j16b_identity_runtime_wiring(monkeypatch):
    monkeypatch.setenv("MIND_ENABLE_CONVERSATION_RECOVERY_CANARY", "1")
    monkeypatch.setenv("MIND_CONVERSATION_RECOVERY_ALLOWLIST", "sender-x")
    reply = whatsapp.eldora_primary_runtime_reply("sender-x", "qual seu nome")
    assert "Eldora" in reply


def test_p495j16b_capability_runtime_wiring(monkeypatch):
    monkeypatch.setenv("MIND_ENABLE_CONVERSATION_RECOVERY_CANARY", "1")
    monkeypatch.setenv("MIND_CONVERSATION_RECOVERY_ALLOWLIST", "sender-x")
    reply = whatsapp.eldora_primary_runtime_reply("sender-x", "o que você faz?")
    assert "ajudo" in reply.lower()


def test_p495j16b_canary_off_does_not_direct_reply(monkeypatch):
    monkeypatch.delenv("MIND_ENABLE_CONVERSATION_RECOVERY_CANARY", raising=False)
    result = whatsapp._p495j16_apply_recovery_if_enabled("qual seu nome", "sender-x", None, {})
    assert result["enabled"] is False
