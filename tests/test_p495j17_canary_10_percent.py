import os
from app.api import whatsapp


def test_canary_percent_env_10(monkeypatch):
    monkeypatch.setenv("MIND_ENABLE_CONVERSATION_RECOVERY_CANARY", "1")
    monkeypatch.setenv("MIND_CONVERSATION_RECOVERY_CANARY_PERCENT", "10")
    monkeypatch.delenv("MIND_CONVERSATION_RECOVERY_ALLOWLIST", raising=False)

    hits = 0
    total = 1000
    for i in range(total):
        if whatsapp._p495j16_recovery_canary_enabled(f"user-{i}"):
            hits += 1

    assert 60 <= hits <= 140


def test_allowlist_still_overrides_percent(monkeypatch):
    monkeypatch.setenv("MIND_ENABLE_CONVERSATION_RECOVERY_CANARY", "1")
    monkeypatch.setenv("MIND_CONVERSATION_RECOVERY_CANARY_PERCENT", "0")
    monkeypatch.setenv("MIND_CONVERSATION_RECOVERY_ALLOWLIST", "sender-x")
    assert whatsapp._p495j16_recovery_canary_enabled("sender-x") is True


def test_runtime_identity_on_allowlist_after_percent_patch(monkeypatch):
    monkeypatch.setenv("MIND_ENABLE_CONVERSATION_RECOVERY_CANARY", "1")
    monkeypatch.setenv("MIND_CONVERSATION_RECOVERY_CANARY_PERCENT", "0")
    monkeypatch.setenv("MIND_CONVERSATION_RECOVERY_ALLOWLIST", "sender-x")
    reply = whatsapp.eldora_primary_runtime_reply("sender-x", "qual seu nome")
    assert "Eldora" in reply
