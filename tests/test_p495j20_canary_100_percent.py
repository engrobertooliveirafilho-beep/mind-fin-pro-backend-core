from app.api import whatsapp


def test_canary_percent_env_100(monkeypatch):
    monkeypatch.setenv("MIND_ENABLE_CONVERSATION_RECOVERY_CANARY", "1")
    monkeypatch.setenv("MIND_CONVERSATION_RECOVERY_CANARY_PERCENT", "100")
    monkeypatch.delenv("MIND_CONVERSATION_RECOVERY_ALLOWLIST", raising=False)
    assert all(whatsapp._p495j16_recovery_canary_enabled(f"user-{i}") for i in range(300))


def test_canary_off_still_blocks_100(monkeypatch):
    monkeypatch.setenv("MIND_ENABLE_CONVERSATION_RECOVERY_CANARY", "0")
    monkeypatch.setenv("MIND_CONVERSATION_RECOVERY_CANARY_PERCENT", "100")
    assert whatsapp._p495j16_recovery_canary_enabled("user-1") is False


def test_identity_response_under_100(monkeypatch):
    monkeypatch.setenv("MIND_ENABLE_CONVERSATION_RECOVERY_CANARY", "1")
    monkeypatch.setenv("MIND_CONVERSATION_RECOVERY_CANARY_PERCENT", "100")
    monkeypatch.delenv("MIND_CONVERSATION_RECOVERY_ALLOWLIST", raising=False)
    reply = whatsapp.eldora_primary_runtime_reply("any-user", "qual seu nome")
    assert "Eldora" in reply
