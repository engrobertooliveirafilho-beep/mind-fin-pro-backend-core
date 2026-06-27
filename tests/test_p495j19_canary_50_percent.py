from app.api import whatsapp


def test_canary_percent_env_50(monkeypatch):
    monkeypatch.setenv("MIND_ENABLE_CONVERSATION_RECOVERY_CANARY", "1")
    monkeypatch.setenv("MIND_CONVERSATION_RECOVERY_CANARY_PERCENT", "50")
    monkeypatch.delenv("MIND_CONVERSATION_RECOVERY_ALLOWLIST", raising=False)

    hits = sum(
        1 for i in range(1000)
        if whatsapp._p495j16_recovery_canary_enabled(f"user-{i}")
    )

    assert 450 <= hits <= 550


def test_canary_off_still_blocks_50(monkeypatch):
    monkeypatch.setenv("MIND_ENABLE_CONVERSATION_RECOVERY_CANARY", "0")
    monkeypatch.setenv("MIND_CONVERSATION_RECOVERY_CANARY_PERCENT", "50")
    assert whatsapp._p495j16_recovery_canary_enabled("user-1") is False


def test_capability_response_under_50_allowlist(monkeypatch):
    monkeypatch.setenv("MIND_ENABLE_CONVERSATION_RECOVERY_CANARY", "1")
    monkeypatch.setenv("MIND_CONVERSATION_RECOVERY_CANARY_PERCENT", "50")
    monkeypatch.setenv("MIND_CONVERSATION_RECOVERY_ALLOWLIST", "sender-x")
    reply = whatsapp.eldora_primary_runtime_reply("sender-x", "o que você faz?")
    assert "ajudo" in reply.lower()
